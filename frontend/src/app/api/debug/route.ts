import { NextResponse } from "next/server";

export async function GET() {
  const API_BASE: string = "https://backend-api-production-8923.up.railway.app";
  return NextResponse.json({
    API_BASE,
    env: process.env.NEXT_PUBLIC_API_URL || "(not set)",
    timestamp: new Date().toISOString(),
  });
}
