import Head from "next/head";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";
import Navbar from "@/components/layout/Navbar";
import { authService } from "@/services/authService";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

const schema = z.object({
  email: z.string().email("Invalid email"),
});

type FormData = z.infer<typeof schema>;

export default function ForgotPassword() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    try {
      await authService.requestPasswordReset(data.email);
      toast.success("If your email is registered, you will receive a reset link shortly.");
    } catch {
      toast.error("An error occurred. Please try again.");
    }
  };

  return (
    <>
      <Head><title>Forgot Password – SafeNZ</title></Head>
      <Navbar />
      <div className="min-h-[calc(100vh-64px)] bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
        <div className="card w-full max-w-md">
          <h1 className="text-2xl font-bold mb-2 text-center">Reset Password</h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm text-center mb-6">
            Enter your email address and we&apos;ll send you a reset link.
          </p>
          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Email Address</label>
              <input type="email" {...register("email")} className="input-field" placeholder="you@example.com" />
              {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
            </div>
            <button type="submit" disabled={isSubmitting} className="btn-primary w-full">
              {isSubmitting ? "Sending…" : "Send Reset Link"}
            </button>
          </form>
        </div>
      </div>
    </>
  );
}
