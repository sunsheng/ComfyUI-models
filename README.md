# ComfyUI 模型清单

本目录是 ComfyUI 的模型根目录。模型二进制文件保留在本地，但由 `.gitignore` 排除；Git 只同步本文件、`AGENTS.md` 和 `.gitignore`。换机时按本清单中的相对路径、仓库和文件名重新下载。

## 下载说明

用户提供模型名称或 Hugging Face 链接即可。默认先按 ModelScope/原下载方式执行并检查结果；仅在超时、无权限、连接失败或文件校验失败时，自动切换 CF 代理。明确写出“使用 CF 代理”或“强制使用 CF”时，直接使用代理，不受之前命令影响。

CF 代理地址格式：

```text
https://hf-mirrors.i-yongqi.xyz/<owner>/<repo>/resolve/<ref>/<file>
```

例如：

```sh
curl -L -C - -o gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors \
  "https://hf-mirrors.i-yongqi.xyz/Lightricks/LTX-2.5/resolve/main/text_encoders/gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors"
```

代理 Worker 项目和部署配置见 [`cloudflare-hf-proxy/`](cloudflare-hf-proxy/)。

## 当前目录树

```text
.
├── AGENTS.md
├── README.md
├── .gitignore
├── diffusion_models/
│   ├── minimax_h3_fl2va_int8_convrot.safetensors
│   ├── minimax_h3_fl2va_pruned_int8_convrot.safetensors
│   ├── minimax_h3_ref2va_int8_convrot.safetensors
│   ├── minimax_h3_ref2va_pruned_int8_convrot.safetensors
│   └── z_image_turbo_bf16.safetensors
├── embeddings/
│   └── minimaxh3_art_is_explosion.safetensors
├── loras/
│   ├── minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors
│   └── minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors
├── latent_upscale_models/
│   └── ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors
├── text_encoders/
│   ├── qwen3vl_32b_minimax_h3_int8_convrot.safetensors
│   ├── qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
│   └── qwen_3_4b.safetensors
├── upscale_models/
│   └── RealESRGAN_x4plus.safetensors
└── vae/
    ├── ae.safetensors
    ├── ltx-2.5-audio-vae-bf16.safetensors
    ├── ltx-2.5-video-vae-bf16.safetensors
    ├── minimax_h3_audio_vae_fp32.safetensors
    └── minimax_h3_video_vae_fp16.safetensors
```

## 模型索引

大小为本地实际字节数；来源使用 ModelScope 仓库 ID。文件名和相对路径是 ComfyUI 的实际加载位置。

| 相对路径 | 字节数 | ModelScope 来源 | 说明 |
| --- | ---: | --- | --- |
| `diffusion_models/minimax_h3_fl2va_int8_convrot.safetensors` | 34038892334 | `Comfy-Org/MiniMax-H3` | FL2VA，完整 INT8 ConvRot |
| `diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors` | 20970379616 | `Comfy-Org/MiniMax-H3` | FL2VA，pruned INT8 ConvRot |
| `diffusion_models/minimax_h3_ref2va_int8_convrot.safetensors` | 34038894550 | `Comfy-Org/MiniMax-H3` | Ref2VA，完整 INT8 ConvRot |
| `diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors` | 20970379616 | `Comfy-Org/MiniMax-H3` | Ref2VA，pruned INT8 ConvRot |
| `diffusion_models/z_image_turbo_bf16.safetensors` | 12309866400 | `Comfy-Org/z_image_turbo` | Z Image Turbo BF16 扩散模型 |
| `embeddings/minimaxh3_art_is_explosion.safetensors` | 512120 | `Comfy-Org/MiniMax-H3` | MiniMax H3 embedding |
| `loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` | 1956193000 | `Comfy-Org/MiniMax-H3` | FL2V LoRA |
| `loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` | 1956193000 | `Comfy-Org/MiniMax-H3` | Ref2V LoRA |
| `latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors` | 995778752 | `Lightricks/LTX-2.5` | LTX 2.5 BF16 latent spatial upscaler x2 |
| `text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors` | 27141342152 | `Comfy-Org/MiniMax-H3` | Qwen3-VL INT8 ConvRot |
| `text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | 15687142551 | `Comfy-Org/MiniMax-H3` | Qwen3-VL NVFP4 AWQ |
| `text_encoders/qwen_3_4b.safetensors` | 8044982048 | `Comfy-Org/z_image_turbo` | Z Image Turbo Qwen 3 4B |
| `upscale_models/RealESRGAN_x4plus.safetensors` | 66857836 | `Comfy-Org/Real-ESRGAN_repackaged` | RealESRGAN x4 |
| `vae/ae.safetensors` | 335304388 | `Comfy-Org/z_image_turbo` | Z Image Turbo VAE |
| `vae/ltx-2.5-audio-vae-bf16.safetensors` | 364866540 | `Lightricks/LTX-2.5` | LTX 2.5 BF16 audio VAE |
| `vae/ltx-2.5-video-vae-bf16.safetensors` | 1472223346 | `Lightricks/LTX-2.5` | LTX 2.5 BF16 video VAE |
| `vae/minimax_h3_audio_vae_fp32.safetensors` | 605254808 | `Comfy-Org/MiniMax-H3` | MiniMax H3 音频 VAE |
| `vae/minimax_h3_video_vae_fp16.safetensors` | 5207808496 | `Comfy-Org/MiniMax-H3` | MiniMax H3 视频 VAE |

## 维护规则

新增或删除模型后，必须同时更新上面的目录树和模型索引，记录相对路径、字节数、来源、精度/架构和用途。临时目录、缓存、日志、下载器元数据和错误分片不属于模型清单。下载命令、断点续传、已有文件跳过和临时文件规则统一见 `AGENTS.md`。
