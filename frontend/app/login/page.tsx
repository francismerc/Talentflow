"use client";

import { useState, type FormEvent } from "react";
import { ArrowRight, LockKeyhole, Sparkles } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/components/auth/auth-provider";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { signIn } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await signIn(email.trim(), password);
      const nextPath = searchParams.get("next");
      router.replace(nextPath?.startsWith("/") ? nextPath : "/");
      router.refresh();
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to sign in.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="grid min-h-screen bg-slate-50 lg:grid-cols-[1.1fr_0.9fr]">
      <section className="hidden overflow-hidden bg-primary p-12 text-white lg:flex lg:flex-col">
        <div className="flex items-center gap-2 text-lg font-bold">
          <Sparkles className="h-5 w-5 text-blue-400" />
          TalentFlow AI
        </div>
        <div className="my-auto max-w-xl">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-300">
            Recruitment intelligence
          </p>
          <h1 className="mt-5 text-5xl font-bold leading-tight">
            Move from application to decision with clarity.
          </h1>
          <p className="mt-6 text-lg leading-8 text-slate-300">
            Review candidates, manage openings, and keep every recruiter action
            accountable in one secure workspace.
          </p>
        </div>
        <p className="text-xs text-slate-500">
          AI recommendations remain reviewable and recruiter-controlled.
        </p>
      </section>

      <section className="grid place-items-center p-5 sm:p-10">
        <div className="w-full max-w-md">
          <div className="mb-8 flex items-center gap-2 text-lg font-bold text-primary lg:hidden">
            <Sparkles className="h-5 w-5 text-accent" />
            TalentFlow AI
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card sm:p-8">
            <span className="grid h-11 w-11 place-items-center rounded-xl bg-blue-50 text-accent">
              <LockKeyhole className="h-5 w-5" />
            </span>
            <h2 className="mt-5 text-2xl font-bold tracking-tight text-primary">
              Recruiter sign in
            </h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              Use the recruiter account created by your TalentFlow administrator.
            </p>

            <form className="mt-7 space-y-4" onSubmit={handleSubmit}>
              <label className="block text-xs font-semibold text-slate-600">
                Email address
                <input
                  required
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="focus-ring mt-1.5 h-11 w-full rounded-lg border border-slate-200 px-3 text-sm"
                  placeholder="recruiter@company.com"
                />
              </label>
              <label className="block text-xs font-semibold text-slate-600">
                Password
                <input
                  required
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  className="focus-ring mt-1.5 h-11 w-full rounded-lg border border-slate-200 px-3 text-sm"
                  placeholder="Enter your password"
                />
              </label>
              {error ? (
                <p className="rounded-lg border border-red-100 bg-red-50 px-3 py-2.5 text-xs text-red-700">
                  {error}
                </p>
              ) : null}
              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting ? "Signing in..." : "Sign in"}
                {!submitting ? <ArrowRight className="h-4 w-4" /> : null}
              </Button>
            </form>
          </div>
          <p className="mt-5 text-center text-xs text-slate-400">
            New recruiter accounts are created in Supabase by an administrator.
          </p>
        </div>
      </section>
    </main>
  );
}
