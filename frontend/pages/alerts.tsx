import Head from "next/head";
import { useQuery } from "@tanstack/react-query";
import Navbar from "@/components/layout/Navbar";
import SeverityBadge from "@/components/ui/SeverityBadge";
import { alertService } from "@/services/dataService";
import { formatDistanceToNow } from "date-fns";
import { Bell } from "lucide-react";

export default function AlertsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["alerts"],
    queryFn: () => alertService.list({ per_page: 50 }),
  });

  const alerts = data?.items || [];

  return (
    <>
      <Head><title>Emergency Alerts – SafeNZ</title></Head>
      <Navbar />
      <div className="min-h-[calc(100vh-64px)] bg-gray-50 dark:bg-gray-900 py-8 px-4">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center gap-3 mb-6">
            <Bell className="w-6 h-6 text-red-500" />
            <h1 className="text-2xl font-bold">Emergency Alerts</h1>
          </div>

          {isLoading ? (
            <div className="flex justify-center py-20">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
            </div>
          ) : alerts.length === 0 ? (
            <div className="text-center py-20 text-gray-500">
              <Bell className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>No active alerts</p>
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              {(alerts as Array<{
                id: string;
                title: string;
                message: string;
                region: string;
                severity: "low" | "medium" | "high" | "critical";
                created_at: string;
              }>).map((alert) => (
                <div
                  key={alert.id}
                  className={`card border-l-4 ${
                    alert.severity === "critical"
                      ? "border-red-500"
                      : alert.severity === "high"
                      ? "border-orange-500"
                      : alert.severity === "medium"
                      ? "border-yellow-500"
                      : "border-green-500"
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h2 className="font-bold text-lg">{alert.title}</h2>
                    <SeverityBadge severity={alert.severity} />
                  </div>
                  <p className="text-gray-700 dark:text-gray-300 mb-2">{alert.message}</p>
                  <div className="flex items-center gap-3 text-xs text-gray-500">
                    <span>📍 {alert.region}</span>
                    <span>{formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
