"use client";

import { useTheme } from "@/contexts/ThemeContext";

export default function ThemeTestPage() {
  const { isDarkMode, toggleDarkMode } = useTheme();

  return (
    <div className="min-h-screen app-bg p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold app-text">Theme Test Page</h1>

        <div className="app-card p-6 space-y-4">
          <h2 className="text-lg font-semibold app-text">
            Current Theme: {isDarkMode ? "Dark" : "Light"}
          </h2>

          <button
            onClick={toggleDarkMode}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Toggle Theme
          </button>

          <div className="space-y-2">
            <p className="app-text">Primary text color</p>
            <p className="app-text-secondary">Secondary text color</p>
            <p className="app-text-tertiary">Tertiary text color</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="app-card p-4">
              <h3 className="app-text font-medium">Nested Card 1</h3>
              <p className="app-text-secondary text-sm">
                This is a nested card to test styling
              </p>
            </div>
            <div className="app-card p-4">
              <h3 className="app-text font-medium">Nested Card 2</h3>
              <p className="app-text-secondary text-sm">Another nested card</p>
            </div>
          </div>
        </div>

        <div className="app-card p-6">
          <h2 className="text-lg font-semibold app-text mb-4">
            CSS Variable Values
          </h2>
          <div className="space-y-2 text-sm font-mono">
            <div>
              Document has dark class:{" "}
              {typeof document !== "undefined" &&
              document.documentElement.classList.contains("dark")
                ? "true"
                : "false"}
            </div>
            <div>Theme state isDarkMode: {isDarkMode ? "true" : "false"}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
