import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  output: "standalone",
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "public-frontend-cos.metadl.com",
      },
    ],
  },
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || "https://backend-api-production-8923.up.railway.app";
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
