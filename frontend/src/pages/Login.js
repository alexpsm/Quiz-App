import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, Lock, User as UserIcon, Chrome } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { PoweredByScore90 } from '../components/Score90Logo';

export default function Login() {
  const navigate = useNavigate();
  const { login, register } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [formData, setFormData] = useState({ email: '', password: '', name: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGoogleLogin = () => {
    const redirectUrl = window.location.origin + '/auth/callback';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const handleSocialLogin = (provider) => {
    setError(`${provider} login requires OAuth credentials. Please configure ${provider} App ID in settings.`);
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
    <div className="min-h-screen bg-gradient-to-br from-background via-[#1a1a2e] to-background flex items-center justify-center p-5">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md"
      >
        {/* QuizBall Logo */}
        <div className="text-center mb-8">
          <h1 className="text-6xl font-extrabold tracking-tighter uppercase text-transparent bg-clip-text bg-gradient-to-r from-neon-blue via-neon-pink to-neon-yellow mb-3">
            QuizBall
          </h1>
          <PoweredByScore90 size="md" className="justify-center mb-3" />
          <p className="text-base text-gray-300">
            Prove your <span className="text-neon-yellow font-bold">Ball Knowledge</span>
          </p>
        </div>

        {/* Auth Card */}
        <div className="bg-card border-2 border-neon-blue/30 rounded-lg p-6 shadow-2xl shadow-neon-blue/20 backdrop-blur-sm">
          <h2 className="text-2xl font-bold uppercase tracking-tight text-center mb-6 text-white">
            {isRegister ? 'Create Account' : 'Welcome Back'}
          </h2>

          {/* Social Login Buttons */}
          <div className="space-y-3 mb-6">
            <button
              onClick={handleGoogleLogin}
              data-testid="google-login-btn"
              className="w-full bg-white text-black hover:bg-gray-100 h-12 px-6 rounded-sm font-bold uppercase tracking-wider flex items-center justify-center gap-3 transition-all active:scale-95 shadow-lg hover:shadow-neon-blue"
            >
              <Chrome size={20} />
              Continue with Google
            </button>

            <button
              onClick={() => handleSocialLogin('Facebook')}
              data-testid="facebook-login-btn"
              className="w-full bg-[#1877F2] text-white hover:bg-[#166FE5] h-12 px-6 rounded-sm font-bold uppercase tracking-wider flex items-center justify-center gap-3 transition-all active:scale-95 shadow-lg"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              Continue with Facebook
            </button>

            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleSocialLogin('X')}
                data-testid="x-login-btn"
                className="bg-black text-white hover:bg-gray-900 h-12 px-4 rounded-sm font-bold uppercase tracking-wider flex items-center justify-center gap-2 transition-all active:scale-95 shadow-lg border border-white/20"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
                X (Twitter)
              </button>

              <button
                onClick={() => handleSocialLogin('Apple')}
                data-testid="apple-login-btn"
                className="bg-black text-white hover:bg-gray-900 h-12 px-4 rounded-sm font-bold uppercase tracking-wider flex items-center justify-center gap-2 transition-all active:scale-95 shadow-lg border border-white/20"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                  <path d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701"/>
                </svg>
                Apple
              </button>
            </div>
          </div>

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
                    className="w-full bg-black/50 border-2 border-neon-blue/30 focus:border-neon-pink focus:ring-2 focus:ring-neon-pink/50 h-12 rounded-sm text-white placeholder:text-white/30 pl-11 pr-4 outline-none transition-all"
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
                  className="w-full bg-black/50 border-2 border-neon-blue/30 focus:border-neon-pink focus:ring-2 focus:ring-neon-pink/50 h-12 rounded-sm text-white placeholder:text-white/30 pl-11 pr-4 outline-none transition-all"
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
                  className="w-full bg-black/50 border-2 border-neon-blue/30 focus:border-neon-pink focus:ring-2 focus:ring-neon-pink/50 h-12 rounded-sm text-white placeholder:text-white/30 pl-11 pr-4 outline-none transition-all"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {error && (
              <div className="bg-destructive/10 border-2 border-destructive rounded-sm p-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <button
              type="submit"
              data-testid="submit-btn"
              disabled={loading}
              className="w-full bg-gradient-to-r from-neon-blue to-neon-pink hover:from-neon-pink hover:to-neon-yellow h-12 px-6 rounded-sm font-bold uppercase tracking-wider shadow-neon-blue hover:shadow-neon-pink transition-all active:scale-95 disabled:opacity-50 text-white"
            >
              {loading ? 'Processing...' : isRegister ? 'Create Account' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => setIsRegister(!isRegister)}
              className="text-sm text-neon-blue hover:text-neon-pink transition-colors"
            >
              {isRegister ? 'Already have an account? Sign in' : "Don't have an account? Register"}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
