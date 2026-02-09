import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Globe, Phone, Calendar } from 'lucide-react';
import { users, clubs } from '../lib/api';
import { PoweredByScore90 } from '../components/Score90Logo';
import { useAuth } from '../context/AuthContext';

const AVATAR_SEEDS = ['Felix', 'Aneka', 'Garfield', 'Boots', 'Tigger', 'Milo', 'Simba', 'Luna'];

export default function Onboarding() {
  const navigate = useNavigate();
  const location = useLocation();
  const { checkAuth } = useAuth();
  const [username, setUsername] = useState('');
  const [selectedAvatar, setSelectedAvatar] = useState(0);
  const [favoriteClub, setFavoriteClub] = useState('');
  const [country, setCountry] = useState('');
  const [age, setAge] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
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
      await users.updateProfile({
        username,
        avatar: avatarUrl,
        favorite_club: favoriteClub,
        country: country || undefined,
        age: age ? parseInt(age) : undefined,
        phone_number: phoneNumber || undefined,
      });
      await checkAuth();
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-[#1a1a2e] to-background flex items-center justify-center p-5">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <h1 className="text-5xl font-extrabold tracking-tighter uppercase text-transparent bg-clip-text bg-gradient-to-r from-neon-blue via-neon-pink to-neon-yellow mb-3">
            QuizBall
          </h1>
          <PoweredByScore90 size="md" className="justify-center mb-3" />
          <p className="text-base text-gray-300">
            Prove your <span className="text-neon-yellow font-bold">Ball Knowledge</span>
          </p>
        </div>

        <div className="bg-card border-2 border-neon-blue/30 rounded-lg p-6 shadow-2xl shadow-neon-blue/20 backdrop-blur-sm">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Avatar Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-3 uppercase tracking-wide">
                Select Avatar
              </label>
              <div className="grid grid-cols-4 gap-3">
                {AVATAR_SEEDS.map((seed, index) => (
                  <button
                    key={seed}
                    type="button"
                    onClick={() => setSelectedAvatar(index)}
                    data-testid={`avatar-${index}`}
                    className={`aspect-square rounded-lg border-2 transition-all ${
                      selectedAvatar === index
                        ? 'border-neon-pink shadow-neon-pink'
                        : 'border-white/20 hover:border-neon-blue/40'
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
                className="w-full bg-black/50 border-2 border-neon-blue/30 focus:border-neon-pink focus:ring-2 focus:ring-neon-pink/50 h-12 rounded-sm text-white placeholder:text-white/30 px-4 outline-none transition-all"
                placeholder="footballmaster"
                required
                minLength={3}
                maxLength={20}
              />
              <p className="text-xs text-gray-500 mt-1">3-20 characters, lowercase letters, numbers, and underscores only</p>
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
                className="w-full bg-black/50 border-2 border-neon-blue/30 focus:border-neon-pink focus:ring-2 focus:ring-neon-pink/50 h-12 rounded-sm text-white px-4 outline-none transition-all"
                required
              >
                <option value="" className="bg-card">Select your favorite club...</option>
                {Object.entries(clubsByLeague).map(([league, clubList]) => (
                  <optgroup key={league} label={league} className="bg-card">
                    {clubList.map((club) => (
                      <option key={club} value={club} className="bg-card">
                        {club}
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-1">Unlock Club Challenge mode and club-specific leaderboards</p>
            </div>

            {/* Country */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">
                Country of Residence
              </label>
              <div className="relative">
                <Globe className="absolute left-3 top-3.5 text-gray-500" size={18} />
                <input
                  type="text"
                  data-testid="country-input"
                  value={country}
                  onChange={(e) => setCountry(e.target.value)}
                  className="w-full bg-black/50 border-2 border-neon-blue/30 focus:border-neon-pink focus:ring-2 focus:ring-neon-pink/50 h-12 rounded-sm text-white placeholder:text-white/30 pl-10 pr-4 outline-none transition-all"
                  placeholder="e.g. United Kingdom"
                />
              </div>
            </div>

            {/* Age & Phone in a row */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">
                  Age
                </label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-3.5 text-gray-500" size={18} />
                  <input
                    type="number"
                    data-testid="age-input"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    className="w-full bg-black/50 border-2 border-neon-blue/30 focus:border-neon-pink focus:ring-2 focus:ring-neon-pink/50 h-12 rounded-sm text-white placeholder:text-white/30 pl-10 pr-4 outline-none transition-all"
                    placeholder="25"
                    min={13}
                    max={120}
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">
                  Phone
                </label>
                <div className="relative">
                  <Phone className="absolute left-3 top-3.5 text-gray-500" size={18} />
                  <input
                    type="tel"
                    data-testid="phone-input"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    className="w-full bg-black/50 border-2 border-neon-blue/30 focus:border-neon-pink focus:ring-2 focus:ring-neon-pink/50 h-12 rounded-sm text-white placeholder:text-white/30 pl-10 pr-4 outline-none transition-all"
                    placeholder="+44..."
                  />
                </div>
              </div>
            </div>

            {error && (
              <div className="bg-destructive/10 border-2 border-destructive rounded-sm p-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <button
              type="submit"
              data-testid="continue-btn"
              disabled={loading || !username || username.length < 3 || !favoriteClub}
              className="w-full bg-gradient-to-r from-neon-blue via-neon-pink to-neon-yellow hover:from-neon-yellow hover:via-neon-pink hover:to-neon-blue h-12 px-6 rounded-sm font-bold uppercase tracking-wider shadow-neon-blue hover:shadow-neon-pink transition-all active:scale-95 disabled:opacity-50 text-white"
            >
              {loading ? 'Saving...' : 'Continue to QuizBall'}
            </button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}
