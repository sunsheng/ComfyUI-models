---
name: model-download
description: Download, resume, verify, stop, or inspect ComfyUI model tasks under a model root using the required ModelScope/CF order and tracked temporary state.
---

# Model Download

Use this skill when the user asks to download a model, continue or stop a task, verify a model, or inspect download status. This project-scoped skill lives at `.codex/skills/model-download/`; run commands from the cloned ComfyUI model root. It owns the complete download state machine; do not invent a parallel downloader in the Agent or README.

## Resolve The Request

Parse a model name or Hugging Face `blob` URL into owner, repository, revision, file path, architecture, precision, and one of the formal target directories. A Hugging Face URL is locator data only: never fetch it, browse it, or use `hf download`. If the requested variant, source, architecture, precision, or license is genuinely ambiguous, ask before downloading. Default to the complete model.

Check the formal target path first. Skip only when the existing file matches the requested variant, authoritative size, and SHA256. Check the matching `._____temp/<target-subdirectory>/` task and PID before starting anything; one file may have only one downloader. At most two independent large-file tasks may run concurrently.

## Source Order

1. Use `.venv/bin/modelscope download` from the model root, with the same repository, revision, and file and `--local_dir .` (ModelScope CLI 1.36.2). Save equivalent remote metadata when available.
2. Only after ModelScope is missing, unavailable, unauthorized, timed out, or failed verification, use the CF URL `https://hf-mirrors.i-yongqi.xyz/<owner>/<repo>/resolve/<revision>/<file>`.
   Load `PROXY_KEY` from the model-root `.env` before making any CF request and fail
   if it is missing. Send `Authorization: Bearer $PROXY_KEY` on both the metadata
   request and the download request; never print the key in task logs or URLs.
3. If both fail, report failure immediately. Do not probe another mirror or retry indefinitely.

Before any transfer, obtain remote metadata. For CF, in the task stage directory issue a read-only request with `Accept: application/vnd.xet-fileinfo+json, /` and `Range: bytes=0-0`, saving the raw JSON as `<task>.metadata.json`. `size` and `hash` (or an equivalent SHA256 field) are authoritative; a failed metadata request is a reported failure, not permission to invent values.

## Transfer And State

For CF, prefer installed `aria2c`; otherwise use resumable `curl -L -C -`, then `wget -c`. Use bounded retries/timeouts (the recommended aria2c settings are `--continue=true --max-connection-per-server=16 --split=16 --min-split-size=64M --max-tries=3 --retry-wait=5 --connect-timeout=15 --timeout=30 --lowest-speed-limit=1K`). Never start two clients for one file.

The temporary directory must mirror the target parent: `._____temp/<target-subdirectory>/`. Keep the partial model and all task controls there until validation succeeds. For task name `<task>` create `<task>.stdin`, `<task>.stdout`, `<task>.stderr`, `<task>.pid`, `<task>.metadata.json`, and `<task>.sha256`. Start the single normalized download command with `nohup setsid`, redirecting stdin/stdout/stderr to those files; append `EXIT_CODE=<n>` to stderr on exit. A ten-minute period with no byte growth stops only that task, preserving its partial file for resume.

Before starting or stopping, read the PID file and require one numeric PID. Confirm ownership with `ps -o pid=,sid=,cmd= -p <pid>`; for a forced stop terminate the process group with `kill -TERM -- -<pid>`, wait five seconds, then use `kill -KILL -- -<pid>` only if it remains. Never kill by a fuzzy command-line match or touch unrelated services.

## Inspect Status

The bundled read-only reporter scans every `._____temp/**/*.pid`, reports process state, PID, size/total, percentage, duration, exit code, hash result, and detected model file. It uses metadata size/hash first and refreshes the cached SHA256 whenever the local size changes. Run it from the model root:

```sh
.venv/bin/python -u .codex/skills/model-download/scripts/download_status.py
```

`RUNNING` means the PID is alive; `DONE` is only an exited process with `EXIT_CODE=0` (the final verification still decides whether the task is acceptable); `FAILED` and `EXITED` require inspection of the task logs and metadata. A missing, malformed, or mismatched metadata/hash is never reported as a successful verified model.

## Finish And Document

After the process exits, require `EXIT_CODE=0`, non-zero file size, authoritative size equality, and SHA256 equality when available. Only then move the expected filename into its formal target directory. Preserve failed or interrupted task files. Clean only temporary files created by this task, and only after all requested models are verified. Update the model root `README.md` directory tree and index with relative path, actual byte count, source repository, precision/architecture, and purpose. Run `git status --ignored` and ensure no model binary is staged.
