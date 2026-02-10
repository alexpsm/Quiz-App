# QuizBall - Product Requirements Document

## Original Problem Statement
QuizBall is a football quiz game application with user registration, single-player modes, leagues, and leaderboards. Users wanted greater question variety with club-specific categories and an adaptive matchmaking system based on a "Ball Knowledge" skill score.

## Core Features (Implemented)
- **Authentication:** Email/password + Emergent Google OAuth
- **Game Modes:** Quick Play (vs bot), Club Challenge (solo), Invite Friend, Ranked Matchmaking
- **Question System:** 3700+ questions, "Club" category (consolidated), 3-month no-repeat guardrail
- **Skill System:** ELO-based skill ranking (Ball Knowledge score)
- **Leagues:** Public/private leagues with leaderboards
- **Club Wars:** Weekly club competition
- **Club Leaderboard:** Filtered by user's favorite club
- **Payments:** Stripe checkout for credits/premium
- **Profile:** Avatar upload, game history, ranks, top players

## Tech Stack
- **Frontend:** React, Vite, TailwindCSS, Shadcn UI, Framer Motion
- **Backend:** Python, FastAPI, SQLAlchemy (Async)
- **Database:** PostgreSQL (Supabase)
- **Auth:** JWT session tokens + cookies

## What's Been Implemented (Dec 2025)
- Full game flow: Quick Play (6 rounds, 3 questions each, vs bot)
- Club Challenge: Solo mode with favorite club questions (6 rounds)
- Ranked Matchmaking with ELO-based skill updates
- 3700+ questions consolidated under "Club" category
- 3-month no-repeat question guardrail (UserQuestionHistory table)
- Club-specific leaderboards (existed, verified working)
- Old sub-categories cleaned up (merged into "Club")
- Profile page data loading fixed (Promise.allSettled)
- Bot thinking time removed (instant bot play)
- Test data cleaned up (removed 24 test leagues)

## Bug Fixes (Dec 2025)
1. Club Challenge never finishing (is_solo logic)
2. correct_option not returned for wrong answers
3. Frontend "waiting" on reload mid-round
4. Timeout sending empty string → sends 'X'
5. Category loading race condition (await loadCategories)
6. Duplicate GameRound entries (get-or-create pattern)
7. Profile page Promise.all failure cascade → Promise.allSettled
8. Bot countdown delay removed (instant bot play)

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
