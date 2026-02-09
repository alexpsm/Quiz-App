import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { users, clubs } from '../lib/api';
import { useAuth } from '../context/AuthContext';

const AVATAR_SEEDS = ['Felix', 'Aneka', 'Garfield', 'Boots', 'Tigger', 'Milo', 'Simba', 'Luna'];

export default function Onboarding() {
  const navigate = useNavigate();
  const location = useLocation();
  const { checkAuth } = useAuth();
  const [username, setUsername] = useState('');
  const [selectedAvatar, setSelectedAvatar] = useState(0);
  const [favoriteClub, setFavoriteClub] = useState('');
  const [clubsByLeague, setClubsByLeague] = useState({});
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadClubs();
  }, []);

  const loadClubs = async () => {
    try {
      const response = await clubs.getAll();
      setClubsByLeague(response.data);
    } catch (error) {
      console.error('Failed to load clubs:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const avatarUrl = `https://api.dicebear.com/7.x/avataaars/svg?seed=${AVATAR_SEEDS[selectedAvatar]}`;
      await users.updateProfile({ username, avatar: avatarUrl, favorite_club: favoriteClub });
      await checkAuth();
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-5">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <h1 className="text-4xl font-extrabold tracking-tighter uppercase text-primary mb-2">
            Complete Profile
          </h1>
          <p className="text-sm text-gray-400">Choose your username and avatar</p>
        </div>

        <div className="bg-card border border-white/10 rounded-lg p-6 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Avatar Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-4 uppercase tracking-wide">
                Select Avatar
              </label>
              <div className="grid grid-cols-4 gap-3">
                {AVATAR_SEEDS.map((seed, index) => (
                  <button
                    key={seed}
                    type="button"
                    onClick={() => setSelectedAvatar(index)}
                    className={`aspect-square rounded-lg border-2 transition-all ${
                      selectedAvatar === index
                        ? 'border-primary shadow-[0_0_20px_-5px_rgba(251,191,36,0.5)]'
                        : 'border-white/20 hover:border-white/40'
                    }`}
                  >
                    <img
                      src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${seed}`}
                      alt={`Avatar ${index + 1}`}
                      className="w-full h-full rounded-lg"
                    />
                  </button>
                ))}
              </div>
            </div>

            {/* Username Input */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">
                Username
              </label>
              <input
                type="text"
                name="username"
                data-testid="username-input"
                value={username}
                onChange={(e) => setUsername(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
                className="w-full bg-black/50 border border-white/20 focus:border-primary focus:ring-1 focus:ring-primary h-12 rounded-sm text-white placeholder:text-white/30 px-4 outline-none"
                placeholder="footballmaster"
                required
                minLength={3}
                maxLength={20}
              />
              <p className="text-xs text-gray-500 mt-2">3-20 characters, lowercase letters, numbers, and underscores only</p>
            </div>

            {/* Favorite Club Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">
                Choose Your Club
              </label>
              <select
                data-testid="club-select"
                value={favoriteClub}
                onChange={(e) => setFavoriteClub(e.target.value)}
                className="w-full bg-black/50 border border-white/20 focus:border-primary focus:ring-1 focus:ring-primary h-12 rounded-sm text-white px-4 outline-none"
                required
              >
                <option value="">Select your favorite club...</option>
                {Object.entries(clubsByLeague).map(([league, clubs]) => (
                  <optgroup key={league} label={league}>
                    {clubs.map((club) => (
                      <option key={club} value={club}>
                        {club}
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-2">This will unlock exclusive Club Challenge mode and club-specific leaderboards</p>
            </div>

            {error && (
              <div className="bg-destructive/10 border border-destructive/50 rounded-sm p-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <button
              type="submit"
              data-testid="continue-btn"
              disabled={loading || !username || username.length < 3}
              className="w-full bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-6 rounded-sm font-bold uppercase tracking-wider shadow-[0_0_15px_rgba(251,191,36,0.3)] transition-all active:scale-95 disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Continue to QuizBall'}
            </button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}