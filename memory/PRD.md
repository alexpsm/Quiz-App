# QuizBall - Product Requirements Document

## Original Problem Statement
QuizBall is a football quiz game with skill-based matchmaking and credit betting.

## Core Features (Implemented)
- **Game Modes:** Quick Play (vs bot), Club Challenge (solo), Invite Friend, Ranked Matchmaking, Weekly Challenges, P2P Bet Games
- **Credit Betting System:**
  - Weekly Challenges: 5 topical challenges per week (Easy/Medium/Hard/Very Hard)
  - Easy: Bet 5, Win 15 (bot 55%), Medium: Bet 10, Win 30 (bot 70%), Hard: Bet 15, Win 45 (bot 80%), Very Hard: Bet 20, Win 60 (bot 90%)
  - P2P Betting: Bet up to 50 credits against friends, winner takes all
- **Question System:** 3,739 unique questions across 10 categories, 3-month no-repeat guardrail
- **Ball Knowledge Score:** ELO-based, updates after every game type
- **Dynamic Bot:** Accuracy mirrors user's correct-answer % (challenges use fixed accuracy)
- **Mixed Categories:** Random clubs + topics presented as category choices

## Tech Stack
- Frontend: React, TailwindCSS, Shadcn UI, Framer Motion
- Backend: FastAPI, SQLAlchemy Async, PostgreSQL
- Auth: JWT session tokens + cookies

## Database Models
- `users`, `questions`, `games` (+ credit_bet, challenge_id), `game_rounds`
- `weekly_challenges` (difficulty, topic, bet/win amounts, bot_accuracy)
- `leagues`, `matchmaking_queue`, `user_question_history`

## Key API Endpoints
- `GET /api/challenges/weekly` - Get 5 weekly challenges
- `POST /api/challenges/{id}/start` - Start challenge (deducts credits)
- `POST /api/games/invite-bet?bet_amount=N` - Create P2P bet game
- `POST /api/games/join-bet/{code}` - Join P2P bet game (deducts credits)

## Future/Backlog
- Club Mastery Badges
- Social OAuth (Facebook, Twitter, Apple)
- Refactor server.py into routers
