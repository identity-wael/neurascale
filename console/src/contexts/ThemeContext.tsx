"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

interface ThemeContextType {
  isDarkMode: boolean;
  toggleDarkMode: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Check if user has a saved preference
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
      setIsDarkMode(savedTheme === "dark");
    } else {
      // Check system preference
      const prefersDark = window.matchMedia(
        "(prefers-color-scheme: dark)",
      ).matches;
      setIsDarkMode(prefersDark);
    }
  }, []);

  useEffect(() => {
    // Apply or remove dark class on document element
    console.log(
      "ThemeContext: Setting theme to",
      isDarkMode ? "dark" : "light",
    );
    if (isDarkMode) {
      document.documentElement.classList.add("dark");
      console.log("ThemeContext: Added dark class to HTML");
    } else {
      document.documentElement.classList.remove("dark");
      console.log("ThemeContext: Removed dark class from HTML");
    }
    console.log(
      "ThemeContext: HTML classes are now:",
      document.documentElement.className,
    );
    // Save preference
    localStorage.setItem("theme", isDarkMode ? "dark" : "light");
  }, [isDarkMode]);

  const toggleDarkMode = () => {
    console.log(
      "ThemeContext: Toggle clicked! Current:",
      isDarkMode,
      "-> New:",
      !isDarkMode,
    );
    setIsDarkMode(!isDarkMode);
  };

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleDarkMode }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}
