/** @type {import('next').NextConfig} */
const offline = process.env.NEXT_PUBLIC_DATA_SOURCE === "replay";

const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  // Offline USB build: plain static files, served by usb/server.js.
  ...(offline ? { output: "export", trailingSlash: true, distDir: ".next-usb" } : {}),
};

export default nextConfig;
