"use client";

import React from "react";
import {
  Users,
  DollarSign,
  TrendingUp,
  CreditCard,
  ArrowUp,
} from "lucide-react";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

export default function Dashboard() {
  // Sample data for charts
  const revenueData = [
    { month: "Jan", value: 30000 },
    { month: "Feb", value: 35000 },
    { month: "Mar", value: 32000 },
    { month: "Apr", value: 40000 },
    { month: "May", value: 38000 },
    { month: "Jun", value: 45000 },
    { month: "Jul", value: 42000 },
  ];

  const activityData = [
    { day: "Mon", value: 120 },
    { day: "Tue", value: 132 },
    { day: "Wed", value: 101 },
    { day: "Thu", value: 134 },
    { day: "Fri", value: 90 },
    { day: "Sat", value: 230 },
    { day: "Sun", value: 210 },
  ];

  const expensesData = [
    { category: "Jan", value: 20 },
    { category: "Feb", value: 35 },
    { category: "Mar", value: 25 },
    { category: "Apr", value: 30 },
    { category: "May", value: 40 },
    { category: "Jun", value: 35 },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-6 space-y-6">
        {/* Header Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* New Visitors Card */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-500 text-sm font-medium">
                New Visitors
              </h3>
              <span className="text-xs text-gray-400">Last Week</span>
            </div>
            <div className="flex items-end justify-between">
              <div>
                <p className="text-3xl font-bold text-gray-900">$48.9k</p>
                <div className="flex items-center gap-1 mt-2">
                  <span className="text-green-500 text-sm font-medium">
                    23%
                  </span>
                  <ArrowUp className="w-3 h-3 text-green-500" />
                </div>
              </div>
              <div className="relative">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-100 to-blue-100 rounded-full flex items-center justify-center">
                  <Users className="w-8 h-8 text-purple-600" />
                </div>
              </div>
            </div>
            <button className="mt-4 w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white text-sm font-medium py-2 rounded-lg hover:opacity-90 transition-opacity">
              VIEW MORE
            </button>
          </div>

          {/* Activity Card */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-500 text-sm font-medium">Activity</h3>
              <span className="text-xs text-gray-400">Last Week</span>
            </div>
            <div className="mb-4">
              <p className="text-3xl font-bold text-gray-900">82%</p>
              <div className="flex items-center gap-1 mt-2">
                <span className="text-green-500 text-sm font-medium">+12%</span>
                <ArrowUp className="w-3 h-3 text-green-500" />
              </div>
            </div>
            <div className="h-16">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={activityData}>
                  <defs>
                    <linearGradient
                      id="colorActivity"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#10B981"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorActivity)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Total Income Card */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <h3 className="text-gray-500 text-sm font-medium mb-4">
              Total Income
            </h3>
            <p className="text-gray-400 text-xs mb-2">Yearly income overview</p>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                    <DollarSign className="w-4 h-4 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Income</p>
                    <p className="text-2xl font-bold text-gray-900">$42,845</p>
                  </div>
                </div>
                <span className="text-green-500 text-sm font-medium">+23%</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                    <CreditCard className="w-4 h-4 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Expense</p>
                    <p className="text-2xl font-bold text-gray-900">$38,658</p>
                  </div>
                </div>
                <span className="text-red-500 text-sm font-medium">-12%</span>
              </div>
            </div>
          </div>

          {/* Report Card */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <h3 className="text-gray-500 text-sm font-medium mb-4">Report</h3>
            <p className="text-gray-400 text-xs mb-4">Monthly Avg: $45,578k</p>
            <div className="relative h-32">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={revenueData}>
                  <defs>
                    <linearGradient
                      id="colorRevenue"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#8B5CF6"
                    strokeWidth={3}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Revenue Overview */}
          <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-gray-900 text-lg font-semibold">
                  Total Revenue
                </h3>
                <div className="flex items-center gap-4 mt-2">
                  <span className="text-3xl font-bold text-gray-900">$96k</span>
                  <span className="text-green-500 text-sm font-medium bg-green-50 px-2 py-1 rounded">
                    +12%
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">Sales</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">Profit</span>
                </div>
              </div>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={revenueData}>
                  <defs>
                    <linearGradient
                      id="salesGradient"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient
                      id="profitGradient"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                  <XAxis dataKey="month" stroke="#9ca3af" fontSize={12} />
                  <YAxis stroke="#9ca3af" fontSize={12} />
                  <Tooltip />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#8B5CF6"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#salesGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Order Statistics */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <h3 className="text-gray-900 text-lg font-semibold mb-2">
              Order Statistics
            </h3>
            <p className="text-4xl font-bold text-gray-900 mb-1">8,258</p>
            <p className="text-gray-500 text-sm mb-6">Total Orders</p>

            <div className="relative h-32 mb-6">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={activityData}>
                  <Bar dataKey="value" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-600 text-sm">Electronics</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div className="w-3/4 h-full bg-gradient-to-r from-purple-500 to-blue-500"></div>
                  </div>
                  <span className="text-sm font-medium">75%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600 text-sm">Fashion</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div className="w-1/2 h-full bg-gradient-to-r from-blue-500 to-green-500"></div>
                  </div>
                  <span className="text-sm font-medium">50%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Performance */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-gray-900 text-lg font-semibold">
                Performance
              </h3>
              <select className="text-sm text-gray-600 bg-transparent border-0 focus:outline-none">
                <option>Week 17</option>
                <option>Week 18</option>
              </select>
            </div>
            <div className="flex items-center justify-center">
              <div className="relative w-48 h-48">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="96"
                    cy="96"
                    r="80"
                    stroke="#e5e7eb"
                    strokeWidth="16"
                    fill="none"
                  />
                  <circle
                    cx="96"
                    cy="96"
                    r="80"
                    stroke="url(#gradient)"
                    strokeWidth="16"
                    fill="none"
                    strokeDasharray={`${2 * Math.PI * 80 * 0.72} ${
                      2 * Math.PI * 80
                    }`}
                    strokeLinecap="round"
                  />
                  <defs>
                    <linearGradient
                      id="gradient"
                      x1="0%"
                      y1="0%"
                      x2="100%"
                      y2="100%"
                    >
                      <stop offset="0%" stopColor="#8B5CF6" />
                      <stop offset="100%" stopColor="#3B82F6" />
                    </linearGradient>
                  </defs>
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <p className="text-3xl font-bold text-gray-900">72%</p>
                  <p className="text-sm text-gray-500">Completion</p>
                </div>
              </div>
            </div>
          </div>

          {/* Conversion Rate */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-gray-900 text-lg font-semibold">
                Conversion Rate
              </h3>
              <TrendingUp className="w-5 h-5 text-green-500" />
            </div>
            <p className="text-gray-500 text-sm mb-4">Compared to Last Month</p>
            <p className="text-4xl font-bold text-gray-900 mb-2">8.72%</p>
            <p className="text-green-500 text-sm font-medium mb-6">+2.1%</p>

            <div className="space-y-3">
              <div>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-600">Impressions</span>
                  <span className="text-red-500">-12.8%</span>
                </div>
                <div className="text-2xl font-bold text-gray-900">$42,389</div>
              </div>
              <div>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-600">Added to Cart</span>
                  <span className="text-green-500">+8.3%</span>
                </div>
                <div className="text-2xl font-bold text-gray-900">$38,211</div>
              </div>
              <div>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-600">Checkout</span>
                  <span className="text-green-500">+4.12%</span>
                </div>
                <div className="text-2xl font-bold text-gray-900">$18,220</div>
              </div>
            </div>
          </div>

          {/* Expenses */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <h3 className="text-gray-900 text-lg font-semibold mb-6">
              Expenses
            </h3>
            <div className="flex items-center justify-between mb-4">
              <p className="text-3xl font-bold text-gray-900">$84.7k</p>
              <span className="text-green-500 text-sm font-medium bg-green-50 px-2 py-1 rounded">
                +8.2%
              </span>
            </div>
            <div className="h-32">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={expensesData}>
                  <Bar dataKey="value" fill="#8B5CF6" radius={[4, 4, 0, 0]}>
                    {expensesData.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={index % 2 === 0 ? "#8B5CF6" : "#3B82F6"}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
