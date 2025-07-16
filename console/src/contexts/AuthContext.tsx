"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import {
  User,
  signInWithPopup,
  signOut,
  onAuthStateChanged,
  UserCredential,
} from "firebase/auth";
import { auth, googleProvider } from "@/lib/firebase";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signInWithGoogle: () => Promise<UserCredential>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if Firebase is properly configured
    if (!auth || !auth.app) {
      setLoading(false);
      return;
    }

    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setUser(user);

      // Set or clear session cookie
      if (user) {
        // Set a session cookie when user is authenticated
        document.cookie = `__session=${user.uid}; path=/; max-age=604800; SameSite=Lax`;
      } else {
        // Clear the session cookie when user is not authenticated
        document.cookie =
          "__session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
      }

      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const signInWithGoogle = async () => {
    if (!auth || !auth.app) {
      throw new Error(
        "Firebase not configured. Please add your Firebase environment variables.",
      );
    }
    try {
      const result = await signInWithPopup(auth, googleProvider);
      return result;
    } catch (error) {
      console.error("Error signing in with Google:", error);
      throw error;
    }
  };

  const logout = async () => {
    if (!auth || !auth.app) {
      throw new Error(
        "Firebase not configured. Please add your Firebase environment variables.",
      );
    }
    try {
      await signOut(auth);
      // Clear the session cookie
      document.cookie =
        "__session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
      // Force reload to trigger middleware
      window.location.href = "/auth/signin";
    } catch (error) {
      console.error("Error signing out:", error);
      throw error;
    }
  };

  const value = {
    user,
    loading,
    signInWithGoogle,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
