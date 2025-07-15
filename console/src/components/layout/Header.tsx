"use client";

import React, { useState } from "react";
import { Search, Menu, Settings, HelpCircle, User } from "lucide-react";
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

interface HeaderProps {
  onMenuClick: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
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
    <header className="flex items-center justify-between border-b border-gray-100 bg-white/80 backdrop-blur-sm px-6 py-3 h-16 shadow-sm">
      {/* Left section */}
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="icon" onClick={onMenuClick}>
          <Menu className="h-5 w-5" />
        </Button>

        <div className="flex items-center gap-4">
          <a className="flex items-center justify-center" href="#">
            <span className="sr-only">NEURASCALE</span>
            <span
              className="font-extrabold text-base sm:text-lg tracking-wider"
              style={{ fontFamily: "Proxima Nova, sans-serif" }}
            >
              <span className="text-black">NEURA</span>
              <span className="text-[#4185f4]">SCALE</span>
            </span>
          </a>
          <div className="w-px h-6 bg-gray-200" />
          <div className="flex items-center">
            {/* MIT Logo */}
            <svg
              className="h-5 lg:h-6 w-auto"
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
      <div className="flex-1 max-w-md mx-4">
        <div className="relative group">
          <input
            type="text"
            placeholder="Search services and resources"
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="w-full pl-4 pr-10 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white transition-all duration-200 placeholder:text-gray-400 text-sm"
          />
          <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
        </div>
      </div>

      {/* Right section */}
      <div className="flex items-center space-x-2">
        <Button variant="ghost" size="icon">
          <HelpCircle className="h-5 w-5" />
        </Button>

        <Button variant="ghost" size="icon">
          <Settings className="h-5 w-5" />
        </Button>

        {user ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-10 w-10 rounded-full p-0">
                <Avatar className="h-8 w-8">
                  <AvatarImage
                    src={user.photoURL || ""}
                    alt={user.displayName || ""}
                  />
                  <AvatarFallback className="bg-blue-600 text-white text-sm">
                    {getUserInitials(user.displayName || user.email || "U")}
                  </AvatarFallback>
                </Avatar>
              </Button>
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
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleSignOut}>
                <span>Sign out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <Button onClick={handleSignIn} variant="outline" size="sm">
            Sign in
          </Button>
        )}
      </div>
    </header>
  );
}
