# QuizBall - Product Requirements Document

## Original Problem Statement
QuizBall is a football quiz game with skill-based matchmaking and credit betting.

## Core Features (Implemented)

### Game Modes
- **Quick Play:** vs bot with dynamic difficulty
- **Club Challenge:** Solo mode testing club knowledge
- **Invite Friend:** P2P games with invite codes
- **Ranked Matchmaking:** Skill-based opponent matching
- **Weekly Challenges:** 5 topical challenges per week with credit betting
- **P2P Bet Games:** Wager credits against friends

### Credit & Betting System
- Weekly Challenges: Easy (Bet 5, Win 15), Medium (Bet 10, Win 30), Hard (Bet 15, Win 45), Very Hard (Bet 20, Win 60)
- P2P Betting: Bet up to 50 credits against friends, winner takes all

### Ball Knowledge Score (ELO)
- Updates after every game type
- PvP: Full ELO calculation
- Bot games: 60% impact
- Solo/Club Challenge: Performance-based

### Player Tier System (NEW - Feb 2025)
- 1-100 tier progression based on total game points
- Tier badges displayed on avatars (Dashboard, Profile, Game screens)
- Color-coded by tier: Gray (1-9), Green (10-19), Yellow (20-39), Blue (40-59), Purple (60-79), Red (80-100)
- Credit rewards on tier-up milestones

### Achievement Badges System (NEW - Feb 2025)
- 20 unique achievements across 7 categories
- Categories: milestone, streak, skill, rating, challenge, club, special
- Examples: First Victory, Hot Streak (3 wins), Perfect Game (18/18 correct), Speed Demon (<2s answer)
- Displayed on Profile page and game over screen
- Automatically awarded after game completion

### Dynamic Bot Difficulty
- Quick Play: Bot accuracy mirrors user's current game performance
- Challenges: Fixed accuracy based on difficulty level

### Question System
- 3,739+ unique questions across 10 categories
- 3-month no-repeat guardrail per user
- Mixed categories: Random clubs + regular topics

## Tech Stack
- **Frontend:** React, TailwindCSS, Shadcn UI, Framer Motion
- **Backend:** FastAPI, SQLAlchemy Async, PostgreSQL (Supabase)
- **Auth:** JWT session tokens + HTTP-only cookies, Google OAuth (Emergent Auth)

## Database Models
- `users` - player_tier, total_game_points, skill_rank, credits
- `user_achievements` - user_id, achievement_id, earned_at (NEW)
- `questions`, `games`, `game_rounds`
- `weekly_challenges` - difficulty, topic, bet/win amounts, bot_accuracy
- `leagues`, `matchmaking_queue`, `user_question_history`

## Key API Endpoints
- `GET /api/achievements` - Get all 20 achievements
- `GET /api/achievements/me` - Get user's earned achievements
- `GET /api/challenges/weekly` - Get 5 weekly challenges
- `POST /api/challenges/{id}/start` - Start challenge (deducts credits)
- `POST /api/games/invite-bet?bet_amount=N` - Create P2P bet game
- `POST /api/games/join-bet/{code}` - Join P2P bet game

## Completed Work (Feb 2025)
- ✅ Fixed Google OAuth cookie bug (session cookie now set properly)
- ✅ Player Tier System with avatar badges
- ✅ Achievement Badges System (20 achievements, 7 categories)
- ✅ Profile page achievements display
- ✅ Game over screen achievement notifications

## Future/Backlog
- Social OAuth (Facebook, Twitter, Apple)
- Refactor server.py into Flask Blueprints
- Use Alembic for database migrations
- Break down Game.js into smaller components
- True recurring subscription with Stripe (currently one-time)
