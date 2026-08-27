import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  async rewrites() {
    // Allows dynamic proxying to the FastAPI backend based on environment
    // Defaults to localhost for development if not provided
    const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
    
    return [
      {
        source: '/api/v1/:path*',
        destination: `${backendUrl}/api/v1/:path*`, // Proxy to Backend
      },
    ]
  },
};

export default nextConfig;
