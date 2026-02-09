import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Trophy, ArrowLeft, Award, Target } from 'lucide-react';
import { Layout } from '../components/Layout';
import { useAuth } from '../context/AuthContext';
import { users } from '../lib/api';
import { useNavigate } from 'react-router-dom';

export default function ClubLeaderboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [leaderboard, setLeaderboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboard();
  }, []);

  const loadLeaderboard = async () => {
    try {
      const response = await users.clubLeaderboard();
      setLeaderboard(response.data);
    } catch (error) {
      console.error('Failed to load club leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user?.favorite_club) {
    return (
      <Layout showNav={false}>
        <div className="min-h-screen flex items-center justify-center p-5">
          <div className="text-center">
            <p className="text-gray-400 mb-4">Please select your favorite club first</p>
            <button
              onClick={() => navigate('/dashboard')}
              className="bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-6 rounded-sm font-bold uppercase tracking-wider"
            >
              Go to Dashboard
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout showNav={false}>
      <div className="min-h-screen bg-gradient-to-b from-slate-900 to-black">
        {/* Header */}
        <div className="p-5 border-b border-white/10">
          <div className="flex items-center gap-4 mb-4">
            <button
              onClick={() => navigate('/dashboard')}
              data-testid="back-btn"
              className="text-gray-400 hover:text-white"
            >
              <ArrowLeft size={24} />
            </button>
            <div className="flex-1">
              <h1 className="text-2xl font-extrabold tracking-tighter uppercase text-white">
                {leaderboard?.club || user.favorite_club}
              </h1>
              <p className="text-sm text-gray-400">Ball Knowledge Rankings</p>
            </div>
          </div>

          {/* User Stats Card */}
          {leaderboard && leaderboard.user_rank && (
            <div className="bg-accent/20 border-2 border-accent rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-accent flex items-center justify-center">
                    <Trophy className="text-white" size={24} />
                  </div>
                  <div>
                    <p className="text-sm text-gray-300">Your Rank</p>
                    <p className="text-3xl font-black tracking-tighter text-accent">#{leaderboard.user_rank}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-300">Score</p>
                  <p className="text-3xl font-black tracking-tighter text-white">{user.club_knowledge_score || 0}</p>
                </div>
              </div>
            </div>
          )}

          <div className="flex items-center justify-between mt-4 bg-black/40 rounded-lg px-4 py-2">
            <div className="flex items-center gap-2">
              <Target className="text-primary" size={16} />
              <span className="text-sm text-gray-400">Total Fans</span>
            </div>
            <span className="text-white font-bold">{leaderboard?.total_fans || 0}</span>
          </div>
        </div>

        {/* Leaderboard */}
        <div className="p-5">
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading leaderboard...</div>
          ) : !leaderboard || leaderboard.leaderboard.length === 0 ? (
            <div className="bg-card border border-white/10 rounded-lg p-6 text-center">
              <p className="text-gray-400">No rankings yet</p>
              <p className="text-sm text-gray-500 mt-2">Be the first {user.favorite_club} fan on the leaderboard!</p>
            </div>
          ) : (
            <div className="space-y-2">
              {leaderboard.leaderboard.map((entry) => (
                <motion.div
                  key={entry.user_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: entry.rank * 0.02 }}
                  className={`rounded-lg p-4 flex items-center gap-4 ${
                    entry.is_current_user
                      ? 'bg-accent/20 border-2 border-accent'
                      : 'bg-card border border-white/10'
                  }`}
                  data-testid={`leaderboard-entry-${entry.rank}`}
                >
                  {/* Rank Badge */}
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                      entry.rank === 1
                        ? 'bg-primary text-black'
                        : entry.rank === 2
                        ? 'bg-gray-400 text-black'
                        : entry.rank === 3
                        ? 'bg-orange-600 text-white'
                        : 'bg-gray-700 text-gray-400'
                    }`}
                  >
                    {entry.rank <= 3 ? <Award size={20} /> : entry.rank}
                  </div>

                  {/* Avatar */}
                  <img
                    src={entry.avatar}
                    alt={entry.username}
                    className="w-12 h-12 rounded-full border-2 border-white/20"
                  />

                  {/* Username */}
                  <div className="flex-1">
                    <p className={`font-bold ${entry.is_current_user ? 'text-accent' : 'text-white'}`}>
                      @{entry.username}
                      {entry.is_current_user && (
                        <span className="ml-2 text-xs bg-accent text-white px-2 py-1 rounded">YOU</span>
                      )}
                    </p>
                    {entry.rank <= 3 && (
                      <p className="text-xs text-gray-400">
                        {entry.rank === 1 ? '🥇 Champion' : entry.rank === 2 ? '🥈 Runner-up' : '🥉 Third Place'}
                      </p>
                    )}
                  </div>

                  {/* Score */}
                  <div className="text-right">
                    <p className="text-2xl font-black tracking-tighter text-primary">
                      {entry.club_knowledge_score}
                    </p>
                    <p className="text-xs text-gray-500 uppercase">Points</p>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
