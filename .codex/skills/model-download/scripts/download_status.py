#!/usr/bin/env python3
"""Print a read-only ASCII report for downloads managed in ._____temp."""

from __future__ import annotations

import os
import json
import hashlib
import argparse
import re
import shutil
import time
import unicodedata
from pathlib import Path


ROOT = Path.cwd()
TEMP = ROOT / "._____temp"
TARGET_DIRS = {
    "diffusion_models",
    "text_encoders",
    "vae",
    "loras",
    "embeddings",
    "clip_vision",
    "upscale_models",
    "latent_upscale_models",
}
UNIT = {"K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except OSError:
        return ""


def process_command(pid: int) -> str:
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
        return " ".join(part.decode(errors="replace") for part in raw.split(b"\0") if part)
    except OSError:
        return ""


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def model_path(command: str, stage_dir: Path, task_name: str, log_text: str) -> Path | None:
    values = re.findall(r"[^\s\"']+\.safetensors", f"{command}\n{log_text}")
    for value in values:
        name = Path(value).name
        candidate = stage_dir / name
        if candidate.exists():
            return candidate
        relative = Path(value.lstrip("./"))
        if not relative.is_absolute() and ".." not in relative.parts:
            candidate = ROOT / relative
            if candidate.is_file():
                return candidate
        for target_dir in ROOT.iterdir():
            candidate = target_dir / name
            if candidate.is_file():
                return candidate
    candidates = sorted(stage_dir.glob("*.safetensors"))
    if len(candidates) == 1:
        return candidates[0]

    # ModelScope may move a completed file directly into the formal target
    # directory when --local_dir is the model root.
    formal = ROOT / stage_dir.name / f"{task_name}.safetensors"
    if formal.exists():
        return formal

    # Older tasks used a human-readable task slug that differs from the
    # downloaded filename (for example hyphens versus underscores).
    normalized_task = re.sub(r"[^a-z0-9]", "", task_name.lower())
    if normalized_task:
        for target_dir in ROOT.iterdir():
            if not target_dir.is_dir() or target_dir.name.startswith("."):
                continue
            for candidate in target_dir.glob("*.safetensors"):
                normalized_name = re.sub(r"[^a-z0-9]", "", candidate.stem.lower())
                if normalized_task in normalized_name or normalized_name in normalized_task:
                    return candidate
    return None


def metadata_size(path: Path) -> int | None:
    try:
        data = json.loads(path.read_text(errors="replace"))
    except (OSError, json.JSONDecodeError):
        return None
    value = data.get("size")
    return int(value) if isinstance(value, (int, float)) and value > 0 else None


def metadata_hash(path: Path) -> str | None:
    try:
        data = json.loads(path.read_text(errors="replace"))
    except (OSError, json.JSONDecodeError):
        return None
    for key in ("sha256", "etag", "hash"):
        value = str(data.get(key, "")).strip().strip('"')
        if re.fullmatch(r"[0-9a-fA-F]{64}", value):
            return value.lower()
    return None


def local_sha256(path: Path, cache_path: Path) -> str | None:
    if not path.is_file():
        return None
    size = path.stat().st_size
    try:
        cached_size, cached_digest = cache_path.read_text().strip().split(maxsplit=1)
        if int(cached_size) == size and re.fullmatch(r"[0-9a-fA-F]{64}", cached_digest):
            return cached_digest.lower()
    except (OSError, ValueError):
        pass
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                digest.update(block)
    except OSError:
        return None
    value = digest.hexdigest()
    try:
        cache_path.write_text(f"{size} {value}\n")
    except OSError:
        pass
    return value


def total_bytes(text: str) -> int | None:
    values = []
    for number, suffix in re.findall(r"(?:/|\s)([0-9]+(?:\.[0-9]+)?)([KMGT])(?:B)?", text):
        values.append(float(number) * UNIT[suffix])
    return int(max(values)) if values else None


def format_size(value: int | None) -> str:
    if value is None:
        return "-"
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    size = float(value)
    unit = units[0]
    for unit in units:
        if size < 1024 or unit == units[-1]:
            break
        size /= 1024
    return f"{size:.1f}{unit}"


def format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days:
        return f"{days}d{hours:02d}h"
    if hours:
        return f"{hours}h{minutes:02d}m"
    return f"{minutes}m{seconds:02d}s"


def display_width(value: str) -> int:
    width = 0
    for char in value:
        if unicodedata.combining(char):
            continue
        width += 2 if unicodedata.east_asian_width(char) in "WFA" else 1
    return width


def shorten(value: str, width: int) -> str:
    value = value.replace("\n", " ")
    if display_width(value) <= width:
        return value
    if width <= 3:
        return "." * width
    result = []
    used = 0
    for char in value:
        char_width = display_width(char)
        if used + char_width > width - 3:
            break
        result.append(char)
        used += char_width
    return "".join(result) + "..."


def format_cell(value: str, alignment: str, width: int) -> str:
    padding = max(0, width - display_width(value))
    if alignment == "<":
        return value + " " * padding
    if alignment == ">":
        return " " * padding + value
    left = padding // 2
    return " " * left + value + " " * (padding - left)


def collect_rows() -> list[list[str]]:
    if not TEMP.is_dir():
        return []
    rows = []
    for pid_file in sorted(TEMP.rglob("*.pid")):
        stage_dir = pid_file.parent
        raw_pid = read_text(pid_file).strip()
        if not raw_pid.isdigit():
            continue
        pid = int(raw_pid)
        command = process_command(pid)
        task_name = pid_file.stem
        logs = [stage_dir / f"{task_name}.stderr",
                stage_dir / f"{task_name}.stdout",
                stage_dir / f"{task_name}.log"]
        log_text = "\n".join(read_text(path) for path in logs if path.exists())
        path = model_path(command, stage_dir, task_name, log_text)
        size = path.stat().st_size if path and path.exists() else None
        metadata = stage_dir / f"{task_name}.metadata.json"
        total = metadata_size(metadata) if metadata.is_file() else None
        total = total or total_bytes(log_text)
        percent = f"{min(100.0, size / total * 100):.1f}%" if size is not None and total else "-"
        exit_match = re.findall(r"EXIT_CODE=([0-9]+)", log_text)
        exit_code = exit_match[-1] if exit_match else "-"
        is_alive = alive(pid)
        if is_alive:
            status = "RUNNING"
        elif exit_code == "0":
            status = "DONE"
        elif exit_code != "-":
            status = "FAILED"
        else:
            status = "EXITED"
        try:
            started = pid_file.stat().st_mtime
        except OSError:
            started = time.time()
        end = time.time()
        if not is_alive:
            finished_files = [candidate for candidate in logs if candidate.exists()]
            if path and path.is_file():
                finished_files.append(path)
            timestamps = [candidate.stat().st_mtime for candidate in finished_files]
            if timestamps:
                end = max(timestamps)
        target = path.name if path and path.is_file() else "-"
        hash_status = "-"
        if not is_alive and exit_code == "0":
            expected_hash = metadata_hash(metadata) if metadata.is_file() else None
            # A digest is meaningful only after the downloaded byte count
            # matches the authoritative metadata size. Avoid hashing partial
            # files from processes that exited unsuccessfully or early.
            complete = bool(path and size and total and size == total)
            if expected_hash and not complete:
                hash_status = "待完成"
            elif expected_hash and complete:
                actual_hash = local_sha256(path, stage_dir / f"{task_name}.sha256")
                hash_status = "是" if actual_hash == expected_hash else "否"
        rows.append([
            status,
            str(pid),
            f"{format_size(size)}/{format_size(total)}",
            percent,
            format_duration(end - started),
            exit_code,
            hash_status,
            target,
        ])
    return rows


def print_table(rows: list[list[str]]) -> None:
    headers = ["STATUS", "PID", "SIZE/TOTAL", "PROGRESS", "DURATION", "EXIT", "HASH", "FILE"]
    widths = []
    for i, header in enumerate(headers):
        values = [display_width(header)]
        values.extend(display_width(row[i]) for row in rows)
        widths.append(max(values))
    file_index = len(headers) - 1
    terminal_width = shutil.get_terminal_size((120, 24)).columns
    table_width = sum(width + 2 for width in widths) + len(widths) + 1
    if table_width > terminal_width:
        widths[file_index] = max(12, widths[file_index] - (table_width - terminal_width))
    alignments = ["<", ">", ">", ">", ">", "^", "^", "<"]
    header_alignments = ["^"] * len(headers)
    line = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
    print(line)
    print("|" + "|".join(f" {format_cell(headers[i], header_alignments[i], widths[i])} " for i in range(len(headers))) + "|")
    print(line)
    for row in rows:
        display = list(row)
        display[file_index] = shorten(display[file_index], widths[file_index])
        print("|" + "|".join(f" {format_cell(display[i], alignments[i], widths[i])} " for i in range(len(headers))) + "|")
    print(line)
    print(f"TASKS: {len(rows)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="ComfyUI model root (default: current directory)",
    )
    args = parser.parse_args()
    ROOT = args.root.resolve()
    TEMP = ROOT / "._____temp"
    # Hashing newly completed multi-gigabyte files can take a while. Emit an
    # immediate, unbuffered progress marker so callers can distinguish work
    # in progress from an empty result.
    print("Scanning download tasks (refreshing SHA256 caches as needed)...", flush=True)
    print_table(collect_rows())
