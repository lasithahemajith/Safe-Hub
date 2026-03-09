import Head from "next/head";
import Link from "next/link";
import Navbar from "@/components/layout/Navbar";
import { AlertTriangle, Map, Bell, Users, Shield } from "lucide-react";

export default function Home() {
  return (
    <>
      <Head>
        <title>SafeNZ – Disaster Incident Reporting Platform</title>
        <meta name="description" content="New Zealand's real-time disaster reporting and emergency management platform" />
      </Head>
      <Navbar />
      <main className="min-h-screen bg-gradient-to-b from-blue-900 to-blue-700 dark:from-gray-900 dark:to-gray-800">
        {/* Hero */}
        <section className="max-w-6xl mx-auto px-4 py-20 text-center text-white">
          <div className="flex justify-center mb-6">
            <Shield className="w-16 h-16 text-blue-300" />
          </div>
          <h1 className="text-5xl font-bold mb-4">SafeNZ</h1>
          <p className="text-xl text-blue-200 mb-8 max-w-2xl mx-auto">
            New Zealand&apos;s real-time disaster incident reporting and emergency management platform.
            Report incidents, find shelters, and stay informed.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/map" className="btn-primary text-lg px-8 py-3">
              View Disaster Map
            </Link>
            <Link href="/incidents/report" className="bg-white text-blue-900 hover:bg-blue-50 font-semibold py-3 px-8 rounded-lg transition-colors text-lg">
              Report Incident
            </Link>
          </div>
        </section>

        {/* Features */}
        <section className="max-w-6xl mx-auto px-4 pb-20 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            {
              icon: <AlertTriangle className="w-8 h-8 text-red-400" />,
              title: "Report Incidents",
              desc: "Report earthquakes, floods, fires and other disasters with photos and GPS location.",
              href: "/incidents/report",
            },
            {
              icon: <Map className="w-8 h-8 text-green-400" />,
              title: "Live Disaster Map",
              desc: "View all active incidents on an interactive map with severity indicators.",
              href: "/map",
            },
            {
              icon: <Bell className="w-8 h-8 text-yellow-400" />,
              title: "Emergency Alerts",
              desc: "Receive real-time alerts via email, SMS, and in-app notifications.",
              href: "/alerts",
            },
            {
              icon: <Users className="w-8 h-8 text-blue-400" />,
              title: "Find Shelters",
              desc: "Locate the nearest emergency shelters with availability information.",
              href: "/shelters",
            },
          ].map((feature) => (
            <Link
              key={feature.title}
              href={feature.href}
              className="card bg-white/10 backdrop-blur border border-white/20 text-white hover:bg-white/20 transition-all cursor-pointer"
            >
              <div className="mb-3">{feature.icon}</div>
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-blue-200 text-sm">{feature.desc}</p>
            </Link>
          ))}
        </section>
      </main>
    </>
  );
}
