import "../styles/globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "NeuraScale Documentation",
  description:
    "Comprehensive documentation for NeuraScale - Open-source neuromorphic computing platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
