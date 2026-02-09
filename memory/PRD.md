# QuizBall - Product Requirements Document

## Original Problem Statement
Build a cross-platform, mobile-first web app called "QuizBall" — a football trivia game similar to QuizDuel, with Score90 social media branding.

## Tech Stack
- **Frontend:** React, Tailwind CSS, Framer Motion, Lucide-React, Shadcn/UI
- **Backend:** FastAPI, SQLAlchemy (async), PostgreSQL (Supabase), Alembic
- **Auth:** Email/Password + Emergent-managed Google OAuth
- **Payments:** Stripe (via emergentintegrations)

## V1 MVP Features (COMPLETE)
- [x] Asynchronous 1v1 duels over 6 rounds, 3 questions per round
- [x] Email/Google Auth, profile creation, category selection
- [x] 20,000+ question database across football categories
- [x] Matchmaking (random & friend invite)
- [x] Club Challenge mode with club-specific leaderboards
- [x] Admin panel for question management

## V2 Features - ALL IMPLEMENTED
- [x] Full UI Reskin with Score90 neon branding (neon-blue, neon-pink, neon-yellow)
- [x] "Ball Knowledge" replaces "Skill Rank" across all screens
- [x] "Powered by Score90" branding on every page
- [x] "Prove your Ball Knowledge" tagline
- [x] Enhanced onboarding: Country, Age, Phone Number fields
- [x] Avatar image upload (custom photos) + DiceBear presets
- [x] Quick Play vs TheScore90Bot
- [x] Game History widget on Profile page
- [x] Social sharing (WhatsApp, Messenger, Instagram) on Matchmaking
- [x] Full League System (create/join/leave public & private leagues)
- [x] "Your Rank" section on Dashboard & Profile (Global, Club, Country, League rankings)
- [x] Social Auth buttons: Facebook, X (Twitter), Apple (UI-ready, require OAuth credentials)
- [x] Stripe Payment integration: Credit packages ($0.99/$3.99/$6.99) + Premium ($4.99)
- [x] Weekly Club Wars — Club vs Club collective competition with weekly leaderboard
- [x] Store with credit packages and Premium purchase
- [x] Ad space placeholder on Store page

## Key API Endpoints
### Auth
- `/api/auth/{register, login, logout, me, session}` - Authentication

### Users
- `/api/users/me` (PUT) - Profile update (incl. country, age, phone)
- `/api/users/avatar` (POST) - Avatar image upload
- `/api/users/my-rank` (GET) - User rankings (global, club, country, league)
- `/api/users/leaderboard` (GET) - Global leaderboard
- `/api/users/club-leaderboard` (GET) - Club-specific leaderboard

### Games
- `/api/games/matchmake` (POST) - Random matchmaking
- `/api/games/quick-play` (POST) - Play vs TheScore90Bot
- `/api/games/club-challenge` (POST) - Solo club challenge
- `/api/games/invite` (POST) - Create invite code
- `/api/games/join/{code}` (POST) - Join by invite
- `/api/games/history` (GET) - Completed game history
- `/api/games/{id}` (GET) - Game details
- `/api/games/{id}/select-category` (POST) - Category selection
- `/api/games/{id}/answer` (POST) - Answer submission

### Leagues
- `/api/leagues` (GET/POST) - List/Create leagues
- `/api/leagues/{id}` (GET) - League details with leaderboard
- `/api/leagues/{id}/join` (POST) - Join league
- `/api/leagues/{id}/leave` (POST) - Leave league
- `/api/leagues/join-code/{code}` (POST) - Join by invite code

### Payments
- `/api/payments/checkout` (POST) - Create Stripe checkout session
- `/api/payments/status/{session_id}` (GET) - Poll payment status
- `/api/webhook/stripe` (POST) - Stripe webhook handler

### Club Wars
- `/api/club-wars/current` (GET) - Current week's standings
- `/api/club-wars/contribute` (POST) - Play game for club war

### Admin
- `/api/questions` (GET/POST) - Question CRUD
- `/api/questions/categories` (GET) - Available categories

## Data Models
- **users:** user_id, email, name, username, avatar, skill_rank, credits, favorite_club, club_knowledge_score, country, age, phone_number
- **questions:** id, question_text, options(a-d), correct_option, category, difficulty
- **games:** id, player1_id, player2_id, status, current_round, turn_player_id, winner_id, invite_code
- **game_rounds:** id, game_id, round_number, category, answers, scores
- **leagues:** id, name, league_type (public/private), invite_code, created_by
- **league_memberships:** id, league_id, user_id
- **payment_transactions:** id, user_id, session_id, package_id, amount, currency, credits_to_add, is_premium, payment_status, status
- **club_wars:** id, week_start, week_end, status
- **club_war_contributions:** id, club_war_id, user_id, club_name, points, games_played

## Pending Features (Backlog)
- [ ] Full Facebook/X/Apple OAuth implementation (requires developer portal credentials)
- [ ] Firebase analytics integration

## Test Credentials
- Test user: testuser@quizball.com / Test12345
- Admin: quizball_admin_2026
- Stripe: sk_test_emergent (test mode)
