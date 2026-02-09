import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Trophy, Clock, Play, Users } from 'lucide-react';
import { Layout } from '../components/Layout';
import { useAuth } from '../context/AuthContext';
import { games } from '../lib/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeGames, setActiveGames] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadGames();
  }, []);

  const loadGames = async () => {
    try {
      const response = await games.list();
      setActiveGames(response.data);
    } catch (error) {
      console.error('Failed to load games:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickPlay = async () => {
    try {
      const response = await games.matchmake();
      navigate(`/game/${response.data.game_id}`);
    } catch (error) {
      console.error('Matchmaking failed:', error);
    }
  };

  const handleClubChallenge = async () => {
    try {
      const response = await games.clubChallenge();
      navigate(`/game/${response.data.game_id}`);
    } catch (error) {
      console.error('Club Challenge failed:', error);
    }
  };

  return (
    <Layout>
      <div className="p-5 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tighter uppercase text-white">
              Welcome Back
            </h1>
            <p className="text-sm text-gray-400 mt-1">@{user?.username}</p>
          </div>
          <div className="flex items-center gap-2 bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg px-4 py-2">
            <Trophy className="text-primary" size={20} />
            <span className="text-2xl font-black tracking-tighter text-primary">{user?.skill_rank || 1000}</span>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-4">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleQuickPlay}
            data-testid="quick-play-btn"
            className="bg-primary text-primary-foreground h-24 rounded-lg font-bold uppercase tracking-wider shadow-[0_0_15px_rgba(251,191,36,0.3)] flex flex-col items-center justify-center gap-2"
          >
            <Play size={28} />
            Quick Play
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => navigate('/matchmaking')}
            data-testid="invite-friend-btn"
            className="bg-secondary text-secondary-foreground h-24 rounded-lg font-bold uppercase tracking-wider shadow-[0_0_15px_rgba(59,130,246,0.3)] flex flex-col items-center justify-center gap-2"
          >
            <Users size={28} />
            Invite Friend
          </motion.button>
        </div>

        {/* Active Games */}
        <div>
          <h2 className="text-xl font-bold uppercase tracking-tight mb-4 text-gray-300">Active Games</h2>
          
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading games...</div>
          ) : activeGames.length === 0 ? (
            <div className="bg-card border border-white/10 rounded-lg p-6 text-center">
              <p className="text-gray-400">No active games</p>
              <p className="text-sm text-gray-500 mt-2">Start a quick match or invite a friend!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {activeGames.map((game) => (
                <motion.div
                  key={game.id}
                  whileHover={{ scale: 1.01 }}
                  onClick={() => navigate(`/game/${game.id}`)}
                  data-testid={`game-card-${game.id}`}
                  className="bg-card border border-white/10 rounded-lg p-4 cursor-pointer hover:border-primary/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <img
                        src={game.player2?.avatar || game.player1.avatar}
                        alt="Opponent"
                        className="w-12 h-12 rounded-full border-2 border-white/20"
                      />
                      <div>
                        <p className="font-bold text-white">
                          vs {game.player2?.username || 'Waiting...'}
                        </p>
                        <p className="text-xs text-gray-400">Round {game.current_round}/6</p>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-2xl font-black tracking-tighter">
                        <span className="text-accent">{game.my_score}</span>
                        <span className="text-gray-600 mx-1">-</span>
                        <span className="text-gray-400">{game.opponent_score}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {game.is_my_turn ? (
                      <>
                        <Clock className="text-accent" size={16} />
                        <span className="text-sm font-bold text-accent uppercase">Your Turn</span>
                      </>
                    ) : (
                      <>
                        <Clock className="text-gray-500" size={16} />
                        <span className="text-sm text-gray-500 uppercase">Opponent's Turn</span>
                      </>
                    )}
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