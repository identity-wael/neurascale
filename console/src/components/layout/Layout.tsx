"use client";

import React, { useState } from "react";
import Header from "./Header";
import Sidebar from "./Sidebar";

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(true);

  const handleMenuClick = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <div className="h-screen flex flex-col bg-[var(--background)]">
      {/* Header */}
      <Header onMenuClick={handleMenuClick} />

      {/* Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          isCollapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        {/* Main Content */}
        <main
          className="flex-1 overflow-x-hidden overflow-y-auto bg-[var(--background)] transition-all duration-200"
          style={{ marginLeft: sidebarCollapsed ? "64px" : "280px" }}
        >
          <div className="h-full">{children}</div>
        </main>
      </div>
    </div>
  );
}
