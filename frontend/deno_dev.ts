import { serve } from "https://deno.land/std@0.205.0/http/server.ts";
import { extname } from "https://deno.land/std@0.205.0/path/mod.ts";

const root = new URL("./", import.meta.url);
const importMapPath = new URL("./import_map.json", root);
const mimeTypes: Record<string, string> = {
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon"
};

const cache = new Map<string, { mtime: number; output: string }>();

async function fileExists(url: URL): Promise<boolean> {
  try {
    const stat = await Deno.stat(url);
    return stat.isFile;
  } catch {
    return false;
  }
}

async function bundleSource(entry: URL): Promise<string> {
  try {
    const result = await Deno.emit(entry, {
      bundle: "module",
      importMapPath: importMapPath.href,
      compilerOptions: {
        jsx: "react-jsx",
        target: "es2022"
      }
    });
    const fileKey = Object.keys(result.files).find(key => key.endsWith("/bundle.js") || key === "deno:///bundle.js" || key === "deno://bundle.js");
    if (!fileKey) {
      throw new Error("Deno bundle output not found.");
    }
    return result.files[fileKey];
  } catch (error) {
    throw new Error(`Deno build failed: ${error.message}`);
  }
}

serve(async (req) => {
  const url = new URL(req.url);
  const pathname = decodeURIComponent(url.pathname === "/" ? "/index.html" : url.pathname);
  const fileUrl = new URL(`.${pathname}`, root);

  if (!fileUrl.href.startsWith(root.href)) {
    return new Response("Not found", { status: 404 });
  }

  if (pathname.endsWith(".tsx") || pathname.endsWith(".ts")) {
    const stat = await Deno.stat(fileUrl);
    const mtime = stat.mtime?.getTime() ?? 0;
    const cached = cache.get(fileUrl.href);
    if (cached && cached.mtime === mtime) {
      return new Response(cached.output, {
        status: 200,
        headers: { "content-type": "application/javascript; charset=utf-8" }
      });
    }

    try {
      const output = await bundleSource(fileUrl);
      cache.set(fileUrl.href, { mtime, output });
      return new Response(output, {
        status: 200,
        headers: { "content-type": "application/javascript; charset=utf-8" }
      });
    } catch (error) {
      return new Response(error.message, { status: 500, headers: { "content-type": "text/plain; charset=utf-8" } });
    }
  }

  if (await fileExists(fileUrl)) {
    const data = await Deno.readFile(fileUrl);
    const headers = new Headers();
    const ext = extname(fileUrl.pathname).toLowerCase();
    headers.set("content-type", mimeTypes[ext] ?? "application/octet-stream");
    return new Response(data, { status: 200, headers });
  }

  return new Response("Not found", { status: 404 });
}, { port: 4173 });
