# 模型目录执行规则

本目录是 ComfyUI 模型根目录。只允许在本目录及其子目录内下载、整理和校验模型；不得创建 `models/models`，不得把模型下载到其他位置后再以不明来源复制进来。

正式模型只能放在以下目录：

- `diffusion_models/`
- `text_encoders/`
- `vae/`
- `loras/`
- `embeddings/`
- `clip_vision/`
- `upscale_models/`
- `latent_upscale_models/`

第三方 ComfyUI 节点如需专用运行时缓存目录，必须先把实体权重按上述正式目录登记和校验；仅允许在模型根目录创建指向正式目录的相对符号链接，供容器内节点使用。当前 Chatterbox 的 `/data1/video-ai/models/chatterbox/chatterbox` 即为此类兼容映射，实体文件仍位于 `diffusion_models/chatterbox/`。

模型下载、续传、状态检查、停止、校验和清理统一使用项目内 `.codex/skills/model-download/` 的 `model-download` skill。skill 中的下载协议是本目录的唯一操作流程；根目录 Agent 不应另行实现或简化该流程。

## ModelScope revision 规则

- 参数名是 `revision`（不是 `reversion`），它表示仓库引用，不是文件名、模型精度或下载目录。
- ModelScope CLI 1.36.2 的模型和数据集默认 revision 都是 `master`。为避免 CLI 默认值、缓存键和日志不一致，正式下载命令必须显式传 `--revision <已确认分支>`，默认写为 `--revision master`；只有已确认仓库存在其他分支时才可使用该分支名。
- 本项目对 ModelScope 下载只使用已确认的分支名称，通常为 `master`。不要把 Hugging Face 的 `main`、完整 URL、`resolve/...` 片段或未经确认的 tag/commit hash 直接填入 ModelScope 的 `--revision`；ModelScope 不存在该分支时应报告失败或先确认真实分支，不能猜测替换。
- Hugging Face 定位信息和 ModelScope 下载使用两套独立值：`hf_revision` 从用户 URL 原样解析（通常是 `main`，仅用于 CF 的 `/resolve/<hf_revision>/...`）；`ms_revision` 按 ModelScope 仓库实际分支归一化（默认 `master`，仅用于 `.venv/bin/modelscope ... --revision <ms_revision>`）。除非已验证两边同名，否则不得复用一个 revision 字符串。
- 推荐的单文件调用形态为：`.venv/bin/modelscope download --model <owner>/<repo> --revision master --local_dir . <repo-relative-file>`。下载前在任务日志或元数据中同时记录 `ms_revision` 和 `hf_revision`（如有），便于复现和排错。

以下边界始终有效：

- 用户提供的 Hugging Face URL 只用于解析仓库、`hf_revision` 和文件路径；禁止访问 Hugging Face 原始地址、网页、`hf download` 或其他第三方镜像。
- 默认优先处理完整模型，模型精度选择顺序由项目需求指定（当前项目为 int8 -> bf16 -> fp16）。当没有可运行的完整模型，或完整模型不满足任务的显存/运行要求时，允许选择兼容的量化或 pruned 变体以保证工作流可用；不得选择测试版、示例文件或不明来源的变体。变体的名称、来源、架构、精度、许可证或兼容性存在真实歧义时先请求确认。
- 使用量化或 pruned 变体时，必须记录降级原因、实际变体、来源、版本、文件大小和 SHA256；不得为了省显存无理由降级，也不得把低精度变体冒充完整模型。
- 不得覆盖已存在但未通过变体、大小和 SHA256 校验的文件；不得把 `.pth` 改名为 `.safetensors`。
- 不得删除已有正式模型或终止无关服务。失败或中断任务应保留其断点和日志，清理只针对本次任务产生的文件。
- 模型二进制、缓存、临时目录和日志不进入 Git；Git 只提交 Markdown 文档及项目内 `.codex/skills/model-download/`。修改模型后同步更新 `README.md` 的目录树和索引。
