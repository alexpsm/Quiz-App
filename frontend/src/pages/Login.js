import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, Lock, User as UserIcon, Chrome } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const navigate = useNavigate();
  const { login, register } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [formData, setFormData] = useState({ email: '', password: '', name: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGoogleLogin = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/auth/callback';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isRegister) {
        await register(formData);
        navigate('/onboarding');
      } else {
        await login({ email: formData.email, password: formData.password });
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-5">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md"
      >
        {/* Score90 Logo */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-extrabold tracking-tighter uppercase text-primary mb-2">
            QuizBall
          </h1>
          <p className="text-sm text-gray-400 uppercase tracking-wider">Score90 Football Trivia</p>
        </div>

        {/* Auth Card */}
        <div className="bg-card border border-white/10 rounded-lg p-6 shadow-2xl">
          <h2 className="text-2xl font-bold uppercase tracking-tight text-center mb-6">
            {isRegister ? 'Create Account' : 'Welcome Back'}
          </h2>

          {/* Google Login */}
          <button
            onClick={handleGoogleLogin}
            data-testid="google-login-btn"
            className="w-full bg-white text-black hover:bg-gray-100 h-12 px-6 rounded-sm font-bold uppercase tracking-wider flex items-center justify-center gap-3 transition-all active:scale-95 mb-6"
          >
            <Chrome size={20} />
            Continue with Google
          </button>

          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/10"></div>
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-gray-500">Or</span>
            </div>
          </div>

          {/* Email/Password Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegister && (
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Name</label>
                <div className="relative">
                  <UserIcon className="absolute left-3 top-3 text-gray-500" size={20} />
                  <input
                    type="text"
                    data-testid="register-name-input"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full bg-black/50 border border-white/20 focus:border-primary focus:ring-1 focus:ring-primary h-12 rounded-sm text-white placeholder:text-white/30 pl-11 pr-4 outline-none"
                    placeholder="Your name"
                    required
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 text-gray-500" size={20} />
                <input
                  type="email"
                  data-testid="email-input"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full bg-black/50 border border-white/20 focus:border-primary focus:ring-1 focus:ring-primary h-12 rounded-sm text-white placeholder:text-white/30 pl-11 pr-4 outline-none"
                  placeholder="your@email.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 text-gray-500" size={20} />
                <input
                  type="password"
                  data-testid="password-input"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full bg-black/50 border border-white/20 focus:border-primary focus:ring-1 focus:ring-primary h-12 rounded-sm text-white placeholder:text-white/30 pl-11 pr-4 outline-none"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {error && (
              <div className="bg-destructive/10 border border-destructive/50 rounded-sm p-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <button
              type="submit"
              data-testid="submit-btn"
              disabled={loading}
              className="w-full bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-6 rounded-sm font-bold uppercase tracking-wider shadow-[0_0_15px_rgba(251,191,36,0.3)] transition-all active:scale-95 disabled:opacity-50"
            >
              {loading ? 'Processing...' : isRegister ? 'Create Account' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => setIsRegister(!isRegister)}
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              {isRegister ? 'Already have an account? Sign in' : "Don't have an account? Register"}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}