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
  sidebarWidth?: number;
}

export function GCPTabs({
  tabs,
  defaultTab,
  className,
  onTabChange,
  sidebarWidth = 0,
}: GCPTabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id);

  const handleTabClick = (tabId: string) => {
    setActiveTab(tabId);
    onTabChange?.(tabId);
  };

  const activeTabContent = tabs.find((tab) => tab.id === activeTab)?.content;

  return (
    <div className={cn("w-full", className)}>
      {/* Tab Navigation */}
      <div className="app-card border-b">
        <div
          className="flex items-center h-12 pr-6 gap-8"
          style={{ paddingLeft: `${sidebarWidth + 32}px` }}
        >
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabClick(tab.id)}
              className={cn(
                "relative h-full flex items-center text-sm font-medium uppercase tracking-[0.25px] transition-colors duration-150",
                "font-['Google_Sans',_'Roboto',_Arial,_sans-serif]",
                activeTab === tab.id
                  ? "app-text"
                  : "app-text-tertiary hover:app-text-secondary",
              )}
              role="tab"
              aria-selected={activeTab === tab.id}
            >
              {tab.label}
              {activeTab === tab.id && (
                <div className="absolute bottom-0 left-0 right-0 h-[3px] bg-gray-900" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div
        className="pt-20 pb-8 app-bg"
        style={{
          paddingLeft: `${sidebarWidth + 32}px`,
          paddingRight: `${sidebarWidth + 32}px`,
        }}
      >
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
