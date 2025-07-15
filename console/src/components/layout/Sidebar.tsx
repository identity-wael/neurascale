"use client";

import React, { useState } from "react";
import { ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface NavItem {
  name: string;
  icon?: string; // SVG file name
  href: string;
  children?: NavItem[];
  isPinned?: boolean;
  badge?: string;
}

const mainNavItems: NavItem[] = [
  {
    name: "Home",
    icon: "Home",
    href: "/",
  },
  {
    name: "Neural Services",
    icon: "AI-Platform-Unified",
    href: "/neural",
    children: [
      {
        name: "Neural Management",
        icon: "AI-Platform",
        href: "/neural/management",
      },
      {
        name: "Neuroprosthetics",
        icon: "Healthcare-NLP-API",
        href: "/neural/prosthetics",
      },
      {
        name: "Brain-Robot Interface",
        icon: "Iot-Core",
        href: "/neural/brain-robot",
      },
      {
        name: "Full-Dive VR",
        icon: "Cloud-Vision-API",
        href: "/neural/full-dive",
      },
    ],
  },
  {
    name: "Cloud Infrastructure",
    icon: "Compute-Engine",
    href: "/infrastructure",
    children: [
      {
        name: "Compute Engine",
        icon: "Compute-Engine",
        href: "/infrastructure/compute",
      },
      {
        name: "Cloud Storage",
        icon: "Cloud-Storage",
        href: "/infrastructure/storage",
      },
      {
        name: "Kubernetes Engine",
        icon: "Google-Kubernetes-Engine",
        href: "/infrastructure/kubernetes",
      },
      {
        name: "Cloud Functions",
        icon: "Cloud-Functions",
        href: "/infrastructure/functions",
      },
    ],
  },
  {
    name: "AI & ML",
    icon: "Vertex-AI",
    href: "/ai",
    children: [
      { name: "AutoML", icon: "AutoML", href: "/ai/automl" },
      { name: "AI Platform", icon: "AI-Platform", href: "/ai/platform" },
      { name: "GPU/TPU", icon: "Cloud-TPU", href: "/ai/accelerators" },
      { name: "Model Registry", icon: "Vertex-AI", href: "/ai/models" },
    ],
  },
  {
    name: "Databases",
    icon: "Cloud-Spanner",
    href: "/databases",
    children: [
      { name: "Cloud SQL", icon: "Cloud-SQL", href: "/databases/sql" },
      { name: "Firestore", icon: "Firestore", href: "/databases/firestore" },
      { name: "BigQuery", icon: "BigQuery", href: "/databases/bigquery" },
      {
        name: "Memorystore",
        icon: "Memorystore",
        href: "/databases/memorystore",
      },
    ],
  },
  {
    name: "Networking",
    icon: "Virtual-Private-Cloud",
    href: "/networking",
    children: [
      { name: "VPC", icon: "Virtual-Private-Cloud", href: "/networking/vpc" },
      {
        name: "Load Balancing",
        icon: "Cloud-Load-Balancing",
        href: "/networking/load-balancer",
      },
      { name: "Cloud CDN", icon: "Cloud-CDN", href: "/networking/cdn" },
      {
        name: "Network Slicing",
        icon: "Network-Topology",
        href: "/networking/slicing",
      },
    ],
  },
  {
    name: "Security",
    icon: "Security-Command-Center",
    href: "/security",
    children: [
      {
        name: "IAM",
        icon: "Identity-And-Access-Management",
        href: "/security/iam",
      },
      {
        name: "Security Center",
        icon: "Security-Command-Center",
        href: "/security/center",
      },
      {
        name: "Key Management",
        icon: "Key-Management-Service",
        href: "/security/keys",
      },
      { name: "Cloud Armor", icon: "Cloud-Armor", href: "/security/armor" },
    ],
  },
  {
    name: "Analytics",
    icon: "Cloud-Monitoring",
    href: "/analytics",
    children: [
      { name: "BigQuery", icon: "BigQuery", href: "/analytics/bigquery" },
      { name: "Data Studio", icon: "Data-Studio", href: "/analytics/studio" },
      {
        name: "Cloud Monitoring",
        icon: "Cloud-Monitoring",
        href: "/analytics/monitoring",
      },
      {
        name: "Cloud Logging",
        icon: "Cloud-Logging",
        href: "/analytics/logging",
      },
    ],
  },
];

// Google Cloud Icon Component
const GCPIcon: React.FC<{ icon?: string; className?: string }> = ({
  icon,
  className,
}) => {
  if (!icon) return null;

  return (
    <img src={`/svg/${icon}.svg`} alt="" className={cn("w-5 h-5", className)} />
  );
};

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
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

  return (
    <div>
      <button
        onClick={hasChildren ? onToggle : undefined}
        className={cn(
          "w-full flex items-center justify-between text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors group",
          level === 0 ? "px-3 py-1.5" : "px-3 py-1 ml-6",
        )}
        title={isCollapsed ? item.name : undefined}
      >
        <div className="flex items-center gap-3">
          <GCPIcon icon={item.icon} className="text-gray-600" />
          {!isCollapsed && <span>{item.name}</span>}
        </div>
        {!isCollapsed && (
          <div className="flex items-center gap-1">
            {item.badge && (
              <span className="px-2 py-0.5 text-xs font-medium text-white bg-blue-600 rounded">
                {item.badge}
              </span>
            )}
            {hasChildren && (
              <ChevronRight
                className={cn(
                  "h-4 w-4 text-gray-400 transition-transform",
                  isExpanded && "rotate-90",
                )}
              />
            )}
          </div>
        )}
      </button>

      {hasChildren && isExpanded && !isCollapsed && (
        <div className="mt-1">
          {item.children!.map((child) => (
            <button
              key={child.href}
              className="w-full flex items-center gap-3 px-3 py-1 ml-8 text-sm text-gray-600 hover:bg-gray-50 rounded-md transition-colors group"
            >
              <GCPIcon icon={child.icon} className="w-4 h-4 text-gray-500" />
              <span className="group-hover:text-gray-800 transition-colors">
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
  isOpen,
  onClose,
  isCollapsed = false,
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
      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "bg-white border-r border-gray-200 overflow-y-auto transition-all duration-200 flex-shrink-0",
          "fixed inset-y-0 left-0 z-40 h-full lg:relative lg:z-0",
          isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
          isCollapsed ? "w-12" : "w-64",
        )}
      >
        <nav className={cn("space-y-1", isCollapsed ? "p-1" : "p-3")}>
          {mainNavItems.map((item) => (
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
