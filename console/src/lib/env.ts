import { z } from "zod";

// Define the schema for environment variables
const envSchema = z.object({
  // Firebase Configuration (Required)
  NEXT_PUBLIC_FIREBASE_API_KEY: z
    .string()
    .min(1, "Firebase API key is required"),
  NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: z
    .string()
    .min(1, "Firebase auth domain is required"),
  NEXT_PUBLIC_FIREBASE_PROJECT_ID: z
    .string()
    .min(1, "Firebase project ID is required"),
  NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET: z
    .string()
    .min(1, "Firebase storage bucket is required"),
  NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID: z
    .string()
    .min(1, "Firebase messaging sender ID is required"),
  NEXT_PUBLIC_FIREBASE_APP_ID: z.string().min(1, "Firebase app ID is required"),

  // Firebase Admin (Server-side only, required)
  FIREBASE_ADMIN_CLIENT_EMAIL: z.string().email("Invalid Firebase admin email"),
  FIREBASE_ADMIN_PRIVATE_KEY: z
    .string()
    .min(1, "Firebase admin private key is required"),

  // Stripe Configuration (Required)
  NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: z
    .string()
    .min(1, "Stripe publishable key is required"),
  STRIPE_SECRET_KEY: z.string().min(1, "Stripe secret key is required"),
  STRIPE_WEBHOOK_SECRET: z.string().min(1, "Stripe webhook secret is required"),

  // Database (Required)
  DATABASE_URL: z.string().url("Invalid database URL"),

  // Application URLs (Required)
  NEXT_PUBLIC_APP_URL: z.string().url("Invalid app URL"),

  // Optional
  NODE_ENV: z
    .enum(["development", "test", "production"])
    .default("development"),

  // Neon Database (Optional)
  NEON_API_KEY: z.string().optional(),
  NEON_PROJECT_ID: z.string().optional(),
  NEON_BRANCH_ID: z.string().optional(),
});

// Type for the environment variables
type Env = z.infer<typeof envSchema>;

// Validate environment variables
function validateEnv(): Env {
  try {
    return envSchema.parse(process.env);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const missingVars = error.errors.map((e) => e.path.join(".")).join(", ");
      throw new Error(
        `Missing or invalid environment variables: ${missingVars}\n${error.message}`,
      );
    }
    throw error;
  }
}

// Export validated environment variables
export const env = validateEnv();

// Helper functions
export const isProduction = () => env.NODE_ENV === "production";
export const isDevelopment = () => env.NODE_ENV === "development";
