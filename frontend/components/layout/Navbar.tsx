import Link from "next/link";
import { useRouter } from "next/router";
import { Shield, Menu, X, Moon, Sun, Bell } from "lucide-react";
import { useState, useEffect } from "react";
import { useAuthStore } from "@/store/authStore";

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const router = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("theme");
    if (saved === "dark" || (!saved && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
      document.documentElement.classList.add("dark");
      setDark(true);
    }
  }, []);

  const toggleDark = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("theme", next ? "dark" : "light");
  };

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  const navLinks = [
    { href: "/map", label: "Map" },
    { href: "/incidents", label: "Incidents" },
    { href: "/alerts", label: "Alerts" },
    { href: "/shelters", label: "Shelters" },
  ];

  return (
    <nav className="bg-blue-900 dark:bg-gray-900 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
        <Link href="/" className="flex items-center gap-2 font-bold text-xl">
          <Shield className="w-6 h-6 text-blue-300" />
          <span>SafeNZ</span>
        </Link>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-6">
          {navLinks.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={`hover:text-blue-300 transition-colors ${router.pathname === l.href ? "text-blue-300 font-semibold" : ""}`}
            >
              {l.label}
            </Link>
          ))}
        </div>

        <div className="hidden md:flex items-center gap-3">
          <button onClick={toggleDark} className="p-2 rounded-lg hover:bg-blue-800 dark:hover:bg-gray-700">
            {dark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
          {isAuthenticated ? (
            <>
              {(user?.role === "admin" || user?.role === "responder") && (
                <Link href="/dashboard" className="hover:text-blue-300">Dashboard</Link>
              )}
              <span className="text-blue-300 text-sm">{user?.name}</span>
              <button onClick={handleLogout} className="btn-secondary text-sm py-1 px-3">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="hover:text-blue-300 text-sm">Login</Link>
              <Link href="/register" className="btn-primary text-sm py-1 px-4">
                Sign Up
              </Link>
            </>
          )}
        </div>

        {/* Mobile menu button */}
        <button className="md:hidden p-2" onClick={() => setMenuOpen(!menuOpen)}>
          {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden bg-blue-800 dark:bg-gray-800 px-4 py-4 flex flex-col gap-3">
          {navLinks.map((l) => (
            <Link key={l.href} href={l.href} className="hover:text-blue-300" onClick={() => setMenuOpen(false)}>
              {l.label}
            </Link>
          ))}
          {isAuthenticated ? (
            <>
              <Link href="/dashboard" onClick={() => setMenuOpen(false)}>Dashboard</Link>
              <button onClick={handleLogout} className="text-left text-red-300">Logout</button>
            </>
          ) : (
            <>
              <Link href="/login" onClick={() => setMenuOpen(false)}>Login</Link>
              <Link href="/register" onClick={() => setMenuOpen(false)}>Sign Up</Link>
            </>
          )}
        </div>
      )}
    </nav>
  );
}
