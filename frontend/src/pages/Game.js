import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, Trophy, ArrowLeft } from 'lucide-react';
import { Layout } from '../components/Layout';
import { useAuth } from '../context/AuthContext';
import { games, questions as questionsApi } from '../lib/api';

const TIMER_DURATION = 15;

export default function Game() {
  const { gameId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [game, setGame] = useState(null);
  const [gamePhase, setGamePhase] = useState('loading'); // loading, category_selection, question, feedback, round_summary, game_over
  const [categories, setCategories] = useState([]);
  const [currentQuestions, setCurrentQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [timeLeft, setTimeLeft] = useState(TIMER_DURATION);
  const [startTime, setStartTime] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const timerRef = useRef(null);

  useEffect(() => {
    loadGame();
    loadCategories();
  }, [gameId]);

  useEffect(() => {
    if (gamePhase === 'question' && startTime) {
      timerRef.current = setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000;
        const remaining = Math.max(0, TIMER_DURATION - elapsed);
        setTimeLeft(remaining);

        if (remaining === 0) {
          handleTimeout();
        }
      }, 100);

      return () => clearInterval(timerRef.current);
    }
  }, [gamePhase, startTime]);

  const loadGame = async () => {
    try {
      const response = await games.get(gameId);
      setGame(response.data);

      if (response.data.status === 'finished') {
        setGamePhase('game_over');
      } else if (!response.data.is_my_turn) {
        setGamePhase('waiting');
      } else {
        setGamePhase('category_selection');
      }
    } catch (error) {
      console.error('Failed to load game:', error);
      navigate('/dashboard');
    }
  };

  const loadCategories = async () => {
    try {
      const response = await questionsApi.categories();
      const allCategories = response.data;
      const randomCategories = allCategories.sort(() => 0.5 - Math.random()).slice(0, 3);
      setCategories(randomCategories);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const handleCategorySelect = async (category) => {
    try {
      const response = await games.selectCategory(gameId, category);
      setCurrentQuestions(response.data.questions);
      setCurrentQuestionIndex(0);
      setGamePhase('question');
      setStartTime(Date.now());
      setTimeLeft(TIMER_DURATION);
    } catch (error) {
      console.error('Failed to select category:', error);
    }
  };

  const handleAnswerSelect = async (option) => {
    if (selectedAnswer) return;

    clearInterval(timerRef.current);
    setSelectedAnswer(option);

    const timeTaken = (Date.now() - startTime) / 1000;
    const currentQuestion = currentQuestions[currentQuestionIndex];

    try {
      const response = await games.submitAnswer(gameId, {
        question_id: currentQuestion.id,
        selected_option: option,
        time_taken: timeTaken,
      });

      setFeedback(response.data);
      setGamePhase('feedback');

      setTimeout(() => {
        if (currentQuestionIndex < currentQuestions.length - 1) {
          setCurrentQuestionIndex(currentQuestionIndex + 1);
          setSelectedAnswer(null);
          setGamePhase('question');
          setStartTime(Date.now());
          setTimeLeft(TIMER_DURATION);
          setFeedback(null);
        } else {
          loadGame();
        }
      }, 2000);
    } catch (error) {
      console.error('Failed to submit answer:', error);
    }
  };

  const handleTimeout = () => {
    if (selectedAnswer) return;
    handleAnswerSelect('');
  };

  if (!game) {
    return (
      <Layout showNav={false}>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-gray-400">Loading game...</p>
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
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => navigate('/dashboard')}
              data-testid="back-btn"
              className="text-gray-400 hover:text-white"
            >
              <ArrowLeft size={24} />
            </button>
            <span className="text-sm text-gray-400 uppercase tracking-wider">Round {game.current_round}/6</span>
          </div>

          {/* Players */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <img src={user?.avatar} alt="You" className="w-12 h-12 rounded-full border-2 border-accent" />
              <div>
                <p className="font-bold text-white">You</p>
                <p className="text-3xl font-black tracking-tighter text-accent">{game.my_score}</p>
              </div>
            </div>

            <div className="text-center">
              <span className="text-gray-600 text-2xl">VS</span>
            </div>

            <div className="flex items-center gap-3 flex-row-reverse">
              <img src={game.player2.avatar} alt="Opponent" className="w-12 h-12 rounded-full border-2 border-gray-400" />
              <div className="text-right">
                <p className="font-bold text-white">{game.player2.username}</p>
                <p className="text-3xl font-black tracking-tighter text-gray-400">{game.opponent_score}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Game Content */}
        <div className="p-5">
          <AnimatePresence mode="wait">
            {gamePhase === 'category_selection' && (
              <motion.div
                key="categories"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <div className="text-center">
                  <h2 className="text-2xl font-extrabold tracking-tighter uppercase text-white mb-2">
                    Select Category
                  </h2>
                  <p className="text-sm text-gray-400">Choose your trivia topic</p>
                </div>

                <div className="space-y-3">
                  {categories.map((category, index) => (
                    <motion.button
                      key={category}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      onClick={() => handleCategorySelect(category)}
                      data-testid={`category-${category}`}
                      className="w-full bg-card border border-white/10 hover:border-primary/50 rounded-lg p-6 text-left transition-all active:scale-[0.98]"
                    >
                      <p className="text-xl font-bold uppercase tracking-tight text-white">{category}</p>
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            )}

            {gamePhase === 'question' && currentQuestions[currentQuestionIndex] && (
              <motion.div
                key="question"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 1.05 }}
                className="space-y-6"
              >
                {/* Timer */}
                <div className="bg-card border border-white/10 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Clock className="text-primary" size={20} />
                      <span className="text-sm text-gray-400 uppercase tracking-wider">Time</span>
                    </div>
                    <span className="text-2xl font-black tracking-tighter text-primary">
                      {Math.ceil(timeLeft)}s
                    </span>
                  </div>
                  <div className="w-full bg-black/50 rounded-full h-2 overflow-hidden">
                    <motion.div
                      className="h-full bg-primary"
                      initial={{ width: '100%' }}
                      animate={{ width: `${(timeLeft / TIMER_DURATION) * 100}%` }}
                      transition={{ duration: 0.1 }}
                    />
                  </div>
                </div>

                {/* Question */}
                <div className="bg-card border border-white/10 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs text-gray-500 uppercase tracking-wider">
                      Question {currentQuestionIndex + 1}/3
                    </span>
                  </div>
                  <p className="text-xl font-bold leading-relaxed text-white">
                    {currentQuestions[currentQuestionIndex].question_text}
                  </p>
                </div>

                {/* Options */}
                <div className="grid grid-cols-1 gap-3">
                  {['option_a', 'option_b', 'option_c', 'option_d'].map((optionKey, index) => {
                    const optionLabel = String.fromCharCode(65 + index);
                    const optionValue = currentQuestions[currentQuestionIndex][optionKey];
                    return (
                      <motion.button
                        key={optionKey}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        onClick={() => handleAnswerSelect(optionLabel)}
                        data-testid={`option-${optionLabel}`}
                        disabled={!!selectedAnswer}
                        className="bg-black/40 border-2 border-white/20 hover:border-primary/50 rounded-lg p-4 text-left transition-all active:scale-[0.98] disabled:opacity-50"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary flex items-center justify-center flex-shrink-0">
                            <span className="font-bold text-primary">{optionLabel}</span>
                          </div>
                          <p className="text-white font-medium">{optionValue}</p>
                        </div>
                      </motion.button>
                    );
                  })}
                </div>
              </motion.div>
            )}

            {gamePhase === 'feedback' && feedback && (
              <motion.div
                key="feedback"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center space-y-6"
              >
                <div className={`w-32 h-32 rounded-full mx-auto flex items-center justify-center ${
                  feedback.is_correct ? 'bg-accent/20 border-4 border-accent' : 'bg-destructive/20 border-4 border-destructive'
                }`}>
                  <span className="text-6xl">
                    {feedback.is_correct ? '✓' : '✗'}
                  </span>
                </div>

                <div>
                  <h2 className={`text-3xl font-extrabold tracking-tighter uppercase ${
                    feedback.is_correct ? 'text-accent' : 'text-destructive'
                  }`}>
                    {feedback.is_correct ? 'Correct!' : 'Wrong'}
                  </h2>
                  <p className="text-2xl font-black tracking-tighter text-primary mt-2">
                    +{feedback.score} points
                  </p>
                </div>
              </motion.div>
            )}

            {gamePhase === 'waiting' && (
              <motion.div
                key="waiting"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-12"
              >
                <div className="animate-pulse mb-6">
                  <Clock className="text-primary mx-auto" size={64} />
                </div>
                <h2 className="text-2xl font-extrabold tracking-tighter uppercase text-white mb-2">
                  Opponent's Turn
                </h2>
                <p className="text-gray-400">Waiting for {game.player2.username} to play...</p>
              </motion.div>
            )}

            {gamePhase === 'game_over' && (
              <motion.div
                key="gameover"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center space-y-8"
              >
                <Trophy className="text-primary mx-auto" size={96} />
                
                <div>
                  <h2 className="text-4xl font-extrabold tracking-tighter uppercase text-primary mb-2">
                    {game.winner_id === user?.user_id ? 'Victory!' : 'Defeat'}
                  </h2>
                  <p className="text-gray-400">Game Over</p>
                </div>

                <div className="bg-card border border-white/10 rounded-lg p-6">
                  <div className="text-5xl font-black tracking-tighter mb-2">
                    <span className={game.my_score > game.opponent_score ? 'text-accent' : 'text-gray-400'}>
                      {game.my_score}
                    </span>
                    <span className="text-gray-600 mx-2">-</span>
                    <span className={game.opponent_score > game.my_score ? 'text-accent' : 'text-gray-400'}>
                      {game.opponent_score}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500">Final Score</p>
                </div>

                <button
                  onClick={() => navigate('/dashboard')}
                  data-testid="return-dashboard-btn"
                  className="bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-8 rounded-sm font-bold uppercase tracking-wider shadow-[0_0_15px_rgba(251,191,36,0.3)] transition-all active:scale-95"
                >
                  Return to Dashboard
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </Layout>
  );
}
