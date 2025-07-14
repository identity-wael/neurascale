import Layout from "@/components/layout/Layout";
import Dashboard from "@/components/dashboard/Dashboard";
import ProtectedRoute from "@/components/auth/ProtectedRoute";

export default function Home() {
  return (
    <ProtectedRoute>
      <Layout>
        <Dashboard />
      </Layout>
    </ProtectedRoute>
  );
}
