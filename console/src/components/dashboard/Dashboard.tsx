"use client";

import React from "react";
import { useAuth } from "@/contexts/AuthContext";

interface ServiceCard {
  id: string;
  title: string;
  description: string;
  icon?: string;
  status?: "Active" | "Beta" | "Coming Soon";
  category?: string;
}

const neuralServices: ServiceCard[] = [
  {
    id: "neural-management",
    title: "Neural Management Systems",
    description:
      "Manage and monitor neural network architectures and brain-computer interfaces",
    icon: "AI-Platform-Unified",
    status: "Active",
    category: "Neural",
  },
  {
    id: "neuroprosthetics",
    title: "Neuroprosthetics Platform",
    description:
      "Control and configure advanced neuroprosthetic devices and interfaces",
    icon: "Healthcare-NLP-API",
    status: "Active",
    category: "Neural",
  },
  {
    id: "brain-robot",
    title: "Brain-Robot Swarm Interface",
    description:
      "Connect consciousness to robotic swarms for distributed control systems",
    icon: "Iot-Core",
    status: "Beta",
    category: "Neural",
  },
  {
    id: "full-dive-vr",
    title: "Full-Dive Virtual Reality",
    description:
      "Immersive neural interface for complete virtual world experiences",
    icon: "Cloud-Vision-API",
    status: "Beta",
    category: "Neural",
  },
];

const infrastructureServices: ServiceCard[] = [
  {
    id: "cloud-infrastructure",
    title: "Cloud Infrastructure",
    description:
      "Scalable compute, storage, and networking resources for neural processing",
    icon: "Compute-Engine",
    status: "Active",
    category: "Infrastructure",
  },
  {
    id: "neural-databases",
    title: "Neural Databases",
    description:
      "Specialized databases optimized for neural pattern storage and retrieval",
    icon: "Cloud-Spanner",
    status: "Active",
    category: "Infrastructure",
  },
  {
    id: "ai-ml-platform",
    title: "AI & ML Platform",
    description:
      "Machine learning tools for neural pattern analysis and enhancement",
    icon: "Vertex-AI",
    status: "Active",
    category: "AI/ML",
  },
  {
    id: "neural-networking",
    title: "Neural Networking",
    description:
      "High-speed networking infrastructure for neural data transmission",
    icon: "Network-Connectivity-Center",
    status: "Active",
    category: "Infrastructure",
  },
];

const securityServices: ServiceCard[] = [
  {
    id: "neuro-security",
    title: "Neuro-Security Suite",
    description:
      "Advanced security protocols for protecting neural interfaces and data",
    icon: "Security-Command-Center",
    status: "Active",
    category: "Security",
  },
  {
    id: "neural-analytics",
    title: "Neural Analytics",
    description:
      "Real-time monitoring and analysis of neural system performance",
    icon: "Cloud-Monitoring",
    status: "Active",
    category: "Analytics",
  },
];

const quickActions = [
  {
    title: "Deploy Neural Instance",
    description: "Launch a new neural compute instance",
    icon: "Compute-Engine",
    gradient: "from-blue-500 to-purple-600",
  },
  {
    title: "Create Neural Database",
    description: "Set up a specialized neural database",
    icon: "Cloud-Spanner",
    gradient: "from-emerald-500 to-teal-600",
  },
  {
    title: "Configure Interface",
    description: "Set up brain-computer interface parameters",
    icon: "Configuration-Management",
    gradient: "from-orange-500 to-red-600",
  },
];

export default function Dashboard() {
  const { user } = useAuth();

  const getStatusStyles = (status?: string) => {
    switch (status) {
      case "Active":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "Beta":
        return "bg-blue-50 text-blue-700 border-blue-200";
      case "Coming Soon":
        return "bg-gray-50 text-gray-600 border-gray-200";
      default:
        return "bg-gray-50 text-gray-600 border-gray-200";
    }
  };

  return (
    <div className="p-6 lg:p-8 xl:p-12 bg-gradient-to-br from-gray-50 via-white to-gray-50 min-h-screen">
      <div className="max-w-screen-2xl mx-auto">
        {/* Welcome Section */}
        <section className="mb-12">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl shadow-lg">
              <img
                src="/svg/AI-Platform-Unified.svg"
                alt=""
                className="w-8 h-8 filter brightness-0 invert"
              />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              Welcome to NeuraScale Console
            </h1>
          </div>

          <div className="glass-card rounded-2xl shadow-xl p-8 lg:p-10 border border-gray-100">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              {user
                ? `Hello, ${user.displayName || user.email}`
                : "Manage your neural computing infrastructure"}
            </h2>
            <p className="text-base text-gray-600 leading-relaxed max-w-3xl">
              Access and control your neural interfaces, brain-computer systems,
              and advanced computing resources from a unified platform.
            </p>
          </div>
        </section>

        {/* Quick Actions */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {quickActions.map((action) => (
              <button
                key={action.title}
                className="group relative bg-white rounded-2xl shadow-lg p-6 hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300 text-left overflow-hidden"
              >
                <div
                  className={`absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-10 transition-opacity duration-300 ${action.gradient}`}
                ></div>
                <div className="relative z-10 flex items-start gap-4">
                  <div
                    className={`p-3 bg-gradient-to-br ${action.gradient} rounded-xl shadow-md group-hover:shadow-lg transition-shadow duration-300`}
                  >
                    <img
                      src={`/svg/${action.icon}.svg`}
                      alt=""
                      className="w-6 h-6 filter brightness-0 invert"
                    />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-800 mb-1 group-hover:text-gray-900">
                      {action.title}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {action.description}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </section>

        {/* Neural Services */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            Neural Services
          </h2>
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {neuralServices.map((service) => (
              <div
                key={service.id}
                className="gradient-border bg-white rounded-2xl shadow-lg p-6 hover:shadow-2xl transition-all duration-300 cursor-pointer group hover-lift"
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl group-hover:from-purple-100 group-hover:to-blue-100 transition-colors duration-300">
                    <img
                      src={`/svg/${service.icon}.svg`}
                      alt=""
                      className="w-8 h-8"
                    />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between gap-4 mb-3">
                      <h3 className="text-lg font-semibold text-gray-800 group-hover:text-gray-900">
                        {service.title}
                      </h3>
                      <span
                        className={`px-3 py-1 text-xs font-medium rounded-full ${getStatusStyles(
                          service.status,
                        )}`}
                      >
                        {service.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {service.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Infrastructure & Platform Services */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            Infrastructure & Platform Services
          </h2>
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {infrastructureServices.map((service) => (
              <div
                key={service.id}
                className="gradient-border bg-white rounded-2xl shadow-lg p-6 hover:shadow-2xl transition-all duration-300 cursor-pointer group hover-lift"
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl group-hover:from-emerald-100 group-hover:to-teal-100 transition-colors duration-300">
                    <img
                      src={`/svg/${service.icon}.svg`}
                      alt=""
                      className="w-8 h-8"
                    />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between gap-4 mb-3">
                      <h3 className="text-lg font-semibold text-gray-800 group-hover:text-gray-900">
                        {service.title}
                      </h3>
                      <span
                        className={`px-3 py-1 text-xs font-medium rounded-full ${getStatusStyles(
                          service.status,
                        )}`}
                      >
                        {service.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {service.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Security & Analytics */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            Security & Analytics
          </h2>
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {securityServices.map((service) => (
              <div
                key={service.id}
                className="gradient-border bg-white rounded-2xl shadow-lg p-6 hover:shadow-2xl transition-all duration-300 cursor-pointer group hover-lift"
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl group-hover:from-amber-100 group-hover:to-orange-100 transition-colors duration-300">
                    <img
                      src={`/svg/${service.icon}.svg`}
                      alt=""
                      className="w-8 h-8"
                    />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between gap-4 mb-3">
                      <h3 className="text-lg font-semibold text-gray-800 group-hover:text-gray-900">
                        {service.title}
                      </h3>
                      <span
                        className={`px-3 py-1 text-xs font-medium rounded-full ${getStatusStyles(
                          service.status,
                        )}`}
                      >
                        {service.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {service.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Recent Activity */}
        <section className="mb-12">
          <div className="glass-card rounded-2xl shadow-xl p-8 lg:p-10 border border-gray-100">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-2xl font-bold text-gray-800">
                Recent Activity
              </h2>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                <span className="font-medium">Live</span>
              </div>
            </div>
            <div className="space-y-4">
              <div className="group flex items-start gap-4 p-4 rounded-xl hover:bg-gray-50 transition-all duration-200 border-l-4 border-emerald-500">
                <div className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center flex-shrink-0 group-hover:bg-emerald-200 transition-colors">
                  <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-800 mb-1">
                    Neural instance "cortex-01" deployed successfully
                  </p>
                  <p className="text-xs text-gray-500">2 minutes ago</p>
                </div>
              </div>
              <div className="group flex items-start gap-4 p-4 rounded-xl hover:bg-gray-50 transition-all duration-200 border-l-4 border-blue-500">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 group-hover:bg-blue-200 transition-colors">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-800 mb-1">
                    Brain-Robot interface configuration updated
                  </p>
                  <p className="text-xs text-gray-500">15 minutes ago</p>
                </div>
              </div>
              <div className="group flex items-start gap-4 p-4 rounded-xl hover:bg-gray-50 transition-all duration-200 border-l-4 border-amber-500">
                <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center flex-shrink-0 group-hover:bg-amber-200 transition-colors">
                  <div className="w-2 h-2 bg-amber-500 rounded-full"></div>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-800 mb-1">
                    Neural database backup completed
                  </p>
                  <p className="text-xs text-gray-500">1 hour ago</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
