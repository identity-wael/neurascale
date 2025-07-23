'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../components/AuthProvider';

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!user) {
      router.push('/login');
    }
  }, [user, router]);

  if (!user) return null;

  const handleLogout = async () => {
    await logout();
    // Navigation handled in AuthProvider
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen space-y-4">
      <h1 className="text-2xl font-bold">Welcome, {user.name || user.email}!</h1>
      <button onClick={handleLogout} className="rounded px-4 py-2 bg-blue-500 text-white">
        Logout
      </button>
    </div>
  );
}
