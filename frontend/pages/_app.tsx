import type { AppProps } from "next/app";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import { useEffect } from "react";
import { useAuthStore } from "@/store/authStore";
import "@/styles/globals.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 30000 },
  },
});

export default function App({ Component, pageProps }: AppProps) {
  const fetchMe = useAuthStore((s) => s.fetchMe);

  useEffect(() => {
    if (typeof window !== "undefined" && localStorage.getItem("access_token")) {
      fetchMe();
    }
  }, [fetchMe]);

  return (
    <QueryClientProvider client={queryClient}>
      <Component {...pageProps} />
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 5000,
          style: {
            background: "#1f2937",
            color: "#f3f4f6",
            border: "1px solid #374151",
          },
        }}
      />
    </QueryClientProvider>
  );
}
