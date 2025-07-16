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
  ChevronDown,
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
      className="flex-shrink-0 flex items-center justify-between h-[48px] px-2 app-header"
      style={{
        padding: "0 8px",
      }}
    >
      {/* Left section */}
      <div className="flex items-center">
        <button
          onClick={onMenuClick}
          className="flex items-center justify-center w-10 h-10 rounded transition-colors app-header-button"
          style={{
            marginLeft: "4px",
            borderRadius: "4px",
          }}
        >
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            style={{ width: "20px", height: "20px" }}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>

        <div className="flex items-center ml-2">
          <div
            className="flex items-center"
            style={{ marginLeft: "8px", marginRight: "16px" }}
          >
            <span className="font-medium text-[18px]">
              <span className="text-black dark:text-[#E8EAED]">NEURA</span>
              <span className="text-[#4185f4]">SCALE</span>
            </span>
          </div>

          {/* Project Selector */}
          <button
            className="flex items-center rounded h-10 app-project-selector"
            style={{
              maxWidth: "280px",
              fontFamily: '"Google Sans Text", Roboto, Arial, sans-serif',
              fontSize: "14px",
              fontWeight: "400",
              lineHeight: "20px",
              letterSpacing: "0.2px",
              borderRadius: "4px",
              height: "40px",
              padding: "5px 8px",
              gap: "8px",
              marginLeft: "16px",
              transition: "all 150ms cubic-bezier(0.4, 0, 0.2, 1)",
              cursor: "pointer",
            }}
            aria-label="Select a project"
          >
            <svg
              className="h-4 w-4 flex-shrink-0 app-project-icon"
              viewBox="0 0 24 24"
              style={{ width: "16px", height: "16px" }}
            >
              <path d="M3 3h8v8H3zm10 0h8v8h-8zM3 13h8v8H3z" />
            </svg>
            <span className="flex-1 text-left overflow-hidden text-ellipsis whitespace-nowrap">
              neurascale-console
            </span>
          </button>
        </div>
      </div>

      {/* Center - Search */}
      <div
        className="flex-1 flex items-center justify-center"
        style={{ margin: "0 16px" }}
      >
        <div
          className="w-full max-w-[720px] h-10 flex items-center rounded app-search-bar"
          style={{
            borderRadius: "4px",
          }}
        >
          <Search className="h-5 w-5 mx-3 app-search-icon" />
          <input
            type="text"
            placeholder="Search resources, docs, and products"
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="flex-1 bg-transparent border-none outline-none text-sm app-text"
            style={{
              fontFamily: "Roboto, Arial, sans-serif",
              fontSize: "14px",
              lineHeight: "20px",
              paddingTop: "0",
              paddingBottom: "0",
            }}
            onKeyPress={(e) => {
              if (e.key === "Enter") {
                console.log("Search triggered:", searchValue);
              }
            }}
          />
          <button
            className="h-10 flex items-center justify-center transition-all duration-200 app-search-button"
            style={{
              fontFamily: '"Google Sans", Roboto, Arial, sans-serif',
              fontSize: "14px",
              fontWeight: "500",
              letterSpacing: "0.25px",
              border: "none",
              borderTopRightRadius: "4px",
              borderBottomRightRadius: "4px",
              minWidth: "100px",
              cursor: "pointer",
              padding: "0 20px",
            }}
            onClick={() => {
              console.log("Search clicked:", searchValue);
            }}
            aria-label="Search"
          >
            <div className="flex items-center gap-2">
              <Search className="h-[18px] w-[18px]" />
              <span>Search</span>
            </div>
          </button>
        </div>
      </div>

      {/* Right section */}
      <div className="flex items-center" style={{ gap: "4px" }}>
        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200 app-header-button"
          title="Gemini AI Assistant"
        >
          <Sparkles className="h-5 w-5" />
        </button>

        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200 app-header-button"
          title="Cloud Shell"
        >
          <Terminal className="h-5 w-5" />
        </button>

        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200 relative app-header-button"
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
          className="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200 app-header-button"
          title="Help"
        >
          <HelpCircle className="h-5 w-5" />
        </button>

        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200 app-header-button"
          onClick={toggleDarkMode}
          title={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
        >
          {isDarkMode ? (
            <Sun className="h-5 w-5" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
        </button>

        <button
          className="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200 app-header-button"
          title="Settings"
        >
          <SettingsIcon className="h-5 w-5" />
        </button>

        {user ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="rounded-full focus:outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#8AB4F8]"
                style={{ marginLeft: "8px" }}
              >
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
