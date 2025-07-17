import {
  initializeApp,
  getApps,
  cert,
  ServiceAccount,
} from "firebase-admin/app";
import { getAuth } from "firebase-admin/auth";

let initialized = false;

export function initAdmin() {
  if (initialized || getApps().length > 0) {
    return;
  }

  // Skip initialization during build time
  if (!process.env.STRIPE_SECRET_KEY && process.env.NODE_ENV === "production") {
    return;
  }

  const projectId = process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID;
  const clientEmail = process.env.FIREBASE_CLIENT_EMAIL;
  const privateKey = process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, "\n");

  if (!projectId || !clientEmail || !privateKey) {
    // Only throw error at runtime, not build time
    if (
      process.env.NODE_ENV !== "production" ||
      process.env.STRIPE_SECRET_KEY
    ) {
      console.error("Missing Firebase Admin environment variables");
      throw new Error("Firebase Admin SDK not properly configured");
    }
    return;
  }

  const serviceAccount: ServiceAccount = {
    projectId,
    clientEmail,
    privateKey,
  };

  initializeApp({
    credential: cert(serviceAccount),
  });

  initialized = true;
}

export { getAuth as auth };
