import Stripe from "stripe";

// Lazy initialization to avoid build-time errors
let stripeInstance: Stripe | null = null;

export function getStripe(): Stripe {
  if (!stripeInstance) {
    if (!process.env.STRIPE_SECRET_KEY) {
      throw new Error("STRIPE_SECRET_KEY is not defined");
    }
    stripeInstance = new Stripe(process.env.STRIPE_SECRET_KEY, {
      apiVersion: "2025-06-30.basil",
      typescript: true,
    });
  }
  return stripeInstance;
}

// Export for backward compatibility
export const stripe = new Proxy({} as Stripe, {
  get(target, prop, receiver) {
    return Reflect.get(getStripe(), prop, receiver);
  },
});

// Subscription plans configuration
export const PLANS = {
  FREE: {
    name: "Free",
    description: "Perfect for trying out NeuraScale",
    price: 0,
    priceId: undefined,
    features: [
      "1 Neural Processor",
      "10 GB Storage",
      "Community Support",
      "Basic Analytics",
    ],
    limits: {
      neuralProcessors: 1,
      storage: 10, // GB
      apiCalls: 1000, // per month
    },
  },
  STARTER: {
    name: "Starter",
    description: "Great for small projects and experimentation",
    price: 49,
    priceId: process.env.STRIPE_PRICE_STARTER_MONTHLY,
    features: [
      "5 Neural Processors",
      "100 GB Storage",
      "Email Support",
      "Advanced Analytics",
      "API Access",
      "Custom Models",
    ],
    limits: {
      neuralProcessors: 5,
      storage: 100, // GB
      apiCalls: 10000, // per month
    },
  },
  PROFESSIONAL: {
    name: "Professional",
    description: "For growing teams and production workloads",
    price: 199,
    priceId: process.env.STRIPE_PRICE_PROFESSIONAL_MONTHLY,
    features: [
      "20 Neural Processors",
      "1 TB Storage",
      "Priority Support",
      "Advanced Analytics",
      "API Access",
      "Custom Models",
      "Team Collaboration",
      "SLA Guarantee",
    ],
    limits: {
      neuralProcessors: 20,
      storage: 1000, // GB
      apiCalls: 100000, // per month
    },
  },
  ENTERPRISE: {
    name: "Enterprise",
    description: "Custom solutions for large organizations",
    price: null, // Custom pricing
    priceId: process.env.STRIPE_PRICE_ENTERPRISE_MONTHLY,
    features: [
      "Unlimited Neural Processors",
      "Unlimited Storage",
      "Dedicated Support",
      "Advanced Analytics",
      "API Access",
      "Custom Models",
      "Team Collaboration",
      "SLA Guarantee",
      "Custom Integration",
      "On-premise Option",
    ],
    limits: {
      neuralProcessors: -1, // unlimited
      storage: -1, // unlimited
      apiCalls: -1, // unlimited
    },
  },
};
