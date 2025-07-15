"use client";

import React, { useState } from "react";
import { Search, Menu, HelpCircle, User } from "lucide-react";
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
    <header className="flex-shrink-0 flex items-center justify-between border-b border-[var(--border)] bg-[var(--card-bg)] px-4 py-2 h-14">
      {/* Left section */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onMenuClick}
          className="p-1.5 hover:bg-gray-100 rounded-md transition-colors"
        >
          <svg
            className="h-5 w-5 text-gray-700"
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

        <div className="flex items-center gap-3">
          <div className="flex items-center">
            <span className="font-extrabold text-lg tracking-wider">
              <span className="text-black">NEURA</span>
              <span className="text-[#4185f4]">SCALE</span>
            </span>
          </div>
          <div className="w-px h-6 bg-gray-300" />
          <div className="flex items-center">
            {/* MIT Logo */}
            <svg
              className="h-5 w-auto"
              viewBox="0 0 536.229 536.229"
              fill="black"
              fillOpacity="1"
              xmlns="http://www.w3.org/2000/svg"
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
      </div>

      {/* Center - Search */}
      <div className="flex-1 max-w-3xl mx-8">
        <div className="relative">
          <input
            type="text"
            placeholder="Search (/)"
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="w-full pl-10 pr-4 py-1.5 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:bg-white focus:border-gray-400 transition-all duration-200 placeholder:text-gray-500 text-sm"
          />
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-500" />
        </div>
      </div>

      {/* Right section */}
      <div className="flex items-center space-x-1">
        <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <svg
            className="h-5 w-5 text-gray-600"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M20 2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM8 20H5c-.55 0-1-.45-1-1v-3h4v4zm0-6H4v-4h4v4zm0-6H4V5c0-.55.45-1 1-1h3v4zm6 12h-4v-4h4v4zm0-6h-4v-4h4v4zm0-6h-4V4h4v4zm6 12h-3c-.55 0-1-.45-1-1v-3h4v4zm0-6h-4v-4h4v4zm0-6h-4V4h3c.55 0 1 .45 1 1v3z" />
          </svg>
        </button>

        <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <svg
            className="h-5 w-5 text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </button>

        <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <SettingsIcon className="h-5 w-5 text-gray-600" />
        </button>

        {user ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="ml-2 rounded-full focus:outline-none">
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
