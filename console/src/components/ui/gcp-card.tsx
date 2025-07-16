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
}

export function GCPCard({
  title,
  icon,
  children,
  className,
  actions,
  onOptionsClick,
}: GCPCardProps) {
  return (
    <div
      className={cn(
        "bg-[var(--card-bg)] border border-[var(--border)] rounded-lg p-6 transition-all duration-150",
        "hover:bg-[var(--card-hover)]",
        className,
      )}
    >
      {(title || icon || actions || onOptionsClick) && (
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            {icon && (
              <div className="flex items-center justify-center">
                {typeof icon === "string" ? (
                  <img
                    src={`/svg/${icon}.svg`}
                    alt=""
                    className="w-6 h-6 opacity-60"
                  />
                ) : (
                  icon
                )}
              </div>
            )}
            {title && (
              <h2 className="text-base font-medium leading-6 text-[var(--text-primary)] tracking-[0.1px] font-['Google_Sans',_'Roboto',_Arial,_sans-serif]">
                {title}
              </h2>
            )}
          </div>
          <div className="flex items-center gap-2">
            {actions}
            {onOptionsClick && (
              <button
                onClick={onOptionsClick}
                className="w-6 h-6 flex items-center justify-center rounded-full transition-colors duration-150 hover:bg-[rgba(60,64,67,0.08)] text-[var(--text-tertiary)]"
                aria-label="More options"
              >
                <MoreVertical className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>
      )}
      <div className="text-[var(--text-secondary)]">{children}</div>
    </div>
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
