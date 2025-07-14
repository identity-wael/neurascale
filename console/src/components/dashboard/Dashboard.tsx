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
      icon: Cpu,
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
      icon: Zap,
      status: "Beta" as const,
    },
    {
      id: "cloud-infrastructure",
      title: "Cloud Infrastructure",
      description:
        "Scalable compute, storage, and networking resources for neural processing",
      icon: Server,
      status: "Active" as const,
    },
    {
      id: "neural-databases",
      title: "Neural Databases",
      description:
        "Specialized databases optimized for neural pattern storage and retrieval",
      icon: Database,
      status: "Active" as const,
    },
    {
      id: "ai-ml-platform",
      title: "AI & ML Platform",
      description:
        "Machine learning tools for neural pattern analysis and enhancement",
      icon: Bot,
      status: "Active" as const,
    },
    {
      id: "neural-networking",
      title: "Neural Networking",
      description:
        "High-speed networking infrastructure for neural data transmission",
      icon: Network,
      status: "Active" as const,
    },
    {
      id: "neuro-security",
      title: "Neuro-Security Suite",
      description:
        "Advanced security protocols for protecting neural interfaces and data",
      icon: Shield,
      status: "Active" as const,
    },
    {
      id: "neural-analytics",
      title: "Neural Analytics",
      description:
        "Real-time monitoring and analysis of neural system performance",
      icon: BarChart3,
      status: "Active" as const,
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome to NeuraScale Console
            </h1>
            <p className="text-gray-600 mt-2">
              {user
                ? `Hello, ${user.displayName || user.email}`
                : "Manage your neural computing infrastructure"}
            </p>
          </div>
          <div className="hidden md:block">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Brain className="h-8 w-8 text-white" />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Cpu className="h-5 w-5 text-blue-600" />
            <span className="text-sm font-medium">Deploy Neural Instance</span>
          </button>
          <button className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Database className="h-5 w-5 text-green-600" />
            <span className="text-sm font-medium">Create Neural Database</span>
          </button>
          <button className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Settings className="h-5 w-5 text-purple-600" />
            <span className="text-sm font-medium">Configure Interface</span>
          </button>
        </div>
      </div>

      {/* Services Grid */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-6">
          NeuraScale Services
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Recent Activity
        </h2>
        <div className="space-y-3">
          <div className="flex items-center space-x-3 text-sm">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-gray-600">
              Neural instance "cortex-01" deployed successfully
            </span>
            <span className="text-gray-400">2 minutes ago</span>
          </div>
          <div className="flex items-center space-x-3 text-sm">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span className="text-gray-600">
              Brain-Robot interface configuration updated
            </span>
            <span className="text-gray-400">15 minutes ago</span>
          </div>
          <div className="flex items-center space-x-3 text-sm">
            <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
            <span className="text-gray-600">
              Neural database backup completed
            </span>
            <span className="text-gray-400">1 hour ago</span>
          </div>
        </div>
      </div>
    </div>
  );
}
