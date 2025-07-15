import React from "react";
import { LucideIcon } from "lucide-react";

interface ServiceCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  status?: "Active" | "Inactive" | "Beta";
  onClick?: () => void;
}

export default function ServiceCard({
  title,
  description,
  icon: Icon,
  status = "Active",
  onClick,
}: ServiceCardProps) {
  const getStatusStyle = (status: string) => {
    switch (status) {
      case "Active":
        return {
          badge:
            "bg-gradient-to-r from-emerald-100 to-green-100 text-emerald-700 border-emerald-200",
          icon: "from-emerald-500 to-green-600",
        };
      case "Beta":
        return {
          badge:
            "bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700 border-blue-200",
          icon: "from-blue-500 to-indigo-600",
        };
      case "Inactive":
        return {
          badge:
            "bg-gradient-to-r from-gray-100 to-gray-100 text-gray-600 border-gray-200",
          icon: "from-gray-400 to-gray-500",
        };
      default:
        return {
          badge:
            "bg-gradient-to-r from-gray-100 to-gray-100 text-gray-600 border-gray-200",
          icon: "from-gray-400 to-gray-500",
        };
    }
  };

  const statusStyle = getStatusStyle(status);

  return (
    <div
      className="bg-white/80 backdrop-blur-sm rounded-xl border border-gray-100 p-6 hover:shadow-xl hover:scale-[1.02] transition-all duration-300 cursor-pointer group relative overflow-hidden"
      onClick={onClick}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-gray-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-3">
          <div
            className={`p-3 bg-gradient-to-br ${statusStyle.icon} rounded-xl shadow-lg group-hover:shadow-xl transition-all duration-300`}
          >
            <Icon className="h-6 w-6 text-white" />
          </div>
          <span
            className={`px-3 py-1.5 text-xs font-semibold rounded-full border ${statusStyle.badge} shadow-sm`}
          >
            {status}
          </span>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900 group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-gray-900 group-hover:to-gray-600 group-hover:bg-clip-text transition-all duration-300 mb-2">
            {title}
          </h3>
          <p className="text-sm text-gray-600 leading-relaxed">{description}</p>
        </div>
      </div>
    </div>
  );
}
