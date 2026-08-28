# 模型目录执行规则

## 适用范围

当前目录就是 ComfyUI 模型根目录。只允许在当前目录及其子目录内下载、整理和校验模型，不得在这里创建 `models/models`。标准目录包括：

- `diffusion_models/`：扩散模型、DiT、UNet、主模型
- `text_encoders/`：文本或视觉文本编码器
- `vae/`：图像、视频或音频 VAE
- `loras/`：LoRA 和适配器
- `embeddings/`：Embedding
- `clip_vision/`：CLIP Vision 编码器
- `upscale_models/`、`latent_upscale_models/`：超分辨率和潜空间超分模型

## 下载来源与顺序

每个文件只能按以下顺序处理，不得边下载边试探多个来源：

1. 先检查正式目标路径。文件已存在且变体、文件大小和 SHA256 均匹配时直接跳过。
2. 优先使用 ModelScope 的相同仓库、revision 和文件：`modelscope download`（当前 CLI 1.36.2）。必须从模型根目录执行并使用 `--local_dir .`；ModelScope 会按目标文件的父目录把临时模型写入 `._____temp/<目标子目录>/`。
3. ModelScope 文件不存在、连接失败、权限失败、超时或校验失败后，才使用 CF 代理：
   `https://hf-mirrors.i-yongqi.xyz/<owner>/<repo>/resolve/<revision>/<file>`。
4. ModelScope 和 CF 都失败时立即报告失败，不得再访问其他来源或反复重试。

用户提供的 `https://huggingface.co/.../blob/...` URL 只用于解析 owner、repo、revision 和文件路径，再拼接 CF URL；禁止访问 Hugging Face 原始地址下载模型。不得使用 Hugging Face 网页、`hf download`、浏览器或其他第三方镜像作为下载来源。

## 下载前元数据

启动下载前必须先获取并保存远端文件元数据。对 CF 任务，在对应临时目录执行只读的 `blob` 元数据请求（`Accept: application/vnd.xet-fileinfo+json, /`、`Range: bytes=0-0`），将原始 JSON 保存为 `<任务名>.metadata.json`；这一步只读取大小和哈希，不下载模型内容。ModelScope 能提供等价的文件元数据时一并保存。JSON 中的 `size` 和 `hash` 是权威记录，状态统计和完成校验优先使用它们；日志中的进度文本只作元数据缺失时的回退。元数据请求失败必须记录并报告，不得伪造大小或哈希。

## CF 传输客户端

CF 文件优先使用已安装的 `aria2c`，以获得并发连接和断点续传；只有 `aria2c` 命令不存在时，才回退到支持续传的 `curl -L -C -`，再无 `curl` 才使用 `wget -c`。不得同时启动多个客户端下载同一文件。

CF 的临时目录必须与最终目标子目录保持一一映射：目标相对路径的父目录决定临时目录名。模型临时文件、`stdin`、`stdout`、`stderr` 和 PID 都放在对应的 `._____temp/<目标子目录>/` 内，确保同一模型的所有运行状态可从一个目录追踪。

建议的 `aria2c` 参数为：`--continue=true --max-connection-per-server=16 --split=16 --min-split-size=64M --max-tries=3 --retry-wait=5 --connect-timeout=15 --timeout=30 --lowest-speed-limit=1K`。回退客户端最多重试 3 次并设置连接/低速超时；禁止无限重试。

大文件最多并行 2 个独立任务，同一文件始终只有一个进程。连续 10 分钟无字节增长时，只停止本次任务，保留部分文件并从同一临时目录续传。

## 后台任务协议

所有下载必须使用 `nohup` 脱离当前会话，禁止以前台命令启动大文件。控制文件必须与对应的模型临时文件位于同一个 `._____temp/<目标子目录>/`，并生成以下四个文件（以模型文件名作为任务名，避免同目录冲突）：

- `<任务名>.stdin`：标准输入；无交互输入时创建为空文件，防止进程等待终端输入
- `<任务名>.stdout`：标准输出，例如进度和正常状态
- `<任务名>.stderr`：标准错误和启动器追加的 `EXIT_CODE=<n>`
- `<任务名>.pid`：`setsid` 进程组 PID，只能包含一个数字
- `<任务名>.metadata.json`：下载前保存的远端文件大小和哈希元数据
- `<任务名>.sha256`：状态脚本缓存的本地 SHA256 和对应文件大小，文件变化后必须重新计算

从模型根目录使用此启动模板，将 `<下载命令>` 替换为规范化的 ModelScope 或 CF 客户端命令。设置 `stage_dir="._____temp/<目标子目录>"`：ModelScope 保持 `--local_dir .`，CF 客户端将 `--dir` 或输出文件指向 `$stage_dir`。这样模型临时文件、stdin、stdout、stderr 和 PID 始终在同一目录；完成后按预期文件名校验并移动。

```sh
stage_dir="._____temp/<目标子目录>"
mkdir -p "$stage_dir"
in="$stage_dir/<任务名>.stdin"
out="$stage_dir/<任务名>.stdout"
err="$stage_dir/<任务名>.stderr"
pid="$stage_dir/<任务名>.pid"
: > "$in"
nohup setsid bash -c '\
  <下载命令>
  rc=$?
  printf "\\nEXIT_CODE=%s\\n" "$rc"
  exit "$rc"
' < "$in" > "$out" 2> "$err" &
printf '%s\\n' "$!" > "$pid"
```

启动前读取 PID 文件：PID 仍存活且命令属于同一文件时，只能监控或续传，禁止重复启动。判断完成必须同时检查 PID、`stdout`、`stderr`、元数据 JSON、正式/临时文件、权威大小和哈希（以及可取得的 SHA256）：进程退出、`stderr` 含 `EXIT_CODE=0` 且校验全部通过才算成功；否则算失败或未完成。

强制终止前必须验证 PID 是数字，并用 `ps -o pid=,sid=,cmd= -p "$(cat "$pid")"` 确认命令属于本任务。确认后终止进程组：`kill -TERM -- -$(cat "$pid")`；等待 5 秒仍存在才使用 `kill -KILL -- -$(cat "$pid")`。禁止按模糊命令行匹配杀死其他服务。

## 模型名称或 URL 的固定流程

1. 解析仓库、revision、文件路径、架构、精度和目标子目录；URL 只作定位信息。
2. 检查正式文件，匹配则跳过。
3. 按“下载来源与顺序”选择 ModelScope 或 CF，并按“后台任务协议”启动。
4. 直至任务完成前，半成品和四个控制文件都留在同一个 `._____temp/<目标子目录>/`；失败或中断时保留原目录和断点文件。
5. 下载成功后检查退出码、非零大小、权威大小和 SHA256，确认无误再 `mv` 到正式目录。
6. 新增或删除模型后更新 `README.md` 的目录树和索引，并报告工具、来源、相对路径、实际字节数、状态和校验结果。

默认下载完整模型，不擅自选择 `pruned`、测试版、示例文件或其他量化变体；名称、来源、架构、精度或许可证有真实歧义时才请求确认。

## 用户脚本、清理与 Git

用户粘贴的脚本禁止原样执行。必须重写仓库、文件名、revision、目标路径、缓存、临时目录、日志和环境变量；下载命令只能是单条 `modelscope download` 或 CF 客户端命令，并套用后台、断点和校验流程。不得执行下载仓库中的脚本或二进制。

日志、缓存、临时文件和错误分片不是模型资产，不写入正式目录，也不纳入 README、目录树或 Git。只有所有必需模型落盘并通过校验后，才清理本次任务产生的 `._____temp/`、`.cache/`、`.msc`、`.mv` 和错误分片；不得删除已有正式模型，不得把 `.pth` 改名为 `.safetensors`。

清理或终止操作只针对本次任务产生的进程和文件；无关服务（例如 ComfyUI）及其子进程不得终止，僵尸进程交由父进程回收。

模型和临时文件由 `.gitignore` 排除，Git 只提交 Markdown 文档。提交前运行 `git status --ignored`，确认大文件没有进入暂存区。
