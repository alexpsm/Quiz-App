import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, User, Trophy, HelpCircle, Check, X, Lightbulb, Clock } from 'lucide-react';
import { Layout } from '../components/Layout';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';

export default function CareerChallenge() {
  const navigate = useNavigate();
  const { user, checkAuth } = useAuth();
  const [challenge, setChallenge] = useState(null);
  const [guess, setGuess] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const inputRef = useRef(null);

  useEffect(() => {
    checkAuth();
    loadChallenge();
  }, []);

  const loadChallenge = async () => {
    try {
      const response = await api.get('/career-challenge/today');
      setChallenge(response.data);
    } catch (error) {
      console.error('Failed to load career challenge:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitGuess = async (e) => {
    e.preventDefault();
    if (!guess.trim() || submitting) return;

    setSubmitting(true);
    setFeedback(null);

    try {
      const response = await api.post('/career-challenge/guess', { guess: guess.trim() });
      setFeedback(response.data);
      
      if (response.data.correct) {
        // Update challenge state with solved
        setChallenge(prev => ({
          ...prev,
          solved: true,
          answer: response.data.answer,
          hints: response.data.hints
        }));
      } else {
        // Update revealed clubs
        setChallenge(prev => ({
          ...prev,
          clubs_revealed: response.data.clubs_revealed,
          revealed_clubs: response.data.revealed_clubs,
          guesses_made: prev.guesses_made + 1,
          guesses: [...(prev.guesses || []), { guess: guess.trim(), correct: false }],
          hints: response.data.hints
        }));
      }
      
      setGuess('');
      
      // Focus input for next guess
      if (!response.data.solved && inputRef.current) {
        setTimeout(() => inputRef.current?.focus(), 100);
      }
    } catch (error) {
      console.error('Failed to submit guess:', error);
      setFeedback({ error: 'Failed to submit guess' });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="relative w-16 h-16">
            <div className="absolute inset-0 border-4 border-neon-yellow/30 rounded-full" />
            <div className="absolute inset-0 border-4 border-neon-yellow border-t-transparent rounded-full animate-spin" />
          </div>
        </div>
      </Layout>
    );
  }

  if (!challenge) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-400">Failed to load challenge</p>
          <button onClick={() => navigate('/dashboard')} className="mt-4 text-neon-blue hover:text-neon-pink">
            Return to Dashboard
          </button>
        </div>
      </Layout>
    );
  }

  const guessesRemaining = challenge.max_guesses - challenge.guesses_made;
  const progressPercent = (challenge.clubs_revealed / challenge.total_clubs) * 100;

  return (
    <Layout>
      <div className="max-w-lg mx-auto space-y-6 pb-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            data-testid="back-btn"
          >
            <ArrowLeft size={20} />
            <span className="text-sm font-medium">Back</span>
          </button>
          <div className="flex items-center gap-2">
            <User className="text-neon-yellow" size={20} />
            <h1 className="text-lg font-extrabold tracking-tighter uppercase text-white">Career Mode</h1>
          </div>
          <span className={`text-[10px] uppercase px-2 py-1 rounded font-bold ${
            challenge.difficulty === 'easy' ? 'bg-green-500/30 text-green-400' :
            challenge.difficulty === 'hard' ? 'bg-red-500/30 text-red-400' :
            'bg-neon-yellow/30 text-neon-yellow'
          }`}>
            {challenge.difficulty}
          </span>
        </div>

        {/* Progress */}
        <div className="bg-card border-2 border-white/10 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400 uppercase">Career Progress</span>
            <span className="text-xs text-neon-yellow">{challenge.clubs_revealed} / {challenge.total_clubs} clubs</span>
          </div>
          <div className="h-2 bg-black/50 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-neon-yellow to-orange-500"
              initial={{ width: 0 }}
              animate={{ width: `${progressPercent}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          <div className="flex items-center justify-between mt-3">
            <div className="text-center">
              <p className="text-xl font-black text-white">{guessesRemaining}</p>
              <p className="text-[10px] text-gray-500 uppercase">Guesses Left</p>
            </div>
            <div className="text-center">
              <p className="text-xl font-black text-neon-yellow">{challenge.guesses_made}</p>
              <p className="text-[10px] text-gray-500 uppercase">Guesses Made</p>
            </div>
          </div>
        </div>

        {/* Revealed Clubs */}
        <div className="bg-card border-2 border-neon-yellow/30 rounded-lg overflow-hidden">
          <div className="bg-gradient-to-r from-neon-yellow/20 to-orange-500/20 px-4 py-3 border-b border-neon-yellow/30">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Career Path</h2>
          </div>
          <div className="p-4 space-y-2 max-h-64 overflow-y-auto">
            {challenge.revealed_clubs?.map((club, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="flex items-center gap-3 bg-black/30 rounded-lg px-4 py-3"
              >
                <span className="w-8 h-8 rounded-full bg-neon-yellow/20 border-2 border-neon-yellow/50 flex items-center justify-center text-sm font-bold text-neon-yellow">
                  {idx + 1}
                </span>
                <div className="flex-1">
                  <p className="text-white font-bold">{club.club}</p>
                  <p className="text-xs text-gray-500">{club.years}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Hints */}
        {challenge.hints && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-card border-2 border-purple-500/30 rounded-lg p-4"
          >
            <div className="flex items-center gap-2 mb-2">
              <Lightbulb className="text-purple-400" size={16} />
              <span className="text-xs text-purple-400 uppercase font-bold">Hints</span>
            </div>
            <div className="flex gap-4">
              {challenge.hints.nationality && (
                <div className="text-center">
                  <p className="text-white font-bold">{challenge.hints.nationality}</p>
                  <p className="text-[10px] text-gray-500">Nationality</p>
                </div>
              )}
              {challenge.hints.position && (
                <div className="text-center">
                  <p className="text-white font-bold">{challenge.hints.position}</p>
                  <p className="text-[10px] text-gray-500">Position</p>
                </div>
              )}
            </div>
          </motion.div>
        )}

        {/* Previous Guesses */}
        {challenge.guesses && challenge.guesses.length > 0 && (
          <div className="bg-card border-2 border-white/10 rounded-lg p-4">
            <h3 className="text-xs text-gray-400 uppercase mb-2">Your Guesses</h3>
            <div className="flex flex-wrap gap-2">
              {challenge.guesses.map((g, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-destructive/20 border border-destructive/50 rounded-full text-xs text-gray-300 flex items-center gap-1"
                >
                  <X size={12} className="text-destructive" />
                  {g.guess}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Guess Input / Result */}
        {challenge.solved ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gradient-to-br from-neon-yellow/20 to-orange-500/20 border-2 border-neon-yellow rounded-lg p-6 text-center"
          >
            <Trophy className="text-neon-yellow mx-auto mb-3" size={48} />
            <h2 className="text-2xl font-black text-white mb-1">Correct!</h2>
            <p className="text-3xl font-black text-neon-yellow mb-4">{challenge.answer}</p>
            {feedback?.credits_earned && (
              <p className="text-sm text-gray-300">
                You earned <span className="text-neon-yellow font-bold">+{feedback.credits_earned} credits</span>!
              </p>
            )}
            <p className="text-xs text-gray-500 mt-4">Come back tomorrow for a new challenge!</p>
            <button
              onClick={() => navigate('/dashboard')}
              className="mt-4 bg-neon-yellow text-black px-6 py-2 rounded-sm font-bold uppercase text-sm hover:bg-orange-500 transition-colors"
            >
              Return to Dashboard
            </button>
          </motion.div>
        ) : guessesRemaining <= 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gradient-to-br from-destructive/20 to-red-900/20 border-2 border-destructive rounded-lg p-6 text-center"
          >
            <X className="text-destructive mx-auto mb-3" size={48} />
            <h2 className="text-2xl font-black text-white mb-1">Out of Guesses!</h2>
            <p className="text-sm text-gray-400 mb-2">The answer was:</p>
            <p className="text-2xl font-black text-white">{feedback?.answer || 'Unknown'}</p>
            <p className="text-xs text-gray-500 mt-4">Try again tomorrow!</p>
            <button
              onClick={() => navigate('/dashboard')}
              className="mt-4 bg-destructive text-white px-6 py-2 rounded-sm font-bold uppercase text-sm hover:bg-red-700 transition-colors"
            >
              Return to Dashboard
            </button>
          </motion.div>
        ) : (
          <form onSubmit={handleSubmitGuess} className="space-y-3">
            <AnimatePresence>
              {feedback && !feedback.correct && feedback.error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="bg-destructive/20 border border-destructive/50 rounded-lg p-3 text-center"
                >
                  <p className="text-sm text-destructive">{feedback.error}</p>
                </motion.div>
              )}
              {feedback && !feedback.correct && !feedback.error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="bg-destructive/20 border border-destructive/50 rounded-lg p-3 text-center"
                >
                  <p className="text-sm text-white">
                    <X className="inline text-destructive mr-1" size={14} />
                    Wrong! A new club has been revealed.
                  </p>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={guess}
                onChange={(e) => setGuess(e.target.value)}
                placeholder="Enter player name..."
                className="flex-1 bg-card border-2 border-white/20 focus:border-neon-yellow rounded-lg px-4 py-3 text-white placeholder:text-gray-500 outline-none transition-colors"
                data-testid="guess-input"
                disabled={submitting}
                autoFocus
              />
              <button
                type="submit"
                disabled={!guess.trim() || submitting}
                className={`px-6 rounded-lg font-bold uppercase text-sm transition-all active:scale-95 ${
                  !guess.trim() || submitting
                    ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-neon-yellow to-orange-500 text-black hover:from-orange-500 hover:to-neon-yellow'
                }`}
                data-testid="submit-guess-btn"
              >
                {submitting ? '...' : 'Guess'}
              </button>
            </div>
            <p className="text-xs text-gray-500 text-center">
              <HelpCircle className="inline mr-1" size={12} />
              Each wrong guess reveals another club from their career
            </p>
          </form>
        )}
      </div>
    </Layout>
  );
}
