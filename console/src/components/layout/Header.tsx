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
    <header
      className="flex-shrink-0 flex items-center justify-between h-[48px] px-2"
      style={{
        backgroundColor: "#303134",
        borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
      }}
    >
      {/* Left section */}
      <div className="flex items-center">
        <button
          onClick={onMenuClick}
          className="flex items-center justify-center w-10 h-10 ml-1 rounded transition-colors"
          style={{
            color: "#E8EAED",
            backgroundColor: "transparent",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.08)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
          }}
          onMouseDown={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.12)";
          }}
          onMouseUp={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.08)";
          }}
        >
          <svg
            className="h-5 w-5"
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

        <div className="flex items-center gap-4 ml-2">
          <div className="flex items-center">
            <span className="font-medium text-[18px]">
              <span style={{ color: "var(--foreground)" }}>NEURA</span>
              <span className="text-[#4185f4]">SCALE</span>
            </span>
          </div>

          {/* Project Selector */}
          <button
            className="flex items-center gap-2 h-9 px-3 rounded transition-all duration-200"
            style={{
              backgroundColor: "transparent",
              color: "#E8EAED",
              border: "1px solid transparent",
              minWidth: "200px",
              maxWidth: "280px",
              fontFamily: '"Google Sans", Roboto, Arial, sans-serif',
              fontSize: "14px",
              fontWeight: "400",
              lineHeight: "20px",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor =
                "rgba(255, 255, 255, 0.08)";
              e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.08)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "transparent";
              e.currentTarget.style.borderColor = "transparent";
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = "#8AB4F8";
              e.currentTarget.style.outline = "none";
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = "transparent";
            }}
          >
            <svg className="h-4 w-4" fill="#8AB4F8" viewBox="0 0 24 24">
              <path d="M3 3h8v8H3zm10 0h8v8h-8zM3 13h8v8H3z" />
            </svg>
            <span>neurascale-console</span>
            <ChevronRight
              className="h-5 w-5 ml-auto"
              style={{
                transform: "rotate(90deg)",
                color: "#9AA0A6",
              }}
            />
          </button>
        </div>
      </div>

      {/* Center - Search */}
      <div className="flex-1 flex items-center justify-center mx-4">
        <div
          className="w-full max-w-[720px] h-10 flex items-center rounded"
          style={{
            backgroundColor: "#202124",
            border: "1px solid #5F6368",
          }}
        >
          <Search className="h-5 w-5 mx-3" style={{ color: "#9AA0A6" }} />
          <input
            type="text"
            placeholder="Search resources, docs, and products"
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="flex-1 bg-transparent border-none outline-none text-sm"
            style={{
              color: "#E8EAED",
              fontFamily: "Roboto, Arial, sans-serif",
              fontSize: "14px",
              lineHeight: "20px",
            }}
            onFocus={(e) => {
              e.currentTarget.parentElement!.style.borderColor = "#8AB4F8";
              e.currentTarget.parentElement!.style.boxShadow =
                "0 0 0 1px #8AB4F8";
            }}
            onBlur={(e) => {
              e.currentTarget.parentElement!.style.borderColor = "#5F6368";
              e.currentTarget.parentElement!.style.boxShadow = "none";
            }}
          />
          <button
            className="h-8 px-6 mr-1 rounded font-medium transition-all duration-200"
            style={{
              backgroundColor: "#1A73E8",
              color: "#FFFFFF",
              fontFamily: '"Google Sans", Roboto, Arial, sans-serif',
              fontSize: "14px",
              fontWeight: "500",
              letterSpacing: "0.25px",
              border: "none",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "#1765CC";
              e.currentTarget.style.boxShadow =
                "0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "#1A73E8";
              e.currentTarget.style.boxShadow = "none";
            }}
            onClick={() => {
              console.log("Search clicked:", searchValue);
            }}
          >
            Search
          </button>
        </div>
      </div>

      {/* Right section */}
      <div className="flex items-center gap-1">
        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200"
          style={{
            color: "#E8EAED",
            backgroundColor: "transparent",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.08)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
          }}
          onMouseDown={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.12)";
          }}
          onMouseUp={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.08)";
          }}
          title="Gemini AI Assistant"
        >
          <Sparkles className="h-5 w-5" />
        </button>

        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200"
          style={{
            color: "#E8EAED",
            backgroundColor: "transparent",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.08)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
          }}
          onMouseDown={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.12)";
          }}
          onMouseUp={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.08)";
          }}
          title="Cloud Shell"
        >
          <Terminal className="h-5 w-5" />
        </button>

        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200 relative"
          style={{
            color: "#E8EAED",
            backgroundColor: "transparent",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.08)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
          }}
          onMouseDown={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.12)";
          }}
          onMouseUp={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.08)";
          }}
          title="Notifications"
        >
          <Bell className="h-5 w-5" />
          <span
            className="absolute top-0.5 right-0.5 min-w-[16px] h-4 px-1 rounded-lg flex items-center justify-center text-[11px] font-medium"
            style={{
              backgroundColor: "#EA4335",
              color: "#FFFFFF",
            }}
          >
            3
          </span>
        </button>

        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200"
          style={{
            color: "#E8EAED",
            backgroundColor: "transparent",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.08)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
          }}
          onMouseDown={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.12)";
          }}
          onMouseUp={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.08)";
          }}
          title="Help"
        >
          <HelpCircle className="h-5 w-5" />
        </button>

        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200"
          style={{
            color: "#E8EAED",
            backgroundColor: "transparent",
          }}
          onClick={toggleDarkMode}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.08)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
          }}
          onMouseDown={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.12)";
          }}
          onMouseUp={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.08)";
          }}
          title={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
        >
          {isDarkMode ? (
            <Sun className="h-5 w-5" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
        </button>

        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200"
          style={{
            color: "#E8EAED",
            backgroundColor: "transparent",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.08)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
          }}
          onMouseDown={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.12)";
          }}
          onMouseUp={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.08)";
          }}
          title="Settings"
        >
          <SettingsIcon className="h-5 w-5" />
        </button>

        {user ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="ml-2 rounded-full focus:outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#8AB4F8]">
                <Avatar className="h-8 w-8">
                  <AvatarImage
                    src={user.photoURL || ""}
                    alt={user.displayName || ""}
                  />
                  <AvatarFallback className="bg-[#1A73E8] text-white text-sm font-medium">
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
