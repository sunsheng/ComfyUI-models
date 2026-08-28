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

模型下载、续传、状态检查、停止、校验和清理统一使用项目内 `.codex/skills/model-download/` 的 `model-download` skill。skill 中的下载协议是本目录的唯一操作流程；根目录 Agent 不应另行实现或简化该流程。

以下边界始终有效：

- 用户提供的 Hugging Face URL 只用于解析仓库、revision 和文件路径；禁止访问 Hugging Face 原始地址、网页、`hf download` 或其他第三方镜像。
- 默认处理完整模型。不得擅自选择 pruned、测试版、示例文件或量化变体；名称、来源、架构、精度或许可证存在真实歧义时先请求确认。
- 不得覆盖已存在但未通过变体、大小和 SHA256 校验的文件；不得把 `.pth` 改名为 `.safetensors`。
- 不得删除已有正式模型或终止无关服务。失败或中断任务应保留其断点和日志，清理只针对本次任务产生的文件。
- 模型二进制、缓存、临时目录和日志不进入 Git；Git 只提交 Markdown 文档及项目内 `.codex/skills/model-download/`。修改模型后同步更新 `README.md` 的目录树和索引。
