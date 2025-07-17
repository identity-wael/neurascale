"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { PLANS } from "@/lib/stripe";
import { Button } from "@/components/ui/button";
import Layout from "@/components/layout/Layout";

export default function PricingPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState<string | null>(null);

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

  return (
    <Layout>
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Choose Your Plan
            </h1>
            <p className="text-xl text-gray-600">
              Scale your neural computing needs with our flexible pricing
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {Object.entries(PLANS).map(([key, plan]) => (
              <div
                key={key}
                className={`rounded-lg border-2 p-6 ${
                  key === "PROFESSIONAL"
                    ? "border-blue-600 shadow-xl scale-105"
                    : "border-gray-200"
                }`}
              >
                {key === "PROFESSIONAL" && (
                  <div className="bg-blue-600 text-white text-center py-1 px-4 rounded-full text-sm font-medium mb-4 -mt-10 mx-auto w-fit">
                    Most Popular
                  </div>
                )}

                <h2 className="text-2xl font-bold mb-2">{plan.name}</h2>
                <p className="text-gray-600 mb-4">{plan.description}</p>

                <div className="mb-6">
                  {plan.price !== null ? (
                    <div>
                      <span className="text-4xl font-bold">${plan.price}</span>
                      <span className="text-gray-600">/month</span>
                    </div>
                  ) : (
                    <div className="text-2xl font-bold">Custom Pricing</div>
                  )}
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <svg
                        className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5"
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
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Button
                  onClick={() => handleSubscribe(key)}
                  disabled={loading !== null}
                  className={`w-full ${
                    key === "PROFESSIONAL"
                      ? "bg-blue-600 hover:bg-blue-700"
                      : key === "FREE"
                        ? "bg-gray-600 hover:bg-gray-700"
                        : "bg-gray-900 hover:bg-gray-800"
                  }`}
                >
                  {loading === key
                    ? "Processing..."
                    : key === "ENTERPRISE"
                      ? "Contact Sales"
                      : key === "FREE"
                        ? "Current Plan"
                        : "Subscribe"}
                </Button>
              </div>
            ))}
          </div>

          <div className="mt-12 text-center text-gray-600">
            <p>
              All plans include SSL certificates, 99.9% uptime SLA, and 24/7
              monitoring.
            </p>
            <p className="mt-2">
              Need a custom solution?{" "}
              <a
                href="mailto:sales@neurascale.io"
                className="text-blue-600 hover:underline"
              >
                Contact our sales team
              </a>
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
}
