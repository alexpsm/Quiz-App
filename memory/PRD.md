# QuizBall - Product Requirements Document

## Original Problem Statement
QuizBall is a football quiz game application with user registration, single-player modes, leagues, and leaderboards. Users wanted greater question variety with club-specific categories and an adaptive matchmaking system based on a "Ball Knowledge" skill score.

## Core Features (Implemented)
- **Authentication:** Email/password + Emergent Google OAuth
- **Game Modes:** Quick Play (vs bot), Club Challenge (solo), Invite Friend, Ranked Matchmaking
- **Question System:** 3700+ questions, mixed club/topic categories, 3-month no-repeat guardrail
- **Ball Knowledge Score:** ELO-based skill ranking that updates after EVERY game type:
  - Bot games: ELO vs bot (60% K-factor), bot skill matched to user
  - PvP games: Full ELO (K=32) with score-diff bonus
  - Solo/Club Challenge: Performance-based (score vs 900 baseline)
- **Leagues:** Public/private leagues with leaderboards
- **Club Wars:** Weekly club competition
- **Club Leaderboard:** Filtered by user's favorite club
- **Payments:** Stripe checkout for credits/premium
- **Profile:** Avatar, game history (5 shown, expandable), top players (5/10), ranks

## Tech Stack
- **Frontend:** React, Vite, TailwindCSS, Shadcn UI, Framer Motion
- **Backend:** Python, FastAPI, SQLAlchemy (Async)
- **Database:** PostgreSQL (Supabase)
- **Auth:** JWT session tokens + cookies

## Key Architecture
- Backend: Monolithic server.py (~1900 lines)
- Frontend: React SPA with pages (Dashboard, Game, Profile, Matchmaking, Onboarding)
- API layer: /app/frontend/src/lib/api.js
- Ball Knowledge update function: `update_ball_knowledge()` in server.py
- Category randomization: `/api/questions/random-categories` endpoint

## Recent Changes (Dec 2025)
- Ball Knowledge scoring system (all game modes)
- Mixed category selection (clubs + topics, weighted 60/40)
- Bot thinking time removed (instant bot play)
- 3-month no-repeat question guardrail
- Game history/leaderboard collapsible UI (show 5, expand to 10)
- Old sub-categories cleaned up
- Profile page data loading fixed (Promise.allSettled)

## Future/Backlog Tasks (P2)
- Club Mastery Badges
- Full Social OAuth (Facebook, Twitter, Apple - currently mocked)
- Fix duplicate answer options in generated questions
- Refactor monolithic server.py into routers
- Consolidate data seeding scripts

## Test Credentials
- testuser@quizball.com / Test12345 (Manchester United fan)
- matchtest@test.com / Test123456

## Mocked Features
- Social login buttons (Facebook, Twitter, Apple) are UI-only
