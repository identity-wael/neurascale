"use client";

import React from "react";
import { useAuth } from "@/contexts/AuthContext";
import {
  GCPCard,
  GCPCardGrid,
  GCPCardContent,
  GCPCardItem,
} from "@/components/ui/gcp-card";
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
  const [sidebarWidth] = React.useState(64); // Collapsed sidebar width

  // Dashboard Tab Content
  const DashboardContent = () => (
    <div className="max-w-[1440px] mx-auto">
      {/* Welcome Section */}
      <div className="mb-6 mt-4">
        <h1 className="text-2xl font-normal app-text">
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
          <GCPCardContent>
            <div className="flex justify-between items-center py-3 border-b app-card-border">
              <span className="text-sm app-text-tertiary">Project name</span>
              <span className="text-sm app-text">neurascale-console</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b app-card-border">
              <span className="text-sm app-text-tertiary">Project ID</span>
              <span className="text-sm app-text">neurascale-console</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b app-card-border">
              <span className="text-sm app-text-tertiary">Project number</span>
              <span className="text-sm app-text">742047715565</span>
            </div>
            <button className="w-full mt-4 gcp-button-primary">
              ADD PEOPLE TO THIS PROJECT
            </button>
            <a
              href="#"
              className="flex items-center gap-2 mt-2 text-sm text-blue-700 hover:underline"
            >
              <Settings className="w-4 h-4" />
              Go to project settings
            </a>
          </GCPCardContent>
        </GCPCard>

        {/* Resources Card */}
        <GCPCard
          title="Resources"
          icon="Compute-Engine"
          onOptionsClick={() => console.log("Resources options")}
        >
          <GCPCardContent spacing="tight">
            <GCPCardItem href="#" icon="AI-Platform">
              <div className="text-sm font-medium app-text">
                Neural Management
              </div>
              <div className="text-xs app-text-tertiary">
                AI-powered neural systems
              </div>
            </GCPCardItem>
            <GCPCardItem href="#" icon="Healthcare-NLP-API">
              <div className="text-sm font-medium app-text">
                NeuroProsthetics
              </div>
              <div className="text-xs app-text-tertiary">
                Advanced prosthetic control
              </div>
            </GCPCardItem>
            <GCPCardItem href="#" icon="Iot-Core">
              <div className="text-sm font-medium app-text">BCI</div>
              <div className="text-xs app-text-tertiary">
                Brain-Computer Interface
              </div>
            </GCPCardItem>
            <GCPCardItem href="#" icon="Game-Servers">
              <div className="text-sm font-medium app-text">Full-Dive VR</div>
              <div className="text-xs app-text-tertiary">
                Immersive virtual reality
              </div>
            </GCPCardItem>
            <GCPCardItem href="#" icon="Vertex-AI">
              <div className="text-sm font-medium app-text">Augmented XR</div>
              <div className="text-xs app-text-tertiary">
                Extended reality platform
              </div>
            </GCPCardItem>
          </GCPCardContent>
        </GCPCard>

        {/* Getting Started Card */}
        <GCPCard
          title="Getting Started"
          icon="Launcher"
          onOptionsClick={() => console.log("Getting started options")}
        >
          <GCPCardContent spacing="tight">
            <GCPCardItem
              href="#"
              icon={<Play className="w-5 h-5 text-blue-700" />}
            >
              <span className="text-sm app-text">
                Deploy your first neural model
              </span>
            </GCPCardItem>
            <GCPCardItem
              href="#"
              icon={<Database className="w-5 h-5 text-blue-700" />}
            >
              <span className="text-sm app-text">Create a neural database</span>
            </GCPCardItem>
            <GCPCardItem
              href="#"
              icon={<Cpu className="w-5 h-5 text-blue-700" />}
            >
              <span className="text-sm app-text">Configure BCI parameters</span>
            </GCPCardItem>
            <GCPCardItem
              href="#"
              icon={<Zap className="w-5 h-5 text-blue-700" />}
            >
              <span className="text-sm app-text">Set up neural monitoring</span>
            </GCPCardItem>
            <GCPCardItem
              href="#"
              icon={<Cloud className="w-5 h-5 text-blue-700" />}
            >
              <span className="text-sm app-text">Install NeuraScale SDK</span>
            </GCPCardItem>
            <div className="mt-4 pt-4 border-t app-card-border">
              <a
                href="#"
                className="flex items-center gap-2 text-sm text-blue-700 hover:underline"
              >
                <ArrowRight className="w-4 h-4" />
                Explore all tutorials
              </a>
            </div>
          </GCPCardContent>
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
          <GCPCardContent spacing="loose">
            <div>
              <div className="text-sm app-text-tertiary mb-2">
                Requests (requests/sec)
              </div>
              <div className="h-[200px] bg-gray-50 dark:bg-gray-800 rounded flex items-center justify-center app-text-tertiary">
                {/* Chart placeholder */}
                <span className="text-xs">API usage chart</span>
              </div>
            </div>
            <div className="flex items-center justify-between pt-4 border-t app-card-border">
              <div className="flex items-center gap-2">
                <span className="text-sm app-text-tertiary">Requests:</span>
                <span className="text-sm font-medium app-text">0.002/s</span>
              </div>
              <a
                href="#"
                className="flex items-center gap-2 text-sm text-blue-700 hover:underline"
              >
                <ArrowRight className="w-4 h-4" />
                Go to APIs overview
              </a>
            </div>
          </GCPCardContent>
        </GCPCard>

        {/* Platform Status Card */}
        <GCPCard
          title="NeuraScale Platform Status"
          icon="Security-Command-Center"
          onOptionsClick={() => console.log("Status options")}
        >
          <GCPCardContent spacing="loose">
            <div className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-800 rounded">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-sm font-medium app-text">
                All services normal
              </span>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between py-2">
                <span className="text-sm app-text-secondary">
                  Neural Management
                </span>
                <span className="flex items-center gap-2 text-sm">
                  <span className="w-2 h-2 bg-green-600 rounded-full"></span>
                  <span className="text-green-600">Operational</span>
                </span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-sm app-text-secondary">BCI Services</span>
                <span className="flex items-center gap-2 text-sm">
                  <span className="w-2 h-2 bg-green-600 rounded-full"></span>
                  <span className="text-green-600">Operational</span>
                </span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-sm app-text-secondary">
                  VR/XR Platform
                </span>
                <span className="flex items-center gap-2 text-sm">
                  <span className="w-2 h-2 bg-green-600 rounded-full"></span>
                  <span className="text-green-600">Operational</span>
                </span>
              </div>
            </div>

            <div className="pt-4 border-t app-card-border">
              <a
                href="#"
                className="flex items-center gap-2 text-sm text-blue-700 hover:underline"
              >
                <ArrowRight className="w-4 h-4" />
                Go to Cloud status dashboard
              </a>
            </div>
          </GCPCardContent>
        </GCPCard>
      </GCPCardGrid>

      {/* Third Row - Activity and News */}
      <GCPCardGrid columns={2}>
        {/* Recent Activity */}
        <GCPCard
          title="Recent Activity"
          icon="Cloud-Logging"
          onOptionsClick={() => console.log("Activity options")}
        >
          <GCPCardContent>
            <GCPCardItem>
              <div className="flex items-start gap-3 w-full">
                <div className="w-2 h-2 bg-green-600 rounded-full flex-shrink-0 mt-2"></div>
                <div className="flex-1">
                  <p className="text-sm app-text">
                    Neural instance "cortex-01" deployed successfully
                  </p>
                  <p className="text-xs app-text-tertiary mt-1">
                    2 minutes ago
                  </p>
                </div>
              </div>
            </GCPCardItem>
            <GCPCardItem>
              <div className="flex items-start gap-3 w-full">
                <div className="w-2 h-2 bg-blue-600 rounded-full flex-shrink-0 mt-2"></div>
                <div className="flex-1">
                  <p className="text-sm app-text">BCI configuration updated</p>
                  <p className="text-xs app-text-tertiary mt-1">
                    15 minutes ago
                  </p>
                </div>
              </div>
            </GCPCardItem>
            <GCPCardItem>
              <div className="flex items-start gap-3 w-full">
                <div className="w-2 h-2 bg-yellow-500 rounded-full flex-shrink-0 mt-2"></div>
                <div className="flex-1">
                  <p className="text-sm app-text">
                    Neural database backup completed
                  </p>
                  <p className="text-xs app-text-tertiary mt-1">1 hour ago</p>
                </div>
              </div>
            </GCPCardItem>
          </GCPCardContent>
        </GCPCard>

        {/* News & Updates */}
        <GCPCard
          title="News & Updates"
          icon="Release-Notes"
          onOptionsClick={() => console.log("News options")}
        >
          <GCPCardContent>
            <GCPCardItem href="#">
              <div>
                <h4 className="text-sm font-medium app-text mb-1">
                  NeuraScale 2.0 Released
                </h4>
                <p className="text-xs app-text-tertiary">
                  Major update includes improved BCI latency and new VR
                  capabilities
                </p>
                <span className="text-xs app-text-tertiary mt-1 block">
                  2 days ago
                </span>
              </div>
            </GCPCardItem>
            <GCPCardItem href="#">
              <div>
                <h4 className="text-sm font-medium app-text mb-1">
                  New Neural Training Models Available
                </h4>
                <p className="text-xs app-text-tertiary">
                  Pre-trained models for faster deployment of neural interfaces
                </p>
                <span className="text-xs app-text-tertiary mt-1 block">
                  1 week ago
                </span>
              </div>
            </GCPCardItem>
            <div className="pt-4 border-t app-card-border">
              <a
                href="#"
                className="flex items-center gap-2 text-sm text-blue-700 hover:underline"
              >
                <ArrowRight className="w-4 h-4" />
                Read all news
              </a>
            </div>
          </GCPCardContent>
        </GCPCard>
      </GCPCardGrid>
    </div>
  );

  // Activity Tab Content
  const ActivityContent = () => (
    <div className="max-w-[1440px] mx-auto">
      <GCPCard title="System Activity Log">
        <div className="text-center py-12 app-text-tertiary">
          Activity log will be displayed here
        </div>
      </GCPCard>
    </div>
  );

  // Recommendations Tab Content
  const RecommendationsContent = () => (
    <div className="max-w-[1440px] mx-auto">
      <GCPCard title="Personalized Recommendations">
        <div className="text-center py-12 app-text-tertiary">
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
    <div className="min-h-screen app-bg">
      {/* Negative margin to extend tabs to the viewport edge */}
      <div
        style={{
          marginLeft: `-${sidebarWidth}px`,
          marginRight: `-${sidebarWidth}px`,
        }}
      >
        <GCPTabs
          tabs={tabs}
          defaultTab="dashboard"
          sidebarWidth={sidebarWidth}
        />
      </div>
    </div>
  );
}
