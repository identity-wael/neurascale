# Firebase Setup Guide for NeuraScale Console

## 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Name it "neurascale-console" or similar
4. Enable Google Analytics (optional)
5. Accept terms and create project

## 2. Enable Authentication

1. In Firebase Console, go to **Authentication** → **Get started**
2. Go to **Sign-in method** tab
3. Click **Google** provider
4. Toggle **Enable**
5. Set support email to your email
6. Add authorized domains:
   - `console.neurascale.io`
   - `localhost` (for development)
7. Save

## 3. Get Configuration Values

1. Go to **Project settings** (gear icon)
2. Scroll down to "Your apps" section
3. Click **Web app** icon (`</>`)
4. Register app name: "NeuraScale Console"
5. Copy the config values:

```javascript
const firebaseConfig = {
  apiKey: "AIza...", // Copy this
  authDomain: "project-id.firebaseapp.com", // Copy this
  projectId: "project-id", // Copy this
  storageBucket: "project-id.appspot.com", // Copy this
  messagingSenderId: "123456789", // Copy this
  appId: "1:123456789:web:abcd...", // Copy this
};
```

## 4. Set Environment Variables in Vercel

Run these commands to set up Vercel environment variables:

```bash
cd /Users/weg/NeuraScale/neurascale/console

# Set Firebase config
npx vercel env add NEXT_PUBLIC_FIREBASE_API_KEY
# Paste your apiKey when prompted

npx vercel env add NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
# Paste your authDomain when prompted

npx vercel env add NEXT_PUBLIC_FIREBASE_PROJECT_ID
# Paste your projectId when prompted

npx vercel env add NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
# Paste your storageBucket when prompted

npx vercel env add NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
# Paste your messagingSenderId when prompted

npx vercel env add NEXT_PUBLIC_FIREBASE_APP_ID
# Paste your appId when prompted
```

## 5. Deploy and Test

After setting environment variables:

```bash
npx vercel --prod
```

## 6. Verify Setup

1. Go to `console.neurascale.io`
2. Should redirect to `/auth/signin`
3. Click "Continue with Google"
4. Should authenticate and redirect to dashboard

## Troubleshooting

- **"Firebase not configured"**: Environment variables not set correctly
- **OAuth error**: Check authorized domains in Firebase Console
- **Redirect issues**: Verify auth domain matches Vercel deployment

---

**Important**: Keep your Firebase config values secure and never commit them to version control.
