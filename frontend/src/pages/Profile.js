import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Target, LogOut } from 'lucide-react';
import { Layout } from '../components/Layout';
import { useAuth } from '../context/AuthContext';
import { PoweredByScore90 } from '../components/Score90Logo';
import { users } from '../lib/api';
import { useNavigate } from 'react-router-dom';

export default function Profile() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboard();
  }, []);

  const loadLeaderboard = async () => {
    try {
      const response = await users.leaderboard(10);
      setLeaderboard(response.data);
    } catch (error) {
      console.error('Failed to load leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <Layout>
      <div className="p-5 space-y-6">
        {/* Header */}
        <div className="text-center">
          <PoweredByScore90 size="md" className="justify-center mb-4" />
        </div>

        {/* Profile Card */}
        <div className="bg-card border-2 border-neon-blue/30 rounded-lg p-6 text-center shadow-neon-blue backdrop-blur-sm">
          <img
            src={user?.avatar}
            alt="Avatar"
            className="w-24 h-24 rounded-full border-4 border-neon-pink mx-auto mb-4 shadow-neon-pink"
          />
          <h2 className="text-2xl font-extrabold tracking-tighter uppercase text-white mb-1">
            @{user?.username}
          </h2>
          <p className="text-sm text-gray-400 mb-4">{user?.email}</p>
          
          <div className="grid grid-cols-2 gap-4 mt-6">
            <div className="bg-black/40 backdrop-blur-xl border-2 border-neon-yellow/50 rounded-lg p-4 shadow-neon-yellow">
              <Brain className="text-neon-yellow mx-auto mb-2" size={28} />
              <p className="text-3xl font-black tracking-tighter text-neon-yellow">{user?.skill_rank}</p>
              <p className="text-xs text-gray-500 uppercase tracking-wider mt-1">Ball Knowledge</p>
            </div>
            <div className="bg-black/40 backdrop-blur-xl border-2 border-neon-blue/50 rounded-lg p-4 shadow-neon-blue">
              <Target className="text-neon-blue mx-auto mb-2" size={28} />
              <p className="text-3xl font-black tracking-tighter text-neon-blue">{user?.credits}</p>
              <p className="text-xs text-gray-500 uppercase tracking-wider mt-1">Credits</p>
            </div>
          </div>
        </div>

        {/* Leaderboard */}
        <div>
          <h3 className="text-xl font-bold uppercase tracking-tight text-white mb-4">
            Top Players
          </h3>
          
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading leaderboard...</div>
          ) : (
            <div className="space-y-2">
              {leaderboard.map((player, index) => (
                <motion.div
                  key={player.user_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="bg-card border-2 border-neon-blue/20 hover:border-neon-pink/50 rounded-lg p-4 flex items-center gap-4 transition-all"
                >
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                      index === 0
                        ? 'bg-gradient-to-br from-neon-yellow to-neon-orange text-black shadow-neon-yellow'
                        : index === 1
                        ? 'bg-gradient-to-br from-gray-300 to-gray-500 text-black'
                        : index === 2
                        ? 'bg-gradient-to-br from-orange-600 to-orange-800 text-white'
                        : 'bg-gray-700 text-gray-400'
                    }`}
                  >
                    {index + 1}
                  </div>
                  <img
                    src={player.avatar}
                    alt={player.username}
                    className="w-10 h-10 rounded-full border-2 border-neon-blue/30"
                  />
                  <div className="flex-1">
                    <p className="font-bold text-white">@{player.username}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-black tracking-tighter text-neon-yellow">
                      {player.skill_rank}
                    </p>
                    <p className="text-xs text-gray-500">Ball Knowledge</p>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          data-testid="logout-btn"
          className="w-full border-2 border-destructive bg-transparent hover:bg-destructive/20 text-destructive h-12 px-6 rounded-sm font-bold uppercase tracking-wider transition-all flex items-center justify-center gap-2"
        >
          <LogOut size={20} />
          Logout
        </button>
      </div>
    </Layout>
  );
}
