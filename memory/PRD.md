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

## Pending (Backlog)
- [ ] Full Facebook/X/Apple OAuth (needs developer credentials)
- [ ] Firebase analytics

## Test Credentials
- Test user: testuser@quizball.com / Test12345
- Admin: quizball_admin_2026
