import Head from "next/head";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Navbar from "@/components/layout/Navbar";
import { shelterService } from "@/services/dataService";
import { MapPin, Phone, Users } from "lucide-react";
import toast from "react-hot-toast";

export default function SheltersPage() {
  const [lat, setLat] = useState<number | null>(null);
  const [lon, setLon] = useState<number | null>(null);
  const [locating, setLocating] = useState(false);

  const { data: allShelters, isLoading: loadingAll } = useQuery({
    queryKey: ["shelters"],
    queryFn: () => shelterService.list(),
    enabled: !lat,
  });

  const { data: nearbyShelters, isLoading: loadingNearby } = useQuery({
    queryKey: ["shelters", "nearby", lat, lon],
    queryFn: () => shelterService.getNearby(lat!, lon!),
    enabled: !!lat && !!lon,
  });

  const shelters = lat ? (nearbyShelters || []) : (allShelters || []);
  const isLoading = lat ? loadingNearby : loadingAll;

  const findNearest = () => {
    if (!navigator.geolocation) {
      toast.error("Geolocation not supported");
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLat(pos.coords.latitude);
        setLon(pos.coords.longitude);
        setLocating(false);
        toast.success("Finding nearest shelters…");
      },
      () => {
        toast.error("Could not detect location");
        setLocating(false);
      }
    );
  };

  return (
    <>
      <Head><title>Shelters – SafeNZ</title></Head>
      <Navbar />
      <div className="min-h-[calc(100vh-64px)] bg-gray-50 dark:bg-gray-900 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold">Emergency Shelters</h1>
            <button
              onClick={findNearest}
              disabled={locating}
              className="btn-primary flex items-center gap-2"
            >
              <MapPin className="w-4 h-4" />
              {locating ? "Locating…" : "Find Nearest"}
            </button>
          </div>

          {lat && (
            <div className="mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 rounded-lg p-3 text-sm text-blue-700 dark:text-blue-300">
              Showing shelters near your location. {shelters.length} shelter(s) found.
            </div>
          )}

          {isLoading ? (
            <div className="flex justify-center py-20">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
            </div>
          ) : shelters.length === 0 ? (
            <div className="text-center py-20 text-gray-500">No shelters found</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {shelters.map((shelter) => (
                <div key={shelter.id} className="card border border-gray-200 dark:border-gray-700">
                  <div className="flex items-start justify-between mb-2">
                    <h2 className="font-semibold">{shelter.name}</h2>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      shelter.is_active
                        ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                        : "bg-red-100 text-red-700"
                    }`}>
                      {shelter.is_active ? "Open" : "Closed"}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{shelter.address}</p>
                  <div className="flex flex-col gap-1 text-sm">
                    <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                      <Users className="w-4 h-4" />
                      <span>{shelter.available_space} / {shelter.capacity} spaces available</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                      <Phone className="w-4 h-4" />
                      <a href={`tel:${shelter.contact_number}`} className="text-blue-600 hover:underline">
                        {shelter.contact_number}
                      </a>
                    </div>
                    {shelter.distance_km !== undefined && (
                      <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                        <MapPin className="w-4 h-4" />
                        <span>{shelter.distance_km.toFixed(1)} km away</span>
                      </div>
                    )}
                  </div>
                  <div className="mt-3 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${(shelter.available_space / shelter.capacity) * 100}%` }}
                    />
                  </div>
                  <a
                    href={`https://www.google.com/maps/dir/?api=1&destination=${shelter.latitude},${shelter.longitude}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-3 btn-secondary text-sm text-center block"
                  >
                    Get Directions
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
