"use client";

import React from "react";
import { useAuth } from "@/contexts/AuthContext";
import { GCPCard, GCPCardGrid } from "@/components/ui/gcp-card";
import { GCPTabs, GCPTabPanel } from "@/components/ui/gcp-tabs";
import {
  ArrowRight,
  Settings,
  Activity,
  Users,
  Database,
  Cpu,
  HardDrive,
  Zap,
  Cloud,
  Play,
  AlertCircle,
  CheckCircle,
  Clock,
  MoreHorizontal,
} from "lucide-react";

export default function Dashboard() {
  const { user } = useAuth();

  // Dashboard Tab Content
  const DashboardContent = () => (
    <div className="max-w-[1440px] mx-auto">
      {/* Welcome Section */}
      <div className="mb-6 mt-4">
        <h1 className="text-2xl font-normal text-[var(--text-primary)]">
          Welcome
          {user
            ? `, ${user.displayName || user.email}`
            : " to NeuraScale Console"}
        </h1>
      </div>

      {/* Project Info and Quick Stats Grid */}
      <GCPCardGrid columns={3} className="mb-4">
        {/* Project Info Card */}
        <GCPCard
          title="Project info"
          icon="Project"
          onOptionsClick={() => console.log("Project options")}
        >
          <div className="space-y-3">
            <div className="flex justify-between items-center py-3 border-b border-[var(--border-light)]">
              <span className="text-sm text-[var(--text-tertiary)]">
                Project name
              </span>
              <span className="text-sm text-[var(--text-primary)]">
                neurascale-console
              </span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-[var(--border-light)]">
              <span className="text-sm text-[var(--text-tertiary)]">
                Project ID
              </span>
              <span className="text-sm text-[var(--text-primary)]">
                neurascale-console
              </span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-[var(--border-light)]">
              <span className="text-sm text-[var(--text-tertiary)]">
                Project number
              </span>
              <span className="text-sm text-[var(--text-primary)]">
                742047715565
              </span>
            </div>
            <button className="w-full mt-4 gcp-button-primary">
              ADD PEOPLE TO THIS PROJECT
            </button>
            <a
              href="#"
              className="flex items-center gap-2 mt-2 text-sm text-[var(--primary)] hover:underline"
            >
              <Settings className="w-4 h-4" />
              Go to project settings
            </a>
          </div>
        </GCPCard>

        {/* Resources Card */}
        <GCPCard
          title="Resources"
          icon="Compute-Engine"
          onOptionsClick={() => console.log("Resources options")}
        >
          <div className="space-y-2">
            <a
              href="#"
              className="flex items-center gap-3 p-2 rounded hover:bg-[var(--card-hover)] transition-colors"
            >
              <img src="/svg/AI-Platform.svg" alt="" className="w-5 h-5" />
              <div className="flex-1">
                <div className="text-sm font-medium text-[var(--text-primary)]">
                  Neural Management
                </div>
                <div className="text-xs text-[var(--text-tertiary)]">
                  AI-powered neural systems
                </div>
              </div>
            </a>
            <a
              href="#"
              className="flex items-center gap-3 p-2 rounded hover:bg-[var(--card-hover)] transition-colors"
            >
              <img
                src="/svg/Healthcare-NLP-API.svg"
                alt=""
                className="w-5 h-5"
              />
              <div className="flex-1">
                <div className="text-sm font-medium text-[var(--text-primary)]">
                  NeuroProsthetics
                </div>
                <div className="text-xs text-[var(--text-tertiary)]">
                  Advanced prosthetic control
                </div>
              </div>
            </a>
            <a
              href="#"
              className="flex items-center gap-3 p-2 rounded hover:bg-[var(--card-hover)] transition-colors"
            >
              <img src="/svg/Iot-Core.svg" alt="" className="w-5 h-5" />
              <div className="flex-1">
                <div className="text-sm font-medium text-[var(--text-primary)]">
                  BCI
                </div>
                <div className="text-xs text-[var(--text-tertiary)]">
                  Brain-Computer Interface
                </div>
              </div>
            </a>
            <a
              href="#"
              className="flex items-center gap-3 p-2 rounded hover:bg-[var(--card-hover)] transition-colors"
            >
              <img src="/svg/Game-Servers.svg" alt="" className="w-5 h-5" />
              <div className="flex-1">
                <div className="text-sm font-medium text-[var(--text-primary)]">
                  Full-Dive VR
                </div>
                <div className="text-xs text-[var(--text-tertiary)]">
                  Immersive virtual reality
                </div>
              </div>
            </a>
            <a
              href="#"
              className="flex items-center gap-3 p-2 rounded hover:bg-[var(--card-hover)] transition-colors"
            >
              <img src="/svg/Vertex-AI.svg" alt="" className="w-5 h-5" />
              <div className="flex-1">
                <div className="text-sm font-medium text-[var(--text-primary)]">
                  Augmented XR
                </div>
                <div className="text-xs text-[var(--text-tertiary)]">
                  Extended reality platform
                </div>
              </div>
            </a>
          </div>
        </GCPCard>

        {/* Getting Started Card */}
        <GCPCard
          title="Getting Started"
          icon="Launcher"
          onOptionsClick={() => console.log("Getting started options")}
        >
          <div className="space-y-2">
            <a
              href="#"
              className="flex items-center gap-3 p-2 rounded hover:bg-[var(--card-hover)] transition-colors"
            >
              <Play className="w-5 h-5 text-[var(--text-tertiary)]" />
              <span className="text-sm text-[var(--text-primary)]">
                Deploy your first neural model
              </span>
            </a>
            <a
              href="#"
              className="flex items-center gap-3 p-2 rounded hover:bg-[var(--card-hover)] transition-colors"
            >
              <Database className="w-5 h-5 text-[var(--text-tertiary)]" />
              <span className="text-sm text-[var(--text-primary)]">
                Create a neural database
              </span>
            </a>
            <a
              href="#"
              className="flex items-center gap-3 p-2 rounded hover:bg-[var(--card-hover)] transition-colors"
            >
              <Cpu className="w-5 h-5 text-[var(--text-tertiary)]" />
              <span className="text-sm text-[var(--text-primary)]">
                Configure BCI parameters
              </span>
            </a>
            <a
              href="#"
              className="flex items-center gap-3 p-2 rounded hover:bg-[var(--card-hover)] transition-colors"
            >
              <Zap className="w-5 h-5 text-[var(--text-tertiary)]" />
              <span className="text-sm text-[var(--text-primary)]">
                Set up neural monitoring
              </span>
            </a>
            <a
              href="#"
              className="flex items-center gap-3 p-2 rounded hover:bg-[var(--card-hover)] transition-colors"
            >
              <Cloud className="w-5 h-5 text-[var(--text-tertiary)]" />
              <span className="text-sm text-[var(--text-primary)]">
                Install NeuraScale SDK
              </span>
            </a>
            <div className="mt-4 pt-4 border-t border-[var(--border-light)]">
              <a
                href="#"
                className="flex items-center gap-2 text-sm text-[var(--primary)] hover:underline"
              >
                <ArrowRight className="w-4 h-4" />
                Explore all tutorials
              </a>
            </div>
          </div>
        </GCPCard>
      </GCPCardGrid>

      {/* Second Row - Monitoring Cards */}
      <GCPCardGrid columns={2} className="mb-4">
        {/* APIs Card */}
        <GCPCard
          title="APIs"
          icon="API"
          onOptionsClick={() => console.log("APIs options")}
        >
          <div className="space-y-4">
            <div>
              <div className="text-sm text-[var(--text-tertiary)] mb-2">
                Requests (requests/sec)
              </div>
              <div className="h-[200px] bg-[var(--background)] rounded flex items-center justify-center text-[var(--text-tertiary)]">
                {/* Chart placeholder */}
                <span className="text-xs">API usage chart</span>
              </div>
            </div>
            <div className="flex items-center justify-between pt-4 border-t border-[var(--border-light)]">
              <div className="flex items-center gap-2">
                <span className="text-sm text-[var(--text-tertiary)]">
                  Requests:
                </span>
                <span className="text-sm font-medium text-[var(--text-primary)]">
                  0.002/s
                </span>
              </div>
              <a
                href="#"
                className="flex items-center gap-2 text-sm text-[var(--primary)] hover:underline"
              >
                <ArrowRight className="w-4 h-4" />
                Go to APIs overview
              </a>
            </div>
          </div>
        </GCPCard>

        {/* Platform Status Card */}
        <GCPCard
          title="NeuraScale Platform Status"
          icon="Security-Command-Center"
          onOptionsClick={() => console.log("Status options")}
        >
          <div className="space-y-4">
            <div className="flex items-center gap-3 p-4 bg-[var(--background)] rounded">
              <CheckCircle className="w-5 h-5 text-[var(--success)]" />
              <span className="text-sm font-medium text-[var(--text-primary)]">
                All services normal
              </span>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between py-2">
                <span className="text-sm text-[var(--text-secondary)]">
                  Neural Management
                </span>
                <span className="flex items-center gap-2 text-sm">
                  <span className="w-2 h-2 bg-[var(--success)] rounded-full"></span>
                  <span className="text-[var(--success)]">Operational</span>
                </span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-sm text-[var(--text-secondary)]">
                  BCI Services
                </span>
                <span className="flex items-center gap-2 text-sm">
                  <span className="w-2 h-2 bg-[var(--success)] rounded-full"></span>
                  <span className="text-[var(--success)]">Operational</span>
                </span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-sm text-[var(--text-secondary)]">
                  VR/XR Platform
                </span>
                <span className="flex items-center gap-2 text-sm">
                  <span className="w-2 h-2 bg-[var(--success)] rounded-full"></span>
                  <span className="text-[var(--success)]">Operational</span>
                </span>
              </div>
            </div>

            <div className="pt-4 border-t border-[var(--border-light)]">
              <a
                href="#"
                className="flex items-center gap-2 text-sm text-[var(--primary)] hover:underline"
              >
                <ArrowRight className="w-4 h-4" />
                Go to Cloud status dashboard
              </a>
            </div>
          </div>
        </GCPCard>
      </GCPCardGrid>

      {/* Third Row - Activity and News */}
      <GCPCardGrid columns={2}>
        {/* Recent Activity */}
        <GCPCard
          title="Recent Activity"
          icon="Activity"
          onOptionsClick={() => console.log("Activity options")}
        >
          <div className="space-y-3">
            <div className="flex items-start gap-3 p-3 rounded hover:bg-[var(--card-hover)] transition-colors">
              <div className="w-8 h-8 rounded-full bg-[var(--success)] bg-opacity-10 flex items-center justify-center flex-shrink-0">
                <div className="w-2 h-2 bg-[var(--success)] rounded-full"></div>
              </div>
              <div className="flex-1">
                <p className="text-sm text-[var(--text-primary)]">
                  Neural instance "cortex-01" deployed successfully
                </p>
                <p className="text-xs text-[var(--text-tertiary)] mt-1">
                  2 minutes ago
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-3 rounded hover:bg-[var(--card-hover)] transition-colors">
              <div className="w-8 h-8 rounded-full bg-[var(--info)] bg-opacity-10 flex items-center justify-center flex-shrink-0">
                <div className="w-2 h-2 bg-[var(--info)] rounded-full"></div>
              </div>
              <div className="flex-1">
                <p className="text-sm text-[var(--text-primary)]">
                  BCI configuration updated
                </p>
                <p className="text-xs text-[var(--text-tertiary)] mt-1">
                  15 minutes ago
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-3 rounded hover:bg-[var(--card-hover)] transition-colors">
              <div className="w-8 h-8 rounded-full bg-[var(--warning)] bg-opacity-10 flex items-center justify-center flex-shrink-0">
                <div className="w-2 h-2 bg-[var(--warning)] rounded-full"></div>
              </div>
              <div className="flex-1">
                <p className="text-sm text-[var(--text-primary)]">
                  Neural database backup completed
                </p>
                <p className="text-xs text-[var(--text-tertiary)] mt-1">
                  1 hour ago
                </p>
              </div>
            </div>
          </div>
        </GCPCard>

        {/* News & Updates */}
        <GCPCard
          title="News & Updates"
          icon="Release-Notes"
          onOptionsClick={() => console.log("News options")}
        >
          <div className="space-y-3">
            <a
              href="#"
              className="block p-3 rounded hover:bg-[var(--card-hover)] transition-colors"
            >
              <h4 className="text-sm font-medium text-[var(--text-primary)] mb-1">
                NeuraScale 2.0 Released
              </h4>
              <p className="text-xs text-[var(--text-tertiary)]">
                Major update includes improved BCI latency and new VR
                capabilities
              </p>
              <span className="text-xs text-[var(--text-tertiary)] mt-1 block">
                2 days ago
              </span>
            </a>
            <a
              href="#"
              className="block p-3 rounded hover:bg-[var(--card-hover)] transition-colors"
            >
              <h4 className="text-sm font-medium text-[var(--text-primary)] mb-1">
                New Neural Training Models Available
              </h4>
              <p className="text-xs text-[var(--text-tertiary)]">
                Pre-trained models for faster deployment of neural interfaces
              </p>
              <span className="text-xs text-[var(--text-tertiary)] mt-1 block">
                1 week ago
              </span>
            </a>
            <div className="pt-4 border-t border-[var(--border-light)]">
              <a
                href="#"
                className="flex items-center gap-2 text-sm text-[var(--primary)] hover:underline"
              >
                <ArrowRight className="w-4 h-4" />
                Read all news
              </a>
            </div>
          </div>
        </GCPCard>
      </GCPCardGrid>
    </div>
  );

  // Activity Tab Content
  const ActivityContent = () => (
    <div className="max-w-[1440px] mx-auto">
      <GCPCard title="System Activity Log">
        <div className="text-center py-12 text-[var(--text-tertiary)]">
          Activity log will be displayed here
        </div>
      </GCPCard>
    </div>
  );

  // Recommendations Tab Content
  const RecommendationsContent = () => (
    <div className="max-w-[1440px] mx-auto">
      <GCPCard title="Personalized Recommendations">
        <div className="text-center py-12 text-[var(--text-tertiary)]">
          Recommendations based on your usage will appear here
        </div>
      </GCPCard>
    </div>
  );

  const tabs = [
    { id: "dashboard", label: "Dashboard", content: <DashboardContent /> },
    { id: "activity", label: "Activity", content: <ActivityContent /> },
    {
      id: "recommendations",
      label: "Recommendations",
      content: <RecommendationsContent />,
    },
  ];

  return (
    <div className="min-h-screen bg-[var(--background)]">
      {/* Position tabs to start from the edge, accounting for sidebar */}
      <div className="-ml-8">
        <GCPTabs tabs={tabs} defaultTab="dashboard" />
      </div>
    </div>
  );
}
