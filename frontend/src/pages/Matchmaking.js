import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, Copy, Check, Share2, MessageCircle, Zap, Shield, Plus, X } from 'lucide-react';
import { Layout } from '../components/Layout';
import { PoweredByScore90 } from '../components/Score90Logo';
import { games, leagues } from '../lib/api';

export default function Matchmaking() {
  const navigate = useNavigate();
  const [inviteCode, setInviteCode] = useState('');
  const [generatedCode, setGeneratedCode] = useState('');
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // League state
  const [publicLeagues, setPublicLeagues] = useState([]);
  const [showCreateLeague, setShowCreateLeague] = useState(false);
  const [createLeagueType, setCreateLeagueType] = useState('public');
  const [leagueName, setLeagueName] = useState('');
  const [leagueCode, setLeagueCode] = useState('');
  const [leagueLoading, setLeagueLoading] = useState(false);

  useEffect(() => {
    loadLeagues();
  }, []);

  const loadLeagues = async () => {
    try {
      const res = await leagues.list();
      setPublicLeagues(res.data);
    } catch (err) {
      console.error('Failed to load leagues:', err);
    }
  };

  const handleCreateInvite = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await games.createInvite();
      setGeneratedCode(response.data.invite_code);
    } catch (err) {
      setError('Failed to create invite');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(generatedCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleShareTo = (platform) => {
    const msg = `Challenge me on QuizBall! Use code: ${generatedCode} to join. Prove your Ball Knowledge!`;
    const encodedMsg = encodeURIComponent(msg);
    const urls = {
      whatsapp: `https://wa.me/?text=${encodedMsg}`,
      messenger: `https://www.facebook.com/dialog/send?link=${encodeURIComponent(window.location.origin)}&app_id=0&redirect_uri=${encodeURIComponent(window.location.origin)}`,
      instagram: null,
    };
    if (urls[platform]) {
      window.open(urls[platform], '_blank');
    } else {
      navigator.clipboard.writeText(msg);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleJoinGame = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await games.joinGame(inviteCode.toUpperCase());
      navigate(`/game/${response.data.game_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to join game');
    } finally {
      setLoading(false);
    }
  };

  const handleRandomMatch = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await games.matchmake();
      navigate(`/game/${response.data.game_id}`);
    } catch (err) {
      setError('No opponents available');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLeague = async (e) => {
    e.preventDefault();
    setLeagueLoading(true);
    try {
      await leagues.create({ name: leagueName, league_type: createLeagueType });
      setLeagueName('');
      setShowCreateLeague(false);
      loadLeagues();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create league');
    } finally {
      setLeagueLoading(false);
    }
  };

  const handleJoinLeague = async (leagueId) => {
    try {
      await leagues.join(leagueId);
      loadLeagues();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to join league');
    }
  };

  const handleLeaveLeague = async (leagueId) => {
    try {
      await leagues.leave(leagueId);
      loadLeagues();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to leave league');
    }
  };

  const handleJoinLeagueByCode = async (e) => {
    e.preventDefault();
    if (!leagueCode) return;
    setLeagueLoading(true);
    try {
      await leagues.joinByCode(leagueCode.toUpperCase());
      setLeagueCode('');
      loadLeagues();
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid league code');
    } finally {
      setLeagueLoading(false);
    }
  };

  return (
    <Layout>
      <div className="p-5 space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-extrabold tracking-tighter uppercase text-transparent bg-clip-text bg-gradient-to-r from-neon-blue via-neon-pink to-neon-yellow mb-2">
            Play
          </h1>
          <PoweredByScore90 size="sm" className="justify-center" />
        </div>

        {/* Random Match */}
        <div className="bg-card border-2 border-neon-blue/30 rounded-lg p-5 shadow-neon-blue">
          <div className="flex items-start gap-4 mb-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-neon-blue to-neon-pink border-2 border-neon-blue flex items-center justify-center flex-shrink-0">
              <Users className="text-white" size={24} />
            </div>
            <div>
              <h3 className="text-lg font-bold uppercase tracking-tight text-white mb-1">Random Opponent</h3>
              <p className="text-sm text-gray-400">Match based on ball knowledge</p>
            </div>
          </div>
          <button
            onClick={handleRandomMatch}
            data-testid="random-match-btn"
            disabled={loading}
            className="w-full bg-gradient-to-r from-neon-blue to-neon-pink hover:from-neon-pink hover:to-neon-yellow h-12 px-6 rounded-sm font-bold uppercase tracking-wider shadow-neon-blue hover:shadow-neon-pink transition-all active:scale-95 disabled:opacity-50 text-white"
          >
            {loading ? 'Finding...' : 'Find Match'}
          </button>
        </div>

        <div className="relative">
          <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-white/10"></div></div>
          <div className="relative flex justify-center text-xs uppercase"><span className="bg-background px-2 text-gray-500">Or</span></div>
        </div>

        {/* Create Invite */}
        <div className="bg-card border-2 border-neon-pink/30 rounded-lg p-5 shadow-neon-pink">
          <h3 className="text-lg font-bold uppercase tracking-tight text-white mb-4">Invite a Friend</h3>
          
          {!generatedCode ? (
            <button
              onClick={handleCreateInvite}
              data-testid="create-invite-btn"
              disabled={loading}
              className="w-full bg-gradient-to-r from-neon-pink to-electric-purple hover:from-electric-purple hover:to-neon-pink h-12 px-6 rounded-sm font-bold uppercase tracking-wider shadow-neon-pink transition-all active:scale-95 disabled:opacity-50 text-white"
            >
              {loading ? 'Generating...' : 'Generate Invite Code'}
            </button>
          ) : (
            <div className="space-y-3">
              <div className="bg-black/50 border-2 border-neon-yellow rounded-sm p-4 flex items-center justify-between shadow-neon-yellow">
                <span className="text-2xl font-black tracking-tighter text-neon-yellow" data-testid="invite-code">{generatedCode}</span>
                <button onClick={handleCopyCode} data-testid="copy-code-btn" className="text-gray-400 hover:text-neon-yellow transition-colors">
                  {copied ? <Check className="text-neon-yellow" size={24} /> : <Copy size={24} />}
                </button>
              </div>
              <div className="flex gap-2">
                <button onClick={() => handleShareTo('whatsapp')} data-testid="share-whatsapp"
                  className="flex-1 bg-[#25D366]/20 border border-[#25D366]/50 hover:bg-[#25D366]/30 text-[#25D366] h-10 rounded-sm font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-1.5 transition-all">
                  <MessageCircle size={16} /> WhatsApp
                </button>
                <button onClick={() => handleShareTo('messenger')} data-testid="share-messenger"
                  className="flex-1 bg-[#0084FF]/20 border border-[#0084FF]/50 hover:bg-[#0084FF]/30 text-[#0084FF] h-10 rounded-sm font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-1.5 transition-all">
                  <MessageCircle size={16} /> Messenger
                </button>
                <button onClick={() => handleShareTo('instagram')} data-testid="share-instagram"
                  className="flex-1 bg-[#E1306C]/20 border border-[#E1306C]/50 hover:bg-[#E1306C]/30 text-[#E1306C] h-10 rounded-sm font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-1.5 transition-all">
                  <Share2 size={16} /> Copy
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Join with Code */}
        <div className="bg-card border-2 border-neon-yellow/30 rounded-lg p-5 shadow-neon-yellow">
          <h3 className="text-lg font-bold uppercase tracking-tight text-white mb-4">Join with Code</h3>
          <form onSubmit={handleJoinGame} className="space-y-3">
            <input
              type="text"
              data-testid="join-code-input"
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
              className="w-full bg-black/50 border-2 border-neon-yellow/50 focus:border-neon-yellow focus:ring-2 focus:ring-neon-yellow/50 h-12 rounded-sm text-white placeholder:text-white/30 px-4 outline-none text-center text-xl font-bold tracking-wider"
              placeholder="Enter code"
              maxLength={8}
              required
            />
            <button type="submit" data-testid="join-game-btn" disabled={loading || inviteCode.length !== 8}
              className="w-full border-2 border-neon-yellow bg-transparent hover:bg-neon-yellow/10 text-neon-yellow h-12 px-6 rounded-sm font-bold uppercase tracking-wider transition-all disabled:opacity-50">
              {loading ? 'Joining...' : 'Join Game'}
            </button>
          </form>
        </div>

        {/* Leagues Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold uppercase tracking-tight text-white flex items-center gap-2">
              <Zap size={20} className="text-electric-purple" /> Leagues
            </h2>
            <button
              onClick={() => setShowCreateLeague(!showCreateLeague)}
              data-testid="toggle-create-league"
              className="flex items-center gap-1 text-sm text-neon-blue hover:text-neon-pink transition-colors font-bold uppercase"
            >
              {showCreateLeague ? <X size={16} /> : <Plus size={16} />}
              {showCreateLeague ? 'Cancel' : 'Create'}
            </button>
          </div>

          {/* Create League Form */}
          <AnimatePresence>
            {showCreateLeague && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden mb-4"
              >
                <form onSubmit={handleCreateLeague} className="bg-card border-2 border-electric-purple/30 rounded-lg p-4 space-y-3">
                  <input
                    type="text"
                    data-testid="league-name-input"
                    value={leagueName}
                    onChange={(e) => setLeagueName(e.target.value)}
                    className="w-full bg-black/50 border-2 border-electric-purple/30 focus:border-electric-purple h-10 rounded-sm text-white placeholder:text-white/30 px-4 outline-none text-sm"
                    placeholder="League name"
                    required
                  />
                  <div className="flex gap-2">
                    <button type="button" onClick={() => setCreateLeagueType('public')}
                      className={`flex-1 h-10 rounded-sm font-bold text-xs uppercase tracking-wider border-2 transition-all ${
                        createLeagueType === 'public' ? 'border-neon-blue bg-neon-blue/20 text-neon-blue' : 'border-white/20 text-gray-400'
                      }`}>
                      <Zap size={14} className="inline mr-1" /> Public
                    </button>
                    <button type="button" onClick={() => setCreateLeagueType('private')}
                      className={`flex-1 h-10 rounded-sm font-bold text-xs uppercase tracking-wider border-2 transition-all ${
                        createLeagueType === 'private' ? 'border-neon-orange bg-neon-orange/20 text-neon-orange' : 'border-white/20 text-gray-400'
                      }`}>
                      <Shield size={14} className="inline mr-1" /> Private
                    </button>
                  </div>
                  <button type="submit" data-testid="create-league-btn" disabled={leagueLoading || !leagueName}
                    className="w-full bg-gradient-to-r from-electric-purple to-neon-pink h-10 rounded-sm font-bold text-xs uppercase tracking-wider text-white transition-all disabled:opacity-50">
                    {leagueLoading ? 'Creating...' : 'Create League'}
                  </button>
                </form>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Join Private League by Code */}
          <form onSubmit={handleJoinLeagueByCode} className="flex gap-2 mb-4">
            <input
              type="text"
              data-testid="league-code-input"
              value={leagueCode}
              onChange={(e) => setLeagueCode(e.target.value.toUpperCase())}
              className="flex-1 bg-black/50 border-2 border-neon-orange/30 focus:border-neon-orange h-10 rounded-sm text-white placeholder:text-white/30 px-3 outline-none text-sm text-center font-bold tracking-wider"
              placeholder="Private League Code"
              maxLength={8}
            />
            <button type="submit" data-testid="join-league-code-btn" disabled={!leagueCode}
              className="border-2 border-neon-orange bg-neon-orange/10 hover:bg-neon-orange/20 text-neon-orange h-10 px-4 rounded-sm font-bold text-xs uppercase tracking-wider transition-all disabled:opacity-50">
              Join
            </button>
          </form>

          {/* League List */}
          <div className="space-y-2">
            {publicLeagues.length === 0 ? (
              <div className="bg-card border-2 border-white/10 rounded-lg p-4 text-center">
                <p className="text-gray-400 text-sm">No leagues yet. Create one!</p>
              </div>
            ) : (
              publicLeagues.map((league) => (
                <div key={league.id} data-testid={`league-${league.id}`}
                  className={`bg-card border-2 rounded-lg p-4 flex items-center gap-3 ${
                    league.league_type === 'public' ? 'border-neon-blue/20' : 'border-neon-orange/20'
                  }`}>
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    league.league_type === 'public' ? 'bg-neon-blue/20' : 'bg-neon-orange/20'
                  }`}>
                    {league.league_type === 'public' ? <Zap className="text-neon-blue" size={20} /> : <Shield className="text-neon-orange" size={20} />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-bold text-white text-sm truncate">{league.name}</p>
                    <p className="text-xs text-gray-500">{league.member_count} members</p>
                  </div>
                  {league.is_member ? (
                    <button onClick={() => handleLeaveLeague(league.id)} data-testid={`leave-league-${league.id}`}
                      className="border border-destructive/50 text-destructive text-xs h-8 px-3 rounded-sm font-bold uppercase hover:bg-destructive/10 transition-all">
                      Leave
                    </button>
                  ) : (
                    <button onClick={() => handleJoinLeague(league.id)} data-testid={`join-league-${league.id}`}
                      className="border border-neon-blue/50 text-neon-blue text-xs h-8 px-3 rounded-sm font-bold uppercase hover:bg-neon-blue/10 transition-all">
                      Join
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {error && (
          <div className="bg-destructive/10 border-2 border-destructive rounded-sm p-3 text-sm text-destructive text-center">
            {error}
          </div>
        )}
      </div>
    </Layout>
  );
}
