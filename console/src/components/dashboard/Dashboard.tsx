"use client";

import React from "react";
import {
  Brain,
  Cpu,
  Database,
  Server,
  Bot,
  Network,
  Shield,
  BarChart3,
  Zap,
  Settings,
  Activity,
  ArrowRight,
  CloudLightning,
  Layers,
  Sparkles,
  Workflow,
  Globe,
  Lock,
  TrendingUp,
} from "lucide-react";
import ServiceCard from "./ServiceCard";
import { useAuth } from "@/contexts/AuthContext";

export default function Dashboard() {
  const { user } = useAuth();

  const services = [
    {
      id: "neural-management",
      title: "Neural Management Systems",
      description:
        "Manage and monitor neural network architectures and brain-computer interfaces",
      icon: Brain,
      status: "Active" as const,
    },
    {
      id: "neuroprosthetics",
      title: "Neuroprosthetics Platform",
      description:
        "Control and configure advanced neuroprosthetic devices and interfaces",
      icon: Workflow,
      status: "Active" as const,
    },
    {
      id: "brain-robot",
      title: "Brain-Robot Swarm Interface",
      description:
        "Connect consciousness to robotic swarms for distributed control systems",
      icon: Bot,
      status: "Beta" as const,
    },
    {
      id: "full-dive-vr",
      title: "Full-Dive Virtual Reality",
      description:
        "Immersive neural interface for complete virtual world experiences",
      icon: Sparkles,
      status: "Beta" as const,
    },
    {
      id: "cloud-infrastructure",
      title: "Cloud Infrastructure",
      description:
        "Scalable compute, storage, and networking resources for neural processing",
      icon: CloudLightning,
      status: "Active" as const,
    },
    {
      id: "neural-databases",
      title: "Neural Databases",
      description:
        "Specialized databases optimized for neural pattern storage and retrieval",
      icon: Layers,
      status: "Active" as const,
    },
    {
      id: "ai-ml-platform",
      title: "AI & ML Platform",
      description:
        "Machine learning tools for neural pattern analysis and enhancement",
      icon: Sparkles,
      status: "Active" as const,
    },
    {
      id: "neural-networking",
      title: "Neural Networking",
      description:
        "High-speed networking infrastructure for neural data transmission",
      icon: Globe,
      status: "Active" as const,
    },
    {
      id: "neuro-security",
      title: "Neuro-Security Suite",
      description:
        "Advanced security protocols for protecting neural interfaces and data",
      icon: Lock,
      status: "Active" as const,
    },
    {
      id: "neural-analytics",
      title: "Neural Analytics",
      description:
        "Real-time monitoring and analysis of neural system performance",
      icon: TrendingUp,
      status: "Active" as const,
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      <div className="absolute inset-0 bg-gradient-to-br from-purple-50/20 via-transparent to-blue-50/20"></div>
      <div className="relative z-10 space-y-10 p-8">
        {/* Welcome Section */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-100 p-8 overflow-hidden relative">
          <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-blue-500/5"></div>
          <div className="relative z-10 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                Welcome to NeuraScale Console
              </h1>
              <p className="text-gray-600 mt-3 text-lg">
                {user
                  ? `Hello, ${user.displayName || user.email}`
                  : "Manage your neural computing infrastructure"}
              </p>
            </div>
            <div className="hidden md:block">
              <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-xl transform hover:scale-105 transition-transform duration-300">
                <Brain className="h-10 w-10 text-white" />
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-100 p-8 pb-10">
          <h2 className="text-xl font-semibold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mb-6">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="group flex items-center justify-between p-5 bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl hover:shadow-lg hover:scale-[1.02] transition-all duration-300">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                  <Cpu className="h-5 w-5 text-white" />
                </div>
                <span className="text-sm font-semibold text-gray-800">
                  Deploy Neural Instance
                </span>
              </div>
              <ArrowRight className="h-4 w-4 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all duration-300" />
            </button>
            <button className="group flex items-center justify-between p-5 bg-gradient-to-br from-emerald-50 to-green-50 border border-emerald-200 rounded-xl hover:shadow-lg hover:scale-[1.02] transition-all duration-300">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-green-600 rounded-lg flex items-center justify-center">
                  <Database className="h-5 w-5 text-white" />
                </div>
                <span className="text-sm font-semibold text-gray-800">
                  Create Neural Database
                </span>
              </div>
              <ArrowRight className="h-4 w-4 text-gray-400 group-hover:text-emerald-600 group-hover:translate-x-1 transition-all duration-300" />
            </button>
            <button className="group flex items-center justify-between p-5 bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-xl hover:shadow-lg hover:scale-[1.02] transition-all duration-300">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
                  <Settings className="h-5 w-5 text-white" />
                </div>
                <span className="text-sm font-semibold text-gray-800">
                  Configure Interface
                </span>
              </div>
              <ArrowRight className="h-4 w-4 text-gray-400 group-hover:text-purple-600 group-hover:translate-x-1 transition-all duration-300" />
            </button>
          </div>
        </div>

        {/* Services Grid */}
        <div>
          <h2 className="text-xl font-semibold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mb-6">
            NeuraScale Services
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-7">
            {services.map((service) => (
              <ServiceCard
                key={service.id}
                title={service.title}
                description={service.description}
                icon={service.icon}
                status={service.status}
                onClick={() => console.log(`Navigate to ${service.id}`)}
              />
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-100 p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              Recent Activity
            </h2>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Activity className="h-4 w-4 animate-pulse text-green-500" />
              <span>Live</span>
            </div>
          </div>
          <div className="space-y-4">
            <div className="flex items-center space-x-4 p-3 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="relative">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <div className="absolute inset-0 w-3 h-3 bg-green-500 rounded-full animate-ping"></div>
              </div>
              <div className="flex-1">
                <span className="text-gray-800 font-medium">
                  Neural instance "cortex-01" deployed successfully
                </span>
                <p className="text-xs text-gray-500 mt-1">2 minutes ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-4 p-3 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <div className="flex-1">
                <span className="text-gray-800 font-medium">
                  Brain-Robot interface configuration updated
                </span>
                <p className="text-xs text-gray-500 mt-1">15 minutes ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-4 p-3 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="w-3 h-3 bg-amber-500 rounded-full"></div>
              <div className="flex-1">
                <span className="text-gray-800 font-medium">
                  Neural database backup completed
                </span>
                <p className="text-xs text-gray-500 mt-1">1 hour ago</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
