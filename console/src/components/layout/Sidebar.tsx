"use client";

import React, { useState } from "react";
import { ChevronRight, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface NavItem {
  name: string;
  icon?: string; // SVG file name
  href: string;
  children?: NavItem[];
  isPinned?: boolean;
  badge?: string;
}

// Navigation items - Home + 6 categories requested
const navItems: NavItem[] = [
  {
    name: "Home",
    icon: "Home",
    href: "/",
  },
  {
    name: "Neural ID",
    icon: "Identity-Platform",
    href: "/neural-id",
  },
  {
    name: "Neura Management",
    icon: "AI-Platform",
    href: "/neura-management",
  },
  {
    name: "NeuroProsthetics",
    icon: "Healthcare-NLP-API",
    href: "/neuroprosthetics",
  },
  {
    name: "BCI",
    icon: "Iot-Core",
    href: "/bci",
  },
  {
    name: "Full-Dive VR",
    icon: "Game-Servers",
    href: "/full-dive-vr",
  },
  {
    name: "Augmented XR",
    icon: "Vertex-AI",
    href: "/augmented-xr",
  },
];

// Google Cloud Icon Component
const GCPIcon: React.FC<{
  icon?: string;
  className?: string;
  style?: React.CSSProperties;
}> = ({ icon, className, style }) => {
  if (!icon) return null;

  return (
    <img
      src={`/svg/${icon}.svg`}
      alt=""
      className={cn("w-6 h-6", className)}
      style={style}
    />
  );
};

interface SidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

interface NavItemComponentProps {
  item: NavItem;
  isExpanded: boolean;
  onToggle: () => void;
  isCollapsed: boolean;
  level?: number;
}

function NavItemComponent({
  item,
  isExpanded,
  onToggle,
  isCollapsed,
  level = 0,
}: NavItemComponentProps) {
  const hasChildren = item.children && item.children.length > 0;
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div>
      <button
        onClick={hasChildren ? onToggle : undefined}
        className="w-full flex items-center justify-between text-sm rounded-sm transition-all group relative"
        style={{
          color: "#E8EAED",
          padding: level === 0 ? "0" : "0 8px 0 0",
          paddingRight: !isCollapsed ? "12px" : "0",
          minHeight: "32px",
          backgroundColor: isHovered
            ? "rgba(232, 234, 237, 0.08)"
            : "transparent",
        }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        title={isCollapsed ? item.name : undefined}
      >
        <div className="flex items-center">
          <div
            className="flex items-center justify-center flex-shrink-0"
            style={{
              width: "48px",
              height: "32px",
              marginLeft: "4px",
            }}
          >
            <GCPIcon
              icon={item.icon}
              className="w-6 h-6"
              style={{ opacity: 0.7 }}
            />
          </div>
          {!isCollapsed && (
            <span
              className="text-[13px] font-normal"
              style={{ letterSpacing: "0.1px", marginLeft: "4px" }}
            >
              {item.name}
            </span>
          )}
        </div>
        {!isCollapsed && hasChildren && (
          <ChevronRight
            className={cn(
              "h-4 w-4 transition-transform",
              isExpanded && "rotate-90",
            )}
            style={{ color: "#9AA0A6" }}
          />
        )}
      </button>

      {hasChildren && isExpanded && !isCollapsed && (
        <div>
          {item.children!.map((child) => (
            <button
              key={child.href}
              className="w-full flex items-center gap-3 text-sm rounded-sm transition-all"
              style={{
                color: "#E8EAED",
                padding: "0 12px 0 0",
                minHeight: "28px",
                opacity: 0.8,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor =
                  "rgba(232, 234, 237, 0.08)";
                e.currentTarget.style.opacity = "1";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = "transparent";
                e.currentTarget.style.opacity = "0.8";
              }}
            >
              <div
                className="flex items-center justify-center flex-shrink-0"
                style={{
                  width: "48px",
                  height: "28px",
                  marginLeft: "4px",
                }}
              >
                {child.icon && (
                  <GCPIcon
                    icon={child.icon}
                    className="w-4 h-4"
                    style={{ opacity: 0.6 }}
                  />
                )}
              </div>
              <span
                className="text-[13px] font-normal"
                style={{ marginLeft: "4px" }}
              >
                {child.name}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Sidebar({
  isCollapsed,
  onToggleCollapse,
}: SidebarProps) {
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  const toggleItem = (itemName: string) => {
    setExpandedItems((prev) =>
      prev.includes(itemName)
        ? prev.filter((name) => name !== itemName)
        : [...prev, itemName],
    );
  };

  return (
    <>
      {/* Overlay when sidebar is expanded */}
      {!isCollapsed && (
        <div
          className="fixed inset-0 bg-black/50 z-40"
          onClick={onToggleCollapse}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "overflow-y-auto transition-all duration-200 flex-shrink-0",
          "fixed left-0 z-50 h-screen",
          isCollapsed ? "top-[48px] h-[calc(100vh-48px)]" : "top-0",
          "translate-x-0",
          isCollapsed ? "w-[56px]" : "w-[280px]",
        )}
        style={{
          backgroundColor: "#1F1F1F",
          borderRight: "1px solid rgba(255, 255, 255, 0.08)",
        }}
      >
        {/* Header with X button and logo when expanded */}
        {!isCollapsed && (
          <div
            className="flex items-center h-[48px]"
            style={{
              borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
              padding: "0 8px",
              backgroundColor: "#303134",
            }}
          >
            <button
              onClick={onToggleCollapse}
              className="flex items-center justify-center w-10 h-10 rounded transition-colors"
              style={{
                color: "#E8EAED",
                backgroundColor: "transparent",
                marginLeft: "4px",
                borderRadius: "4px",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor =
                  "rgba(255, 255, 255, 0.08)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = "transparent";
              }}
              title="Close menu"
            >
              <X
                className="h-5 w-5"
                style={{ width: "20px", height: "20px" }}
              />
            </button>

            <div className="flex items-center ml-2">
              <div
                className="flex items-center"
                style={{ marginLeft: "8px", marginRight: "16px" }}
              >
                <span className="font-medium text-[18px]">
                  <span style={{ color: "var(--foreground)" }}>NEURA</span>
                  <span className="text-[#4185f4]">SCALE</span>
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="py-2" style={{ backgroundColor: "#1F1F1F" }}>
          {navItems.map((item) => (
            <NavItemComponent
              key={item.name}
              item={item}
              isExpanded={expandedItems.includes(item.name)}
              onToggle={() => toggleItem(item.name)}
              isCollapsed={isCollapsed}
            />
          ))}
        </nav>
      </aside>
    </>
  );
}
