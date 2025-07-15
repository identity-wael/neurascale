"use client";

import React, { useState } from "react";
import {
  Search,
  Menu,
  HelpCircle,
  User,
  Moon,
  Sun,
  ChevronRight,
  Sparkles,
  Terminal,
  Bell,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import { SettingsIcon } from "@/components/icons/GCPIcons";

interface HeaderProps {
  onMenuClick: () => void;
  onHideSidebar?: () => void;
  isSidebarHidden?: boolean;
}

export default function Header({
  onMenuClick,
  onHideSidebar,
  isSidebarHidden,
}: HeaderProps) {
  const { user, signInWithGoogle, logout } = useAuth();
  const { isDarkMode, toggleDarkMode } = useTheme();
  const [searchValue, setSearchValue] = useState("");

  const handleSignIn = async () => {
    try {
      await signInWithGoogle();
    } catch (error) {
      console.error("Sign in failed:", error);
    }
  };

  const handleSignOut = async () => {
    try {
      await logout();
    } catch (error) {
      console.error("Sign out failed:", error);
    }
  };

  const getUserInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <header className="flex-shrink-0 flex items-center justify-between border-b border-[var(--border)] bg-[var(--card-bg)] h-[48px]">
      {/* Left section */}
      <div className="flex items-center">
        <button
          onClick={onMenuClick}
          className="flex items-center justify-center w-12 h-12 ml-2 rounded-full transition-colors"
          style={{
            color: "var(--foreground)",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(59, 130, 246, 0.1)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
          }}
        >
          <svg
            className="h-6 w-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>

        <div className="flex items-center gap-3 ml-3">
          <div className="flex items-center">
            <span className="font-medium text-[18px]">
              <span style={{ color: "var(--foreground)" }}>NEURA</span>
              <span className="text-[#4185f4]">SCALE</span>
            </span>
          </div>

          {/* Project Selector */}
          <button
            className="flex items-center gap-2 px-3 py-1.5 rounded-md transition-colors text-sm"
            style={{
              backgroundColor: "transparent",
              color: "var(--foreground)",
              border: "1px solid var(--border)",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "var(--card-hover)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "transparent";
            }}
          >
            <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M3 3h8v8H3zm10 0h8v8h-8zM3 13h8v8H3z" />
            </svg>
            <span className="font-medium">neurascale-console</span>
            <ChevronRight
              className="h-4 w-4"
              style={{ transform: "rotate(90deg)" }}
            />
          </button>
        </div>
      </div>

      {/* Center - Search */}
      <div className="flex-1 max-w-3xl mx-4">
        <div className="flex items-center">
          <div className="relative flex-1">
            <input
              type="text"
              placeholder="Search (/) for resources, docs, products, and more"
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              className="w-full pl-4 pr-10 h-[38px] rounded-l focus:outline-none transition-all duration-200 text-[14px] leading-[20px] placeholder:text-[#9aa0a6]"
              style={{
                backgroundColor: "rgba(32, 33, 36, 1)",
                border: "1px solid rgba(95, 99, 104, 1)",
                borderRight: "none",
                borderRadius: "4px 0 0 4px",
                color: "rgba(232, 234, 237, 1)",
              }}
              onFocus={(e) => {
                e.currentTarget.style.backgroundColor = "rgba(48, 49, 52, 1)";
                e.currentTarget.style.borderColor = "rgba(138, 180, 248, 1)";
              }}
              onBlur={(e) => {
                e.currentTarget.style.backgroundColor = "rgba(32, 33, 36, 1)";
                e.currentTarget.style.borderColor = "rgba(95, 99, 104, 1)";
              }}
            />
          </div>
          <button
            className="px-3 h-[38px] rounded-r font-medium text-[14px] transition-colors flex items-center justify-center gap-1"
            style={{
              backgroundColor: "rgba(48, 49, 52, 1)",
              border: "1px solid rgba(95, 99, 104, 1)",
              borderLeft: "none",
              borderRadius: "0 4px 4px 0",
              color: "rgba(138, 180, 248, 1)",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "rgba(60, 64, 67, 1)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "rgba(48, 49, 52, 1)";
            }}
            title="Search"
          >
            <Search className="h-[18px] w-[18px]" />
            <span className="sr-only">Search</span>
          </button>
        </div>
      </div>

      {/* Right section */}
      <div className="flex items-center gap-1 mr-2">
        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-colors"
          style={{ color: "var(--foreground)" }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(59, 130, 246, 0.1)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
          }}
          title="Gemini AI Assistant"
        >
          <Sparkles className="h-[18px] w-[18px]" />
        </button>

        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-colors"
          style={{ color: "var(--foreground)" }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(59, 130, 246, 0.1)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
          }}
          title="Cloud Shell"
        >
          <Terminal className="h-[18px] w-[18px]" />
        </button>

        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-colors relative"
          style={{ color: "var(--foreground)" }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(59, 130, 246, 0.1)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
          }}
          title="Notifications"
        >
          <Bell className="h-[18px] w-[18px]" />
          <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"></span>
        </button>

        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-colors"
          style={{ color: "var(--foreground)" }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(59, 130, 246, 0.1)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
          }}
          title="Help"
        >
          <HelpCircle className="h-[18px] w-[18px]" />
        </button>

        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-colors"
          style={{ color: "var(--foreground)" }}
          onClick={toggleDarkMode}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(59, 130, 246, 0.1)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
          }}
          title={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
        >
          {isDarkMode ? (
            <Sun className="h-[18px] w-[18px]" />
          ) : (
            <Moon className="h-[18px] w-[18px]" />
          )}
        </button>

        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-colors"
          style={{ color: "var(--foreground)" }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(59, 130, 246, 0.1)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
          }}
        >
          <SettingsIcon className="h-[18px] w-[18px]" />
        </button>

        {user ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="ml-3 rounded-full focus:outline-none">
                <Avatar className="h-8 w-8">
                  <AvatarImage
                    src={user.photoURL || ""}
                    alt={user.displayName || ""}
                  />
                  <AvatarFallback className="bg-blue-600 text-white text-sm">
                    {getUserInitials(user.displayName || user.email || "U")}
                  </AvatarFallback>
                </Avatar>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">
                    {user.displayName}
                  </p>
                  <p className="text-xs leading-none text-muted-foreground">
                    {user.email}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="mr-2 h-4 w-4" />
                <span>Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <SettingsIcon className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleSignOut}>
                <span>Sign out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <button
            onClick={handleSignIn}
            className="ml-2 px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
          >
            Sign in
          </button>
        )}
      </div>
    </header>
  );
}
