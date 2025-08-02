"use client";

export function LogoLink({ children }) {
  return (
    <a
      href="https://neurascale.io"
      style={{ textDecoration: "none", color: "inherit" }}
    >
      {children}
    </a>
  );
}
