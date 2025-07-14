import { initializeApp, getApps, FirebaseApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, Auth } from "firebase/auth";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "demo-api-key",
  authDomain:
    process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "demo.firebaseapp.com",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "demo-project",
  storageBucket:
    process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "demo.appspot.com",
  messagingSenderId:
    process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "123456789",
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "demo-app-id",
};

let app: FirebaseApp;
let auth: Auth;

// Only initialize Firebase if we have a valid API key
const hasValidConfig =
  process.env.NEXT_PUBLIC_FIREBASE_API_KEY &&
  process.env.NEXT_PUBLIC_FIREBASE_API_KEY !== "demo-api-key";

if (hasValidConfig && !getApps().length) {
  app = initializeApp(firebaseConfig);
} else if (hasValidConfig) {
  app = getApps()[0];
} else {
  // Create a mock app for build time
  app = {} as FirebaseApp;
}

auth = hasValidConfig ? getAuth(app) : ({} as Auth);

export const googleProvider = hasValidConfig
  ? new GoogleAuthProvider()
  : ({} as GoogleAuthProvider);

if (hasValidConfig && googleProvider.setCustomParameters) {
  googleProvider.setCustomParameters({
    prompt: "select_account",
  });
}

export { auth };
export default app;
