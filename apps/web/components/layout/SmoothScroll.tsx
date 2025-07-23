export default function SmoothScroll({ children }: { children: React.ReactNode }) {
  // Just return children without any smooth scroll library
  // Use native CSS scroll-behavior: smooth instead
  return <>{children}</>;
}
