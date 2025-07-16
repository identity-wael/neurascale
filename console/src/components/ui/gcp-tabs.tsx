"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";

interface Tab {
  id: string;
  label: string;
  content: React.ReactNode;
}

interface GCPTabsProps {
  tabs: Tab[];
  defaultTab?: string;
  className?: string;
  onTabChange?: (tabId: string) => void;
}

export function GCPTabs({
  tabs,
  defaultTab,
  className,
  onTabChange,
}: GCPTabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id);

  const handleTabClick = (tabId: string) => {
    setActiveTab(tabId);
    onTabChange?.(tabId);
  };

  const activeTabContent = tabs.find((tab) => tab.id === activeTab)?.content;

  return (
    <div className={cn("w-full", className)}>
      {/* Tab Navigation - Extended to account for sidebar */}
      <div className="bg-[var(--card-bg)] border-b border-[var(--border)] -ml-[64px] mr-0">
        <div className="flex items-center h-12 pl-[88px] pr-6 gap-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabClick(tab.id)}
              className={cn(
                "relative h-full flex items-center text-sm font-medium uppercase tracking-[0.25px] transition-colors duration-150",
                "font-['Google_Sans',_'Roboto',_Arial,_sans-serif]",
                activeTab === tab.id
                  ? "text-[var(--primary)]"
                  : "text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]",
              )}
              role="tab"
              aria-selected={activeTab === tab.id}
            >
              {tab.label}
              {activeTab === tab.id && (
                <div className="absolute bottom-0 left-0 right-0 h-[3px] bg-[var(--primary)]" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="px-8 pt-20 pb-8 bg-[var(--background)]">
        {activeTabContent}
      </div>
    </div>
  );
}

interface GCPTabPanelProps {
  children: React.ReactNode;
  className?: string;
}

export function GCPTabPanel({ children, className }: GCPTabPanelProps) {
  return <div className={cn("w-full", className)}>{children}</div>;
}
