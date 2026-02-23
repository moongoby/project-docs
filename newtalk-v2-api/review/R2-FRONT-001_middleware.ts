import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const TOKEN_KEY = "newtalk_token";
const PUBLIC_PATHS = ["/login", "/register", "/"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (PUBLIC_PATHS.some((p) => p === pathname || pathname.startsWith("/register"))) {
    return NextResponse.next();
  }
  const token = request.cookies.get(TOKEN_KEY)?.value;
  if (!token) {
    const login = new URL("/login", request.url);
    return NextResponse.redirect(login);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
