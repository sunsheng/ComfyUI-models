# ComfyUI 模型清单

本目录是 ComfyUI 的模型根目录。模型二进制文件保留在本地并由 `.gitignore` 排除；Git 同步本文件、`AGENTS.md`、`.gitignore` 和项目内 `.codex/skills/model-download/`。下载、续传、状态检查、校验和清理流程统一见 `model-download` skill。

## 复现环境

在项目根目录执行以下命令创建并初始化项目专用虚拟环境。`.venv/` 不进入 Git，依赖版本由 `requirements.txt` 固定。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

初始化后，下载流程使用 `.venv/bin/modelscope`，状态检查使用 `.venv/bin/python`。CF 传输按 skill 规定依次使用已安装的 `aria2c`、`curl` 或 `wget`；这些是传输工具，不属于 Python 依赖。

## 当前目录树

```text
.
├── AGENTS.md
├── README.md
├── .gitignore
├── .codex/
│   └── skills/model-download/
├── clip_vision/
│   └── clip_vision_h.safetensors
├── diffusion_models/
│   ├── chatterbox/
│   ├── chatterbox_multilingual/
│   │   ├── conds.pt
│   │   ├── s3gen.safetensors
│   │   ├── t3_cfg.safetensors
│   │   ├── tokenizer.json
│   │   └── ve.safetensors
│   ├── minimax_h3_fl2va_int8_convrot.safetensors
│   ├── minimax_h3_fl2va_pruned_int8_convrot.safetensors
│   ├── minimax_h3_ref2va_int8_convrot.safetensors
│   ├── minimax_h3_ref2va_pruned_int8_convrot.safetensors
│   ├── flux2_dev_fp8mixed.safetensors
│   ├── seedvr2_3b_int8_convrot.safetensors
│   ├── seedvr2_7b_int8_convrot.safetensors
│   ├── wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors
│   ├── wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors
│   ├── wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors
│   ├── wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors
│   ├── wan_animate_2_int8_convrot.safetensors
│   └── z_image_turbo_bf16.safetensors
├── embeddings/
│   └── minimaxh3_art_is_explosion.safetensors
├── loras/
│   ├── Flux_2-Turbo-LoRA_comfyui.safetensors
│   ├── lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors
│   ├── minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors
│   ├── minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors
│   └── minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors
├── latent_upscale_models/
│   └── ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors
├── text_encoders/
│   ├── qwen3vl_32b_minimax_h3_int8_convrot.safetensors
│   ├── qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
│   ├── qwen_3_4b.safetensors
│   ├── mistral_3_small_flux2_bf16.safetensors
│   └── umt5_xxl_fp8_e4m3fn_scaled.safetensors
├── upscale_models/
│   └── RealESRGAN_x4plus.safetensors
└── vae/
    ├── Wan2_1_VAE_bf16.safetensors
    ├── wan_2.1_vae.safetensors
    ├── ae.safetensors
    ├── ltx-2.5-audio-vae-bf16.safetensors
    ├── ltx-2.5-video-vae-bf16.safetensors
    ├── minimax_h3_audio_vae_fp32.safetensors
    ├── minimax_h3_video_vae_fp16.safetensors
    ├── flux2-vae.safetensors
    ├── full_encoder_small_decoder.safetensors
    └── seedvr2_ema_vae_fp16.safetensors
```

## 模型索引

大小为本地实际字节数；来源为实际下载仓库 ID（优先 ModelScope）。文件名和相对路径是 ComfyUI 的实际加载位置。

| 相对路径 | 字节数 | 来源仓库 | 说明 |
| --- | ---: | --- | --- |
| `clip_vision/clip_vision_h.safetensors` | 1264219396 | `Comfy-Org/Wan-Animate-2` | Wan Animate 2 CLIP Vision H |
| `diffusion_models/minimax_h3_fl2va_int8_convrot.safetensors` | 34038892334 | `Comfy-Org/MiniMax-H3` | FL2VA，完整 INT8 ConvRot |
| `diffusion_models/chatterbox/conds.pt` | 107374 | `ResembleAI/chatterbox` | Chatterbox 标准 TTS 条件缓存 |
| `diffusion_models/chatterbox/s3gen.safetensors` | 1056484620 | `ResembleAI/chatterbox` | Chatterbox S3Gen |
| `diffusion_models/chatterbox/t3_cfg.safetensors` | 2129653744 | `ResembleAI/chatterbox` | Chatterbox T3 CFG |
| `diffusion_models/chatterbox/tokenizer.json` | 25470 | `ResembleAI/chatterbox` | Chatterbox 文本 tokenizer |
| `diffusion_models/chatterbox/ve.safetensors` | 5695784 | `ResembleAI/chatterbox` | Chatterbox voice encoder |
| `diffusion_models/chatterbox_multilingual/ve.pt` | 5698626 | `ResembleAI/chatterbox` | Chatterbox multilingual voice encoder |
| `diffusion_models/chatterbox_multilingual/t3_mtl23ls_v2.safetensors` | 2143989752 | `ResembleAI/chatterbox` | Chatterbox multilingual T3 |
| `diffusion_models/chatterbox_multilingual/s3gen.pt` | 1057165844 | `ResembleAI/chatterbox` | Chatterbox multilingual S3Gen |
| `diffusion_models/chatterbox_multilingual/grapheme_mtl_merged_expanded_v1.json` | 69989 | `ResembleAI/chatterbox` | Chatterbox multilingual grapheme config |
| `diffusion_models/chatterbox_multilingual/conds.pt` | 107374 | `ResembleAI/chatterbox` | Chatterbox multilingual condition cache |
| `diffusion_models/chatterbox_multilingual/Cangjie5_TC.json` | 1920163 | `ResembleAI/chatterbox` | Chatterbox multilingual tokenizer config |
| `diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors` | 20970379616 | `Comfy-Org/MiniMax-H3` | FL2VA，pruned INT8 ConvRot |
| `diffusion_models/minimax_h3_ref2va_int8_convrot.safetensors` | 34038894550 | `Comfy-Org/MiniMax-H3` | Ref2VA，完整 INT8 ConvRot |
| `diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors` | 20970379616 | `Comfy-Org/MiniMax-H3` | Ref2VA，pruned INT8 ConvRot |
| `diffusion_models/flux2_dev_fp8mixed.safetensors` | 35455599592 | `Comfy-Org/flux2-dev` | FLUX.2 dev FP8 mixed diffusion model |
| `diffusion_models/seedvr2_3b_int8_convrot.safetensors` | 3458259704 | `Comfy-Org/SeedVR2` | SeedVR2 3B INT8 ConvRot |
| `diffusion_models/seedvr2_7b_int8_convrot.safetensors` | 8334897976 | `Comfy-Org/SeedVR2` | SeedVR2 7B INT8 ConvRot |
| `diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors` | 14294742832 | `Comfy-Org/Wan_2.2_ComfyUI_Repackaged` | Wan2.2 I2V/FLF2V high-noise 14B FP8 scaled |
| `diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors` | 14294742832 | `Comfy-Org/Wan_2.2_ComfyUI_Repackaged` | Wan2.2 I2V/FLF2V low-noise 14B FP8 scaled |
| `diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors` | 14293923632 | `Comfy-Org/Wan_2.2_ComfyUI_Repackaged` | Wan2.2 T2V high-noise 14B FP8 scaled |
| `diffusion_models/wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors` | 14293923632 | `Comfy-Org/Wan_2.2_ComfyUI_Repackaged` | Wan2.2 T2V low-noise 14B FP8 scaled |
| `diffusion_models/wan_animate_2_int8_convrot.safetensors` | 16653175528 | `Comfy-Org/Wan-Animate-2` | Wan Animate 2 INT8 ConvRot 扩散模型 |
| `diffusion_models/z_image_turbo_bf16.safetensors` | 12309866400 | `Comfy-Org/z_image_turbo` | Z Image Turbo BF16 扩散模型 |
| `embeddings/minimaxh3_art_is_explosion.safetensors` | 512120 | `Comfy-Org/MiniMax-H3` | MiniMax H3 embedding |
| `loras/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors` | 738005744 | `Comfy-Org/Wan-Animate-2` | Wan Animate 2 LightX2V 14B 480p CFG-step distilled Rank64 BF16 LoRA |
| `loras/Flux_2-Turbo-LoRA_comfyui.safetensors` | 2760814880 | `ByteZSzn/Flux.2-Turbo-ComfyUI` | FLUX.2 Turbo ComfyUI LoRA（ModelScope 缺失，CF 回退） |
| `loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` | 1956193000 | `Comfy-Org/MiniMax-H3` | FL2V LoRA |
| `loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` | 1956193000 | `Comfy-Org/MiniMax-H3` | Ref2V LoRA |
| `loras/minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors` | 1956193000 | `lightx2v/Minimax-h3-Turbo` | Ref2V 8-step 768p BF16 LoRA |
| `latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors` | 995778752 | `Lightricks/LTX-2.5` | LTX 2.5 BF16 latent spatial upscaler x2 |
| `text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors` | 27141342152 | `Comfy-Org/MiniMax-H3` | Qwen3-VL INT8 ConvRot |
| `text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | 15687142551 | `Comfy-Org/MiniMax-H3` | Qwen3-VL NVFP4 AWQ |
| `text_encoders/qwen_3_4b.safetensors` | 8044982048 | `Comfy-Org/z_image_turbo` | Z Image Turbo Qwen 3 4B |
| `text_encoders/mistral_3_small_flux2_bf16.safetensors` | 35584897447 | `Comfy-Org/flux2-dev` | FLUX.2 Mistral-Small-24B BF16 |
| `text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors` | 6735906897 | `Comfy-Org/Wan-Animate-2` | Wan Animate 2 UMT5-XXL FP8 E4M3FN scaled 文本编码器 |
| `upscale_models/RealESRGAN_x4plus.safetensors` | 66857836 | `Comfy-Org/Real-ESRGAN_repackaged` | RealESRGAN x4 |
| `vae/ae.safetensors` | 335304388 | `Comfy-Org/z_image_turbo` | Z Image Turbo VAE |
| `vae/flux2-vae.safetensors` | 336213556 | `Comfy-Org/flux2-dev` | FLUX.2 VAE |
| `vae/full_encoder_small_decoder.safetensors` | 249519092 | `black-forest-labs/FLUX.2-small-decoder` | FLUX.2 完整编码器、小型解码器 VAE |
| `vae/ltx-2.5-audio-vae-bf16.safetensors` | 364866540 | `Lightricks/LTX-2.5` | LTX 2.5 BF16 audio VAE |
| `vae/ltx-2.5-video-vae-bf16.safetensors` | 1472223346 | `Lightricks/LTX-2.5` | LTX 2.5 BF16 video VAE |
| `vae/minimax_h3_audio_vae_fp32.safetensors` | 605254808 | `Comfy-Org/MiniMax-H3` | MiniMax H3 音频 VAE |
| `vae/minimax_h3_video_vae_fp16.safetensors` | 5207808496 | `Comfy-Org/MiniMax-H3` | MiniMax H3 视频 VAE |
| `vae/seedvr2_ema_vae_fp16.safetensors` | 501324814 | `Comfy-Org/SeedVR2` | SeedVR2 EMA VAE FP16 |
| `vae/wan_2.1_vae.safetensors` | 253815318 | `Comfy-Org/Wan_2.2_ComfyUI_Repackaged` | Wan2.2 官方 VAE |
| `vae/Wan2_1_VAE_bf16.safetensors` | 253806278 | `Comfy-Org/Wan-Animate-2` | Wan Animate 2 BF16 VAE |

## 维护规则

新增或删除模型后，必须同步更新上面的目录树和模型索引，记录相对路径、字节数、来源、精度/架构和用途。临时目录、缓存、日志、下载器元数据和错误分片不属于模型清单。
