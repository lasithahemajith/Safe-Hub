import Head from "next/head";
import { useRouter } from "next/router";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import Navbar from "@/components/layout/Navbar";
import { incidentService } from "@/services/incidentService";
import { useAuthStore } from "@/store/authStore";
import Link from "next/link";
import { useEffect, useState } from "react";
import { MapPin } from "lucide-react";

const schema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters"),
  description: z.string().min(20, "Description must be at least 20 characters"),
  disaster_type: z.enum(["earthquake", "flood", "landslide", "storm", "fire", "other"]),
  severity: z.enum(["low", "medium", "high", "critical"]),
  latitude: z.number({ invalid_type_error: "Latitude is required" }).min(-90).max(90),
  longitude: z.number({ invalid_type_error: "Longitude is required" }).min(-180).max(180),
});

type FormData = z.infer<typeof schema>;

export default function ReportIncident() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [locating, setLocating] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { severity: "medium", disaster_type: "flood" },
  });

  const lat = watch("latitude");
  const lon = watch("longitude");

  useEffect(() => {
    if (!isAuthenticated) router.push("/login");
  }, [isAuthenticated, router]);

  const detectLocation = () => {
    if (!navigator.geolocation) {
      toast.error("Geolocation not supported");
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setValue("latitude", pos.coords.latitude);
        setValue("longitude", pos.coords.longitude);
        setLocating(false);
        toast.success("Location detected!");
      },
      () => {
        toast.error("Could not detect location");
        setLocating(false);
      }
    );
  };

  const onSubmit = async (data: FormData) => {
    try {
      const incident = await incidentService.create(data);
      toast.success("Incident reported successfully!");
      router.push(`/incidents/${incident.id}`);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      toast.error(error.response?.data?.detail || "Failed to report incident");
    }
  };

  return (
    <>
      <Head><title>Report Incident – SafeNZ</title></Head>
      <Navbar />
      <div className="min-h-[calc(100vh-64px)] bg-gray-50 dark:bg-gray-900 py-8 px-4">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-2xl font-bold mb-6">Report a Disaster Incident</h1>
          <div className="card">
            <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5">
              <div>
                <label className="block text-sm font-medium mb-1">Title <span className="text-red-500">*</span></label>
                <input {...register("title")} className="input-field" placeholder="e.g., Flooding on State Highway 1" />
                {errors.title && <p className="text-red-500 text-xs mt-1">{errors.title.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Description <span className="text-red-500">*</span></label>
                <textarea
                  {...register("description")}
                  rows={4}
                  className="input-field resize-none"
                  placeholder="Describe the incident in detail…"
                />
                {errors.description && <p className="text-red-500 text-xs mt-1">{errors.description.message}</p>}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Disaster Type <span className="text-red-500">*</span></label>
                  <select {...register("disaster_type")} className="input-field">
                    <option value="earthquake">🌍 Earthquake</option>
                    <option value="flood">🌊 Flood</option>
                    <option value="landslide">🏔️ Landslide</option>
                    <option value="storm">⛈️ Storm</option>
                    <option value="fire">🔥 Fire</option>
                    <option value="other">⚠️ Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Severity <span className="text-red-500">*</span></label>
                  <select {...register("severity")} className="input-field">
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-sm font-medium">Location <span className="text-red-500">*</span></label>
                  <button
                    type="button"
                    onClick={detectLocation}
                    disabled={locating}
                    className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700"
                  >
                    <MapPin className="w-3 h-3" />
                    {locating ? "Detecting…" : "Use my location"}
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <input
                      type="number"
                      step="any"
                      {...register("latitude", { valueAsNumber: true })}
                      className="input-field"
                      placeholder="Latitude (e.g., -41.29)"
                    />
                    {errors.latitude && <p className="text-red-500 text-xs mt-1">{errors.latitude.message}</p>}
                  </div>
                  <div>
                    <input
                      type="number"
                      step="any"
                      {...register("longitude", { valueAsNumber: true })}
                      className="input-field"
                      placeholder="Longitude (e.g., 174.78)"
                    />
                    {errors.longitude && <p className="text-red-500 text-xs mt-1">{errors.longitude.message}</p>}
                  </div>
                </div>
                {lat && lon && (
                  <p className="text-xs text-gray-500 mt-1">
                    Location: {lat.toFixed(6)}, {lon.toFixed(6)}
                  </p>
                )}
              </div>

              <div className="flex gap-3 pt-2">
                <button type="submit" disabled={isSubmitting} className="btn-primary flex-1">
                  {isSubmitting ? "Reporting…" : "Report Incident"}
                </button>
                <Link href="/incidents" className="btn-secondary text-center flex-1">
                  Cancel
                </Link>
              </div>
            </form>
          </div>
        </div>
      </div>
    </>
  );
}
