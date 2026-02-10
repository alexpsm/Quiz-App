import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { TieredAvatar } from '../components/TieredAvatar';
import { Brain, Clock, Play, Users, Globe, Trophy, Shield, Swords, ChevronDown, ChevronUp } from 'lucide-react';
import { Layout } from '../components/Layout';
import { useAuth } from '../context/AuthContext';
import { PoweredByScore90 } from '../components/Score90Logo';
import { games, users } from '../lib/api';
import api from '../lib/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, checkAuth } = useAuth();
  const [activeGames, setActiveGames] = useState([]);
  const [ranks, setRanks] = useState(null);
  const [clubWar, setClubWar] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAllGames, setShowAllGames] = useState(false);

  useEffect(() => {
    checkAuth();
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [gamesRes, rankRes, warRes] = await Promise.allSettled([
        games.list(),
        users.myRank(),
        api.get('/club-wars/current')
      ]);
      if (gamesRes.status === 'fulfilled') setActiveGames(gamesRes.value.data);
      if (rankRes.status === 'fulfilled') setRanks(rankRes.value.data);
      if (warRes.status === 'fulfilled') setClubWar(warRes.value.data);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickPlay = async () => {
    try {
      const response = await games.quickPlay();
      navigate(`/game/${response.data.game_id}`);
    } catch (error) {
      console.error('Quick play failed:', error);
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

  const handleClubWarContribute = async () => {
    try {
      const response = await api.post('/club-wars/contribute');
      navigate(`/game/${response.data.game_id}`);
    } catch (error) {
      console.error('Club War contribution failed:', error);
    }
  };

  return (
    <Layout>
      <div className="p-5 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-extrabold tracking-tighter uppercase text-transparent bg-clip-text bg-gradient-to-r from-neon-blue via-neon-pink to-neon-yellow">
              QuizBall
            </h1>
            <PoweredByScore90 size="sm" className="mt-1" />
          </div>
          <div className="flex items-center gap-3">
            <img
              src={user?.avatar}
              alt={user?.username}
              className="w-12 h-12 rounded-full border-2 border-neon-blue shadow-neon-blue"
            />
            <div className="flex items-center gap-2 bg-card border-2 border-neon-yellow/50 rounded-lg px-4 py-2 shadow-neon-yellow">
              <Brain className="text-neon-yellow" size={20} />
              <span className="text-2xl font-black tracking-tighter text-neon-yellow">{user?.skill_rank || 1000}</span>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-4">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleQuickPlay}
            data-testid="quick-play-btn"
            className="bg-gradient-to-br from-neon-blue to-neon-blue/70 h-24 rounded-lg font-bold uppercase tracking-wider shadow-neon-blue hover:shadow-neon-blue/80 flex flex-col items-center justify-center gap-2 text-white border-2 border-neon-blue/50 transition-all"
          >
            <Play size={28} />
            Quick Play
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => navigate('/matchmaking')}
            data-testid="invite-friend-btn"
            className="bg-gradient-to-br from-neon-pink to-neon-pink/70 h-24 rounded-lg font-bold uppercase tracking-wider shadow-neon-pink hover:shadow-neon-pink/80 flex flex-col items-center justify-center gap-2 text-white border-2 border-neon-pink/50 transition-all"
          >
            <Users size={28} />
            Invite Friend
          </motion.button>
        </div>

        {/* Your Rank Section */}
        {ranks && (
          <div>
            <h2 className="text-xl font-bold uppercase tracking-tight mb-3 text-white flex items-center gap-2">
              <Trophy size={20} className="text-neon-yellow" />
              Your Rank
            </h2>
            <div className="grid grid-cols-3 gap-3">
              {/* Global Rank */}
              <div className="bg-card border-2 border-neon-blue/30 rounded-lg p-3 text-center" data-testid="rank-global">
                <Globe className="text-neon-blue mx-auto mb-1" size={20} />
                <p className="text-xl font-black tracking-tighter text-neon-blue">
                  #{ranks.global?.rank || '-'}
                </p>
                <p className="text-[10px] text-gray-500 uppercase">Global</p>
                <p className="text-[10px] text-gray-600">of {ranks.global?.total || 0}</p>
              </div>

              {/* Club Rank */}
              <div className="bg-card border-2 border-neon-yellow/30 rounded-lg p-3 text-center" data-testid="rank-club">
                <Shield className="text-neon-yellow mx-auto mb-1" size={20} />
                <p className="text-xl font-black tracking-tighter text-neon-yellow">
                  #{ranks.club?.rank || '-'}
                </p>
                <p className="text-[10px] text-gray-500 uppercase truncate">{ranks.club?.name || 'No Club'}</p>
                <p className="text-[10px] text-gray-600">of {ranks.club?.total || 0}</p>
              </div>

              {/* Country Rank */}
              <div className="bg-card border-2 border-neon-pink/30 rounded-lg p-3 text-center" data-testid="rank-country">
                <Globe className="text-neon-pink mx-auto mb-1" size={20} />
                <p className="text-xl font-black tracking-tighter text-neon-pink">
                  #{ranks.country?.rank || '-'}
                </p>
                <p className="text-[10px] text-gray-500 uppercase truncate">{ranks.country?.name || 'No Country'}</p>
                <p className="text-[10px] text-gray-600">of {ranks.country?.total || 0}</p>
              </div>
            </div>

            {/* League Ranks */}
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

        {/* Club Challenge Banner */}
        {user?.favorite_club && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-r from-neon-yellow/20 to-neon-orange/20 border-2 border-neon-yellow rounded-lg p-6 shadow-neon-yellow"
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-xl font-extrabold tracking-tighter uppercase text-white mb-1">
                  {user.favorite_club} Challenge
                </h3>
                <p className="text-sm text-gray-300">Test your ball knowledge about {user.favorite_club}</p>
              </div>
              <div className="bg-neon-yellow/20 border-2 border-neon-yellow rounded-lg px-3 py-2 text-center">
                <p className="text-2xl font-black tracking-tighter text-neon-yellow">{user.club_knowledge_score || 0}</p>
                <p className="text-xs text-gray-400 uppercase">Score</p>
              </div>
            </div>
            <button
              onClick={handleClubChallenge}
              data-testid="club-challenge-btn"
              className="w-full bg-gradient-to-r from-neon-yellow to-neon-orange text-black hover:from-neon-orange hover:to-neon-yellow h-12 px-6 rounded-sm font-bold uppercase tracking-wider shadow-neon-yellow hover:shadow-neon-orange transition-all active:scale-95"
            >
              Start Club Challenge
            </button>
            <button
              onClick={() => navigate('/club-leaderboard')}
              className="w-full mt-2 border-2 border-neon-yellow bg-transparent hover:bg-neon-yellow/10 text-neon-yellow h-10 px-6 rounded-sm font-bold uppercase tracking-wider text-sm transition-all"
            >
              View {user.favorite_club} Leaderboard
            </button>
          </motion.div>
        )}

        {/* Weekly Club Wars */}
        {user?.favorite_club && clubWar && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-card border-2 border-electric-purple/50 rounded-lg overflow-hidden shadow-electric-purple"
            data-testid="club-wars-section"
          >
            <div className="bg-gradient-to-r from-electric-purple/30 to-neon-pink/30 p-4 border-b border-electric-purple/30">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Swords className="text-electric-purple" size={22} />
                  <h3 className="text-lg font-extrabold tracking-tighter uppercase text-white">Weekly Club Wars</h3>
                </div>
                <span className="text-[10px] text-gray-400 uppercase bg-black/30 px-2 py-1 rounded">
                  Ends {new Date(clubWar.week_end).toLocaleDateString(undefined, {weekday: 'short', month: 'short', day: 'numeric'})}
                </span>
              </div>
            </div>

            <div className="p-4 space-y-3">
              {/* Top 5 Clubs */}
              {clubWar.standings && clubWar.standings.length > 0 ? (
                <div className="space-y-2">
                  {clubWar.standings.slice(0, 5).map((club) => {
                    const isMyClub = club.club_name === user.favorite_club;
                    return (
                      <div
                        key={club.club_name}
                        data-testid={`war-club-${club.rank}`}
                        className={`flex items-center gap-3 p-2 rounded-lg ${
                          isMyClub ? 'bg-electric-purple/20 border border-electric-purple/30' : ''
                        }`}
                      >
                        <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                          club.rank === 1 ? 'bg-neon-yellow text-black' :
                          club.rank === 2 ? 'bg-gray-400 text-black' :
                          club.rank === 3 ? 'bg-orange-600 text-white' :
                          'bg-gray-700 text-gray-400'
                        }`}>
                          {club.rank}
                        </span>
                        <span className={`font-bold text-sm flex-1 truncate ${isMyClub ? 'text-electric-purple' : 'text-white'}`}>
                          {club.club_name}
                        </span>
                        <span className="text-xs text-gray-500">{club.member_count} fans</span>
                        <span className="text-lg font-black tracking-tighter text-neon-yellow">{club.total_points}</span>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-4">
                  <p className="text-gray-400 text-sm">No contributions yet this week</p>
                  <p className="text-xs text-gray-500">Be the first to fight for your club!</p>
                </div>
              )}

              {/* My Contribution */}
              {clubWar.my_contribution && (
                <div className="bg-black/30 rounded-lg p-3 flex items-center justify-between border border-white/10">
                  <span className="text-xs text-gray-400 uppercase">Your contribution</span>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-500">{clubWar.my_contribution.games_played} games</span>
                    <span className="text-lg font-black tracking-tighter text-electric-purple">{clubWar.my_contribution.points} pts</span>
                  </div>
                </div>
              )}

              {/* Play for Club */}
              <button
                onClick={handleClubWarContribute}
                data-testid="club-war-play-btn"
                className="w-full bg-gradient-to-r from-electric-purple to-neon-pink hover:from-neon-pink hover:to-electric-purple h-11 px-6 rounded-sm font-bold uppercase tracking-wider text-white transition-all active:scale-95 shadow-electric-purple"
              >
                Fight for {user.favorite_club}!
              </button>
            </div>
          </motion.div>
        )}

        {/* Active Games */}
        <div>
          <h2 className="text-xl font-bold uppercase tracking-tight mb-4 text-gray-300">Active Games</h2>
          
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading games...</div>
          ) : activeGames.length === 0 ? (
            <div className="bg-card border-2 border-white/10 rounded-lg p-6 text-center">
              <p className="text-gray-400">No active games</p>
              <p className="text-sm text-gray-500 mt-2">Start a quick match or invite a friend!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {activeGames.slice(0, showAllGames ? 10 : 5).map((game) => (
                <motion.div
                  key={game.id}
                  whileHover={{ scale: 1.01 }}
                  onClick={() => navigate(`/game/${game.id}`)}
                  data-testid={`game-card-${game.id}`}
                  className="bg-card border-2 border-neon-blue/30 rounded-lg p-4 cursor-pointer hover:border-neon-pink transition-all hover:shadow-neon-blue"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <img
                        src={game.player2?.avatar || game.player1.avatar}
                        alt="Opponent"
                        className="w-12 h-12 rounded-full border-2 border-neon-blue"
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
                        <span className="text-neon-yellow">{game.my_score}</span>
                        <span className="text-gray-600 mx-1">-</span>
                        <span className="text-gray-400">{game.opponent_score}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {game.is_my_turn ? (
                      <>
                        <Clock className="text-neon-yellow" size={16} />
                        <span className="text-sm font-bold text-neon-yellow uppercase">Your Turn</span>
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
              {activeGames.length > 5 && (
                <button
                  onClick={() => setShowAllGames(!showAllGames)}
                  data-testid="toggle-games-btn"
                  className="w-full py-2 text-sm font-bold uppercase tracking-wider text-neon-blue hover:text-neon-pink transition-colors flex items-center justify-center gap-1"
                >
                  {showAllGames ? <><ChevronUp size={16} /> Show Less</> : <><ChevronDown size={16} /> Show All ({activeGames.length})</>}
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
