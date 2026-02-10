import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, Trophy, ArrowLeft, Brain, Eye } from 'lucide-react';
import { Layout } from '../components/Layout';
import { PoweredByScore90 } from '../components/Score90Logo';
import { useAuth } from '../context/AuthContext';
import { TieredAvatar } from '../components/TieredAvatar';
import { InlineAd, ResultsAd } from '../components/AdWidget';
import { InstagramCarousel } from '../components/InstagramCarousel';
import { games, questions as questionsApi, challengesApi } from '../lib/api';

const TIMER_DURATION = 15;
const BOT_USERNAME = 'TheScore90Bot';

function formatCountdown(ms) {
  if (ms <= 0) return 'Time up!';
  const totalSecs = Math.floor(ms / 1000);
  const h = Math.floor(totalSecs / 3600);
  const m = Math.floor((totalSecs % 3600) / 60);
  const s = totalSecs % 60;
  if (h > 0) return `${h}h ${m}m ${s}s`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

export default function Game() {
  const { gameId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [game, setGame] = useState(null);
  const [gamePhase, setGamePhase] = useState('loading');
  const [categories, setCategories] = useState([]);
  const [currentQuestions, setCurrentQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [timeLeft, setTimeLeft] = useState(TIMER_DURATION);
  const [startTime, setStartTime] = useState(null);
  const [feedback, setFeedback] = useState(null);
  // Turn deadline countdown
  const [turnTimeLeft, setTurnTimeLeft] = useState(null);
  // Bot play state
  const [botAnswers, setBotAnswers] = useState(null);
  const [botAnswerIndex, setBotAnswerIndex] = useState(0);
  const [botPhaseStep, setBotPhaseStep] = useState('idle'); // idle | thinking | answered
  const [bkUpdate, setBkUpdate] = useState(null); // {old, new, delta}
  const [creditsWon, setCreditsWon] = useState(null);
  const [tierUpdate, setTierUpdate] = useState(null);
  const [achievementsEarned, setAchievementsEarned] = useState([]);
  const [botCountdown, setBotCountdown] = useState(45);
  // Playback state
  const [playbackAnswers, setPlaybackAnswers] = useState(null);
  const [playbackIndex, setPlaybackIndex] = useState(0);

  const timerRef = useRef(null);
  const turnTimerRef = useRef(null);

  const loadGame = useCallback(async () => {
    try {
      const response = await games.get(gameId);
      const g = response.data;
      setGame(g);

      const isSolo = g.player1?.user_id === g.player2?.user_id;

      if (g.status === 'finished') {
        setGamePhase('game_over');
      } else if (!g.is_my_turn && !isSolo) {
        // Check if bot game - show countdown with Instagram carousel before bot plays
        if (g.is_bot_game) {
          setBotCountdown(5); // Short countdown to show carousel
          setGamePhase('bot_countdown');
        } else {
          setGamePhase('waiting');
        }
      } else {
        const currentRound = g.rounds?.find(r => r.round_number === g.current_round);
        // Check if there are opponent answers to playback first (not for solo games)
        if (!isSolo) {
          const prevRound = g.rounds?.find(r => r.round_number === g.current_round - 1);
          if (prevRound && prevRound.opponent_answers && prevRound.opponent_answers.length > 0 && prevRound.questions?.length > 0) {
            setPlaybackAnswers({ answers: prevRound.opponent_answers, questions: prevRound.questions, round: prevRound.round_number });
            setPlaybackIndex(0);
            setGamePhase('playback');
            return;
          }
        }

        if (currentRound && currentRound.category_selected && currentRound.questions?.length > 0) {
          // Round has category but user may need to resume answering
          const myAnswered = (currentRound.my_answers || []).length;
          if (myAnswered < 3) {
            // Resume: load questions and skip already answered ones
            try {
              const catResp = await games.selectCategory(gameId, currentRound.category_selected);
              setCurrentQuestions(catResp.data.questions);
              setCurrentQuestionIndex(myAnswered);
              setSelectedAnswer(null);
              setFeedback(null);
              setGamePhase('question');
              setStartTime(Date.now());
              setTimeLeft(TIMER_DURATION);
            } catch {
              // If select-category fails, just go to category selection
              loadCategories();
              setGamePhase('category_selection');
            }
          } else {
            // All answers submitted for this round, waiting for next phase
            if (isSolo) {
              // Solo game: auto-advance to next category
              setSelectedAnswer(null);
              setFeedback(null);
              setCurrentQuestions([]);
              setCurrentQuestionIndex(0);
              handleCategorySelect('Club');
            } else {
              setGamePhase('waiting');
            }
          }
        } else {
          // Fresh round - reset all question state
          setSelectedAnswer(null);
          setFeedback(null);
          setCurrentQuestions([]);
          setCurrentQuestionIndex(0);
          
          // For Club Challenge mode, auto-select "Club" category
          if (g.status === 'club_challenge') {
            handleCategorySelect('Club');
          } else if (g.challenge_id) {
            // Challenge game: auto-select the challenge topic
            try {
              const chRes = await challengesApi.weekly();
              const ch = chRes.data.find(c => c.id === g.challenge_id);
              if (ch) {
                handleCategorySelect(ch.topic);
              } else {
                await loadCategories();
                setGamePhase('category_selection');
              }
            } catch {
              await loadCategories();
              setGamePhase('category_selection');
            }
          } else {
            await loadCategories();
            setGamePhase('category_selection');
          }
        }
      }
    } catch (error) {
      console.error('Failed to load game:', error);
      navigate('/dashboard');
    }
  }, [gameId, navigate]);

  useEffect(() => {
    loadGame();
  }, [gameId, loadGame]);

  // 3-hour turn deadline countdown
  useEffect(() => {
    if (gamePhase === 'waiting' && game?.turn_deadline) {
      const update = () => {
        const remaining = new Date(game.turn_deadline).getTime() - Date.now();
        setTurnTimeLeft(Math.max(0, remaining));
      };
      update();
      turnTimerRef.current = setInterval(update, 1000);
      return () => clearInterval(turnTimerRef.current);
    }
    return () => clearInterval(turnTimerRef.current);
  }, [gamePhase, game]);

  // Per-question timer
  useEffect(() => {
    if (gamePhase === 'question' && startTime) {
      timerRef.current = setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000;
        const remaining = Math.max(0, TIMER_DURATION - elapsed);
        setTimeLeft(remaining);
        if (remaining === 0) handleTimeout();
      }, 100);
      return () => clearInterval(timerRef.current);
    }
  }, [gamePhase, startTime]);

  // Bot countdown (45s) then trigger bot play
  useEffect(() => {
    if (gamePhase === 'bot_countdown') {
      const interval = setInterval(() => {
        setBotCountdown(prev => {
          if (prev <= 1) {
            clearInterval(interval);
            triggerBotPlay();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [gamePhase]);

  // Bot live answer animation
  useEffect(() => {
    if (gamePhase === 'bot_live' && botAnswers && botAnswerIndex < botAnswers.length) {
      setBotPhaseStep('thinking');
      const thinkTime = (botAnswers[botAnswerIndex].time_taken || 5) * 1000;
      const thinkTimer = setTimeout(() => {
        setBotPhaseStep('answered');
        const showTimer = setTimeout(() => {
          if (botAnswerIndex < botAnswers.length - 1) {
            setBotAnswerIndex(prev => prev + 1);
            setBotPhaseStep('thinking');
          } else {
            // Bot done, reload game
            setTimeout(() => loadGame(), 1000);
          }
        }, 2000);
        return () => clearTimeout(showTimer);
      }, Math.min(thinkTime, 4000)); // Cap visual delay at 4s for UX
      return () => clearTimeout(thinkTimer);
    }
  }, [gamePhase, botAnswers, botAnswerIndex, loadGame]);

  const triggerBotPlay = async () => {
    try {
      const response = await games.botPlay(gameId);
      if (response.data.ball_knowledge_update) {
        setBkUpdate(response.data.ball_knowledge_update);
      }
      if (response.data.credits_won) {
        setCreditsWon(response.data.credits_won);
      }
      if (response.data.tier_update) {
        setTierUpdate(response.data.tier_update);
      }
      if (response.data.achievements_earned) {
        setAchievementsEarned(prev => [...prev, ...response.data.achievements_earned]);
      }
      setBotAnswers(response.data.bot_answers);
      setBotAnswerIndex(0);
      setGamePhase('bot_live');
    } catch (error) {
      console.error('Bot play failed:', error);
      loadGame();
    }
  };

  const loadCategories = async () => {
    try {
      const response = await questionsApi.randomCategories();
      setCategories(response.data);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const handleCategorySelect = async (category) => {
    try {
      const response = await games.selectCategory(gameId, category);
      setCurrentQuestions(response.data.questions);
      setCurrentQuestionIndex(0);
      setSelectedAnswer(null);
      setFeedback(null);
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
    const qIndex = currentQuestionIndex; // Capture index for feedback

    try {
      const response = await games.submitAnswer(gameId, {
        question_id: currentQuestion.id,
        selected_option: option,
        time_taken: timeTaken,
      });

      if (response.data.ball_knowledge_update) {
        setBkUpdate(response.data.ball_knowledge_update);
      }
      if (response.data.achievements_earned) {
        setAchievementsEarned(prev => [...prev, ...response.data.achievements_earned]);
      }

      setFeedback({ ...response.data, _questionIndex: qIndex });
      setGamePhase('feedback');

      setTimeout(() => {
        if (qIndex < currentQuestions.length - 1) {
          setCurrentQuestionIndex(qIndex + 1);
          setSelectedAnswer(null);
          setGamePhase('question');
          setStartTime(Date.now());
          setTimeLeft(TIMER_DURATION);
          setFeedback(null);
        } else {
          // Turn done, reload to check state
          loadGame();
        }
      }, 2500);
    } catch (error) {
      console.error('Failed to submit answer:', error);
      // Reload game on error to recover
      loadGame();
    }
  };

  const handleTimeout = () => {
    if (selectedAnswer) return;
    // Submit timeout as an intentionally wrong answer
    handleAnswerSelect('X');
  };

  const advancePlayback = async () => {
    if (playbackIndex < (playbackAnswers?.answers?.length || 0) - 1) {
      setPlaybackIndex(prev => prev + 1);
    } else {
      // Done playback, reset all round state and go to category selection
      setPlaybackAnswers(null);
      setPlaybackIndex(0);
      setSelectedAnswer(null);
      setFeedback(null);
      setCurrentQuestions([]);
      setCurrentQuestionIndex(0);
      setBotAnswers(null);
      setBotAnswerIndex(0);
      setBotPhaseStep('idle');
      await loadCategories();
      setGamePhase('category_selection');
    }
  };

  if (!game) {
    return (
      <Layout showNav={false}>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="relative w-16 h-16 mx-auto mb-4">
              <div className="absolute inset-0 border-4 border-neon-blue/30 rounded-full" />
              <div className="absolute inset-0 border-4 border-neon-pink border-t-transparent rounded-full animate-spin" />
            </div>
            <p className="text-gray-400">Loading game...</p>
          </div>
        </div>
      </Layout>
    );
  }

  const opponent = game.player2;

  return (
    <Layout showNav={false}>
      <div className="min-h-screen">
        {/* Header */}
        <div className="p-5 border-b border-white/10 bg-card/50 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-4">
            <button onClick={() => navigate('/dashboard')} data-testid="back-btn" className="text-gray-400 hover:text-neon-blue transition-colors">
              <ArrowLeft size={24} />
            </button>
            <span className="text-sm text-gray-400 uppercase tracking-wider font-bold">Round {game.current_round}/6</span>
            <PoweredByScore90 size="xs" />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <TieredAvatar src={user?.avatar} alt="You" tier={user?.player_tier || 1} size="md" />
              <div>
                <p className="font-bold text-white text-sm">You</p>
                <p className="text-3xl font-black tracking-tighter text-neon-yellow">{game.my_score}</p>
              </div>
            </div>
            <span className="text-gray-600 text-2xl font-black">VS</span>
            <div className="flex items-center gap-3 flex-row-reverse">
              <TieredAvatar src={opponent?.avatar} alt="Opponent" tier={opponent?.player_tier || 1} size="md" />
              <div className="text-right">
                <p className="font-bold text-white text-sm">{opponent?.username || 'Waiting...'}</p>
                <p className="text-3xl font-black tracking-tighter text-gray-400">{game.opponent_score}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="p-5">
          <AnimatePresence mode="wait">
            {/* CATEGORY SELECTION */}
            {gamePhase === 'category_selection' && (
              <motion.div key="categories" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="space-y-6">
                <div className="text-center">
                  <h2 className="text-2xl font-extrabold tracking-tighter uppercase text-white mb-2">Select Category</h2>
                  <p className="text-sm text-gray-400">Choose your trivia topic</p>
                </div>
                {categories.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="relative w-12 h-12 mx-auto mb-3">
                      <div className="absolute inset-0 border-4 border-neon-blue/30 rounded-full" />
                      <div className="absolute inset-0 border-4 border-neon-pink border-t-transparent rounded-full animate-spin" />
                    </div>
                    <p className="text-gray-400 text-sm">Loading categories...</p>
                  </div>
                ) : (
                  <div className="space-y-3" data-testid="category-list">
                    {categories.map((category, index) => {
                      const colors = ['border-neon-blue/50 hover:border-neon-blue shadow-neon-blue/30', 'border-neon-pink/50 hover:border-neon-pink shadow-neon-pink/30', 'border-neon-yellow/50 hover:border-neon-yellow shadow-neon-yellow/30'];
                      return (
                        <motion.button key={category} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.1 }}
                          onClick={() => handleCategorySelect(category)} data-testid={`category-${category}`}
                          className={`w-full bg-card border-2 ${colors[index]} rounded-lg p-6 text-left transition-all active:scale-[0.98] hover:shadow-lg`}>
                          <p className="text-xl font-bold uppercase tracking-tight text-white">{category}</p>
                        </motion.button>
                      );
                    })}
                  </div>
                )}
                {/* Unobtrusive ad during category selection */}
                <div className="flex justify-center pt-2">
                  <InlineAd type="flashscore" />
                </div>
              </motion.div>
            )}

            {/* QUESTION */}
            {gamePhase === 'question' && currentQuestions[currentQuestionIndex] && (
              <motion.div key="question" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 1.05 }} className="space-y-6">
                <div className="bg-card border-2 border-neon-blue/30 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Clock className="text-neon-blue" size={20} />
                      <span className="text-sm text-gray-400 uppercase tracking-wider">Time</span>
                    </div>
                    <span className={`text-2xl font-black tracking-tighter ${timeLeft <= 5 ? 'text-destructive' : 'text-neon-blue'}`}>{Math.ceil(timeLeft)}s</span>
                  </div>
                  <div className="w-full bg-black/50 rounded-full h-2 overflow-hidden">
                    <motion.div className={`h-full ${timeLeft <= 5 ? 'bg-destructive' : 'bg-neon-blue'}`}
                      initial={{ width: '100%' }} animate={{ width: `${(timeLeft / TIMER_DURATION) * 100}%` }} transition={{ duration: 0.1 }} />
                  </div>
                </div>

                <div className="bg-card border-2 border-neon-pink/30 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs text-gray-500 uppercase tracking-wider">Question {currentQuestionIndex + 1}/3</span>
                    <Brain className="text-neon-yellow" size={20} />
                  </div>
                  <p className="text-xl font-bold leading-relaxed text-white">{currentQuestions[currentQuestionIndex].question_text}</p>
                </div>

                <div className="grid grid-cols-1 gap-3">
                  {['option_a', 'option_b', 'option_c', 'option_d'].map((optionKey, index) => {
                    const label = String.fromCharCode(65 + index);
                    const value = currentQuestions[currentQuestionIndex][optionKey];
                    const clr = ['neon-blue', 'neon-pink', 'neon-yellow', 'electric-purple'][index];
                    return (
                      <motion.button key={optionKey} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.05 }}
                        onClick={() => handleAnswerSelect(label)} data-testid={`option-${label}`} disabled={!!selectedAnswer}
                        className={`bg-black/40 border-2 border-${clr}/30 hover:border-${clr} rounded-lg p-4 text-left transition-all active:scale-[0.98] disabled:opacity-50`}>
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-full bg-${clr}/20 border-2 border-${clr} flex items-center justify-center flex-shrink-0`}>
                            <span className={`font-bold text-${clr}`}>{label}</span>
                          </div>
                          <p className="text-white font-medium">{value}</p>
                        </div>
                      </motion.button>
                    );
                  })}
                </div>
              </motion.div>
            )}

            {/* FEEDBACK */}
            {gamePhase === 'feedback' && feedback && (
              <motion.div key="feedback" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="text-center space-y-6 py-8" data-testid="answer-feedback">
                <div className={`w-32 h-32 rounded-full mx-auto flex items-center justify-center ${feedback.is_correct ? 'bg-neon-yellow/20 border-4 border-neon-yellow shadow-neon-yellow' : 'bg-destructive/20 border-4 border-destructive'}`}>
                  <span className="text-6xl font-black">{feedback.is_correct ? '\u2713' : '\u2717'}</span>
                </div>
                <div>
                  <h2 className={`text-3xl font-extrabold tracking-tighter uppercase ${feedback.is_correct ? 'text-neon-yellow' : 'text-destructive'}`} data-testid="feedback-result">{feedback.is_correct ? 'Correct!' : 'Wrong'}</h2>
                  <p className="text-2xl font-black tracking-tighter text-neon-blue mt-2">+{feedback.score} points</p>
                  {!feedback.is_correct && feedback.correct_option && currentQuestions[feedback._questionIndex ?? currentQuestionIndex] && (
                    <p className="text-sm text-gray-400 mt-3" data-testid="correct-answer-reveal">
                      Correct answer: <span className="text-neon-yellow font-bold">{currentQuestions[feedback._questionIndex ?? currentQuestionIndex][`option_${feedback.correct_option.toLowerCase()}`]}</span> ({feedback.correct_option})
                    </p>
                  )}
                </div>
              </motion.div>
            )}

            {/* WAITING (Real Player) - 3hr countdown */}
            {gamePhase === 'waiting' && (
              <motion.div key="waiting" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                <div className="text-center">
                  <div className="relative w-16 h-16 mx-auto mb-4">
                    <div className="absolute inset-0 border-4 border-neon-blue/30 rounded-full" />
                    <div className="absolute inset-0 border-4 border-neon-pink border-t-transparent rounded-full animate-spin" />
                  </div>
                  <h2 className="text-xl font-extrabold tracking-tighter uppercase text-white mb-1">Opponent's Turn</h2>
                  <p className="text-sm text-gray-400 mb-4">Waiting for {opponent?.username || 'opponent'} to play...</p>
                  {turnTimeLeft !== null && (
                    <div className="bg-card border-2 border-neon-yellow/30 rounded-lg p-3 inline-block shadow-neon-yellow" data-testid="turn-countdown">
                      <Clock className="text-neon-yellow mx-auto mb-1" size={20} />
                      <p className="text-xl font-black tracking-tighter text-neon-yellow">{formatCountdown(turnTimeLeft)}</p>
                      <p className="text-[10px] text-gray-500 uppercase mt-1">Time remaining</p>
                    </div>
                  )}
                </div>
                
                {/* Instagram Carousel - shown while waiting */}
                <InstagramCarousel autoPlay={true} interval={4000} />
              </motion.div>
            )}

            {/* BOT COUNTDOWN (45s) */}
            {gamePhase === 'bot_countdown' && (
              <motion.div key="bot_countdown" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                <div className="text-center">
                  <img src={opponent?.avatar} alt={BOT_USERNAME} className="w-16 h-16 rounded-full border-4 border-neon-blue mx-auto mb-3 shadow-neon-blue" />
                  <h2 className="text-xl font-extrabold tracking-tighter uppercase text-white mb-1">{BOT_USERNAME}</h2>
                  <p className="text-sm text-gray-400 mb-4">is preparing to answer...</p>
                  <div className="bg-card border-2 border-neon-blue/30 rounded-lg p-4 max-w-xs mx-auto shadow-neon-blue" data-testid="bot-countdown">
                    <p className="text-4xl font-black tracking-tighter text-neon-blue mb-2">{botCountdown}s</p>
                    <div className="w-full bg-black/50 rounded-full h-2 overflow-hidden">
                      <motion.div className="h-full bg-neon-blue" initial={{ width: '100%' }} animate={{ width: `${(botCountdown / 45) * 100}%` }} transition={{ duration: 0.5 }} />
                    </div>
                    <p className="text-xs text-gray-500 uppercase mt-2">Bot is thinking</p>
                  </div>
                  <button onClick={() => { setBotCountdown(0); triggerBotPlay(); }} data-testid="skip-bot-wait"
                    className="mt-3 text-xs text-neon-pink hover:text-neon-yellow transition-colors underline">
                    Skip wait
                  </button>
                </div>
                
                {/* Instagram Carousel - shown while bot is "thinking" */}
                <InstagramCarousel autoPlay={true} interval={4000} />
              </motion.div>
            )}

            {/* BOT LIVE ANSWERING */}
            {gamePhase === 'bot_live' && botAnswers && botAnswers[botAnswerIndex] && (
              <motion.div key="bot_live" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                <div className="flex items-center gap-3 mb-2">
                  <img src={opponent?.avatar} alt={BOT_USERNAME} className="w-10 h-10 rounded-full border-2 border-neon-blue" />
                  <div>
                    <p className="text-sm font-bold text-neon-blue uppercase">{BOT_USERNAME} is answering</p>
                    <p className="text-xs text-gray-500">Question {botAnswerIndex + 1}/3</p>
                  </div>
                  <Eye className="text-neon-pink ml-auto" size={20} />
                </div>

                <div className="bg-card border-2 border-neon-blue/30 rounded-lg p-6">
                  <p className="text-lg font-bold leading-relaxed text-white">{botAnswers[botAnswerIndex].question_text}</p>
                </div>

                <div className="grid grid-cols-1 gap-3">
                  {['A', 'B', 'C', 'D'].map((label) => {
                    const optKey = `option_${label.toLowerCase()}`;
                    const botAnswer = botAnswers[botAnswerIndex];
                    const isSelected = botPhaseStep === 'answered' && botAnswer.selected_option === label;
                    const isCorrect = botPhaseStep === 'answered' && botAnswer.correct_option === label;

                    let borderClass = 'border-white/10';
                    if (botPhaseStep === 'answered') {
                      if (isCorrect) borderClass = 'border-neon-yellow bg-neon-yellow/10';
                      else if (isSelected && !botAnswer.is_correct) borderClass = 'border-destructive bg-destructive/10';
                    }

                    return (
                      <div key={label} className={`border-2 rounded-lg p-4 transition-all ${borderClass}`}>
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-white/10 border-2 border-white/20 flex items-center justify-center flex-shrink-0">
                            <span className="font-bold text-white">{label}</span>
                          </div>
                          <p className="text-white font-medium flex-1">{botAnswer[optKey]}</p>
                          {botPhaseStep === 'answered' && isSelected && (
                            <div className={`w-6 h-6 rounded-full flex items-center justify-center ${botAnswer.is_correct ? 'bg-neon-yellow' : 'bg-destructive'}`}>
                              <span className="text-xs font-bold text-white">{botAnswer.is_correct ? '\u2713' : '\u2717'}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>

                {botPhaseStep === 'thinking' && (
                  <div className="text-center">
                    <div className="inline-flex items-center gap-2 bg-card border border-neon-blue/30 rounded-full px-4 py-2">
                      <div className="w-2 h-2 bg-neon-blue rounded-full animate-pulse" />
                      <div className="w-2 h-2 bg-neon-blue rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
                      <div className="w-2 h-2 bg-neon-blue rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
                      <span className="text-xs text-gray-400 ml-1">Thinking...</span>
                    </div>
                  </div>
                )}

                {botPhaseStep === 'answered' && (
                  <div className="text-center">
                    <p className={`text-lg font-bold ${botAnswers[botAnswerIndex].is_correct ? 'text-neon-yellow' : 'text-destructive'}`}>
                      {botAnswers[botAnswerIndex].is_correct ? `Correct! +${botAnswers[botAnswerIndex].score}` : 'Wrong!'}
                    </p>
                  </div>
                )}
              </motion.div>
            )}

            {/* OPPONENT ANSWER PLAYBACK */}
            {gamePhase === 'playback' && playbackAnswers && playbackAnswers.answers[playbackIndex] && (
              <motion.div key="playback" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                <div className="flex items-center gap-3 mb-2">
                  <img src={opponent?.avatar} alt="Opponent" className="w-10 h-10 rounded-full border-2 border-neon-pink" />
                  <div>
                    <p className="text-sm font-bold text-neon-pink uppercase flex items-center gap-2">
                      <Eye size={16} /> {opponent?.username}'s answers - Round {playbackAnswers.round}
                    </p>
                    <p className="text-xs text-gray-500">Question {playbackIndex + 1}/{playbackAnswers.answers.length}</p>
                  </div>
                </div>

                <PlaybackCard
                  answer={playbackAnswers.answers[playbackIndex]}
                  questionId={playbackAnswers.questions[playbackIndex]}
                  onNext={advancePlayback}
                  isLast={playbackIndex >= playbackAnswers.answers.length - 1}
                />
              </motion.div>
            )}

            {/* GAME OVER */}
            {gamePhase === 'game_over' && (
              <motion.div key="gameover" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="text-center space-y-8 py-8" data-testid="game-over-screen">
                <Trophy className={`mx-auto ${game.winner_id === user?.user_id ? 'text-neon-yellow' : 'text-gray-500'}`} size={96} />
                <div>
                  <h2 className={`text-4xl font-extrabold tracking-tighter uppercase mb-2 ${game.winner_id === user?.user_id ? 'text-neon-yellow' : 'text-destructive'}`}>
                    {game.winner_id === user?.user_id ? 'Victory!' : 'Defeat'}
                  </h2>
                </div>
                <div className="bg-card border-2 border-neon-blue/30 rounded-lg p-6 shadow-neon-blue">
                  <div className="text-5xl font-black tracking-tighter mb-2">
                    <span className={game.my_score > game.opponent_score ? 'text-neon-yellow' : 'text-gray-400'}>{game.my_score}</span>
                    <span className="text-gray-600 mx-2">-</span>
                    <span className={game.opponent_score > game.my_score ? 'text-neon-yellow' : 'text-gray-400'}>{game.opponent_score}</span>
                  </div>
                  <p className="text-sm text-gray-500">Final Score</p>
                </div>
                {bkUpdate && bkUpdate.delta !== 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-card border-2 border-neon-pink/30 rounded-lg p-5"
                    data-testid="bk-update"
                  >
                    <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Ball Knowledge</p>
                    <div className="flex items-center justify-center gap-3">
                      <span className="text-2xl font-black text-gray-400">{bkUpdate.old}</span>
                      <span className={`text-2xl font-black ${bkUpdate.delta > 0 ? 'text-neon-yellow' : 'text-destructive'}`}>
                        {bkUpdate.delta > 0 ? '+' : ''}{bkUpdate.delta}
                      </span>
                      <span className="text-2xl font-black text-white">{bkUpdate.new}</span>
                    </div>
                  </motion.div>
                )}
                {creditsWon && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.5 }}
                    className="bg-card border-2 border-neon-yellow/50 rounded-lg p-5"
                    data-testid="credits-won"
                  >
                    <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Credits Won</p>
                    <p className="text-3xl font-black text-neon-yellow">+{creditsWon}</p>
                  </motion.div>
                )}
                {tierUpdate && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.7 }}
                    className="bg-card border-2 border-purple-500/50 rounded-lg p-5"
                    data-testid="tier-update"
                  >
                    <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Tier Up!</p>
                    <div className="flex items-center justify-center gap-3">
                      <span className="text-2xl font-black text-gray-400">Tier {tierUpdate.old_tier}</span>
                      <span className="text-2xl font-black text-purple-400">&rarr;</span>
                      <span className="text-2xl font-black text-purple-300">Tier {tierUpdate.new_tier}</span>
                    </div>
                    {tierUpdate.credits_awarded > 0 && (
                      <p className="text-sm text-neon-yellow mt-2 font-bold">+{tierUpdate.credits_awarded} credits reward!</p>
                    )}
                  </motion.div>
                )}
                {achievementsEarned.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.9 }}
                    className="bg-card border-2 border-neon-pink/50 rounded-lg p-5"
                    data-testid="achievements-earned"
                  >
                    <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">🏆 Achievements Unlocked!</p>
                    <div className="space-y-2">
                      {achievementsEarned.map((ach, idx) => (
                        <div key={ach.id || idx} className="flex items-center gap-3 bg-black/30 rounded-lg p-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-neon-pink to-neon-yellow flex items-center justify-center">
                            <Trophy size={20} className="text-white" />
                          </div>
                          <div className="flex-1 text-left">
                            <p className="text-sm font-bold text-white">{ach.name}</p>
                            <p className="text-xs text-gray-400">{ach.description}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
                {/* Sponsored ad on game over screen */}
                <ResultsAd className="mt-4" />
                <button onClick={() => navigate('/dashboard')} data-testid="return-dashboard-btn"
                  className="bg-gradient-to-r from-neon-blue to-neon-pink hover:from-neon-pink hover:to-neon-yellow h-12 px-8 rounded-sm font-bold uppercase tracking-wider shadow-neon-blue hover:shadow-neon-pink transition-all active:scale-95 text-white">
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

function PlaybackCard({ answer, onNext, isLast }) {
  // answer has: question_id, selected_option, is_correct, time_taken, score
  // We don't have the full question text in the playback data from the backend, so show what we have
  return (
    <div className="space-y-4">
      <div className="bg-card border-2 border-neon-pink/30 rounded-lg p-5">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs text-gray-500">Time: {answer.time_taken?.toFixed(1)}s</span>
          <span className={`text-sm font-bold ${answer.is_correct ? 'text-neon-yellow' : 'text-destructive'}`}>
            {answer.is_correct ? `+${answer.score} pts` : '+0 pts'}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl font-black ${
            answer.is_correct ? 'bg-neon-yellow/20 border-2 border-neon-yellow text-neon-yellow' : 'bg-destructive/20 border-2 border-destructive text-destructive'
          }`}>
            {answer.selected_option}
          </div>
          <div className="flex-1">
            <p className="text-white font-bold">
              Selected: <span className={answer.is_correct ? 'text-neon-yellow' : 'text-destructive'}>Option {answer.selected_option}</span>
            </p>
            <p className="text-xs text-gray-500">
              {answer.is_correct ? 'Answered correctly' : `Correct answer was ${answer.correct_option || '?'}`}
            </p>
          </div>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${answer.is_correct ? 'bg-neon-yellow' : 'bg-destructive'}`}>
            <span className="text-white text-sm font-bold">{answer.is_correct ? '\u2713' : '\u2717'}</span>
          </div>
        </div>
      </div>

      <button onClick={onNext} data-testid="playback-next-btn"
        className="w-full bg-gradient-to-r from-neon-pink to-electric-purple hover:from-electric-purple hover:to-neon-pink h-11 px-6 rounded-sm font-bold uppercase tracking-wider text-white transition-all active:scale-95">
        {isLast ? 'Your Turn' : 'Next Answer'}
      </button>
    </div>
  );
}
