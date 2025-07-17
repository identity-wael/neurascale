"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { PLANS } from "@/lib/stripe";
import { Button } from "@/components/ui/button";
import Layout from "@/components/layout/Layout";

interface Subscription {
  id: string;
  status: string;
  plan: string;
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
}

interface Invoice {
  id: string;
  amountPaid: number;
  currency: string;
  status: string;
  createdAt: string;
  hostedInvoiceUrl: string;
}

export default function BillingPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [cancelLoading, setCancelLoading] = useState(false);

  useEffect(() => {
    if (!user) {
      router.push("/auth/signin");
      return;
    }

    fetchBillingInfo();
  }, [user, router]);

  const fetchBillingInfo = async () => {
    try {
      const idToken = await user?.getIdToken();

      const response = await fetch("/api/stripe/billing-info", {
        headers: {
          Authorization: `Bearer ${idToken}`,
        },
      });
      const data = await response.json();

      setSubscription(data.subscription);
      setInvoices(data.invoices || []);
    } catch (error) {
      console.error("Error fetching billing info:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!confirm("Are you sure you want to cancel your subscription?")) {
      return;
    }

    try {
      setCancelLoading(true);
      const idToken = await user?.getIdToken();

      const response = await fetch("/api/stripe/cancel-subscription", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${idToken}`,
        },
      });

      if (response.ok) {
        await fetchBillingInfo();
        alert(
          "Your subscription will be canceled at the end of the billing period.",
        );
      }
    } catch (error) {
      console.error("Error canceling subscription:", error);
      alert("Failed to cancel subscription. Please try again.");
    } finally {
      setCancelLoading(false);
    }
  };

  const handleManageBilling = async () => {
    try {
      const idToken = await user?.getIdToken();

      const response = await fetch("/api/stripe/create-portal-session", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${idToken}`,
        },
      });

      const { url } = await response.json();
      if (url) {
        window.location.href = url;
      }
    } catch (error) {
      console.error("Error creating portal session:", error);
      alert("Failed to open billing portal. Please try again.");
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="p-8">
          <div className="text-center">Loading billing information...</div>
        </div>
      </Layout>
    );
  }

  const currentPlan = subscription
    ? PLANS[subscription.plan as keyof typeof PLANS]
    : PLANS.FREE;

  return (
    <Layout>
      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Billing & Subscription</h1>

          {/* Current Plan */}
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Current Plan</h2>

            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-2xl font-bold">{currentPlan.name}</h3>
                <p className="text-gray-600">{currentPlan.description}</p>

                {subscription && subscription.status === "ACTIVE" && (
                  <div className="mt-4">
                    <p className="text-sm text-gray-500">
                      {subscription.cancelAtPeriodEnd
                        ? `Cancels on ${new Date(
                            subscription.currentPeriodEnd,
                          ).toLocaleDateString()}`
                        : `Renews on ${new Date(
                            subscription.currentPeriodEnd,
                          ).toLocaleDateString()}`}
                    </p>
                  </div>
                )}
              </div>

              <div className="text-right">
                {currentPlan.price !== null && (
                  <div>
                    <span className="text-3xl font-bold">
                      ${currentPlan.price}
                    </span>
                    <span className="text-gray-600">/month</span>
                  </div>
                )}
              </div>
            </div>

            <div className="flex gap-4">
              <Button onClick={() => router.push("/pricing")} variant="outline">
                Change Plan
              </Button>

              {subscription && subscription.plan !== "FREE" && (
                <>
                  <Button onClick={handleManageBilling} variant="outline">
                    Manage Billing
                  </Button>

                  {!subscription.cancelAtPeriodEnd && (
                    <Button
                      onClick={handleCancelSubscription}
                      variant="outline"
                      className="text-red-600 border-red-600 hover:bg-red-50"
                      disabled={cancelLoading}
                    >
                      {cancelLoading ? "Canceling..." : "Cancel Subscription"}
                    </Button>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Usage */}
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Current Usage</h2>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span>Neural Processors</span>
                  <span className="font-medium">
                    2 /{" "}
                    {currentPlan.limits.neuralProcessors === -1
                      ? "∞"
                      : currentPlan.limits.neuralProcessors}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{
                      width:
                        currentPlan.limits.neuralProcessors === -1
                          ? "10%"
                          : `${
                              (2 / currentPlan.limits.neuralProcessors) * 100
                            }%`,
                    }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <span>Storage</span>
                  <span className="font-medium">
                    15 GB /{" "}
                    {currentPlan.limits.storage === -1
                      ? "∞"
                      : `${currentPlan.limits.storage} GB`}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{
                      width:
                        currentPlan.limits.storage === -1
                          ? "5%"
                          : `${(15 / currentPlan.limits.storage) * 100}%`,
                    }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <span>API Calls (this month)</span>
                  <span className="font-medium">
                    842 /{" "}
                    {currentPlan.limits.apiCalls === -1
                      ? "∞"
                      : currentPlan.limits.apiCalls.toLocaleString()}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{
                      width:
                        currentPlan.limits.apiCalls === -1
                          ? "2%"
                          : `${(842 / currentPlan.limits.apiCalls) * 100}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Invoices */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Invoice History</h2>

            {invoices.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">Date</th>
                      <th className="text-left py-2">Amount</th>
                      <th className="text-left py-2">Status</th>
                      <th className="text-left py-2">Invoice</th>
                    </tr>
                  </thead>
                  <tbody>
                    {invoices.map((invoice) => (
                      <tr key={invoice.id} className="border-b">
                        <td className="py-3">
                          {new Date(invoice.createdAt).toLocaleDateString()}
                        </td>
                        <td className="py-3">
                          ${(invoice.amountPaid / 100).toFixed(2)}{" "}
                          {invoice.currency.toUpperCase()}
                        </td>
                        <td className="py-3">
                          <span
                            className={`px-2 py-1 rounded text-sm ${
                              invoice.status === "paid"
                                ? "bg-green-100 text-green-800"
                                : "bg-gray-100 text-gray-800"
                            }`}
                          >
                            {invoice.status}
                          </span>
                        </td>
                        <td className="py-3">
                          {invoice.hostedInvoiceUrl && (
                            <a
                              href={invoice.hostedInvoiceUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:underline"
                            >
                              View
                            </a>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-500">No invoices yet.</p>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
