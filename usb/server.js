// Dependency-free static server for the offline USB package.
// Serves ./site on port 3010 to this PC and the local network (for TVs).
const http = require("http");
const fs = require("fs");
const path = require("path");
const os = require("os");

const root = path.join(__dirname, "site");
const port = Number(process.env.PORT || 3010);
const types = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8",
  ".txt": "text/plain; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png",
  ".ico": "image/x-icon", ".woff2": "font/woff2",
};

function resolve(urlPath) {
  let file = path.normalize(path.join(root, decodeURIComponent(urlPath)));
  if (!file.startsWith(root)) return null;
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, "index.html");
  if (!fs.existsSync(file) && fs.existsSync(file + ".html")) file += ".html";
  return fs.existsSync(file) ? file : null;
}

http.createServer((req, res) => {
  const file = resolve(new URL(req.url, "http://localhost").pathname);
  if (!file) {
    res.writeHead(404, { "Content-Type": types[".html"] });
    return fs.createReadStream(path.join(root, "404.html")).pipe(res);
  }
  res.writeHead(200, { "Content-Type": types[path.extname(file)] || "application/octet-stream", "Cache-Control": "no-cache" });
  fs.createReadStream(file).pipe(res);
}).listen(port, "0.0.0.0", () => {
  const ips = Object.values(os.networkInterfaces()).flat()
    .filter((n) => n && n.family === "IPv4" && !n.internal).map((n) => n.address);
  console.log("");
  console.log("  Onumcilik gozegciligi isleyar (SIMULYASIYA)");
  console.log(`  Bu kompyuter : http://localhost:${port}/`);
  console.log(`  TV gornusi   : http://localhost:${port}/tv/`);
  ips.forEach((ip) => console.log(`  Tor arkaly   : http://${ip}:${port}/tv/`));
  console.log("");
  console.log("  Yapmak ucin su penjireni yapyn.");
});
