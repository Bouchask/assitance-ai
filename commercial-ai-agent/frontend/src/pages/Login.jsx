import React, { useState } from 'react';
import { Bot, LogIn, Sparkles } from 'lucide-react';
import { useGoogleLogin } from '@react-oauth/google';

const API_BASE_URL = import.meta.env.VITE_API_URL || "";

export default function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  const googleLogin = useGoogleLogin({
    flow: 'auth-code',
    scope: 'https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/calendar',
    prompt: 'consent',
    onSuccess: async (codeResponse) => {
      setIsGoogleLoading(true);
      setError('');
      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/google`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code: codeResponse.code }),
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.error || 'Erreur de connexion avec Google');
        }
        
        onLoginSuccess(data.token, data.user);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsGoogleLoading(false);
      }
    },
    onError: (errorResponse) => {
      setError('La connexion avec Google a échoué ou a été annulée.');
      console.error(errorResponse);
    }
  });

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
              disabled={isLoading || isGoogleLoading || !email || !password}
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

          <div className="my-6 flex items-center justify-center space-x-2">
            <div className="h-px w-full bg-white/[0.05]"></div>
            <span className="text-xs font-medium text-zinc-500 uppercase tracking-wider">OU</span>
            <div className="h-px w-full bg-white/[0.05]"></div>
          </div>

          <button
            type="button"
            onClick={() => googleLogin()}
            disabled={isLoading || isGoogleLoading}
            className="flex w-full items-center justify-center gap-3 rounded-xl border border-white/[0.07] bg-black/20 px-4 py-3 text-sm font-medium text-zinc-200 transition-all hover:bg-white/[0.03] disabled:opacity-50"
          >
            {isGoogleLoading ? (
              <span className="thinking-dots"><i /><i /><i /></span>
            ) : (
              <>
                <svg className="size-5" viewBox="0 0 24 24">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                </svg>
                Continuer avec Google
              </>
            )}
          </button>
        </div>

      </div>
    </div>
  );
}
