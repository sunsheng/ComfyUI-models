const HF_ORIGIN = "https://huggingface.co";
const FORWARDED_REQUEST_HEADERS = [
  "accept",
  "if-match",
  "if-modified-since",
  "if-none-match",
  "if-range",
  "range",
  "user-agent",
];

function unauthorized() {
  return new Response("Unauthorized", {
    status: 401,
    headers: { "WWW-Authenticate": "Bearer realm=hf-proxy" },
  });
}

function parseDownloadPath(pathname, env) {
  const parts = pathname.split("/").filter(Boolean);
  if (parts.length < 5) return null;

  const [owner, name, kind, ref, ...fileParts] = parts;
  if (kind !== "blob" && kind !== "resolve") return null;
  if (!ref || fileParts.length === 0) return null;

  let repo;
  let file;
  try {
    repo = `${decodeURIComponent(owner)}/${decodeURIComponent(name)}`;
    file = fileParts.map((part) => decodeURIComponent(part)).join("/");
  } catch {
    return null;
  }

  if (repo.includes("..") || ref.includes("..") || file.split("/").some((part) => part === ".." || part === ".")) {
    return null;
  }

  return { repo, ref, file };
}

function clientHeaders(request) {
  const headers = new Headers();
  for (const name of FORWARDED_REQUEST_HEADERS) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  return headers;
}

function responseHeaders(response) {
  const headers = new Headers(response.headers);
  // Never expose origin cookies or an origin challenge to proxy clients.
  headers.delete("set-cookie");
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("Cache-Control", "private, no-store");
  return headers;
}

function isRedirect(status) {
  return status >= 300 && status < 400;
}

export default {
  async fetch(request, env) {
    const debug = env.DEBUG === "true" || env.DEBUG === "1";
    const log = (event, fields = {}) => {
      if (debug) console.log(JSON.stringify({ event, ...fields }));
    };

    const incoming = new URL(request.url);
    log("request", {
      method: request.method,
      path: incoming.pathname,
      hasHFToken: Boolean(env.HF_TOKEN),
      hfTokenLength: env.HF_TOKEN?.length || 0,
      hasProxyKey: Boolean(env.PROXY_KEY),
      envKeys: Object.keys(env).sort(),
    });

    if (request.method !== "GET" && request.method !== "HEAD") {
      log("rejected_method", { method: request.method });
      return new Response("Method Not Allowed", {
        status: 405,
        headers: { Allow: "GET, HEAD" },
      });
    }

    if (!env.HF_TOKEN) {
      log("missing_hf_token");
      return new Response("HF_TOKEN is not configured", { status: 500 });
    }

    if (env.PROXY_KEY) {
      const authorization = request.headers.get("authorization") || "";
      if (authorization !== `Bearer ${env.PROXY_KEY}`) {
        log("rejected_proxy_key");
        return unauthorized();
      }
    }

    const parsed = parseDownloadPath(incoming.pathname, env);
    if (!parsed) {
      log("rejected_path");
      return new Response(
        "Use /<owner>/<repo>/(blob|resolve)/<ref>/<path> for a Hugging Face file",
        { status: 404 },
      );
    }

    const target = new URL(
      `/${encodeURIComponent(parsed.repo).replaceAll("%2F", "/")}/resolve/${encodeURIComponent(parsed.ref)}/${parsed.file
        .split("/")
        .map(encodeURIComponent)
        .join("/")}`,
      HF_ORIGIN,
    );
    log("target", { repo: parsed.repo, ref: parsed.ref, file: parsed.file });
    for (const [key, value] of incoming.searchParams) target.searchParams.append(key, value);

    // Follow a short redirect chain ourselves so the HF token is only ever
    // sent to huggingface.co, never to a signed storage/CDN host.
    let response;
    let currentURL = target;
    for (let hop = 0; hop < 4; hop += 1) {
      const requestHeaders = clientHeaders(request);
      if (currentURL.origin === HF_ORIGIN) {
        requestHeaders.set("Authorization", `Bearer ${env.HF_TOKEN}`);
      }
      try {
        response = await fetch(currentURL, {
          method: request.method,
          headers: requestHeaders,
          redirect: "manual",
        });
        log("origin_response", {
          hop,
          status: response.status,
          origin: currentURL.origin,
          redirected: isRedirect(response.status),
        });
      } catch {
        log("origin_fetch_error", { hop, origin: currentURL.origin });
        return new Response("Unable to reach Hugging Face", { status: 502 });
      }
      if (!isRedirect(response.status)) break;
      const location = response.headers.get("location");
      if (!location) return new Response("Origin redirect without location", { status: 502 });
      currentURL = new URL(location, currentURL);
      log("redirect", { hop, nextOrigin: currentURL.origin });
      if (hop === 3) return new Response("Too many origin redirects", { status: 502 });
    }

    return new Response(request.method === "HEAD" ? null : response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders(response),
    });
  },
};
