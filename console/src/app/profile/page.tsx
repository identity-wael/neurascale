"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import Image from "next/image";
import Layout from "@/components/layout/Layout";
import {
  GCPCard,
  GCPCardGrid,
  GCPCardContent,
  GCPCardItem,
} from "@/components/ui/gcp-card";

interface UserProfile {
  id: string;
  email: string;
  name: string | null;
  image: string | null;
  organization: string | null;
  department: string | null;
  role: string;
  createdAt: string;
  lastLoginAt: string | null;
}

// Helper component for label-value pairs
function ProfileField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <GCPCardItem>
      <div className="flex items-center justify-between w-full">
        <span className="text-sm text-gray-600 dark:text-gray-400 min-w-[120px]">{label}</span>
        <div className="flex-1 text-right">
          {children}
        </div>
      </div>
    </GCPCardItem>
  );
}

export default function ProfilePage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    organization: "",
    department: "",
  });

  useEffect(() => {
    console.log("Auth state:", { user, loading });
    if (!loading && !user) {
      router.push("/auth/signin");
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (user) {
      console.log("User authenticated, fetching profile");
      fetchProfile();
    }
  }, [user]);

  const fetchProfile = async () => {
    try {
      console.log("Fetching profile...");

      // Get the current user's ID token
      const token = await user?.getIdToken();
      if (!token) {
        console.error("No auth token available");
        return;
      }

      const response = await fetch("/api/profile", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      console.log("Response status:", response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Profile fetch error:", errorData);
        return;
      }

      const data = await response.json();
      console.log("Profile data:", data);
      setProfile(data);
      setFormData({
        name: data.name || "",
        organization: data.organization || "",
        department: data.department || "",
      });
    } catch (error) {
      console.error("Error fetching profile:", error);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const token = await user?.getIdToken();
      if (!token) {
        console.error("No auth token available");
        return;
      }

      const response = await fetch("/api/profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const updatedProfile = await response.json();
        setProfile(updatedProfile);
        setIsEditing(false);
      }
    } catch (error) {
      console.error("Error updating profile:", error);
    } finally {
      setIsSaving(false);
    }
  };

  if (loading || !profile) {
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
                Profile Settings
              </h1>
            </div>

            {/* Profile Cards Grid */}
            <GCPCardGrid columns={2} className="mb-4">
              {/* Basic Information Card */}
              <GCPCard
                title="Basic Information"
                icon="User-Preferences"
                actions={
                  isEditing ? (
                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          setIsEditing(false);
                          setFormData({
                            name: profile.name || "",
                            organization: profile.organization || "",
                            department: profile.department || "",
                          });
                        }}
                        className="px-3 py-1 text-sm font-medium text-[#5f6368] hover:bg-[#f1f3f4] dark:text-[#9aa0a6] dark:hover:bg-[#394457] rounded transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleSave}
                        disabled={isSaving}
                        className="px-3 py-1 text-sm font-medium text-white bg-[#1a73e8] hover:bg-[#1967d2] disabled:opacity-50 rounded transition-colors"
                      >
                        {isSaving ? "Saving..." : "Save"}
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setIsEditing(true)}
                      className="px-3 py-1 text-sm font-medium text-[#1a73e8] hover:bg-[#e8f0fe] dark:hover:bg-[#394457] rounded transition-colors"
                    >
                      Edit
                    </button>
                  )
                }
              >
                <GCPCardContent>
                  {/* Avatar and Name */}
                  <div className="flex items-center space-x-4 mb-6">
                    <div className="flex-shrink-0">
                      {profile.image ? (
                        <Image
                          src={profile.image}
                          alt={profile.name || "Profile"}
                          width={64}
                          height={64}
                          className="rounded-full"
                        />
                      ) : (
                        <div className="w-16 h-16 rounded-full app-card-bg flex items-center justify-center">
                          <span className="text-xl font-medium app-text">
                            {profile.email[0].toUpperCase()}
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="flex-1">
                      <h3 className="text-lg font-medium app-text">
                        {profile.name || "Unnamed User"}
                      </h3>
                      <p className="text-sm app-text-secondary">
                        {profile.email}
                      </p>
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 mt-1">
                        {profile.role}
                      </span>
                    </div>
                  </div>

                  {/* Profile Fields */}
                  <ProfileField label="Name">
                    {isEditing ? (
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) =>
                          setFormData({ ...formData, name: e.target.value })
                        }
                        className="w-full px-3 py-1.5 rounded border app-input-border app-bg app-text text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                      />
                    ) : (
                      <span className="app-text">
                        {profile.name || "Not set"}
                      </span>
                    )}
                  </ProfileField>

                  <ProfileField label="Email">
                    <span className="app-text">{profile.email}</span>
                  </ProfileField>

                  <ProfileField label="Role">
                    <span className="app-text capitalize">
                      {profile.role.toLowerCase()}
                    </span>
                  </ProfileField>
                </GCPCardContent>
              </GCPCard>

              {/* Organization Information Card */}
              <GCPCard title="Organization" icon="Administration">
                <GCPCardContent>
                  <ProfileField label="Organization">
                    {isEditing ? (
                      <input
                        type="text"
                        value={formData.organization}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            organization: e.target.value,
                          })
                        }
                        className="w-full px-3 py-1.5 rounded border app-input-border app-bg app-text text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                      />
                    ) : (
                      <span className="app-text">
                        {profile.organization || "Not set"}
                      </span>
                    )}
                  </ProfileField>

                  <ProfileField label="Department">
                    {isEditing ? (
                      <input
                        type="text"
                        value={formData.department}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            department: e.target.value,
                          })
                        }
                        className="w-full px-3 py-1.5 rounded border app-input-border app-bg app-text text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                      />
                    ) : (
                      <span className="app-text">
                        {profile.department || "Not set"}
                      </span>
                    )}
                  </ProfileField>
                </GCPCardContent>
              </GCPCard>

              {/* Account Activity Card */}
              <GCPCard title="Account Activity" icon="Cloud-Logging">
                <GCPCardContent>
                  <ProfileField label="Member since">
                    <span className="app-text">
                      {new Date(profile.createdAt).toLocaleDateString("en-US", {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })}
                    </span>
                  </ProfileField>

                  {profile.lastLoginAt && (
                    <ProfileField label="Last login">
                      <span className="app-text">
                        {new Date(profile.lastLoginAt).toLocaleString("en-US", {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>
                    </ProfileField>
                  )}

                  <ProfileField label="Account status">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                      Active
                    </span>
                  </ProfileField>
                </GCPCardContent>
              </GCPCard>
            </GCPCardGrid>
          </div>
        </div>
      </div>
    </Layout>
  );
}
