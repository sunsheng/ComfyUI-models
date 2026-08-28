# Cloudflare Hugging Face gated-model proxy

This Worker proxies allowlisted Hugging Face files through `hf-mirrors.i-yongqi.xyz`.
It uses the Hugging Face token only at the origin request and streams the response, including HTTP range requests used by download tools.

## Deploy

From this directory:

```sh
wrangler secret put HF_TOKEN
wrangler secret put PROXY_KEY
wrangler deploy
```

Attach the custom domain `hf-mirrors.i-yongqi.xyz` to the Worker in Cloudflare. `PROXY_KEY` is required when set; keep it separate from `HF_TOKEN` and share it only with trusted clients.

The default allowlist is `Lightricks/LTX-2.5`. Add more repositories by changing `ALLOWED_REPOS` in `wrangler.toml`, separated by commas, then redeploy.

## Download URL

The Worker accepts the familiar browser URL and rewrites `blob` to Hugging Face's file endpoint:

```text
https://hf-mirrors.i-yongqi.xyz/Lightricks/LTX-2.5/blob/main/text_encoders/gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors
```

For command-line clients, pass the proxy key if configured:

```sh
curl -L -C - -H "Authorization: Bearer $PROXY_KEY" \
  -o gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors \
  "https://hf-mirrors.i-yongqi.xyz/Lightricks/LTX-2.5/resolve/main/text_encoders/gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors"
```

Do not put `HF_TOKEN` in a URL or client configuration. If `PROXY_KEY` is omitted, the Worker is public and anyone can consume the token's gated access and your Cloudflare bandwidth.
