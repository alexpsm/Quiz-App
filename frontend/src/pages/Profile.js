import React, { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Brain, Target, LogOut, Trophy, Clock, Globe, Calendar, Shield, Camera, ChevronDown, ChevronUp } from 'lucide-react';
import { Layout } from '../components/Layout';
import { TieredAvatar } from '../components/TieredAvatar';
import { useAuth } from '../context/AuthContext';
import { PoweredByScore90 } from '../components/Score90Logo';
import { users, games } from '../lib/api';
import { useNavigate } from 'react-router-dom';

export default function Profile() {
  const navigate = useNavigate();
  const { user, logout, checkAuth } = useAuth();
  const fileInputRef = useRef(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [gameHistory, setGameHistory] = useState([]);
  const [ranks, setRanks] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAllPlayers, setShowAllPlayers] = useState(false);
  const [showAllHistory, setShowAllHistory] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    checkAuth();
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [lbRes, histRes, rankRes] = await Promise.allSettled([
        users.leaderboard(10),
        games.history(10),
        users.myRank()
      ]);
      if (lbRes.status === 'fulfilled') setLeaderboard(lbRes.value.data);
      if (histRes.status === 'fulfilled') setGameHistory(histRes.value.data);
      if (rankRes.status === 'fulfilled') setRanks(rankRes.value.data);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    try {
      await users.uploadAvatar(file);
      await checkAuth();
    } catch (err) {
      console.error('Upload failed:', err);
    } finally {
      setUploading(false);
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
          <div className="relative inline-block">
            <TieredAvatar src={user?.avatar} alt="Avatar" tier={user?.player_tier || 1} size="xl" />
            <button
              onClick={() => fileInputRef.current?.click()}
              data-testid="change-avatar-btn"
              className="absolute bottom-0 right-0 w-8 h-8 rounded-full bg-neon-blue border-2 border-background flex items-center justify-center hover:bg-neon-pink transition-colors"
            >
              {uploading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Camera size={14} className="text-white" />
              )}
            </button>
            <input ref={fileInputRef} type="file" accept="image/*" onChange={handleAvatarUpload} className="hidden" data-testid="profile-avatar-input" />
          </div>
          <h2 className="text-2xl font-extrabold tracking-tighter uppercase text-white mb-1 mt-2" data-testid="profile-username">
            @{user?.username}
          </h2>
          <p className="text-sm text-gray-400 mb-2">{user?.email}</p>
          
          {/* Extra Info */}
          <div className="flex items-center justify-center gap-4 text-xs text-gray-500 mb-4 flex-wrap">
            {user?.country && (
              <span className="flex items-center gap-1"><Globe size={12} /> {user.country}</span>
            )}
            {user?.age && (
              <span className="flex items-center gap-1"><Calendar size={12} /> {user.age} yrs</span>
            )}
            {user?.favorite_club && (
              <span className="bg-neon-yellow/20 text-neon-yellow px-2 py-0.5 rounded text-xs font-bold">{user.favorite_club}</span>
            )}
          </div>
          
          <div className="grid grid-cols-2 gap-4">
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

        {/* Your Rank Section */}
        {ranks && (
          <div>
            <h3 className="text-xl font-bold uppercase tracking-tight text-white mb-3 flex items-center gap-2">
              <Trophy size={20} className="text-neon-yellow" />
              Your Rank
            </h3>
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-card border-2 border-neon-blue/30 rounded-lg p-3 text-center" data-testid="profile-rank-global">
                <Globe className="text-neon-blue mx-auto mb-1" size={20} />
                <p className="text-xl font-black tracking-tighter text-neon-blue">#{ranks.global?.rank || '-'}</p>
                <p className="text-[10px] text-gray-500 uppercase">Global</p>
                <p className="text-[10px] text-gray-600">of {ranks.global?.total || 0}</p>
              </div>
              <div className="bg-card border-2 border-neon-yellow/30 rounded-lg p-3 text-center" data-testid="profile-rank-club">
                <Shield className="text-neon-yellow mx-auto mb-1" size={20} />
                <p className="text-xl font-black tracking-tighter text-neon-yellow">#{ranks.club?.rank || '-'}</p>
                <p className="text-[10px] text-gray-500 uppercase truncate">{ranks.club?.name || 'No Club'}</p>
                <p className="text-[10px] text-gray-600">of {ranks.club?.total || 0}</p>
              </div>
              <div className="bg-card border-2 border-neon-pink/30 rounded-lg p-3 text-center" data-testid="profile-rank-country">
                <Globe className="text-neon-pink mx-auto mb-1" size={20} />
                <p className="text-xl font-black tracking-tighter text-neon-pink">#{ranks.country?.rank || '-'}</p>
                <p className="text-[10px] text-gray-500 uppercase truncate">{ranks.country?.name || 'No Country'}</p>
                <p className="text-[10px] text-gray-600">of {ranks.country?.total || 0}</p>
              </div>
            </div>
            {ranks.leagues && ranks.leagues.length > 0 && (
              <div className="mt-3 space-y-2">
                {ranks.leagues.map((lr) => (
                  <div key={lr.league_id} className="bg-card border-2 border-electric-purple/30 rounded-lg px-4 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Trophy className="text-electric-purple" size={16} />
                      <span className="text-sm font-bold text-white truncate">{lr.league_name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-black tracking-tighter text-electric-purple">#{lr.rank}</span>
                      <span className="text-xs text-gray-500">/ {lr.total}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Game History */}
        <div>
          <h3 className="text-xl font-bold uppercase tracking-tight text-white mb-4 flex items-center gap-2">
            <Clock size={20} className="text-neon-pink" />
            Game History
          </h3>
          
          {gameHistory.length === 0 ? (
            <div className="bg-card border-2 border-white/10 rounded-lg p-6 text-center">
              <p className="text-gray-400">No completed games yet</p>
              <p className="text-sm text-gray-500 mt-1">Play some duels to see your history!</p>
            </div>
          ) : (
            <div className="space-y-2">
              {gameHistory.slice(0, showAllHistory ? 10 : 5).map((game) => (
                <motion.div
                  key={game.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`bg-card border-2 rounded-lg p-4 flex items-center gap-3 ${
                    game.won ? 'border-neon-yellow/30' : 'border-white/10'
                  }`}
                  data-testid={`history-${game.id}`}
                >
                  <img src={game.opponent_avatar} alt={game.opponent_username} className="w-10 h-10 rounded-full border-2 border-neon-blue/30" />
                  <div className="flex-1">
                    <p className="font-bold text-white text-sm">vs @{game.opponent_username}</p>
                    <p className="text-xs text-gray-500">{game.date ? new Date(game.date).toLocaleDateString() : ''}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-black tracking-tighter">
                      <span className={game.won ? 'text-neon-yellow' : 'text-gray-400'}>{game.my_score}</span>
                      <span className="text-gray-600 mx-1">-</span>
                      <span className={!game.won ? 'text-neon-yellow' : 'text-gray-400'}>{game.opponent_score}</span>
                    </div>
                    <span className={`text-xs font-bold uppercase ${game.won ? 'text-neon-yellow' : 'text-destructive'}`}>
                      {game.won ? 'Won' : 'Lost'}
                    </span>
                  </div>
                </motion.div>
              ))}
              {gameHistory.length > 5 && (
                <button
                  onClick={() => setShowAllHistory(!showAllHistory)}
                  data-testid="toggle-history-btn"
                  className="w-full py-2 text-sm font-bold uppercase tracking-wider text-neon-blue hover:text-neon-pink transition-colors flex items-center justify-center gap-1"
                >
                  {showAllHistory ? <><ChevronUp size={16} /> Show Less</> : <><ChevronDown size={16} /> Show All ({gameHistory.length})</>}
                </button>
              )}
            </div>
          )}
        </div>

        {/* Leaderboard */}
        <div>
          <h3 className="text-xl font-bold uppercase tracking-tight text-white mb-4 flex items-center gap-2">
            <Trophy size={20} className="text-neon-yellow" />
            Top Players
          </h3>
          
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading...</div>
          ) : (
            <div className="space-y-2">
              {leaderboard.slice(0, showAllPlayers ? 10 : 5).map((player, index) => (
                <motion.div
                  key={player.user_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="bg-card border-2 border-neon-blue/20 hover:border-neon-pink/50 rounded-lg p-4 flex items-center gap-4 transition-all"
                >
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                    index === 0 ? 'bg-gradient-to-br from-neon-yellow to-neon-orange text-black shadow-neon-yellow'
                    : index === 1 ? 'bg-gradient-to-br from-gray-300 to-gray-500 text-black'
                    : index === 2 ? 'bg-gradient-to-br from-orange-600 to-orange-800 text-white'
                    : 'bg-gray-700 text-gray-400'
                  }`}>
                    {index + 1}
                  </div>
                  <img src={player.avatar} alt={player.username} className="w-10 h-10 rounded-full border-2 border-neon-blue/30" />
                  <div className="flex-1">
                    <p className="font-bold text-white">@{player.username}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-black tracking-tighter text-neon-yellow">{player.skill_rank}</p>
                    <p className="text-xs text-gray-500">Ball Knowledge</p>
                  </div>
                </motion.div>
              ))}
              {leaderboard.length > 5 && (
                <button
                  onClick={() => setShowAllPlayers(!showAllPlayers)}
                  data-testid="toggle-players-btn"
                  className="w-full py-2 text-sm font-bold uppercase tracking-wider text-neon-blue hover:text-neon-pink transition-colors flex items-center justify-center gap-1"
                >
                  {showAllPlayers ? <><ChevronUp size={16} /> Show Less</> : <><ChevronDown size={16} /> Show Top 10</>}
                </button>
              )}
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
