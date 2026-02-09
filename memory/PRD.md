# QuizBall - Product Requirements Document

## Original Problem Statement
Build a cross-platform, mobile-first web app called "QuizBall" — a football trivia game similar to QuizDuel, with Score90 social media branding.

## Tech Stack
- **Frontend:** React, Tailwind CSS, Framer Motion, Lucide-React, Shadcn/UI
- **Backend:** FastAPI, SQLAlchemy (async), PostgreSQL (Supabase), Alembic
- **Auth:** Email/Password + Emergent-managed Google OAuth

## Core Features (MVP V1 - COMPLETE)
- Asynchronous 1v1 duels over 6 rounds, 3 questions per round
- Email/Google Auth, profile creation, category selection
- 20,000+ question database across football categories
- Matchmaking (random & friend invite)
- Club Challenge mode with club-specific leaderboards
- Admin panel for question management

## V2 Features - IMPLEMENTED
- [x] Full UI Reskin with Score90 neon branding (neon-blue, neon-pink, neon-yellow)
- [x] "Ball Knowledge" replaces "Skill Rank" across all screens
- [x] "Powered by Score90" branding on every page
- [x] "Prove your Ball Knowledge" tagline
- [x] Enhanced onboarding: Country, Age, Phone Number fields
- [x] Quick Play vs TheScore90Bot
- [x] Game History widget on Profile page
- [x] Social sharing (WhatsApp, Messenger, Instagram) on Matchmaking
- [x] League widgets (Public & Private - Coming Soon placeholders)
- [x] Store page with credit packages and Premium option
- [x] Ad space placeholder on Store page

## Pending V2 Features (Backlog)
- [ ] Avatar image upload (custom photos instead of DiceBear)
- [ ] Meta (Facebook) Auth provider
- [ ] X (Twitter) Auth provider
- [ ] Apple Auth provider
- [ ] Full League system (create/join public & private leagues)
- [ ] Advanced "Your Rank" section (Club, Country, League rankings)
- [ ] Store payment integration (Stripe or in-app purchases)

## Key API Endpoints
- `/api/auth/{register, login, logout, me, session}` - Authentication
- `/api/users/me` - Profile update (incl. country, age, phone)
- `/api/users/leaderboard` - Global leaderboard
- `/api/users/club-leaderboard` - Club-specific leaderboard
- `/api/clubs` - Available football clubs
- `/api/games/{matchmake, quick-play, club-challenge, invite, join, history}` - Game management
- `/api/games/{id}/select-category` - Category selection
- `/api/games/{id}/answer` - Answer submission
- `/api/questions` - Question CRUD (admin)

## Data Models
- **users:** user_id, email, name, username, avatar, skill_rank, credits, favorite_club, club_knowledge_score, country, age, phone_number
- **questions:** id, question_text, options(a-d), correct_option, category, difficulty
- **games:** id, player1_id, player2_id, status, current_round, turn_player_id, winner_id, invite_code
- **game_rounds:** id, game_id, round_number, category, answers, scores
- **leagues:** id, name, league_type, invite_code, created_by
- **league_memberships:** id, league_id, user_id

## Test Credentials
- Test user: testuser@quizball.com / Test12345
- Admin: quizball_admin_2026
