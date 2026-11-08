"use client";

import React, { useState } from "react";
import { Mail, Lock, Loader2, AlertCircle, CheckCircle2 } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL;
export default function LoginForm() {
  const [email, setEmail] = useState("admin@ad.min");
  const [password, setPassword] = useState("admin");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // 1. Validation for empty email or password
    if (!email.trim() || !password.trim()) {
      setError("Please enter both email and password.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/users/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({ username: email, password: password }),
      });

      const data = await response.json();

      if (!response.ok) {
        // 2. Handling specific error cases from server
        if (response.status === 401 || response.status === 403) {
          setError("Invalid email or password. Please try again.");
        } else {
          setError(
            data.message ||
              "An error occurred on the server. Please try again later.",
          );
        }
        setLoading(false);
        return;
      }

      // 3. Save the JWT token
      if (data.access_token || data.token) {
        const token = data.access_token || data.token;
        document.cookie = `jwt_token=${token}; path=/`;
        setSuccess(true);

        // Redirect after a short delay
        setTimeout(() => {
          window.location.href = "/dashboard";
        }, 1500);
      } else {
        setError("Login successful, but no token was received.");
        setLoading(false);
      }
    } catch (err) {
      // 4. Handling network or unexpected errors
      setError(
        "Unable to connect to the server. Please check your internet connection.",
      );
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md p-8 bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 animate-in fade-in zoom-in duration-500">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-text-primary tracking-tight mb-2">
          Welcome Back
        </h1>
        <p className="text-text-secondary">
          Please enter your details to sign in
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Error Message */}
        {error && (
          <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-100 text-red-600 rounded-2xl animate-in slide-in-from-top-2 duration-300">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="flex items-center gap-3 p-4 bg-emerald-50 border border-emerald-100 text-emerald-600 rounded-2xl animate-in slide-in-from-top-2 duration-300">
            <CheckCircle2 className="w-5 h-5 shrink-0" />
            <p className="text-sm font-medium">
              Login successful! Redirecting...
            </p>
          </div>
        )}

        <div className="space-y-2">
          <label
            htmlFor="email"
            className="text-sm font-semibold text-text-primary ml-1">
            Email Address
          </label>
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-text-secondary group-focus-within:text-text-active transition-colors">
              <Mail className="w-5 h-5" />
            </div>
            <input
              id="email"
              type="email"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full pl-12 pr-4 py-3.5 bg-bg-light border border-border rounded-2xl outline-none focus:ring-2 focus:ring-text-active/20 focus:border-text-active transition-all"
              required
            />
          </div>
        </div>

        <div className="space-y-2">
          <label
            htmlFor="password"
            className="text-sm font-semibold text-text-primary ml-1">
            Password
          </label>
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-text-secondary group-focus-within:text-text-active transition-colors">
              <Lock className="w-5 h-5" />
            </div>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full pl-12 pr-4 py-3.5 bg-bg-light border border-border rounded-2xl outline-none focus:ring-2 focus:ring-text-active/20 focus:border-text-active transition-all"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || success}
          className="w-full py-4 px-6 bg-bg-active text-white font-bold rounded-2xl shadow-lg shadow-text-active/30 hover:shadow-xl hover:shadow-text-active/40 hover:-translate-y-0.5 active:translate-y-0 transition-all disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:translate-y-0 flex items-center justify-center gap-2">
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Signing in...
            </>
          ) : (
            "Sign In"
          )}
        </button>

        <div className="text-center pt-2">
          <p className="text-sm text-text-secondary">
            Use{" "}
            <span className="text-text-active font-semibold">admin@ad.min</span>{" "}
            email and{" "}
            <span className="text-text-active font-semibold">admin</span>{" "}
            password to login.
          </p>
        </div>
      </form>
    </div>
  );
}
