"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { PLANS } from "@/lib/stripe";
import Layout from "@/components/layout/Layout";
import { GCPCard, GCPCardContent, GCPCardItem } from "@/components/ui/gcp-card";

interface Subscription {
  plan: string;
  status: string;
}

export default function PricingPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState<string | null>(null);
  const [currentSubscription, setCurrentSubscription] =
    useState<Subscription | null>(null);
  const [fetchingBilling, setFetchingBilling] = useState(true);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth/signin");
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      fetchBillingInfo();
    }
  }, [user]);

  const fetchBillingInfo = async () => {
    try {
      const token = await user?.getIdToken();
      if (!token) return;

      const response = await fetch("/api/stripe/billing-info", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentSubscription(data.subscription);
      }
    } catch (error) {
      console.error("Error fetching billing info:", error);
    } finally {
      setFetchingBilling(false);
    }
  };

  const handleSubscribe = async (planKey: string) => {
    if (!user) {
      router.push("/auth/signin");
      return;
    }

    // Free plan doesn't need Stripe checkout
    if (planKey === "FREE") {
      router.push("/");
      return;
    }

    try {
      setLoading(planKey);

      const idToken = await user.getIdToken();

      const response = await fetch("/api/stripe/create-checkout-session", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${idToken}`,
        },
        body: JSON.stringify({
          priceId: PLANS[planKey as keyof typeof PLANS].priceId,
          planKey,
        }),
      });

      const { sessionUrl } = await response.json();

      if (sessionUrl) {
        window.location.href = sessionUrl;
      }
    } catch (error) {
      console.error("Error creating checkout session:", error);
      alert("Failed to create checkout session. Please try again.");
    } finally {
      setLoading(null);
    }
  };

  const handleManageBilling = async () => {
    try {
      setLoading("manage");
      const token = await user?.getIdToken();

      const response = await fetch("/api/stripe/create-portal-session", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const { url } = await response.json();
      if (url) {
        window.location.href = url;
      }
    } catch (error) {
      console.error("Error creating portal session:", error);
    } finally {
      setLoading(null);
    }
  };

  if (authLoading || fetchingBilling) {
    return (
      <Layout>
        <div className="min-h-screen app-bg flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen app-bg">
        {/* Match dashboard tab content padding */}
        <div
          style={{
            paddingTop: "32px",
            paddingLeft: "96px",
            paddingRight: "96px",
            paddingBottom: "32px",
          }}
        >
          <div className="max-w-[1440px] mx-auto">
            {/* Page Header */}
            <div className="mb-6 mt-4">
              <h1 className="text-2xl font-normal app-text">
                Billing & Subscriptions
              </h1>
              <p className="text-sm app-text-secondary mt-2">
                Manage your subscription and billing details
              </p>
            </div>

            {/* Current Plan Card */}
            {currentSubscription && (
              <GCPCard
                title="Current Plan"
                icon="Billing"
                className="mb-6"
                actions={
                  currentSubscription.plan !== "FREE" && (
                    <button
                      onClick={handleManageBilling}
                      disabled={loading === "manage"}
                      className="px-3 py-1 text-sm font-medium text-[#1a73e8] hover:bg-[#e8f0fe] dark:hover:bg-[#394457] rounded transition-colors"
                    >
                      {loading === "manage" ? "Loading..." : "Manage Billing"}
                    </button>
                  )
                }
              >
                <GCPCardContent>
                  <GCPCardItem>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-lg font-medium app-text">
                          {PLANS[currentSubscription.plan as keyof typeof PLANS]
                            ?.name || "Free Plan"}
                        </p>
                        <p className="text-sm app-text-secondary mt-1">
                          Status:{" "}
                          <span className="capitalize">
                            {currentSubscription.status}
                          </span>
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-semibold app-text">
                          $
                          {PLANS[currentSubscription.plan as keyof typeof PLANS]
                            ?.price || 0}
                        </p>
                        <p className="text-sm app-text-secondary">per month</p>
                      </div>
                    </div>
                  </GCPCardItem>
                </GCPCardContent>
              </GCPCard>
            )}

            {/* Available Plans */}
            <div className="mb-6">
              <h2 className="text-lg font-medium app-text mb-4">
                Available Plans
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4 items-stretch">
              {Object.entries(PLANS).map(([key, plan]) => {
                const isCurrentPlan = currentSubscription?.plan === key;
                const isProfessional = key === "PROFESSIONAL";

                return (
                  <div key={key} className="flex flex-col h-full">
                    <GCPCard
                      title={plan.name}
                      icon="Cloud-SQL"
                      className="transition-all duration-200 hover:ring-2 hover:ring-[#1a73e8] hover:shadow-lg h-full flex flex-col relative"
                    >
                      {isProfessional && (
                        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                          <span className="bg-[#1a73e8] text-white text-xs font-medium px-3 py-1 rounded-full">
                            RECOMMENDED
                          </span>
                        </div>
                      )}
                      <div className="flex flex-col h-full px-6 pb-6 pt-2">
                        <p className="text-sm app-text-secondary mb-4 min-h-[3rem]">
                          {plan.description}
                        </p>

                        <div className="mb-6">
                          {plan.price !== null ? (
                            <div>
                              <span className="text-3xl font-semibold app-text">
                                ${plan.price}
                              </span>
                              <span className="text-sm app-text-secondary">
                                /month
                              </span>
                            </div>
                          ) : (
                            <div className="text-2xl font-semibold app-text">
                              Custom Pricing
                            </div>
                          )}
                        </div>

                        <ul className="space-y-2 flex-grow">
                          {plan.features.map((feature, index) => (
                            <li
                              key={index}
                              className="flex items-start text-sm"
                            >
                              <svg
                                className="h-4 w-4 text-green-600 dark:text-green-400 mr-2 flex-shrink-0 mt-0.5"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M5 13l4 4L19 7"
                                />
                              </svg>
                              <span className="app-text-secondary">
                                {feature}
                              </span>
                            </li>
                          ))}
                        </ul>

                        <button
                          onClick={() => handleSubscribe(key)}
                          disabled={loading !== null || isCurrentPlan}
                          className={`w-full px-4 py-2 text-sm font-medium rounded transition-colors mt-6 ${
                            isCurrentPlan
                              ? "bg-[#e8f0fe] text-[#5f6368] cursor-not-allowed dark:bg-[#394457] dark:text-[#9aa0a6]"
                              : "bg-[#1a73e8] text-white hover:bg-[#1967d2]"
                          }`}
                        >
                          {loading === key
                            ? "Processing..."
                            : isCurrentPlan
                              ? "Current Plan"
                              : key === "ENTERPRISE"
                                ? "Contact Sales"
                                : "Subscribe"}
                        </button>
                      </div>
                    </GCPCard>
                  </div>
                );
              })}
            </div>

            {/* Additional Information */}
            <div className="mt-8 p-4 rounded-lg app-card-bg border app-card-border">
              <p className="text-sm app-text-secondary text-center">
                All plans include SSL certificates, 99.9% uptime SLA, and 24/7
                monitoring. Need a custom solution?{" "}
                <a
                  href="mailto:sales@neurascale.io"
                  className="text-[#1a73e8] hover:underline"
                >
                  Contact our sales team
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
