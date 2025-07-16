import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  // Get the pathname of the request (e.g. /, /auth/signin)
  const path = request.nextUrl.pathname;

  // Define paths that require authentication
  const isProtectedPath = path === "/" || path.startsWith("/dashboard");
  const isAuthPath = path.startsWith("/auth");

  // Get the token from the cookies
  const token = request.cookies.get("__session"); // Firebase Auth uses __session cookie name

  // Redirect to /auth/signin if the user is not authenticated and trying to access a protected route
  if (isProtectedPath && !token) {
    return NextResponse.redirect(new URL("/auth/signin", request.url));
  }

  // Redirect to / if the user is authenticated and trying to access an auth route
  if (isAuthPath && token) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

// See "Matching Paths" below to learn more
export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
