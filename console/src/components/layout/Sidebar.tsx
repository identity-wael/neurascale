"use client";

import React from "react";
import {
  Home,
  Database,
  Server,
  Cpu,
  Network,
  Shield,
  BarChart3,
  Settings,
  ChevronRight,
  Bot,
  Brain,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

interface NavItem {
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  href: string;
  children?: NavItem[];
}

const navItems: NavItem[] = [
  {
    name: "Home",
    icon: Home,
    href: "/",
  },
  {
    name: "Neural Services",
    icon: Brain,
    href: "/neural",
    children: [
      { name: "Neural Management", icon: Settings, href: "/neural/management" },
      { name: "Neuroprosthetics", icon: Cpu, href: "/neural/prosthetics" },
      { name: "Brain-Robot Interface", icon: Bot, href: "/neural/brain-robot" },
      { name: "Full-Dive VR", icon: Zap, href: "/neural/full-dive" },
    ],
  },
  {
    name: "Cloud Infrastructure",
    icon: Server,
    href: "/infrastructure",
    children: [
      { name: "Compute Engine", icon: Cpu, href: "/infrastructure/compute" },
      {
        name: "Cloud Storage",
        icon: Database,
        href: "/infrastructure/storage",
      },
      {
        name: "Kubernetes Engine",
        icon: Server,
        href: "/infrastructure/kubernetes",
      },
      { name: "Cloud Functions", icon: Zap, href: "/infrastructure/functions" },
    ],
  },
  {
    name: "AI & ML",
    icon: Bot,
    href: "/ai",
    children: [
      { name: "AutoML", icon: Bot, href: "/ai/automl" },
      { name: "AI Platform", icon: Brain, href: "/ai/platform" },
      { name: "GPU/TPU", icon: Cpu, href: "/ai/accelerators" },
      { name: "Model Registry", icon: Database, href: "/ai/models" },
    ],
  },
  {
    name: "Databases",
    icon: Database,
    href: "/databases",
    children: [
      { name: "Cloud SQL", icon: Database, href: "/databases/sql" },
      { name: "Firestore", icon: Database, href: "/databases/firestore" },
      { name: "BigQuery", icon: BarChart3, href: "/databases/bigquery" },
      { name: "Memorystore", icon: Database, href: "/databases/memorystore" },
    ],
  },
  {
    name: "Networking",
    icon: Network,
    href: "/networking",
    children: [
      { name: "VPC", icon: Network, href: "/networking/vpc" },
      {
        name: "Load Balancing",
        icon: Network,
        href: "/networking/load-balancer",
      },
      { name: "Cloud CDN", icon: Network, href: "/networking/cdn" },
      { name: "Network Slicing", icon: Network, href: "/networking/slicing" },
    ],
  },
  {
    name: "Security",
    icon: Shield,
    href: "/security",
    children: [
      { name: "IAM", icon: Shield, href: "/security/iam" },
      { name: "Security Center", icon: Shield, href: "/security/center" },
      { name: "Key Management", icon: Shield, href: "/security/keys" },
      { name: "Cloud Armor", icon: Shield, href: "/security/armor" },
    ],
  },
  {
    name: "Analytics",
    icon: BarChart3,
    href: "/analytics",
    children: [
      { name: "BigQuery", icon: BarChart3, href: "/analytics/bigquery" },
      { name: "Data Studio", icon: BarChart3, href: "/analytics/studio" },
      {
        name: "Cloud Monitoring",
        icon: BarChart3,
        href: "/analytics/monitoring",
      },
      { name: "Cloud Logging", icon: BarChart3, href: "/analytics/logging" },
    ],
  },
];

interface NavItemComponentProps {
  item: NavItem;
  isExpanded: boolean;
  onToggle: () => void;
  isCollapsed: boolean;
}

function NavItemComponent({
  item,
  isExpanded,
  onToggle,
  isCollapsed,
}: NavItemComponentProps) {
  const Icon = item.icon;
  const hasChildren = item.children && item.children.length > 0;

  return (
    <div>
      <button
        onClick={hasChildren ? onToggle : undefined}
        className={cn(
          "w-full flex items-center justify-between text-sm text-gray-700 hover:bg-gradient-to-r hover:from-gray-50 hover:to-gray-100 rounded-xl transition-all duration-200 group",
          hasChildren && "cursor-pointer",
          isCollapsed ? "px-2 py-3" : "px-4 py-3",
        )}
        title={isCollapsed ? item.name : undefined}
      >
        <div
          className={cn(
            "flex items-center",
            isCollapsed ? "justify-center" : "space-x-3",
          )}
        >
          <Icon className="h-5 w-5 text-gray-500 group-hover:text-blue-600 transition-colors flex-shrink-0" />
          {!isCollapsed && (
            <span className="font-medium group-hover:text-gray-900 transition-colors">
              {item.name}
            </span>
          )}
        </div>
        {hasChildren && !isCollapsed && (
          <ChevronRight
            className={cn(
              "h-4 w-4 transition-transform",
              isExpanded && "rotate-90",
            )}
          />
        )}
      </button>

      {hasChildren && isExpanded && !isCollapsed && (
        <div className="ml-6 mt-1 space-y-1">
          {item.children!.map((child) => {
            const ChildIcon = child.icon;
            return (
              <button
                key={child.href}
                className="w-full flex items-center space-x-3 px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg transition-all duration-200 group"
              >
                <ChildIcon className="h-4 w-4 text-gray-400 group-hover:text-blue-500 transition-colors" />
                <span className="group-hover:text-gray-800 transition-colors">
                  {child.name}
                </span>
              </button>
            );
          })}
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
  const [expandedItems, setExpandedItems] = React.useState<string[]>([]);

  const toggleItem = (itemName: string) => {
    setExpandedItems((prev) =>
      prev.includes(itemName)
        ? prev.filter((name) => name !== itemName)
        : [...prev, itemName],
    );
  };

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-16 h-[calc(100vh-64px)] bg-white/90 backdrop-blur-sm border-r border-gray-100 transform transition-all duration-300 ease-in-out z-50 overflow-y-auto shadow-lg",
          isOpen ? "translate-x-0" : "-translate-x-full",
          "lg:translate-x-0 lg:static lg:transform-none lg:shadow-none",
          isCollapsed ? "w-16" : "w-64",
        )}
      >
        <nav className={cn("space-y-2", isCollapsed ? "p-2" : "p-6")}>
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
