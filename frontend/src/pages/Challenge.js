import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Layout from '../components/Layout';
import { challengesApi, games } from '../lib/api';
import { motion } from 'framer-motion';
import { Trophy, Zap, Shield, Flame, Copy, Check, Users } from 'lucide-react';

const DIFF_CONFIG = {
  easy: { icon: Zap, color: 'text-green-400', border: 'border-green-400/40', bg: 'bg-green-400/10', label: 'Easy' },
  medium: { icon: Shield, color: 'text-neon-yellow', border: 'border-neon-yellow/40', bg: 'bg-neon-yellow/10', label: 'Medium' },
  hard: { icon: Flame, color: 'text-neon-pink', border: 'border-neon-pink/40', bg: 'bg-neon-pink/10', label: 'Hard' },
  very_hard: { icon: Trophy, color: 'text-red-500', border: 'border-red-500/40', bg: 'bg-red-500/10', label: 'Very Hard' },
};

export default function Challenge() {
  const navigate = useNavigate();
  const { user, checkAuth } = useAuth();
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(null);
  const [betAmount, setBetAmount] = useState(10);
  const [inviteCode, setInviteCode] = useState('');
  const [joinCode, setJoinCode] = useState('');
  const [copied, setCopied] = useState(false);
  const [tab, setTab] = useState('weekly'); // weekly | pvp

  useEffect(() => {
    checkAuth();
    loadChallenges();
  }, []);

  const loadChallenges = async () => {
    try {
      const res = await challengesApi.weekly();
      setChallenges(res.data);
    } catch (err) {
      console.error('Failed to load challenges:', err);
    } finally {
      setLoading(false);
    }
  };

  const startChallenge = async (challengeId) => {
    setStarting(challengeId);
    try {
      const res = await challengesApi.start(challengeId);
      navigate(`/game/${res.data.game_id}`);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to start challenge');
      setStarting(null);
    }
  };

  const createBetGame = async () => {
    try {
      const res = await games.createInviteBet(betAmount);
      setInviteCode(res.data.invite_code);
      checkAuth();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create game');
    }
  };

  const joinBetGame = async () => {
    try {
      const res = await games.joinBetGame(joinCode);
      navigate(`/game/${res.data.game_id}`);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to join game');
    }
  };

  const copyCode = () => {
    navigator.clipboard.writeText(inviteCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const credits = user?.credits || 0;

  return (
    <Layout>
      <div className="max-w-lg mx-auto px-4 py-6 space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-extrabold tracking-tighter uppercase text-white">Challenge</h1>
          <p className="text-sm text-gray-400 mt-1">Bet credits. Win big.</p>
          <div className="mt-2 inline-flex items-center gap-2 bg-card border border-neon-yellow/30 rounded-full px-4 py-1">
            <span className="text-neon-yellow font-black" data-testid="credits-display">{credits}</span>
            <span className="text-xs text-gray-400">Credits</span>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex gap-2" data-testid="challenge-tabs">
          <button onClick={() => setTab('weekly')} className={`flex-1 py-2 rounded-sm font-bold uppercase text-sm tracking-wider transition-all ${tab === 'weekly' ? 'bg-neon-blue text-white' : 'bg-card border border-white/10 text-gray-400'}`} data-testid="tab-weekly">
            Weekly
          </button>
          <button onClick={() => setTab('pvp')} className={`flex-1 py-2 rounded-sm font-bold uppercase text-sm tracking-wider transition-all ${tab === 'pvp' ? 'bg-neon-pink text-white' : 'bg-card border border-white/10 text-gray-400'}`} data-testid="tab-pvp">
            P2P Bet
          </button>
        </div>

        {/* WEEKLY CHALLENGES */}
        {tab === 'weekly' && (
          <div className="space-y-3">
            <p className="text-xs text-gray-500 uppercase tracking-wider">This week's challenges</p>
            {loading ? (
              <div className="text-center py-12 text-gray-500">Loading...</div>
            ) : (
              challenges.map((ch, i) => {
                const cfg = DIFF_CONFIG[ch.difficulty] || DIFF_CONFIG.medium;
                const Icon = cfg.icon;
                return (
                  <motion.div
                    key={ch.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.08 }}
                    className={`bg-card border-2 ${cfg.border} rounded-lg p-4 space-y-3`}
                    data-testid={`challenge-card-${ch.difficulty}`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-full ${cfg.bg} flex items-center justify-center`}>
                          <Icon className={cfg.color} size={20} />
                        </div>
                        <div>
                          <p className="font-bold text-white text-sm">{ch.topic}</p>
                          <p className={`text-xs font-bold uppercase ${cfg.color}`}>{cfg.label}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-gray-500">Bet {ch.bet_amount}</p>
                        <p className="text-lg font-black text-neon-yellow">Win {ch.win_amount}</p>
                      </div>
                    </div>
                    {ch.played ? (
                      <div className="text-center py-1 text-xs text-gray-500 uppercase tracking-wider">Already played</div>
                    ) : (
                      <button
                        onClick={() => startChallenge(ch.id)}
                        disabled={starting === ch.id || credits < ch.bet_amount}
                        data-testid={`start-challenge-${ch.difficulty}`}
                        className={`w-full py-2 rounded-sm font-bold uppercase text-sm tracking-wider transition-all active:scale-95 ${
                          credits < ch.bet_amount
                            ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                            : `bg-gradient-to-r from-neon-blue to-neon-pink text-white hover:shadow-neon-blue`
                        }`}
                      >
                        {starting === ch.id ? 'Starting...' : credits < ch.bet_amount ? `Need ${ch.bet_amount} credits` : `Play for ${ch.bet_amount} credits`}
                      </button>
                    )}
                  </motion.div>
                );
              })
            )}
          </div>
        )}

        {/* P2P BET */}
        {tab === 'pvp' && (
          <div className="space-y-6">
            {/* Create */}
            <div className="bg-card border-2 border-neon-pink/30 rounded-lg p-5 space-y-4" data-testid="pvp-create-section">
              <div className="flex items-center gap-2">
                <Users className="text-neon-pink" size={20} />
                <h3 className="font-bold text-white uppercase tracking-wider text-sm">Create Bet Game</h3>
              </div>
              <div>
                <label className="text-xs text-gray-400 block mb-2">Bet Amount (max 50)</label>
                <div className="flex gap-2">
                  {[5, 10, 20, 50].map(amt => (
                    <button key={amt} onClick={() => setBetAmount(amt)}
                      className={`flex-1 py-2 rounded-sm font-bold text-sm transition-all ${betAmount === amt ? 'bg-neon-pink text-white' : 'bg-card border border-white/10 text-gray-400'}`}
                      data-testid={`bet-amount-${amt}`}
                    >
                      {amt}
                    </button>
                  ))}
                </div>
              </div>
              {inviteCode ? (
                <div className="space-y-2">
                  <p className="text-xs text-gray-400">Share this code with your friend:</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-background border border-neon-yellow/50 rounded-sm px-4 py-2 text-center font-mono text-xl font-bold text-neon-yellow tracking-widest" data-testid="invite-code-display">{inviteCode}</div>
                    <button onClick={copyCode} className="p-2 bg-card border border-white/10 rounded-sm" data-testid="copy-code-btn">
                      {copied ? <Check size={20} className="text-green-400" /> : <Copy size={20} className="text-gray-400" />}
                    </button>
                  </div>
                  <p className="text-xs text-gray-500">Bet: {betAmount} credits each. Winner takes {betAmount * 2}.</p>
                </div>
              ) : (
                <button onClick={createBetGame} disabled={credits < betAmount}
                  data-testid="create-bet-btn"
                  className={`w-full py-3 rounded-sm font-bold uppercase text-sm tracking-wider transition-all active:scale-95 ${
                    credits < betAmount ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-gradient-to-r from-neon-pink to-neon-yellow text-black hover:shadow-neon-pink'
                  }`}
                >
                  {credits < betAmount ? `Need ${betAmount} credits` : `Create Game (${betAmount} credits)`}
                </button>
              )}
            </div>

            {/* Join */}
            <div className="bg-card border-2 border-neon-blue/30 rounded-lg p-5 space-y-4" data-testid="pvp-join-section">
              <div className="flex items-center gap-2">
                <Users className="text-neon-blue" size={20} />
                <h3 className="font-bold text-white uppercase tracking-wider text-sm">Join Bet Game</h3>
              </div>
              <input
                value={joinCode} onChange={e => setJoinCode(e.target.value.toUpperCase())}
                placeholder="Enter invite code"
                data-testid="join-code-input"
                className="w-full bg-background border border-white/10 rounded-sm px-4 py-3 text-center font-mono text-lg tracking-widest text-white placeholder:text-gray-600 focus:border-neon-blue outline-none"
              />
              <button onClick={joinBetGame} disabled={!joinCode}
                data-testid="join-bet-btn"
                className={`w-full py-3 rounded-sm font-bold uppercase text-sm tracking-wider transition-all active:scale-95 ${
                  !joinCode ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-gradient-to-r from-neon-blue to-neon-pink text-white hover:shadow-neon-blue'
                }`}
              >
                Join Game
              </button>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
