# QuizBall - Product Requirements Document

## Original Problem Statement
Build a cross-platform, mobile-first web app called "QuizBall" — a football trivia game similar to QuizDuel, with Score90 social media branding.

## Tech Stack
- **Frontend:** React, Tailwind CSS, Framer Motion, Lucide-React, Shadcn/UI
- **Backend:** FastAPI, SQLAlchemy (async), PostgreSQL (Supabase), Alembic
- **Auth:** Email/Password + Emergent-managed Google OAuth
- **Payments:** Stripe (via emergentintegrations)

## All Implemented Features

### V1 MVP
- [x] Asynchronous 1v1 duels over 6 rounds, 3 questions per round
- [x] Email/Google Auth, profile creation, category selection
- [x] 20,000+ question database across football categories
- [x] Matchmaking (random & friend invite)
- [x] Club Challenge mode with club-specific leaderboards
- [x] Admin panel for question management

### V2 Branding & UI
- [x] Full UI Reskin with Score90 neon branding
- [x] "Ball Knowledge" branding, "Powered by Score90" on every page
- [x] Social auth buttons: Google (functional), Facebook, X, Apple (UI placeholders)

### V2 Onboarding
- [x] Required fields: Username, Favourite Club, Country (dropdown), Age (12-99 dropdown), Mobile Phone
- [x] Football-themed person-like avatars + custom image upload
- [x] GDPR marketing consent checkbox (opt-in)
- [x] Club dropdown: Premier League, Bundesliga, Ligue 1, Serie A, La Liga
- [x] Incomplete profiles redirect to onboarding

### V2 Gameplay
- [x] Quick Play vs TheScore90Bot
- [x] **3-hour time limit per round** with visible countdown for real players
- [x] **Bot plays in 45 seconds** with countdown and skip button
- [x] **Live bot answering** — watch bot think and select answers in real-time
- [x] **Opponent answer playback** — review how opponent answered each question
- [x] Game History widget on Profile page

### V2 Social & Leagues
- [x] Full League System (create/join/leave public & private leagues by code)
- [x] Social sharing (WhatsApp, Messenger, Instagram)
- [x] "Your Rank" on Dashboard & Profile (Global, Club, Country, League)

### V2 Store & Monetization
- [x] Stripe Payment: Credit packages ($0.99/$3.99/$6.99) + Premium ($4.99)
- [x] Weekly Club Wars (club vs club competition)
- [x] Ad space placeholder

### V3 Adaptive Matchmaking & Club Questions (December 2025)
- [x] **Unified 'Club' Category** — Single "Club" category replaces 68+ club-specific subcategories
- [x] **869 Club Questions** — Covers all 96 clubs from 5 leagues (Premier League, Bundesliga, La Liga, Serie A, Ligue 1)
- [x] **Question Types:** nickname, stadium, city, founded year, colors, league, reverse questions
- [x] **Club Challenge Mode Enhancement** — Auto-selects "Club" category, filters questions by user's favorite club
- [x] **18 Total Categories** — Reduced from 85+ to streamlined 18 categories
- [x] **Skill-Based Matchmaking Queue** — New MatchmakingQueue table with skill_rank matching
- [x] **ELO-Like Ranking System** — skill_rank updates after ranked (non-bot) games
  - K-factor: 32
  - Score bonus: up to 10 extra points based on score difference
  - Minimum rank: 100
- [x] **Matchmaking Endpoints:**
  - POST /api/matchmaking/join — Join queue with skill_rank
  - GET /api/matchmaking/status — Returns waiting/matched status with queue stats
  - DELETE /api/matchmaking/leave — Leave queue
  - POST /api/matchmaking/bot-fallback — Play bot when no opponent found
- [x] **Dynamic Skill Range Expansion** — Starts at ±150, expands by 50 every 15s up to ±500
- [x] **Frontend Ranked Match UI** — Shows skill rank, wait time, skill range, queue count, cancel button

## Pending (Backlog)
- [ ] Full Facebook/X/Apple OAuth (needs developer credentials)
- [ ] Firebase analytics
- [ ] More club-specific questions for remaining clubs

## Test Credentials
- Test user: matchtest@test.com / Test123456
- Admin: quizball_admin_2026

## Key API Endpoints
- POST /api/matchmaking/join — Join skill-based matchmaking queue
- GET /api/matchmaking/status — Check matchmaking status
- DELETE /api/matchmaking/leave — Leave matchmaking queue
- POST /api/matchmaking/bot-fallback — Accept bot match
- POST /api/games/club-challenge — Start Club Challenge (questions filtered by user's favorite club)
- GET /api/questions/categories — Returns 18 categories including unified "Club"

## Database Schema Updates (V3)
- **MatchmakingQueue table:** id, user_id, skill_rank, joined_at, status
- Indexes: idx_matchmaking_skill, idx_matchmaking_status_skill
- **Questions table:** "Club" category contains 869 questions for 96 clubs
