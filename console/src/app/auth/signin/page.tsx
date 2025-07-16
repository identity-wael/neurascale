"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";

export default function SignInPage() {
  const { user, signInWithGoogle, loading } = useAuth();
  const router = useRouter();
  const [isSigningIn, setIsSigningIn] = useState(false);

  useEffect(() => {
    if (user) {
      // Force reload to trigger middleware with new cookie
      window.location.href = "/";
    }
  }, [user]);

  const handleSignIn = async () => {
    console.log("Sign in button clicked");
    setIsSigningIn(true);
    try {
      console.log("Attempting Google sign in...");
      await signInWithGoogle();
      console.log("Sign in successful");
    } catch (error) {
      console.error("Sign in failed:", error);
      alert(
        `Sign in failed: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
      );
    } finally {
      setIsSigningIn(false);
    }
  };

  if (loading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: "var(--background)" }}
      >
        <div
          className="animate-spin rounded-full h-32 w-32 border-b-2"
          style={{ borderColor: "var(--primary)" }}
        ></div>
      </div>
    );
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4"
      style={{ backgroundColor: "var(--background)" }}
    >
      <div className="w-full max-w-md">
        {/* Logo Section */}
        <div className="flex justify-center">
          <div className="flex items-center gap-4">
            <span
              className="font-extrabold text-2xl tracking-wider"
              style={{ fontFamily: "Proxima Nova, sans-serif" }}
            >
              <span className="text-black">NEURA</span>
              <span className="text-[#4185f4]">SCALE</span>
            </span>
            <div
              className="w-px h-6"
              style={{ backgroundColor: "var(--foreground)", opacity: 0.3 }}
            />
            <svg
              className="h-8 w-auto"
              viewBox="0 0 536.229 536.229"
              fill="currentColor"
              fillOpacity="0.8"
              xmlns="http://www.w3.org/2000/svg"
              style={{ color: "var(--foreground)" }}
            >
              <g>
                <g>
                  <rect y="130.031" width="58.206" height="276.168" />
                  <rect
                    x="95.356"
                    y="130.031"
                    width="58.206"
                    height="190.712"
                  />
                  <rect
                    x="190.712"
                    y="130.031"
                    width="58.206"
                    height="276.168"
                  />
                  <rect
                    x="381.425"
                    y="217.956"
                    width="58.212"
                    height="188.236"
                  />
                  <rect
                    x="381.425"
                    y="130.031"
                    width="154.805"
                    height="58.206"
                  />
                  <rect x="286.074" y="217.956" width="58.2" height="188.236" />
                  <rect x="286.074" y="130.031" width="58.2" height="58.206" />
                </g>
              </g>
            </svg>
          </div>
        </div>

        {/* Spacer */}
        <div style={{ height: "40px" }}></div>

        {/* Title Section */}
        <div className="text-center">
          <h2
            className="text-3xl font-bold"
            style={{ color: "var(--foreground)" }}
          >
            Sign in to your account
          </h2>
          <div style={{ height: "12px" }}></div>
          <p
            className="text-sm"
            style={{ color: "var(--foreground)", opacity: 0.7 }}
          >
            Access your Application Cloud Console
          </p>
        </div>

        {/* Spacer */}
        <div style={{ height: "40px" }}></div>

        {/* Card Section */}
        <div
          className="shadow-md rounded-lg"
          style={{
            backgroundColor: "var(--card-bg)",
            padding: "32px 28px",
            border: "1px solid var(--border)",
          }}
        >
          {/* Google Sign In Button */}
          <Button
            onClick={handleSignIn}
            disabled={isSigningIn}
            className="w-full flex justify-center items-center px-4 py-3 border rounded-md shadow-sm text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors custom-focus-ring"
            style={
              {
                borderColor: "var(--border)",
                backgroundColor: "var(--card-bg)",
                color: "var(--foreground)",
              } as React.CSSProperties
            }
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "var(--card-hover)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "var(--card-bg)";
            }}
            variant="outline"
          >
            <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="currentColor"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="currentColor"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="currentColor"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            {isSigningIn ? "Signing in..." : "Continue with Google"}
          </Button>

          {/* Spacer */}
          <div style={{ height: "24px" }}></div>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div
                className="w-full border-t"
                style={{ borderColor: "var(--border)" }}
              />
            </div>
            <div className="relative flex justify-center text-sm">
              <span
                className="px-3"
                style={{
                  backgroundColor: "var(--card-bg)",
                  color: "var(--foreground)",
                  opacity: 0.5,
                }}
              >
                Secure authentication powered by Firebase
              </span>
            </div>
          </div>

          {/* Spacer */}
          <div style={{ height: "24px" }}></div>

          {/* Terms */}
          <div className="text-center">
            <p
              className="text-xs leading-5"
              style={{ color: "var(--foreground)", opacity: 0.5 }}
            >
              By signing in, you agree to our Terms of Service and Privacy
              Policy.
              <br />
              New to NeuraScale? Your account will be created automatically.
            </p>
          </div>
        </div>

        {/* Spacer */}
        <div style={{ height: "24px" }}></div>

        {/* Footer Link */}
        <div className="text-center">
          <a
            href="https://neurascale.io"
            className="inline-flex items-center text-sm transition-colors"
            style={{ color: "var(--foreground)", opacity: 0.7 }}
            onMouseEnter={(e) => {
              e.currentTarget.style.opacity = "1";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = "0.7";
            }}
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to NeuraScale
          </a>
        </div>
      </div>
    </div>
  );
}
