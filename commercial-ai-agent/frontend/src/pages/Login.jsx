import React, { useState } from 'react';
import { Bot, LogIn, Sparkles } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || "";

export default function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Erreur de connexion');
      }

      onLoginSuccess(data.token, data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#212121] px-4">
      <div className="w-full max-w-[400px]">
        
        {/* Header */}
        <div className="mb-10 text-center">
          <div className="mx-auto mb-4 grid size-12 place-items-center rounded-xl bg-zinc-100 text-zinc-900 shadow-xl">
            <Sparkles className="size-6" />
          </div>
          <h1 className="text-2xl font-semibold text-zinc-100">Bienvenue</h1>
          <p className="mt-2 text-sm text-zinc-400">Connectez-vous pour accéder à Commercial AI</p>
        </div>

        {/* Form */}
        <div className="rounded-2xl border border-white/[0.07] bg-[#171717] p-8 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="rounded-xl bg-red-500/10 p-3 text-sm text-red-500 border border-red-500/20">
                {error}
              </div>
            )}
            
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-zinc-300" htmlFor="email">
                Adresse email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@atlas.com"
                required
                className="w-full rounded-xl border border-white/[0.07] bg-black/20 px-4 py-2.5 text-sm text-zinc-100 placeholder:text-zinc-600 focus:border-emerald-500/50 focus:outline-none focus:ring-1 focus:ring-emerald-500/50 transition-colors"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium text-zinc-300" htmlFor="password">
                Mot de passe
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full rounded-xl border border-white/[0.07] bg-black/20 px-4 py-2.5 text-sm text-zinc-100 placeholder:text-zinc-600 focus:border-emerald-500/50 focus:outline-none focus:ring-1 focus:ring-emerald-500/50 transition-colors"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading || !email || !password}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-3 text-sm font-medium text-white transition-all hover:bg-emerald-500 disabled:opacity-50 disabled:hover:bg-emerald-600"
            >
              {isLoading ? (
                <span className="thinking-dots"><i /><i /><i /></span>
              ) : (
                <>
                  Se connecter
                  <LogIn className="size-4" />
                </>
              )}
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}
