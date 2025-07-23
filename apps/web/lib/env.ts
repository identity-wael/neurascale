import { z } from 'zod';

// Define the schema for environment variables
const envSchema = z.object({
  // Required environment variables
  NEXT_PUBLIC_SANITY_PROJECT_ID: z.string().min(1, 'Sanity project ID is required'),
  NEXT_PUBLIC_SANITY_DATASET: z.string().min(1, 'Sanity dataset is required'),
  SANITY_API_TOKEN: z.string().min(1, 'Sanity API token is required'),
  SANITY_WEBHOOK_SECRET: z.string().min(1, 'Sanity webhook secret is required'),

  // Optional with defaults
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),

  // Email configuration
  EMAIL_HOST: z.string().optional(),
  EMAIL_PORT: z.string().optional(),
  EMAIL_USER: z.string().optional(),
  EMAIL_PASS: z.string().optional(),
  EMAIL_FROM: z.string().optional(),
  EMAIL_TO: z.string().optional(),
});

// Type for the environment variables
type Env = z.infer<typeof envSchema>;

// Validate environment variables
function validateEnv(): Env {
  try {
    return envSchema.parse(process.env);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const missingVars = error.errors.map((e) => e.path.join('.')).join(', ');
      throw new Error(`Missing or invalid environment variables: ${missingVars}\n${error.message}`);
    }
    throw error;
  }
}

// Export validated environment variables
export const env = validateEnv();

// Helper to check if email is configured
export const isEmailConfigured = () => {
  return !!(env.EMAIL_HOST && env.EMAIL_PORT && env.EMAIL_USER && env.EMAIL_PASS);
};
