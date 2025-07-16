"use client";

import React from "react";
import { MoreVertical } from "lucide-react";
import { cn } from "@/lib/utils";

interface GCPCardProps {
  title?: string;
  icon?: React.ReactNode | string;
  children: React.ReactNode;
  className?: string;
  actions?: React.ReactNode;
  onOptionsClick?: () => void;
  noPadding?: boolean;
}

export function GCPCard({
  title,
  icon,
  children,
  className,
  actions,
  onOptionsClick,
  noPadding = false,
}: GCPCardProps) {
  return (
    <div
      className={cn(
        "app-card rounded-lg transition-all duration-150",
        "hover:opacity-95",
        className,
      )}
    >
      {(title || icon || actions || onOptionsClick) && (
        <div className="px-6 py-4 border-b app-card-border">
          <div className="flex items-center justify-between mx-8 md:mx-12 my-4">
            <div className="flex items-center gap-3">
              {icon && (
                <div className="flex items-center justify-center">
                  {typeof icon === "string" ? (
                    <img
                      src={`/svg/${icon}.svg`}
                      alt=""
                      className="w-5 h-5 md:w-6 md:h-6 opacity-60"
                    />
                  ) : (
                    icon
                  )}
                </div>
              )}
              {title && (
                <h2 className="text-sm md:text-base font-medium leading-6 app-text tracking-[0.1px] font-['Google_Sans',_'Roboto',_Arial,_sans-serif]">
                  {title}
                </h2>
              )}
            </div>
            <div className="flex items-center gap-2">
              {actions}
              {onOptionsClick && (
                <button
                  onClick={onOptionsClick}
                  className="w-6 h-6 flex items-center justify-center rounded-full transition-colors duration-150 hover:bg-[rgba(60,64,67,0.08)] app-text-tertiary"
                  aria-label="More options"
                >
                  <MoreVertical className="w-4 h-4 md:w-5 md:h-5" />
                </button>
              )}
            </div>
          </div>
        </div>
      )}
      <div className={cn("app-text-secondary", !noPadding && "px-6 py-4")}>
        <div className="mx-8 md:mx-12 my-4">{children}</div>
      </div>
    </div>
  );
}

// Card content wrapper for consistent spacing
interface GCPCardContentProps {
  children: React.ReactNode;
  className?: string;
  spacing?: "tight" | "normal" | "loose";
}

export function GCPCardContent({
  children,
  className,
  spacing = "normal",
}: GCPCardContentProps) {
  const spacingClasses = {
    tight: "space-y-2",
    normal: "space-y-3",
    loose: "space-y-4",
  };

  return (
    <div className={cn(spacingClasses[spacing], className)}>{children}</div>
  );
}

// Card item for consistent list items
interface GCPCardItemProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  href?: string;
  icon?: React.ReactNode | string;
}

export function GCPCardItem({
  children,
  className,
  onClick,
  href,
  icon,
}: GCPCardItemProps) {
  const Component = href ? "a" : onClick ? "button" : "div";

  return (
    <Component
      href={href}
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 px-0 py-3",
        "rounded-md transition-colors duration-150",
        (href || onClick) &&
          "hover:bg-gray-50 dark:hover:bg-gray-600 cursor-pointer",
        onClick && "w-full text-left",
        className,
      )}
    >
      {icon && (
        <div className="flex-shrink-0">
          {typeof icon === "string" ? (
            <img
              src={`/svg/${icon}.svg`}
              alt=""
              className="w-5 h-5 opacity-70"
            />
          ) : (
            icon
          )}
        </div>
      )}
      <div className="flex-1 min-w-0">{children}</div>
    </Component>
  );
}

interface GCPCardGridProps {
  children: React.ReactNode;
  className?: string;
  columns?: 1 | 2 | 3;
}

export function GCPCardGrid({
  children,
  className,
  columns = 3,
}: GCPCardGridProps) {
  const gridCols = {
    1: "grid-cols-1",
    2: "grid-cols-1 lg:grid-cols-2",
    3: "grid-cols-1 md:grid-cols-2 xl:grid-cols-3",
  };

  return (
    <div className={cn("grid gap-4", gridCols[columns], className)}>
      {children}
    </div>
  );
}
