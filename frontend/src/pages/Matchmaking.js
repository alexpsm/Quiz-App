import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Users, Copy, Check } from 'lucide-react';
import { Layout } from '../components/Layout';
import { PoweredByScore90 } from '../components/Score90Logo';
import { games } from '../lib/api';

export default function Matchmaking() {
  const navigate = useNavigate();
  const [inviteCode, setInviteCode] = useState('');
  const [generatedCode, setGeneratedCode] = useState('');
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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

  return (
    <Layout>
      <div className="p-5 space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-extrabold tracking-tighter uppercase text-transparent bg-clip-text bg-gradient-to-r from-neon-blue via-neon-pink to-neon-yellow mb-2">
            Matchmaking
          </h1>
          <PoweredByScore90 size="sm" className="justify-center" />
          <p className="text-sm text-gray-400 mt-2">Find opponents and start playing</p>
        </div>

        {/* Random Match */}
        <div className="bg-card border-2 border-neon-blue/30 rounded-lg p-6 shadow-neon-blue">
          <div className="flex items-start gap-4 mb-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-neon-blue to-neon-pink border-2 border-neon-blue flex items-center justify-center flex-shrink-0">
              <Users className="text-white" size={24} />
            </div>
            <div>
              <h3 className="text-xl font-bold uppercase tracking-tight text-white mb-1">
                Random Opponent
              </h3>
              <p className="text-sm text-gray-400">
                Match with a random player based on ball knowledge
              </p>
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
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-white/10"></div>
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-background px-2 text-gray-500">Or</span>
          </div>
        </div>

        {/* Create Invite */}
        <div className="bg-card border-2 border-neon-pink/30 rounded-lg p-6 shadow-neon-pink">
          <h3 className="text-xl font-bold uppercase tracking-tight text-white mb-4">
            Invite a Friend
          </h3>
          
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
                <span className="text-2xl font-black tracking-tighter text-neon-yellow" data-testid="invite-code">
                  {generatedCode}
                </span>
                <button
                  onClick={handleCopyCode}
                  data-testid="copy-code-btn"
                  className="text-gray-400 hover:text-neon-yellow transition-colors"
                >
                  {copied ? <Check className="text-neon-yellow" size={24} /> : <Copy size={24} />}
                </button>
              </div>
              <p className="text-xs text-gray-500 text-center">
                Share this code with your friend to start a match
              </p>
            </div>
          )}
        </div>

        {/* Join with Code */}
        <div className="bg-card border-2 border-neon-yellow/30 rounded-lg p-6 shadow-neon-yellow">
          <h3 className="text-xl font-bold uppercase tracking-tight text-white mb-4">
            Join with Code
          </h3>
          
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
            <button
              type="submit"
              data-testid="join-game-btn"
              disabled={loading || inviteCode.length !== 8}
              className="w-full border-2 border-neon-yellow bg-transparent hover:bg-neon-yellow/10 text-neon-yellow h-12 px-6 rounded-sm font-bold uppercase tracking-wider transition-all disabled:opacity-50"
            >
              {loading ? 'Joining...' : 'Join Game'}
            </button>
          </form>
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