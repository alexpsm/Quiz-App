# QuizBall - Product Requirements Document

## Original Problem Statement
QuizBall is a football quiz game application with user registration, single-player modes, leagues, and leaderboards. Users wanted greater question variety with club-specific categories and an adaptive matchmaking system based on a "Ball Knowledge" skill score.

## Core Features (Implemented)
- **Authentication:** Email/password + Emergent Google OAuth
- **Game Modes:** Quick Play (vs bot), Club Challenge (solo), Invite Friend, Ranked Matchmaking
- **Question System:** 3700+ questions, primarily in "Club" category
- **Skill System:** ELO-based skill ranking (Ball Knowledge score)
- **Leagues:** Public/private leagues with leaderboards
- **Club Wars:** Weekly club competition
- **Payments:** Stripe checkout for credits/premium
- **Profile:** Avatar upload, game history, ranks

## Tech Stack
- **Frontend:** React, Vite, TailwindCSS, Shadcn UI, Framer Motion
- **Backend:** Python, FastAPI, SQLAlchemy (Async)
- **Database:** PostgreSQL (Supabase)
- **Auth:** JWT session tokens + cookies

## Key Architecture
- Backend: Monolithic server.py (~1900 lines) with all routes
- Frontend: React SPA with pages (Dashboard, Game, Profile, Matchmaking, Onboarding)
- API layer: /app/frontend/src/lib/api.js

## What's Been Implemented
- Full game flow: Quick Play (6 rounds, 3 questions each, vs bot)
- Club Challenge: Solo mode with favorite club questions (6 rounds)
- Ranked Matchmaking with ELO-based skill updates
- Massive question database (3700+ questions)
- Leaderboards (global, club, country)
- Game history tracking
- Stripe payments integration
- Club Wars weekly competition

## Bug Fixes (Dec 2025)
1. **Club Challenge never finishing** - Fixed: Added is_solo check so rounds advance properly
2. **correct_option not returned for wrong answers** - Fixed: Always return correct_option
3. **Frontend "waiting" on reload mid-round** - Fixed: Resume questions from where left off
4. **Timeout sending empty string** - Fixed: Sends 'X' as intentionally wrong
5. **Category loading race condition** - Fixed: Await loadCategories before showing UI
6. **Duplicate GameRound entries** - Fixed: Get-or-create pattern (previous session)

## Upcoming Tasks (P1)
- Club-Specific Leaderboards (filtered by club)

## Future/Backlog Tasks (P2)
- Club Mastery Badges
- Full Social OAuth (Facebook, Twitter, Apple - currently mocked)
- Clean up old sub-categories in DB
- Fix duplicate answer options in generated questions
- Refactor monolithic server.py into routers
- Consolidate data seeding scripts

## Test Credentials
- testuser@quizball.com / Test12345 (Manchester United fan)
- matchtest@test.com / Test123456

## Mocked Features
- Social login buttons (Facebook, Twitter, Apple) are UI-only
