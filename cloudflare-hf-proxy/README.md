# Cloudflare Hugging Face gated-model proxy

This Worker proxies Hugging Face files through `hf-mirrors.i-yongqi.xyz`.
It uses the Hugging Face token only at the origin request and streams the response, including HTTP range requests used by download tools.

## Deploy

From this directory:

```sh
wrangler secret put HF_TOKEN
wrangler secret put PROXY_KEY
wrangler deploy
```

`PROXY_KEY` is required. The Worker rejects every request when it is missing,
and every request must include `Authorization: Bearer <PROXY_KEY>`.

Attach the custom domain `hf-mirrors.i-yongqi.xyz` to the Worker in Cloudflare. `PROXY_KEY` is required; keep it separate from `HF_TOKEN` and share it only with trusted clients.

Any Hugging Face repository path is accepted. The Worker is protected by `PROXY_KEY`; automated downloads should not be placed behind interactive Cloudflare Access.

## GitHub Actions deployment

Pushes to `main` that change this directory deploy the Worker through
`.github/workflows/deploy-proxy.yml`. Add these repository secrets in GitHub:

- `CLOUDFLARE_API_TOKEN` with permission to deploy Workers
- `CLOUDFLARE_ACCOUNT_ID`

After the first deployment, open the Worker in the Cloudflare dashboard and add
`PROXY_KEY` and `HF_TOKEN` under **Settings > Variables and Secrets** as Secret
values. `PROXY_KEY` must match the value in the model-root `.env`.

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

Do not put `HF_TOKEN` in a URL or client configuration. If `PROXY_KEY` is omitted, the Worker is public and anyone can proxy Hugging Face downloads, consume the token's gated access, and use your Cloudflare bandwidth.
