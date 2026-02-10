from fastapi import FastAPI, APIRouter, Depends, HTTPException, Response, Cookie, Header, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from database import get_db
from models import User, UserSession, Question, Game, GameRound, League, LeagueMembership, PaymentTransaction, MatchmakingQueue, UserQuestionHistory, WeeklyChallenge, UserAchievement, CareerPathChallenge, CareerPathAttempt
from clubs_data import CLUBS_BY_LEAGUE, get_all_clubs, get_club_league
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from pathlib import Path
import os
import logging
import uuid
import bcrypt
import jwt
import random
import string
import requests
import shutil

UPLOAD_DIR = Path("/app/backend/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI()
api_router = APIRouter(prefix="/api")

JWT_SECRET = os.environ.get('JWT_SECRET', 'default_secret_key')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    username: Optional[str] = None
    picture: Optional[str] = None
    avatar: Optional[str] = None
    skill_rank: int = 1000
    credits: int = 100

class UpdateProfileRequest(BaseModel):
    username: Optional[str] = None
    avatar: Optional[str] = None
    favorite_club: Optional[str] = None
    country: Optional[str] = None
    age: Optional[int] = None
    phone_number: Optional[str] = None
    marketing_consent: Optional[bool] = None

class QuestionCreate(BaseModel):
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    category: str
    difficulty: int = 1

class QuestionResponse(BaseModel):
    id: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    category: str
    difficulty: int

class AnswerSubmit(BaseModel):
    question_id: str
    selected_option: str
    time_taken: float

class GameResponse(BaseModel):
    id: str
    player1: UserResponse
    player2: UserResponse
    current_round: int
    status: str
    turn_player_id: Optional[str]
    winner_id: Optional[str]
    invite_code: Optional[str]
    my_score: int
    opponent_score: int

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def generate_invite_code() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def calculate_tier(total_points: int) -> int:
    """Calculate player tier (1-100) from total game points.
    Tier 1: 0 pts, Tier 2: 100 pts, scaling increases each tier.
    Formula: tier N requires sum of (N-1)*100 points total.
    Tier 10 ~= 4,500 pts, Tier 25 ~= 30,000, Tier 50 ~= 122,500, Tier 100 ~= 495,000
    """
    tier = 1
    threshold = 0
    for t in range(1, 101):
        threshold += t * 100
        if total_points < threshold:
            break
        tier = t + 1
    return min(tier, 100)

TIER_CREDIT_REWARDS = {
    5: 10, 10: 25, 15: 40, 20: 60, 25: 100,
    30: 120, 35: 150, 40: 200, 45: 250, 50: 500,
    55: 300, 60: 350, 65: 400, 70: 500, 75: 750,
    80: 600, 85: 700, 90: 800, 95: 900, 100: 2000,
}

async def update_player_tier(user, game_score: int) -> dict:
    """Add game score to total, recalculate tier, award credits if tier up."""
    old_tier = user.player_tier or 1
    user.total_game_points = (user.total_game_points or 0) + game_score
    new_tier = calculate_tier(user.total_game_points)
    user.player_tier = new_tier

    credits_awarded = 0
    if new_tier > old_tier:
        for t in range(old_tier + 1, new_tier + 1):
            credits_awarded += TIER_CREDIT_REWARDS.get(t, t)  # default: tier number as credits
        user.credits = (user.credits or 0) + credits_awarded

    if new_tier != old_tier or credits_awarded:
        return {"old_tier": old_tier, "new_tier": new_tier, "credits_awarded": credits_awarded}
    return None


# ========== ACHIEVEMENT BADGES SYSTEM ==========

ACHIEVEMENTS = {
    # Game milestone achievements
    "first_win": {
        "name": "First Victory",
        "description": "Win your first game",
        "icon": "trophy",
        "category": "milestone"
    },
    "win_streak_3": {
        "name": "Hot Streak",
        "description": "Win 3 games in a row",
        "icon": "flame",
        "category": "streak"
    },
    "win_streak_5": {
        "name": "On Fire",
        "description": "Win 5 games in a row",
        "icon": "fire",
        "category": "streak"
    },
    "win_streak_10": {
        "name": "Unstoppable",
        "description": "Win 10 games in a row",
        "icon": "zap",
        "category": "streak"
    },
    "perfect_game": {
        "name": "Perfect Game",
        "description": "Answer all 18 questions correctly in one game",
        "icon": "star",
        "category": "skill"
    },
    "perfect_round": {
        "name": "Flawless Round",
        "description": "Answer all 3 questions correctly in under 15 seconds total",
        "icon": "clock",
        "category": "skill"
    },
    "games_10": {
        "name": "Getting Started",
        "description": "Play 10 games",
        "icon": "play",
        "category": "milestone"
    },
    "games_50": {
        "name": "Regular Player",
        "description": "Play 50 games",
        "icon": "gamepad",
        "category": "milestone"
    },
    "games_100": {
        "name": "Dedicated Fan",
        "description": "Play 100 games",
        "icon": "heart",
        "category": "milestone"
    },
    "wins_25": {
        "name": "Quarter Century",
        "description": "Win 25 games",
        "icon": "award",
        "category": "milestone"
    },
    "wins_50": {
        "name": "Half Century",
        "description": "Win 50 games",
        "icon": "medal",
        "category": "milestone"
    },
    "wins_100": {
        "name": "Century Club",
        "description": "Win 100 games",
        "icon": "crown",
        "category": "milestone"
    },
    "ball_knowledge_1200": {
        "name": "Rising Star",
        "description": "Reach 1200 Ball Knowledge rating",
        "icon": "trending-up",
        "category": "rating"
    },
    "ball_knowledge_1500": {
        "name": "Expert",
        "description": "Reach 1500 Ball Knowledge rating",
        "icon": "brain",
        "category": "rating"
    },
    "ball_knowledge_1800": {
        "name": "Master",
        "description": "Reach 1800 Ball Knowledge rating",
        "icon": "gem",
        "category": "rating"
    },
    "challenge_winner": {
        "name": "Challenge Champion",
        "description": "Win a weekly challenge",
        "icon": "flag",
        "category": "challenge"
    },
    "hard_challenge_winner": {
        "name": "Fearless",
        "description": "Win a hard or very hard weekly challenge",
        "icon": "shield",
        "category": "challenge"
    },
    "club_devotee": {
        "name": "Club Devotee",
        "description": "Win 10 club challenge games",
        "icon": "home",
        "category": "club"
    },
    "comeback_king": {
        "name": "Comeback King",
        "description": "Win a game after being down by 300+ points",
        "icon": "refresh-cw",
        "category": "special"
    },
    "speed_demon": {
        "name": "Speed Demon",
        "description": "Answer a question correctly in under 2 seconds",
        "icon": "zap",
        "category": "skill"
    },
}


async def check_and_award_achievements(db: AsyncSession, user: User, game: Game = None, round_data: dict = None) -> List[dict]:
    """
    Check if user has earned any new achievements and award them.
    Returns list of newly earned achievements.
    """
    newly_earned = []
    
    # Get user's existing achievements
    result = await db.execute(
        select(UserAchievement.achievement_id).where(UserAchievement.user_id == user.user_id)
    )
    existing = {row[0] for row in result.all()}
    
    async def award_if_new(achievement_id: str):
        if achievement_id not in existing and achievement_id in ACHIEVEMENTS:
            db.add(UserAchievement(
                id=str(uuid.uuid4()),
                user_id=user.user_id,
                achievement_id=achievement_id
            ))
            newly_earned.append({
                "id": achievement_id,
                **ACHIEVEMENTS[achievement_id]
            })
            existing.add(achievement_id)
    
    # Count user's games and wins
    games_result = await db.execute(
        select(func.count()).select_from(Game).where(
            or_(Game.player1_id == user.user_id, Game.player2_id == user.user_id),
            Game.status == 'finished'
        )
    )
    total_games = games_result.scalar() or 0
    
    wins_result = await db.execute(
        select(func.count()).select_from(Game).where(
            Game.winner_id == user.user_id,
            Game.status == 'finished'
        )
    )
    total_wins = wins_result.scalar() or 0
    
    # Check game count milestones
    if total_games >= 10:
        await award_if_new("games_10")
    if total_games >= 50:
        await award_if_new("games_50")
    if total_games >= 100:
        await award_if_new("games_100")
    
    # Check win milestones
    if total_wins >= 1:
        await award_if_new("first_win")
    if total_wins >= 25:
        await award_if_new("wins_25")
    if total_wins >= 50:
        await award_if_new("wins_50")
    if total_wins >= 100:
        await award_if_new("wins_100")
    
    # Check Ball Knowledge rating milestones
    skill_rank = user.skill_rank or 1000
    if skill_rank >= 1200:
        await award_if_new("ball_knowledge_1200")
    if skill_rank >= 1500:
        await award_if_new("ball_knowledge_1500")
    if skill_rank >= 1800:
        await award_if_new("ball_knowledge_1800")
    
    # Check win streaks (last N consecutive wins)
    streak_result = await db.execute(
        select(Game).where(
            or_(Game.player1_id == user.user_id, Game.player2_id == user.user_id),
            Game.status == 'finished'
        ).order_by(Game.updated_at.desc()).limit(10)
    )
    recent_games = streak_result.scalars().all()
    
    current_streak = 0
    for g in recent_games:
        if g.winner_id == user.user_id:
            current_streak += 1
        else:
            break
    
    if current_streak >= 3:
        await award_if_new("win_streak_3")
    if current_streak >= 5:
        await award_if_new("win_streak_5")
    if current_streak >= 10:
        await award_if_new("win_streak_10")
    
    # Check game-specific achievements if game is provided
    if game and game.status == 'finished':
        # Perfect game check (all 18 questions correct)
        is_p1 = game.player1_id == user.user_id
        total_correct = 0
        total_questions = 0
        
        for r in game.rounds:
            answers = r.player1_answers if is_p1 else r.player2_answers
            if answers:
                for ans in answers:
                    total_questions += 1
                    if ans.get("is_correct"):
                        total_correct += 1
        
        if total_questions >= 18 and total_correct == total_questions:
            await award_if_new("perfect_game")
        
        # Comeback king check
        if game.winner_id == user.user_id:
            # Check if user was ever down by 300+ during the game
            running_user = 0
            running_opp = 0
            max_deficit = 0
            for r in sorted(game.rounds, key=lambda x: x.round_number):
                if is_p1:
                    running_user += r.player1_score
                    running_opp += r.player2_score
                else:
                    running_user += r.player2_score
                    running_opp += r.player1_score
                deficit = running_opp - running_user
                if deficit > max_deficit:
                    max_deficit = deficit
            
            if max_deficit >= 300:
                await award_if_new("comeback_king")
        
        # Challenge achievements
        if game.challenge_id and game.winner_id == user.user_id:
            await award_if_new("challenge_winner")
            # Check difficulty
            ch_result = await db.execute(select(WeeklyChallenge).where(WeeklyChallenge.id == game.challenge_id))
            challenge = ch_result.scalar_one_or_none()
            if challenge and challenge.difficulty in ('hard', 'very_hard'):
                await award_if_new("hard_challenge_winner")
        
        # Club challenge wins
        if game.status == 'finished' and game.player1_id == game.player2_id:
            club_wins_result = await db.execute(
                select(func.count()).select_from(Game).where(
                    Game.player1_id == user.user_id,
                    Game.player2_id == user.user_id,
                    Game.winner_id == user.user_id,
                    Game.status == 'finished'
                )
            )
            club_wins = club_wins_result.scalar() or 0
            if club_wins >= 10:
                await award_if_new("club_devotee")
    
    # Check round-specific achievements
    if round_data:
        answers = round_data.get("answers", [])
        total_time = sum(a.get("time_taken", 0) for a in answers)
        all_correct = all(a.get("is_correct") for a in answers) if answers else False
        
        # Flawless round: all correct in under 15 seconds total
        if len(answers) >= 3 and all_correct and total_time < 15:
            await award_if_new("perfect_round")
        
        # Speed demon: any answer under 2 seconds
        for ans in answers:
            if ans.get("is_correct") and ans.get("time_taken", 999) < 2:
                await award_if_new("speed_demon")
                break
    
    if newly_earned:
        await db.commit()
    
    return newly_earned


def calculate_elo_change(player_rank: int, opponent_rank: int, winner_is_p1: bool, score_diff: int = 0) -> tuple:
    """
    Calculate ELO rating changes for both players after a match.
    
    Uses a simplified ELO system:
    - K-factor of 32 (standard for most games)
    - Expected score based on rating difference
    - Small bonus/penalty based on score difference
    
    Returns: (player1_delta, player2_delta)
    """
    K = 32  # Base K-factor
    
    # Calculate expected scores
    expected_p1 = 1 / (1 + 10 ** ((opponent_rank - player_rank) / 400))
    expected_p2 = 1 - expected_p1
    
    # Actual scores (1 for win, 0 for loss, 0.5 for draw)
    if winner_is_p1:
        actual_p1 = 1.0
        actual_p2 = 0.0
    else:
        actual_p1 = 0.0
        actual_p2 = 1.0
    
    # Calculate base ELO changes
    delta_p1 = K * (actual_p1 - expected_p1)
    delta_p2 = K * (actual_p2 - expected_p2)
    
    # Add bonus based on score difference (max 10 extra points)
    score_bonus = min(10, score_diff // 50)
    if winner_is_p1:
        delta_p1 += score_bonus
        delta_p2 -= score_bonus // 2
    else:
        delta_p2 += score_bonus
        delta_p1 -= score_bonus // 2
    
    return (int(round(delta_p1)), int(round(delta_p2)))


async def update_ball_knowledge(db: AsyncSession, game: Game, user: User):
    """
    Update a user's Ball Knowledge (skill_rank) after a game finishes.
    
    - Bot games: ELO vs bot (bot skill = user's skill), K reduced to 20
    - PvP games: Full ELO (K=32) against opponent
    - Solo/Club Challenge: Performance-based (score vs baseline of 600/1080)
    
    Returns: (old_rank, new_rank, delta) for the user
    """
    total_p1 = sum(r.player1_score for r in game.rounds)
    total_p2 = sum(r.player2_score for r in game.rounds)
    user_rank = user.skill_rank or 1000
    old_rank = user_rank
    is_solo = game.player1_id == game.player2_id
    is_p1 = game.player1_id == user.user_id
    user_score = total_p1 if is_p1 else total_p2
    opp_score = total_p2 if is_p1 else total_p1
    won = game.winner_id == user.user_id

    if is_solo:
        # Solo / Club Challenge: performance-based
        # Max possible = 18 questions * 150 points = 2700, baseline ~ 900 (6 correct out of 18)
        # Scale: above baseline gains, below loses
        baseline = 900
        performance_ratio = (user_score - baseline) / baseline  # range ~ -1.0 to +2.0
        delta = int(round(15 * performance_ratio))  # max ~+30 / -15
        delta = max(-15, min(30, delta))
    elif game.is_bot_game:
        # Bot games: bot's "skill" matches user, reduced K-factor
        bot_skill = user_rank  # bot is calibrated to user
        delta, _ = calculate_elo_change(user_rank, bot_skill, winner_is_p1=won, score_diff=abs(user_score - opp_score))
        # Reduce impact: bot games worth ~60% of PvP
        delta = int(round(delta * 0.6))
    else:
        # PvP: full ELO against real opponent
        opp_result = await db.execute(
            select(User).where(User.user_id == (game.player2_id if is_p1 else game.player1_id))
        )
        opponent = opp_result.scalar_one_or_none()
        opp_rank = (opponent.skill_rank or 1000) if opponent else 1000

        if is_p1:
            p1_delta, p2_delta = calculate_elo_change(user_rank, opp_rank, winner_is_p1=won, score_diff=abs(user_score - opp_score))
            delta = p1_delta
            # Update opponent too
            if opponent:
                opponent.skill_rank = max(100, (opponent.skill_rank or 1000) + p2_delta)
        else:
            p1_delta, p2_delta = calculate_elo_change(opp_rank, user_rank, winner_is_p1=(not won), score_diff=abs(user_score - opp_score))
            delta = p2_delta
            if opponent:
                opponent.skill_rank = max(100, (opponent.skill_rank or 1000) + p1_delta)

    new_rank = max(100, user_rank + delta)
    user.skill_rank = new_rank

    # Update player tier based on game score
    tier_update = await update_player_tier(user, user_score)

    return old_rank, new_rank, delta, tier_update

async def get_current_user(db: AsyncSession = Depends(get_db), session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)) -> User:
    token = session_token
    if not token and authorization and authorization.startswith('Bearer '):
        token = authorization.replace('Bearer ', '')
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.execute(
        select(UserSession).options(selectinload(UserSession.user)).where(UserSession.session_token == token)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        await db.delete(session)
        await db.commit()
        raise HTTPException(status_code=401, detail="Session expired")
    
    return session.user

# Auth Endpoints
@api_router.post("/auth/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        user_id=str(uuid.uuid4()),
        email=data.email,
        name=data.name,
        password_hash=hash_password(data.password),
        avatar=f"https://api.dicebear.com/7.x/avataaars/svg?seed={uuid.uuid4()}"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    session_token = str(uuid.uuid4())
    session = UserSession(
        user_id=user.user_id,
        session_token=session_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(session)
    await db.commit()
    
    response = JSONResponse(content={"message": "User registered successfully"})
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7*24*60*60,
        path="/"
    )
    return response

@api_router.post("/auth/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    
    if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    session_token = str(uuid.uuid4())
    session = UserSession(
        user_id=user.user_id,
        session_token=session_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(session)
    await db.commit()
    
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7*24*60*60,
        path="/"
    )
    return response

@api_router.get("/auth/session")
async def process_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Process Emergent Auth session_id and create/update user"""
    try:
        # REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
        response = requests.get(
            'https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data',
            headers={'X-Session-ID': session_id},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        result = await db.execute(select(User).where(User.email == data['email']))
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                user_id=str(uuid.uuid4()),
                email=data['email'],
                name=data['name'],
                picture=data.get('picture'),
                avatar=data.get('picture') or f"https://api.dicebear.com/7.x/avataaars/svg?seed={uuid.uuid4()}"
            )
            db.add(user)
        else:
            user.name = data['name']
            user.picture = data.get('picture')
            if not user.avatar:
                user.avatar = data.get('picture')
        
        await db.commit()
        await db.refresh(user)
        
        session_token = data['session_token']
        session = UserSession(
            user_id=user.user_id,
            session_token=session_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db.add(session)
        await db.commit()
        
        # Return response with cookie set
        json_response = JSONResponse(content={
            "session_token": session_token,
            "user": {
                "user_id": user.user_id,
                "email": user.email,
                "name": user.name,
                "username": user.username,
                "avatar": user.avatar,
                "picture": user.picture,
                "skill_rank": user.skill_rank,
                "credits": user.credits
            }
        })
        json_response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=7*24*60*60,
            path="/"
        )
        return json_response
    except Exception as e:
        logger.error(f"Session processing error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "name": current_user.name,
        "username": current_user.username,
        "avatar": current_user.avatar,
        "picture": current_user.picture,
        "skill_rank": current_user.skill_rank,
        "player_tier": current_user.player_tier or 1,
        "total_game_points": current_user.total_game_points or 0,
        "credits": current_user.credits,
        "is_admin": current_user.is_admin,
        "favorite_club": current_user.favorite_club,
        "club_knowledge_score": current_user.club_knowledge_score or 0,
        "country": current_user.country,
        "age": current_user.age,
        "phone_number": current_user.phone_number
    }

@api_router.post("/auth/logout")
async def logout(response: Response, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db), session_token: Optional[str] = Cookie(None)):
    if session_token:
        result = await db.execute(select(UserSession).where(UserSession.session_token == session_token))
        session = result.scalar_one_or_none()
        if session:
            await db.delete(session)
            await db.commit()
    
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully"}

# User Endpoints
@api_router.put("/users/me")
async def update_profile(data: UpdateProfileRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if data.username:
        result = await db.execute(select(User).where(User.username == data.username, User.user_id != current_user.user_id))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = data.username
    
    if data.avatar:
        current_user.avatar = data.avatar
    
    if data.favorite_club:
        current_user.favorite_club = data.favorite_club
    
    if data.country is not None:
        current_user.country = data.country
    
    if data.age is not None:
        current_user.age = data.age
    
    if data.phone_number is not None:
        current_user.phone_number = data.phone_number
    
    if data.marketing_consent is not None:
        current_user.marketing_consent = data.marketing_consent
    
    # Check if this is initial profile setup — all required fields must be present
    missing = []
    if not current_user.username:
        missing.append("username")
    if not current_user.favorite_club:
        missing.append("favorite club")
    if not current_user.country:
        missing.append("country of residence")
    if not current_user.age:
        missing.append("age")
    if not current_user.phone_number:
        missing.append("mobile phone number")
    
    if missing:
        raise HTTPException(status_code=400, detail=f"Required fields missing: {', '.join(missing)}")
    
    await db.commit()
    await db.refresh(current_user)
    
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "name": current_user.name,
        "username": current_user.username,
        "avatar": current_user.avatar,
        "skill_rank": current_user.skill_rank,
        "credits": current_user.credits,
        "favorite_club": current_user.favorite_club,
        "club_knowledge_score": current_user.club_knowledge_score or 0,
        "country": current_user.country,
        "age": current_user.age,
        "phone_number": current_user.phone_number
    }

@api_router.get("/clubs")
async def get_clubs():
    """Get all available clubs organized by league"""
    return CLUBS_BY_LEAGUE

@api_router.get("/clubs/list")
async def get_clubs_list():
    """Get flat list of all clubs"""
    return get_all_clubs()

@api_router.get("/users/leaderboard")
async def get_leaderboard(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.username.isnot(None)).order_by(User.skill_rank.desc()).limit(limit)
    )
    users = result.scalars().all()
    
    return [{
        "user_id": user.user_id,
        "username": user.username,
        "avatar": user.avatar,
        "skill_rank": user.skill_rank,
        "player_tier": user.player_tier or 1
    } for user in users]

@api_router.get("/users/club-leaderboard")
async def get_club_leaderboard(club: Optional[str] = None, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get leaderboard for a specific club based on ball knowledge score"""
    target_club = club or current_user.favorite_club
    
    if not target_club:
        raise HTTPException(status_code=400, detail="No club specified")
    
    result = await db.execute(
        select(User).where(
            User.favorite_club == target_club,
            User.username.isnot(None)
        ).order_by(User.club_knowledge_score.desc()).limit(100)
    )
    users = result.scalars().all()
    
    # Find current user's rank
    user_rank = None
    for idx, user in enumerate(users):
        if user.user_id == current_user.user_id:
            user_rank = idx + 1
            break
    
    return {
        "club": target_club,
        "total_fans": len(users),
        "user_rank": user_rank,
        "leaderboard": [{
            "rank": idx + 1,
            "user_id": user.user_id,
            "username": user.username,
            "avatar": user.avatar,
            "club_knowledge_score": user.club_knowledge_score or 0,
            "is_current_user": user.user_id == current_user.user_id
        } for idx, user in enumerate(users)]
    }

@api_router.get("/users/search")
async def search_users(q: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(
            User.username.ilike(f"%{q}%"),
            User.user_id != current_user.user_id
        ).limit(10)
    )
    users = result.scalars().all()
    
    return [{
        "user_id": user.user_id,
        "username": user.username,
        "avatar": user.avatar,
        "skill_rank": user.skill_rank
    } for user in users]

# Avatar Upload
@api_router.post("/users/avatar")
async def upload_avatar(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Upload a custom avatar image"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Limit to 5MB
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be under 5MB")
    
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "png"
    filename = f"{current_user.user_id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = UPLOAD_DIR / filename
    
    with open(filepath, "wb") as f:
        f.write(contents)
    
    avatar_url = f"/api/uploads/{filename}"
    current_user.avatar = avatar_url
    await db.commit()
    
    return {"avatar": avatar_url}

# Your Rank Endpoint
@api_router.get("/users/my-rank")
async def get_my_rank(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get user's rank across club, country, and global"""
    ranks = {}
    
    # Global rank
    global_result = await db.execute(
        select(func.count()).select_from(User).where(
            User.username.isnot(None),
            User.skill_rank > current_user.skill_rank
        )
    )
    global_above = global_result.scalar() or 0
    global_total_result = await db.execute(
        select(func.count()).select_from(User).where(User.username.isnot(None))
    )
    global_total = global_total_result.scalar() or 1
    ranks["global"] = {"rank": global_above + 1, "total": global_total}
    
    # Club rank
    if current_user.favorite_club:
        club_result = await db.execute(
            select(func.count()).select_from(User).where(
                User.favorite_club == current_user.favorite_club,
                User.username.isnot(None),
                User.skill_rank > current_user.skill_rank
            )
        )
        club_above = club_result.scalar() or 0
        club_total_result = await db.execute(
            select(func.count()).select_from(User).where(
                User.favorite_club == current_user.favorite_club,
                User.username.isnot(None)
            )
        )
        club_total = club_total_result.scalar() or 1
        ranks["club"] = {"rank": club_above + 1, "total": club_total, "name": current_user.favorite_club}
    
    # Country rank
    if current_user.country:
        country_result = await db.execute(
            select(func.count()).select_from(User).where(
                User.country == current_user.country,
                User.username.isnot(None),
                User.skill_rank > current_user.skill_rank
            )
        )
        country_above = country_result.scalar() or 0
        country_total_result = await db.execute(
            select(func.count()).select_from(User).where(
                User.country == current_user.country,
                User.username.isnot(None)
            )
        )
        country_total = country_total_result.scalar() or 1
        ranks["country"] = {"rank": country_above + 1, "total": country_total, "name": current_user.country}
    
    # League ranks
    league_ranks = []
    memberships_result = await db.execute(
        select(LeagueMembership).options(selectinload(LeagueMembership.league)).where(
            LeagueMembership.user_id == current_user.user_id
        )
    )
    memberships = memberships_result.scalars().all()
    
    for membership in memberships:
        league = membership.league
        # Count members with higher skill_rank in this league
        league_rank_result = await db.execute(
            select(func.count()).select_from(LeagueMembership).join(User).where(
                LeagueMembership.league_id == league.id,
                User.skill_rank > current_user.skill_rank
            )
        )
        league_above = league_rank_result.scalar() or 0
        league_member_count_result = await db.execute(
            select(func.count()).select_from(LeagueMembership).where(
                LeagueMembership.league_id == league.id
            )
        )
        league_member_count = league_member_count_result.scalar() or 1
        league_ranks.append({
            "league_id": league.id,
            "league_name": league.name,
            "rank": league_above + 1,
            "total": league_member_count
        })
    
    ranks["leagues"] = league_ranks
    
    return ranks

# League Endpoints
class CreateLeagueRequest(BaseModel):
    name: str
    league_type: str = "public"  # "public" or "private"

@api_router.post("/leagues")
async def create_league(data: CreateLeagueRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Create a new league"""
    invite_code = generate_invite_code()
    
    league = League(
        id=str(uuid.uuid4()),
        name=data.name,
        league_type=data.league_type,
        invite_code=invite_code,
        created_by=current_user.user_id
    )
    db.add(league)
    
    # Auto-join creator
    membership = LeagueMembership(
        id=str(uuid.uuid4()),
        league_id=league.id,
        user_id=current_user.user_id
    )
    db.add(membership)
    await db.commit()
    await db.refresh(league)
    
    return {
        "id": league.id,
        "name": league.name,
        "league_type": league.league_type,
        "invite_code": league.invite_code,
        "member_count": 1
    }

@api_router.get("/leagues")
async def list_leagues(league_type: Optional[str] = None, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List leagues (public or user's private leagues)"""
    query = select(League).options(selectinload(League.memberships))
    
    if league_type == "public":
        query = query.where(League.league_type == "public")
    elif league_type == "private":
        # Only show private leagues the user belongs to
        query = query.join(LeagueMembership).where(
            League.league_type == "private",
            LeagueMembership.user_id == current_user.user_id
        )
    else:
        # Show all public + user's private
        query = query.where(
            or_(
                League.league_type == "public",
                League.id.in_(
                    select(LeagueMembership.league_id).where(
                        LeagueMembership.user_id == current_user.user_id
                    )
                )
            )
        )
    
    result = await db.execute(query.order_by(League.created_at.desc()).limit(50))
    leagues = result.scalars().unique().all()
    
    # Check which leagues the user is a member of
    user_memberships_result = await db.execute(
        select(LeagueMembership.league_id).where(LeagueMembership.user_id == current_user.user_id)
    )
    user_league_ids = {row[0] for row in user_memberships_result.all()}
    
    return [{
        "id": league.id,
        "name": league.name,
        "league_type": league.league_type,
        "invite_code": league.invite_code if league.league_type == "private" else None,
        "member_count": len(league.memberships),
        "is_member": league.id in user_league_ids,
        "is_creator": league.created_by == current_user.user_id
    } for league in leagues]

@api_router.post("/leagues/{league_id}/join")
async def join_league(league_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Join a league by ID"""
    result = await db.execute(select(League).where(League.id == league_id))
    league = result.scalar_one_or_none()
    
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    # Check if already a member
    existing = await db.execute(
        select(LeagueMembership).where(
            LeagueMembership.league_id == league_id,
            LeagueMembership.user_id == current_user.user_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already a member")
    
    membership = LeagueMembership(
        id=str(uuid.uuid4()),
        league_id=league_id,
        user_id=current_user.user_id
    )
    db.add(membership)
    await db.commit()
    
    return {"message": "Joined league successfully"}

@api_router.post("/leagues/join-code/{invite_code}")
async def join_league_by_code(invite_code: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Join a private league by invite code"""
    result = await db.execute(select(League).where(League.invite_code == invite_code))
    league = result.scalar_one_or_none()
    
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    existing = await db.execute(
        select(LeagueMembership).where(
            LeagueMembership.league_id == league.id,
            LeagueMembership.user_id == current_user.user_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already a member")
    
    membership = LeagueMembership(
        id=str(uuid.uuid4()),
        league_id=league.id,
        user_id=current_user.user_id
    )
    db.add(membership)
    await db.commit()
    
    return {"message": "Joined league successfully", "league_id": league.id, "league_name": league.name}

@api_router.post("/leagues/{league_id}/leave")
async def leave_league(league_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Leave a league"""
    result = await db.execute(
        select(LeagueMembership).where(
            LeagueMembership.league_id == league_id,
            LeagueMembership.user_id == current_user.user_id
        )
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(status_code=404, detail="Not a member of this league")
    
    await db.delete(membership)
    await db.commit()
    
    return {"message": "Left league successfully"}

@api_router.get("/leagues/{league_id}")
async def get_league(league_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get league details with leaderboard"""
    result = await db.execute(
        select(League).options(
            selectinload(League.memberships).selectinload(LeagueMembership.user)
        ).where(League.id == league_id)
    )
    league = result.scalar_one_or_none()
    
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    members = sorted(league.memberships, key=lambda m: m.user.skill_rank if m.user else 0, reverse=True)
    
    return {
        "id": league.id,
        "name": league.name,
        "league_type": league.league_type,
        "invite_code": league.invite_code,
        "member_count": len(members),
        "leaderboard": [{
            "rank": idx + 1,
            "user_id": m.user.user_id,
            "username": m.user.username,
            "avatar": m.user.avatar,
            "skill_rank": m.user.skill_rank,
            "is_current_user": m.user.user_id == current_user.user_id
        } for idx, m in enumerate(members) if m.user]
    }

# Question Endpoints (Admin)
@api_router.post("/questions")
async def create_question(data: QuestionCreate, password: str, db: AsyncSession = Depends(get_db)):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin password")
    
    question = Question(
        id=str(uuid.uuid4()),
        question_text=data.question_text,
        option_a=data.option_a,
        option_b=data.option_b,
        option_c=data.option_c,
        option_d=data.option_d,
        correct_option=data.correct_option,
        category=data.category,
        difficulty=data.difficulty
    )
    db.add(question)
    await db.commit()
    await db.refresh(question)
    
    return {
        "id": question.id,
        "question_text": question.question_text,
        "option_a": question.option_a,
        "option_b": question.option_b,
        "option_c": question.option_c,
        "option_d": question.option_d,
        "correct_option": question.correct_option,
        "category": question.category,
        "difficulty": question.difficulty
    }

@api_router.get("/questions")
async def list_questions(category: Optional[str] = None, limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    query = select(Question)
    if category:
        query = query.where(Question.category == category)
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    questions = result.scalars().all()
    
    return [{
        "id": q.id,
        "question_text": q.question_text,
        "option_a": q.option_a,
        "option_b": q.option_b,
        "option_c": q.option_c,
        "option_d": q.option_d,
        "correct_option": q.correct_option,
        "category": q.category,
        "difficulty": q.difficulty
    } for q in questions]

@api_router.get("/questions/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Question.category).distinct())
    categories = [row[0] for row in result.all()]
    return categories

@api_router.get("/questions/random-categories")
async def get_random_categories(db: AsyncSession = Depends(get_db)):
    """Return 3 random categories — a mix of club names and regular topics"""
    import random
    from clubs_data import get_all_clubs

    result = await db.execute(
        select(Question.category, func.count(Question.id))
        .where(Question.category != "Club")
        .group_by(Question.category)
        .having(func.count(Question.id) >= 3)
    )
    topics = [row[0] for row in result.all()]
    clubs = get_all_clubs()

    # Pick 3 items: each slot has ~40% chance of being a topic, ~60% club
    picks = []
    for _ in range(3):
        if topics and (random.random() < 0.4 or not clubs):
            pick = random.choice(topics)
        else:
            pick = random.choice(clubs)
        # Avoid duplicates
        while pick in picks:
            pick = random.choice(topics + clubs)
        picks.append(pick)
    return picks

# Game Endpoints
BOT_USERNAME = "TheScore90Bot"
BOT_AVATAR = "https://customer-assets.emergentagent.com/job_d6d8626b-a5b2-4b68-bfb7-a1cde78903a3/artifacts/0bpnaz6x_Black-Avatar.png"

async def get_or_create_bot(db: AsyncSession) -> User:
    """Get or create the TheScore90Bot user"""
    result = await db.execute(select(User).where(User.username == BOT_USERNAME))
    bot = result.scalar_one_or_none()
    if not bot:
        bot = User(
            user_id=str(uuid.uuid4()),
            email="bot@score90.com",
            name="Score90 Bot",
            username=BOT_USERNAME,
            avatar=BOT_AVATAR,
            skill_rank=1000,
            is_admin=False,
        )
        db.add(bot)
        await db.commit()
        await db.refresh(bot)
    elif bot.avatar != BOT_AVATAR:
        bot.avatar = BOT_AVATAR
        await db.commit()
    return bot

@api_router.post("/games/quick-play")
async def quick_play(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Start a quick play game against TheScore90Bot"""
    bot = await get_or_create_bot(db)
    # Match bot rank to user's rank
    bot.skill_rank = current_user.skill_rank
    
    game = Game(
        id=str(uuid.uuid4()),
        player1_id=current_user.user_id,
        player2_id=bot.user_id,
        current_round=1,
        status='active',
        turn_player_id=current_user.user_id,
        is_bot_game=True,
        turn_started_at=datetime.now(timezone.utc)
    )
    db.add(game)
    await db.commit()
    await db.refresh(game)
    
    return {"game_id": game.id, "opponent": BOT_USERNAME}

@api_router.get("/games/history")
async def get_game_history(current_user: User = Depends(get_current_user), limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Get user's completed game history"""
    result = await db.execute(
        select(Game).options(
            selectinload(Game.player1),
            selectinload(Game.player2),
            selectinload(Game.rounds)
        ).where(
            or_(Game.player1_id == current_user.user_id, Game.player2_id == current_user.user_id),
            Game.status == 'finished'
        ).order_by(Game.updated_at.desc()).limit(limit)
    )
    finished_games = result.scalars().all()
    
    history = []
    for game in finished_games:
        my_score = sum(r.player1_score if game.player1_id == current_user.user_id else r.player2_score for r in game.rounds)
        opponent_score = sum(r.player2_score if game.player1_id == current_user.user_id else r.player1_score for r in game.rounds)
        opponent = game.player2 if game.player1_id == current_user.user_id else game.player1
        
        history.append({
            "id": game.id,
            "opponent_username": opponent.username,
            "opponent_avatar": opponent.avatar,
            "my_score": my_score,
            "opponent_score": opponent_score,
            "won": game.winner_id == current_user.user_id,
            "date": game.updated_at.isoformat() if game.updated_at else None
        })
    
    return history

@api_router.post("/games/matchmake")
async def matchmake(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Find an opponent (simple random for MVP)
    result = await db.execute(
        select(User).where(User.user_id != current_user.user_id).order_by(func.random()).limit(1)
    )
    opponent = result.scalar_one_or_none()
    
    if not opponent:
        raise HTTPException(status_code=404, detail="No opponents available")
    
    game = Game(
        id=str(uuid.uuid4()),
        player1_id=current_user.user_id,
        player2_id=opponent.user_id,
        current_round=1,
        status='active',
        turn_player_id=current_user.user_id
    )
    db.add(game)
    await db.commit()
    await db.refresh(game)
    
    return {"game_id": game.id}

@api_router.post("/games/club-challenge")
async def start_club_challenge(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Start a solo club challenge game with questions about user's favorite club"""
    if not current_user.favorite_club:
        raise HTTPException(status_code=400, detail="Please select your favorite club first")
    
    # Create a special single-player game
    game = Game(
        id=str(uuid.uuid4()),
        player1_id=current_user.user_id,
        player2_id=current_user.user_id,  # Same player for solo mode
        current_round=1,
        status='club_challenge',
        turn_player_id=current_user.user_id
    )
    db.add(game)
    await db.commit()
    await db.refresh(game)
    
    return {"game_id": game.id, "club": current_user.favorite_club}

@api_router.post("/games/invite")
async def create_invite(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    invite_code = generate_invite_code()
    
    # Create game with placeholder for player2
    game = Game(
        id=str(uuid.uuid4()),
        player1_id=current_user.user_id,
        player2_id=current_user.user_id,  # Temporary, will be updated when someone joins
        current_round=0,  # Game hasn't started yet
        status='pending',
        invite_code=invite_code
    )
    db.add(game)
    await db.commit()
    
    return {"invite_code": invite_code, "game_id": game.id}

@api_router.post("/games/join/{invite_code}")
async def join_game(invite_code: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Game).where(Game.invite_code == invite_code))
    game = result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if game.status != 'pending':
        raise HTTPException(status_code=400, detail="Game already started")
    
    if game.player1_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot join your own game")
    
    game.player2_id = current_user.user_id
    game.current_round = 1
    game.status = 'active'
    game.turn_player_id = game.player1_id
    
    await db.commit()
    
    return {"game_id": game.id}

@api_router.get("/games")
async def list_games(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Game).options(
            selectinload(Game.player1),
            selectinload(Game.player2),
            selectinload(Game.rounds)
        ).where(
            or_(Game.player1_id == current_user.user_id, Game.player2_id == current_user.user_id),
            Game.status.in_(['active', 'pending'])
        ).order_by(Game.updated_at.desc())
    )
    games = result.scalars().all()
    
    game_list = []
    for game in games:
        my_score = sum(r.player1_score if game.player1_id == current_user.user_id else r.player2_score for r in game.rounds)
        opponent_score = sum(r.player2_score if game.player1_id == current_user.user_id else r.player1_score for r in game.rounds)
        
        game_list.append({
            "id": game.id,
            "player1": {
                "user_id": game.player1.user_id,
                "username": game.player1.username,
                "avatar": game.player1.avatar,
                "skill_rank": game.player1.skill_rank
            },
            "player2": {
                "user_id": game.player2.user_id,
                "username": game.player2.username,
                "avatar": game.player2.avatar,
                "skill_rank": game.player2.skill_rank
            } if game.player2_id != game.player1_id else None,
            "current_round": game.current_round,
            "status": game.status,
            "turn_player_id": game.turn_player_id,
            "is_my_turn": game.turn_player_id == current_user.user_id,
            "my_score": my_score,
            "opponent_score": opponent_score,
            "invite_code": game.invite_code
        })
    
    return game_list

@api_router.get("/games/{game_id}")
async def get_game(game_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Game).options(
            selectinload(Game.player1),
            selectinload(Game.player2),
            selectinload(Game.rounds)
        ).where(Game.id == game_id)
    )
    game = result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if game.player1_id != current_user.user_id and game.player2_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    my_score = sum(r.player1_score if game.player1_id == current_user.user_id else r.player2_score for r in game.rounds)
    opponent_score = sum(r.player2_score if game.player1_id == current_user.user_id else r.player1_score for r in game.rounds)
    
    is_player1 = game.player1_id == current_user.user_id
    
    # Calculate turn deadline (3 hours for real players)
    turn_deadline = None
    if game.turn_started_at and game.status == 'active':
        turn_deadline = (game.turn_started_at + timedelta(hours=3)).isoformat()
    
    # Build rounds data with opponent answers for playback
    rounds_data = []
    for r in sorted(game.rounds, key=lambda x: x.round_number):
        rd = {
            "round_number": r.round_number,
            "category_selected": r.category_selected,
            "player1_score": r.player1_score,
            "player2_score": r.player2_score,
        }
        # Include opponent's answers for completed rounds (playback)
        my_answers = r.player1_answers if is_player1 else r.player2_answers
        opp_answers = r.player2_answers if is_player1 else r.player1_answers
        rd["my_answers"] = my_answers or []
        # Only show opponent answers after both sides answered this round
        if len(my_answers or []) >= 3 and len(opp_answers or []) >= 3:
            rd["opponent_answers"] = opp_answers
        else:
            rd["opponent_answers"] = []
        rd["questions"] = r.questions or []
        rounds_data.append(rd)
    
    return {
        "id": game.id,
        "player1": {
            "user_id": game.player1.user_id,
            "username": game.player1.username,
            "avatar": game.player1.avatar,
            "skill_rank": game.player1.skill_rank,
            "player_tier": game.player1.player_tier or 1
        },
        "player2": {
            "user_id": game.player2.user_id,
            "username": game.player2.username,
            "avatar": game.player2.avatar,
            "skill_rank": game.player2.skill_rank,
            "player_tier": game.player2.player_tier or 1
        },
        "current_round": game.current_round,
        "status": game.status,
        "turn_player_id": game.turn_player_id,
        "is_my_turn": game.turn_player_id == current_user.user_id,
        "winner_id": game.winner_id,
        "my_score": my_score,
        "opponent_score": opponent_score,
        "is_bot_game": game.is_bot_game or False,
        "turn_started_at": game.turn_started_at.isoformat() if game.turn_started_at else None,
        "turn_deadline": turn_deadline,
        "rounds": rounds_data,
        "my_ball_knowledge": current_user.skill_rank or 1000,
        "credit_bet": game.credit_bet or 0,
        "challenge_id": game.challenge_id,
    }

@api_router.post("/games/{game_id}/bot-play")
async def bot_play(game_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Simulate the bot playing its turn. Returns the bot's answers for live playback."""
    result = await db.execute(
        select(Game).options(selectinload(Game.rounds)).where(Game.id == game_id)
    )
    game = result.scalar_one_or_none()
    
    if not game or not game.is_bot_game:
        raise HTTPException(status_code=400, detail="Not a bot game")
    
    # Bot should be player2 and it should be the bot's turn
    if game.turn_player_id != game.player2_id:
        raise HTTPException(status_code=400, detail="Not the bot's turn")
    
    # Get current round (use first() to handle potential duplicates gracefully)
    round_result = await db.execute(
        select(GameRound).where(
            GameRound.game_id == game_id,
            GameRound.round_number == game.current_round
        ).order_by(GameRound.id).limit(1)
    )
    game_round = round_result.scalar_one_or_none()
    
    if not game_round or not game_round.questions:
        raise HTTPException(status_code=400, detail="Round not set up")
    
    # Load the questions for this round
    q_ids = game_round.questions
    q_result = await db.execute(select(Question).where(Question.id.in_(q_ids)))
    questions_map = {q.id: q for q in q_result.scalars().all()}
    
    # Calculate bot accuracy
    if game.challenge_id:
        # Challenge game: use fixed bot accuracy from the challenge
        challenge_result = await db.execute(select(WeeklyChallenge).where(WeeklyChallenge.id == game.challenge_id))
        challenge = challenge_result.scalar_one_or_none()
        bot_accuracy = challenge.bot_accuracy if challenge else 0.7
    else:
        # Regular game: dynamically match user's performance
        total_answers = 0
        correct_answers = 0
        for r in game.rounds:
            for ans in (r.player1_answers or []):
                total_answers += 1
                if ans.get("is_correct"):
                    correct_answers += 1
        
        if total_answers > 0:
            user_accuracy = correct_answers / total_answers
        else:
            user_accuracy = 0.5
        
        bot_accuracy = max(0.15, min(0.95, user_accuracy + random.uniform(-0.10, 0.10)))
    
    bot_answers = []
    bot_score = 0
    
    for q_id in q_ids:
        question = questions_map.get(q_id)
        if not question:
            continue
        
        # Bot decides if it gets it right
        is_correct = random.random() < bot_accuracy
        
        if is_correct:
            selected = question.correct_option
            time_taken = random.uniform(3.0, 12.0)  # Bot takes 3-12 seconds
            base_score = 100
            time_bonus = max(0, int(50 * (1 - min(time_taken / 15, 1))))
            score = base_score + time_bonus
        else:
            # Pick a wrong answer
            options = ['A', 'B', 'C', 'D']
            options.remove(question.correct_option)
            selected = random.choice(options)
            time_taken = random.uniform(5.0, 14.0)
            score = 0
        
        bot_answers.append({
            "question_id": q_id,
            "selected_option": selected,
            "correct_option": question.correct_option,
            "is_correct": is_correct,
            "time_taken": round(time_taken, 1),
            "score": score,
            "question_text": question.question_text,
            "option_a": question.option_a,
            "option_b": question.option_b,
            "option_c": question.option_c,
            "option_d": question.option_d,
        })
        bot_score += score
    
    # Save bot answers
    game_round.player2_answers = [{
        "question_id": a["question_id"],
        "selected_option": a["selected_option"],
        "correct_option": a["correct_option"],
        "is_correct": a["is_correct"],
        "time_taken": a["time_taken"],
        "score": a["score"]
    } for a in bot_answers]
    game_round.player2_score = bot_score
    
    # Advance game
    credits_won = 0
    achievements_earned = []
    if game.current_round >= 6:
        total_p1 = sum(r.player1_score for r in game.rounds)
        total_p2 = sum(r.player2_score for r in game.rounds)
        game.winner_id = game.player1_id if total_p1 >= total_p2 else game.player2_id
        game.status = 'finished'
        
        # Credit payout for challenge/bet games
        if game.credit_bet and game.credit_bet > 0:
            if game.winner_id == current_user.user_id:
                # Winner gets the payout
                if game.challenge_id:
                    # Challenge: win_amount from challenge
                    ch_result = await db.execute(select(WeeklyChallenge).where(WeeklyChallenge.id == game.challenge_id))
                    ch = ch_result.scalar_one_or_none()
                    credits_won = ch.win_amount if ch else game.credit_bet * 2
                else:
                    # P2P: winner takes all (both bets)
                    credits_won = game.credit_bet * 2
                current_user.credits = (current_user.credits or 0) + credits_won
            # Loser already had credits deducted at game start
        
        # Update Ball Knowledge score
        old_rank, new_rank, delta, tier_update = await update_ball_knowledge(db, game, current_user)
        
        # Check for achievements
        achievements_earned = await check_and_award_achievements(db, current_user, game)
    else:
        game.current_round += 1
        game.turn_player_id = game.player1_id
        game.turn_started_at = datetime.now(timezone.utc)
        old_rank, new_rank, delta, tier_update = None, None, None, None
    
    await db.commit()
    
    return {
        "bot_answers": bot_answers,
        "bot_score": bot_score,
        "round_complete": True,
        "game_status": game.status,
        "ball_knowledge_update": {"old": old_rank, "new": new_rank, "delta": delta} if delta is not None else None,
        "credits_won": credits_won if credits_won > 0 else None,
        "tier_update": tier_update,
        "achievements_earned": achievements_earned if achievements_earned else None,
    }

@api_router.post("/games/{game_id}/select-category")
async def select_category(game_id: str, category: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Game).options(selectinload(Game.rounds)).where(Game.id == game_id)
    )
    game = result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if game.turn_player_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not your turn")
    
    # Get question IDs this user has seen in the last 3 months
    three_months_ago = datetime.now(timezone.utc) - timedelta(days=90)
    seen_result = await db.execute(
        select(UserQuestionHistory.question_id).where(
            UserQuestionHistory.user_id == current_user.user_id,
            UserQuestionHistory.served_at >= three_months_ago
        )
    )
    seen_ids = {row[0] for row in seen_result.all()}
    
    # Build base query with exclusion of seen questions
    if game.status == 'club_challenge' and current_user.favorite_club:
        # Club Challenge: questions about user's favorite club
        club_name = current_user.favorite_club
        base_filter = [
            Question.category == "Club",
            Question.question_text.ilike(f"%{club_name}%")
        ]
        fallback_filter = [Question.category == "Club"]
    else:
        # Regular game: category is a club name — filter questions mentioning that club
        from clubs_data import get_all_clubs
        all_clubs = get_all_clubs()
        if category in all_clubs:
            base_filter = [
                Question.category == "Club",
                Question.question_text.ilike(f"%{category}%")
            ]
            fallback_filter = [Question.category == "Club"]
        else:
            base_filter = [Question.category == category]
            fallback_filter = base_filter
    
    # Try with exclusion first
    exclusion = [Question.id.notin_(seen_ids)] if seen_ids else []
    q_result = await db.execute(
        select(Question).where(*base_filter, *exclusion).order_by(func.random()).limit(3)
    )
    questions = q_result.scalars().all()
    
    # Fallback: broaden to all Club questions (still excluding seen)
    if len(questions) < 3:
        q_result = await db.execute(
            select(Question).where(*fallback_filter, *exclusion).order_by(func.random()).limit(3)
        )
        questions = q_result.scalars().all()
    
    # Ultimate fallback: allow repeats if the pool is exhausted
    if len(questions) < 3:
        q_result = await db.execute(
            select(Question).where(*fallback_filter).order_by(func.random()).limit(3)
        )
        questions = q_result.scalars().all()
        questions = q_result.scalars().all()
    
    if len(questions) < 3:
        raise HTTPException(status_code=400, detail="Not enough questions in this category")
    
    # Record these questions in user history
    for q in questions:
        db.add(UserQuestionHistory(
            id=str(uuid.uuid4()),
            user_id=current_user.user_id,
            question_id=q.id
        ))
    
    # Create or update round
    round_result = await db.execute(
        select(GameRound).where(
            GameRound.game_id == game_id,
            GameRound.round_number == game.current_round
        ).order_by(GameRound.id).limit(1)
    )
    game_round = round_result.scalar_one_or_none()
    
    if not game_round:
        game_round = GameRound(
            id=str(uuid.uuid4()),
            game_id=game_id,
            round_number=game.current_round,
            category_selected=category,
            questions=[q.id for q in questions],
            player1_answers=[],
            player2_answers=[]
        )
        db.add(game_round)
    else:
        game_round.category_selected = category
        game_round.questions = [q.id for q in questions]
    
    await db.commit()
    
    return {
        "questions": [{
            "id": q.id,
            "question_text": q.question_text,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d
        } for q in questions]
    }

@api_router.post("/games/{game_id}/answer")
async def submit_answer(game_id: str, data: AnswerSubmit, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Game).options(selectinload(Game.rounds)).where(Game.id == game_id)
    )
    game = result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if game.turn_player_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not your turn")
    
    # Get current round (use first() to handle potential duplicates gracefully)
    round_result = await db.execute(
        select(GameRound).where(
            GameRound.game_id == game_id,
            GameRound.round_number == game.current_round
        ).order_by(GameRound.id).limit(1)
    )
    game_round = round_result.scalar_one_or_none()
    
    if not game_round:
        raise HTTPException(status_code=404, detail="Round not found")
    
    # Get question
    q_result = await db.execute(select(Question).where(Question.id == data.question_id))
    question = q_result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Calculate score (correct answer + speed bonus)
    is_correct = data.selected_option == question.correct_option
    score = 0
    if is_correct:
        base_score = 100
        # Speed bonus: max 50 points if answered in 1 second, decreasing linearly
        time_bonus = max(0, int(50 * (1 - min(data.time_taken / 15, 1))))
        score = base_score + time_bonus
    
    # Update round
    is_solo = game.player1_id == game.player2_id  # Club challenge / solo mode
    is_player1 = game.player1_id == current_user.user_id
    
    answer_entry = {
        "question_id": data.question_id,
        "selected_option": data.selected_option,
        "correct_option": question.correct_option,
        "is_correct": is_correct,
        "time_taken": data.time_taken,
        "score": score
    }
    
    bk_update = None
    achievements_earned = []
    
    if is_solo:
        # Solo / Club Challenge mode: all answers go to player1, round completes after 3 answers
        answers = list(game_round.player1_answers or [])
        answers.append(answer_entry)
        game_round.player1_answers = answers
        game_round.player1_score += score
        
        if len(answers) >= 3:
            # Check for round-specific achievements
            round_achievements = await check_and_award_achievements(
                db, current_user, None, {"answers": answers}
            )
            achievements_earned.extend(round_achievements)
            
            # Round complete in solo mode
            if game.current_round >= 6:
                game.winner_id = game.player1_id
                game.status = 'finished'
                old_rank, new_rank, delta, tier_up = await update_ball_knowledge(db, game, current_user)
                bk_update = {"old": old_rank, "new": new_rank, "delta": delta}
                # Check game completion achievements
                game_achievements = await check_and_award_achievements(db, current_user, game)
                achievements_earned.extend(game_achievements)
            else:
                game.current_round += 1
                game.turn_player_id = game.player1_id
                game.turn_started_at = datetime.now(timezone.utc)
    elif is_player1:
        answers = list(game_round.player1_answers or [])
        answers.append(answer_entry)
        game_round.player1_answers = answers
        game_round.player1_score += score
        
        # Check if player1 completed all 3 questions
        if len(answers) >= 3:
            # Check for round-specific achievements
            round_achievements = await check_and_award_achievements(
                db, current_user, None, {"answers": answers}
            )
            achievements_earned.extend(round_achievements)
            # Switch turn to player2
            game.turn_player_id = game.player2_id
            game.turn_started_at = datetime.now(timezone.utc)
    else:
        answers = list(game_round.player2_answers or [])
        answers.append(answer_entry)
        game_round.player2_answers = answers
        game_round.player2_score += score
        
        # Check if player2 completed all 3 questions
        if len(answers) >= 3:
            # Check for round-specific achievements
            round_achievements = await check_and_award_achievements(
                db, current_user, None, {"answers": answers}
            )
            achievements_earned.extend(round_achievements)
            
            # Round complete, move to next round
            if game.current_round >= 6:
                # Game finished
                total_p1 = sum(r.player1_score for r in game.rounds)
                total_p2 = sum(r.player2_score for r in game.rounds)
                game.winner_id = game.player1_id if total_p1 > total_p2 else game.player2_id
                game.status = 'finished'
                old_rank, new_rank, delta, tier_up = await update_ball_knowledge(db, game, current_user)
                bk_update = {"old": old_rank, "new": new_rank, "delta": delta}
                # Check game completion achievements
                game_achievements = await check_and_award_achievements(db, current_user, game)
                achievements_earned.extend(game_achievements)
                
                # P2P credit payout
                if game.credit_bet and game.credit_bet > 0:
                    winner_id = game.winner_id
                    winner_result = await db.execute(select(User).where(User.user_id == winner_id))
                    winner_user = winner_result.scalar_one_or_none()
                    if winner_user:
                        winner_user.credits = (winner_user.credits or 0) + game.credit_bet * 2
            else:
                game.current_round += 1
                game.turn_player_id = game.player1_id
                game.turn_started_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return {
        "is_correct": is_correct,
        "score": score,
        "correct_option": question.correct_option,
        "ball_knowledge_update": bk_update,
        "achievements_earned": achievements_earned if achievements_earned else None
    }


# ========== WEEKLY CHALLENGES & CREDIT BETTING ==========

CHALLENGE_CONFIG = [
    {"difficulty": "easy", "bet": 5, "win": 15, "bot_accuracy": 0.55},
    {"difficulty": "medium", "bet": 10, "win": 30, "bot_accuracy": 0.70},
    {"difficulty": "hard", "bet": 15, "win": 45, "bot_accuracy": 0.80},
    {"difficulty": "very_hard", "bet": 20, "win": 60, "bot_accuracy": 0.90},
]

CHALLENGE_THEMES = [
    ("Stadiums", "Stadium Showdown"), ("History", "History Buff"),
    ("Champions League", "European Glory"), ("Players", "Player Expert"),
    ("Country", "International Master"), ("Fan Culture", "True Fan"),
    ("League", "League Guru"), ("Rules", "Referee's Test"),
    ("Terminology", "Football Lingo"), ("International Tournaments", "Tournament Trivia"),
]

async def ensure_weekly_challenges(db: AsyncSession):
    """Generate 5 challenges for the current week if they don't exist"""
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)
    
    result = await db.execute(
        select(WeeklyChallenge).where(WeeklyChallenge.week_start == week_start)
    )
    existing = result.scalars().all()
    if len(existing) >= 5:
        return existing
    
    # Generate 5 new challenges
    import random as _rng
    themes = _rng.sample(CHALLENGE_THEMES, min(5, len(CHALLENGE_THEMES)))
    # Distribute difficulties: 1 easy, 2 medium, 1 hard, 1 very_hard
    difficulties = [
        CHALLENGE_CONFIG[0], CHALLENGE_CONFIG[1], CHALLENGE_CONFIG[1],
        CHALLENGE_CONFIG[2], CHALLENGE_CONFIG[3],
    ]
    _rng.shuffle(difficulties)
    
    challenges = []
    for i in range(5):
        topic, title_base = themes[i]
        cfg = difficulties[i]
        ch = WeeklyChallenge(
            id=str(uuid.uuid4()),
            week_start=week_start,
            week_end=week_end,
            difficulty=cfg["difficulty"],
            topic=topic,
            title=f"{title_base}: {cfg['difficulty'].replace('_', ' ').title()}",
            bet_amount=cfg["bet"],
            win_amount=cfg["win"],
            bot_accuracy=cfg["bot_accuracy"],
        )
        db.add(ch)
        challenges.append(ch)
    
    await db.commit()
    return challenges


@api_router.get("/challenges/weekly")
async def get_weekly_challenges(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    challenges = await ensure_weekly_challenges(db)
    
    # Check which ones the user has already played this week
    ch_ids = [c.id for c in challenges]
    played_result = await db.execute(
        select(Game.challenge_id).where(
            Game.player1_id == current_user.user_id,
            Game.challenge_id.in_(ch_ids),
        )
    )
    played_ids = {row[0] for row in played_result.all()}
    
    return [{
        "id": c.id,
        "difficulty": c.difficulty,
        "topic": c.topic,
        "title": c.title,
        "bet_amount": c.bet_amount,
        "win_amount": c.win_amount,
        "bot_accuracy": c.bot_accuracy,
        "played": c.id in played_ids,
        "week_end": c.week_end.isoformat(),
    } for c in challenges]


@api_router.post("/challenges/{challenge_id}/start")
async def start_challenge(challenge_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Get challenge
    result = await db.execute(select(WeeklyChallenge).where(WeeklyChallenge.id == challenge_id))
    challenge = result.scalar_one_or_none()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    now = datetime.now(timezone.utc)
    if now > challenge.week_end:
        raise HTTPException(status_code=400, detail="Challenge has expired")
    
    # Check if already played
    existing = await db.execute(
        select(Game).where(
            Game.player1_id == current_user.user_id,
            Game.challenge_id == challenge_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="You already played this challenge")
    
    # Check credits
    user_credits = current_user.credits or 0
    if user_credits < challenge.bet_amount:
        raise HTTPException(status_code=400, detail=f"Not enough credits. Need {challenge.bet_amount}, have {user_credits}")
    
    # Deduct credits
    current_user.credits = user_credits - challenge.bet_amount
    
    # Get or create bot
    bot = await get_or_create_bot(db)
    
    game = Game(
        id=str(uuid.uuid4()),
        player1_id=current_user.user_id,
        player2_id=bot.user_id,
        status='active',
        is_bot_game=True,
        current_round=1,
        turn_player_id=current_user.user_id,
        turn_started_at=now,
        credit_bet=challenge.bet_amount,
        challenge_id=challenge_id,
    )
    db.add(game)
    await db.commit()
    
    return {
        "game_id": game.id,
        "bet_amount": challenge.bet_amount,
        "win_amount": challenge.win_amount,
        "topic": challenge.topic,
        "difficulty": challenge.difficulty,
        "credits_remaining": current_user.credits,
    }


@api_router.post("/games/invite-bet")
async def create_invite_bet(bet_amount: int = 0, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Create a P2P game with credit betting"""
    if bet_amount < 0 or bet_amount > 50:
        raise HTTPException(status_code=400, detail="Bet must be between 0 and 50 credits")
    
    if bet_amount > 0:
        user_credits = current_user.credits or 0
        if user_credits < bet_amount:
            raise HTTPException(status_code=400, detail=f"Not enough credits. Need {bet_amount}, have {user_credits}")
        current_user.credits = user_credits - bet_amount
    
    invite_code = generate_invite_code()
    game = Game(
        id=str(uuid.uuid4()),
        player1_id=current_user.user_id,
        player2_id=current_user.user_id,  # Placeholder until friend joins
        status='pending',
        current_round=1,
        turn_player_id=current_user.user_id,
        invite_code=invite_code,
        credit_bet=bet_amount,
    )
    db.add(game)
    await db.commit()
    
    return {
        "game_id": game.id,
        "invite_code": invite_code,
        "bet_amount": bet_amount,
        "credits_remaining": current_user.credits,
    }


@api_router.post("/games/join-bet/{invite_code}")
async def join_bet_game(invite_code: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Join a P2P bet game"""
    result = await db.execute(select(Game).where(Game.invite_code == invite_code, Game.status == 'pending'))
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found or already started")
    if game.player1_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot join your own game")
    
    bet = game.credit_bet or 0
    if bet > 0:
        user_credits = current_user.credits or 0
        if user_credits < bet:
            raise HTTPException(status_code=400, detail=f"Not enough credits. Need {bet}, have {user_credits}")
        current_user.credits = user_credits - bet
    
    game.player2_id = current_user.user_id
    game.status = 'active'
    game.turn_started_at = datetime.now(timezone.utc)
    await db.commit()
    
    return {
        "game_id": game.id,
        "bet_amount": bet,
        "credits_remaining": current_user.credits,
    }


# ========== STRIPE PAYMENT ENDPOINTS ==========
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from fastapi import Request
from dotenv import load_dotenv
load_dotenv()

CREDIT_PACKAGES = {
    "credits_100": {"amount": 0.99, "credits": 100, "label": "100 Credits"},
    "credits_500": {"amount": 3.99, "credits": 500, "label": "500 Credits"},
    "credits_1000": {"amount": 6.99, "credits": 1000, "label": "1000 Credits"},
    "premium": {"amount": 0.99, "credits": 0, "label": "Premium (Ad-Free)", "is_premium": True},
}

class CheckoutRequest(BaseModel):
    package_id: str
    origin_url: str

@api_router.post("/payments/checkout")
async def create_checkout(data: CheckoutRequest, request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Create a Stripe checkout session for a credit package"""
    if data.package_id not in CREDIT_PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package")
    
    package = CREDIT_PACKAGES[data.package_id]
    stripe_api_key = os.environ.get("STRIPE_API_KEY")
    
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
    
    success_url = f"{data.origin_url}/store?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{data.origin_url}/store"
    
    checkout_metadata = {
        "user_id": current_user.user_id,
        "package_id": data.package_id,
        "credits": str(package.get("credits", 0)),
        "is_premium": str(package.get("is_premium", False)),
    }
    
    checkout_request = CheckoutSessionRequest(
        amount=package["amount"],
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=checkout_metadata
    )
    
    session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Create payment transaction record
    transaction = PaymentTransaction(
        id=str(uuid.uuid4()),
        user_id=current_user.user_id,
        session_id=session.session_id,
        package_id=data.package_id,
        amount=package["amount"],
        currency="usd",
        credits_to_add=package.get("credits", 0),
        is_premium=package.get("is_premium", False),
        payment_status="pending",
        status="initiated",
        payment_metadata=checkout_metadata
    )
    db.add(transaction)
    await db.commit()
    
    return {"url": session.url, "session_id": session.session_id}

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str, request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Check payment status and fulfill if paid"""
    stripe_api_key = os.environ.get("STRIPE_API_KEY")
    
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
    
    checkout_status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
    
    # Update transaction
    result = await db.execute(
        select(PaymentTransaction).where(PaymentTransaction.session_id == session_id)
    )
    transaction = result.scalar_one_or_none()
    
    if transaction:
        # Only fulfill once
        already_fulfilled = transaction.status == "completed"
        
        transaction.payment_status = checkout_status.payment_status
        transaction.status = "completed" if checkout_status.payment_status == "paid" else checkout_status.status
        
        # Add credits or premium only once
        if checkout_status.payment_status == "paid" and not already_fulfilled:
            if transaction.credits_to_add > 0:
                current_user.credits = (current_user.credits or 0) + transaction.credits_to_add
            if transaction.is_premium:
                current_user.is_admin = False  # placeholder for premium flag
        
        await db.commit()
    
    return {
        "status": checkout_status.status,
        "payment_status": checkout_status.payment_status,
        "amount_total": checkout_status.amount_total,
        "currency": checkout_status.currency
    }

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events"""
    stripe_api_key = os.environ.get("STRIPE_API_KEY")
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
    
    body = await request.body()
    signature = request.headers.get("Stripe-Signature", "")
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        if webhook_response.payment_status == "paid":
            result = await db.execute(
                select(PaymentTransaction).where(PaymentTransaction.session_id == webhook_response.session_id)
            )
            transaction = result.scalar_one_or_none()
            
            if transaction and transaction.status != "completed":
                transaction.payment_status = "paid"
                transaction.status = "completed"
                
                # Fulfill
                user_result = await db.execute(select(User).where(User.user_id == transaction.user_id))
                user = user_result.scalar_one_or_none()
                if user:
                    if transaction.credits_to_add > 0:
                        user.credits = (user.credits or 0) + transaction.credits_to_add
                
                await db.commit()
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error"}

# ========== CLUB WARS ENDPOINTS ==========

def get_current_week_bounds():
    """Get the start and end of the current week (Monday-Sunday)"""
    now = datetime.now(timezone.utc)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=7)
    return start_of_week, end_of_week


# ========== CAREER PATH CHALLENGE ==========

# Initial 10 Career Path Challenges
CAREER_PATH_DATA = [
    {
        "player_name": "Zlatan Ibrahimović",
        "career_clubs": [
            {"club": "Malmö FF", "years": "1999-2001", "order": 1},
            {"club": "Ajax", "years": "2001-2004", "order": 2},
            {"club": "Juventus", "years": "2004-2006", "order": 3},
            {"club": "Inter Milan", "years": "2006-2009", "order": 4},
            {"club": "Barcelona", "years": "2009-2010", "order": 5},
            {"club": "AC Milan", "years": "2010-2012", "order": 6},
            {"club": "Paris Saint-Germain", "years": "2012-2016", "order": 7},
            {"club": "Manchester United", "years": "2016-2018", "order": 8},
            {"club": "LA Galaxy", "years": "2018-2019", "order": 9},
            {"club": "AC Milan", "years": "2020-2023", "order": 10},
        ],
        "hints": {"nationality": "Sweden", "position": "Striker"},
        "difficulty": "normal"
    },
    {
        "player_name": "Cristiano Ronaldo",
        "career_clubs": [
            {"club": "Sporting CP", "years": "2002-2003", "order": 1},
            {"club": "Manchester United", "years": "2003-2009", "order": 2},
            {"club": "Real Madrid", "years": "2009-2018", "order": 3},
            {"club": "Juventus", "years": "2018-2021", "order": 4},
            {"club": "Manchester United", "years": "2021-2022", "order": 5},
            {"club": "Al-Nassr", "years": "2023-present", "order": 6},
        ],
        "hints": {"nationality": "Portugal", "position": "Forward"},
        "difficulty": "easy"
    },
    {
        "player_name": "Thierry Henry",
        "career_clubs": [
            {"club": "Monaco", "years": "1994-1999", "order": 1},
            {"club": "Juventus", "years": "1999", "order": 2},
            {"club": "Arsenal", "years": "1999-2007", "order": 3},
            {"club": "Barcelona", "years": "2007-2010", "order": 4},
            {"club": "New York Red Bulls", "years": "2010-2014", "order": 5},
            {"club": "Arsenal", "years": "2012 (loan)", "order": 6},
        ],
        "hints": {"nationality": "France", "position": "Striker"},
        "difficulty": "normal"
    },
    {
        "player_name": "David Beckham",
        "career_clubs": [
            {"club": "Manchester United", "years": "1992-2003", "order": 1},
            {"club": "Real Madrid", "years": "2003-2007", "order": 2},
            {"club": "LA Galaxy", "years": "2007-2012", "order": 3},
            {"club": "AC Milan", "years": "2009 (loan)", "order": 4},
            {"club": "Paris Saint-Germain", "years": "2013", "order": 5},
        ],
        "hints": {"nationality": "England", "position": "Midfielder"},
        "difficulty": "easy"
    },
    {
        "player_name": "Nicolas Anelka",
        "career_clubs": [
            {"club": "Paris Saint-Germain", "years": "1996-1997", "order": 1},
            {"club": "Arsenal", "years": "1997-1999", "order": 2},
            {"club": "Real Madrid", "years": "1999-2000", "order": 3},
            {"club": "Paris Saint-Germain", "years": "2000-2002", "order": 4},
            {"club": "Liverpool", "years": "2001-2002 (loan)", "order": 5},
            {"club": "Manchester City", "years": "2002-2005", "order": 6},
            {"club": "Fenerbahçe", "years": "2005-2006", "order": 7},
            {"club": "Bolton Wanderers", "years": "2006-2008", "order": 8},
            {"club": "Chelsea", "years": "2008-2012", "order": 9},
            {"club": "Shanghai Shenhua", "years": "2012", "order": 10},
            {"club": "Juventus", "years": "2013", "order": 11},
            {"club": "West Bromwich Albion", "years": "2013-2014", "order": 12},
        ],
        "hints": {"nationality": "France", "position": "Striker"},
        "difficulty": "hard"
    },
    {
        "player_name": "Samuel Eto'o",
        "career_clubs": [
            {"club": "Real Madrid", "years": "1997-2000", "order": 1},
            {"club": "Leganés", "years": "1997-1998 (loan)", "order": 2},
            {"club": "Espanyol", "years": "1998-1999 (loan)", "order": 3},
            {"club": "Mallorca", "years": "2000-2004", "order": 4},
            {"club": "Barcelona", "years": "2004-2009", "order": 5},
            {"club": "Inter Milan", "years": "2009-2011", "order": 6},
            {"club": "Anzhi Makhachkala", "years": "2011-2013", "order": 7},
            {"club": "Chelsea", "years": "2013-2014", "order": 8},
            {"club": "Everton", "years": "2014", "order": 9},
            {"club": "Sampdoria", "years": "2014-2015", "order": 10},
            {"club": "Antalyaspor", "years": "2015-2016", "order": 11},
        ],
        "hints": {"nationality": "Cameroon", "position": "Striker"},
        "difficulty": "hard"
    },
    {
        "player_name": "Ronaldinho",
        "career_clubs": [
            {"club": "Grêmio", "years": "1998-2001", "order": 1},
            {"club": "Paris Saint-Germain", "years": "2001-2003", "order": 2},
            {"club": "Barcelona", "years": "2003-2008", "order": 3},
            {"club": "AC Milan", "years": "2008-2011", "order": 4},
            {"club": "Flamengo", "years": "2011", "order": 5},
            {"club": "Atlético Mineiro", "years": "2012-2014", "order": 6},
            {"club": "Querétaro", "years": "2014-2015", "order": 7},
            {"club": "Fluminense", "years": "2015", "order": 8},
        ],
        "hints": {"nationality": "Brazil", "position": "Attacking Midfielder"},
        "difficulty": "normal"
    },
    {
        "player_name": "Wayne Rooney",
        "career_clubs": [
            {"club": "Everton", "years": "2002-2004", "order": 1},
            {"club": "Manchester United", "years": "2004-2017", "order": 2},
            {"club": "Everton", "years": "2017-2018", "order": 3},
            {"club": "D.C. United", "years": "2018-2019", "order": 4},
            {"club": "Derby County", "years": "2020-2021", "order": 5},
        ],
        "hints": {"nationality": "England", "position": "Forward"},
        "difficulty": "easy"
    },
    {
        "player_name": "Cesc Fàbregas",
        "career_clubs": [
            {"club": "Arsenal", "years": "2003-2011", "order": 1},
            {"club": "Barcelona", "years": "2011-2014", "order": 2},
            {"club": "Chelsea", "years": "2014-2019", "order": 3},
            {"club": "Monaco", "years": "2019-2022", "order": 4},
            {"club": "Como 1907", "years": "2022-present", "order": 5},
        ],
        "hints": {"nationality": "Spain", "position": "Midfielder"},
        "difficulty": "normal"
    },
    {
        "player_name": "Robinho",
        "career_clubs": [
            {"club": "Santos", "years": "2002-2005", "order": 1},
            {"club": "Real Madrid", "years": "2005-2008", "order": 2},
            {"club": "Manchester City", "years": "2008-2010", "order": 3},
            {"club": "Santos", "years": "2010 (loan)", "order": 4},
            {"club": "AC Milan", "years": "2010-2015", "order": 5},
            {"club": "Guangzhou Evergrande", "years": "2015", "order": 6},
            {"club": "Atlético Mineiro", "years": "2016", "order": 7},
            {"club": "Sivasspor", "years": "2018", "order": 8},
            {"club": "İstanbul Başakşehir", "years": "2018-2020", "order": 9},
            {"club": "Santos", "years": "2020", "order": 10},
        ],
        "hints": {"nationality": "Brazil", "position": "Winger"},
        "difficulty": "hard"
    },
]


async def get_todays_career_challenge(db: AsyncSession):
    """Get or create today's career path challenge"""
    from datetime import date
    today = date.today()
    
    result = await db.execute(
        select(CareerPathChallenge).where(CareerPathChallenge.active_date == today)
    )
    challenge = result.scalar_one_or_none()
    
    if not challenge:
        # Pick a random challenge from the data based on day of year
        day_index = today.timetuple().tm_yday % len(CAREER_PATH_DATA)
        data = CAREER_PATH_DATA[day_index]
        
        challenge = CareerPathChallenge(
            id=str(uuid.uuid4()),
            player_name=data["player_name"],
            career_clubs=data["career_clubs"],
            hints=data.get("hints"),
            difficulty=data.get("difficulty", "normal"),
            active_date=today
        )
        db.add(challenge)
        await db.commit()
        await db.refresh(challenge)
    
    return challenge


@api_router.get("/career-challenge/today")
async def get_career_challenge_today(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get today's career path challenge"""
    challenge = await get_todays_career_challenge(db)
    
    # Get user's attempt if exists
    result = await db.execute(
        select(CareerPathAttempt).where(
            CareerPathAttempt.user_id == current_user.user_id,
            CareerPathAttempt.challenge_id == challenge.id
        )
    )
    attempt = result.scalar_one_or_none()
    
    total_clubs = len(challenge.career_clubs)
    clubs_to_show = 1
    guesses = []
    solved = False
    
    if attempt:
        clubs_to_show = attempt.clubs_revealed
        guesses = attempt.guesses or []
        solved = attempt.solved
    
    # Only reveal clubs up to clubs_to_show
    revealed_clubs = challenge.career_clubs[:clubs_to_show]
    
    return {
        "challenge_id": challenge.id,
        "difficulty": challenge.difficulty,
        "total_clubs": total_clubs,
        "clubs_revealed": clubs_to_show,
        "max_guesses": total_clubs,
        "guesses_made": len(guesses),
        "guesses": guesses,
        "revealed_clubs": revealed_clubs,
        "solved": solved,
        "answer": challenge.player_name if solved else None,
        "hints": challenge.hints if solved or clubs_to_show >= total_clubs // 2 else None
    }


class CareerGuess(BaseModel):
    guess: str


@api_router.post("/career-challenge/guess")
async def submit_career_guess(
    guess_data: CareerGuess,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit a guess for the career path challenge"""
    challenge = await get_todays_career_challenge(db)
    
    # Get or create attempt
    result = await db.execute(
        select(CareerPathAttempt).where(
            CareerPathAttempt.user_id == current_user.user_id,
            CareerPathAttempt.challenge_id == challenge.id
        )
    )
    attempt = result.scalar_one_or_none()
    
    if not attempt:
        attempt = CareerPathAttempt(
            id=str(uuid.uuid4()),
            user_id=current_user.user_id,
            challenge_id=challenge.id,
            guesses=[],
            clubs_revealed=1
        )
        db.add(attempt)
    
    if attempt.solved:
        return {"error": "Already solved", "solved": True, "answer": challenge.player_name}
    
    total_clubs = len(challenge.career_clubs)
    if len(attempt.guesses or []) >= total_clubs:
        return {"error": "No more guesses", "solved": False, "answer": challenge.player_name}
    
    # Check guess
    guess = guess_data.guess.strip()
    is_correct = guess.lower() == challenge.player_name.lower()
    
    # Update guesses
    guesses = list(attempt.guesses or [])
    guesses.append({"guess": guess, "correct": is_correct})
    attempt.guesses = guesses
    
    if is_correct:
        attempt.solved = True
        attempt.completed_at = datetime.now(timezone.utc)
        # Award credits based on how few guesses used
        clubs_used = attempt.clubs_revealed
        bonus_credits = max(10, 50 - (clubs_used * 5))
        current_user.credits = (current_user.credits or 0) + bonus_credits
    else:
        # Reveal next club
        attempt.clubs_revealed = min(attempt.clubs_revealed + 1, total_clubs)
    
    await db.commit()
    
    return {
        "correct": is_correct,
        "solved": attempt.solved,
        "clubs_revealed": attempt.clubs_revealed,
        "guesses_remaining": total_clubs - len(guesses),
        "revealed_clubs": challenge.career_clubs[:attempt.clubs_revealed],
        "answer": challenge.player_name if attempt.solved or len(guesses) >= total_clubs else None,
        "credits_earned": bonus_credits if is_correct else None,
        "hints": challenge.hints if attempt.solved or attempt.clubs_revealed >= total_clubs // 2 else None
    }


# ========== SKILL-BASED MATCHMAKING ENDPOINTS ==========

MATCHMAKING_SKILL_RANGE = 150  # Initial skill range to search for opponents
MATCHMAKING_EXPANSION_RATE = 50  # Expand range by this amount each check
MATCHMAKING_MAX_RANGE = 500  # Maximum skill range
MATCHMAKING_TIMEOUT_SECONDS = 120  # 2 minutes before expanding to bot match

@api_router.post("/matchmaking/join")
async def join_matchmaking_queue(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Join the skill-based matchmaking queue"""
    # Check if already in queue
    existing = await db.execute(
        select(MatchmakingQueue).where(
            MatchmakingQueue.user_id == current_user.user_id,
            MatchmakingQueue.status == 'waiting'
        )
    )
    if existing.scalar_one_or_none():
        return {"status": "already_queued", "message": "Already in matchmaking queue"}
    
    # Add to queue
    queue_entry = MatchmakingQueue(
        id=str(uuid.uuid4()),
        user_id=current_user.user_id,
        skill_rank=current_user.skill_rank or 1000,
        status='waiting'
    )
    db.add(queue_entry)
    await db.commit()
    
    return {
        "status": "queued",
        "skill_rank": current_user.skill_rank or 1000,
        "message": "Added to matchmaking queue"
    }

@api_router.delete("/matchmaking/leave")
async def leave_matchmaking_queue(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Leave the matchmaking queue"""
    result = await db.execute(
        select(MatchmakingQueue).where(
            MatchmakingQueue.user_id == current_user.user_id,
            MatchmakingQueue.status == 'waiting'
        )
    )
    entry = result.scalar_one_or_none()
    
    if entry:
        await db.delete(entry)
        await db.commit()
        return {"status": "left", "message": "Left matchmaking queue"}
    
    return {"status": "not_in_queue", "message": "Not in matchmaking queue"}

@api_router.get("/matchmaking/status")
async def get_matchmaking_status(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Check matchmaking status and attempt to find a match"""
    # Get user's queue entry
    result = await db.execute(
        select(MatchmakingQueue).where(
            MatchmakingQueue.user_id == current_user.user_id
        ).order_by(MatchmakingQueue.joined_at.desc())
    )
    my_entry = result.scalar_one_or_none()
    
    if not my_entry or my_entry.status != 'waiting':
        return {"status": "not_queued"}
    
    my_rank = my_entry.skill_rank
    wait_time = (datetime.now(timezone.utc) - my_entry.joined_at).total_seconds()
    
    # Calculate dynamic skill range based on wait time
    # Expand range by 50 every 15 seconds
    skill_range = min(
        MATCHMAKING_MAX_RANGE,
        MATCHMAKING_SKILL_RANGE + int(wait_time / 15) * MATCHMAKING_EXPANSION_RATE
    )
    
    # Find potential opponents within skill range
    potential_matches = await db.execute(
        select(MatchmakingQueue).options(selectinload(MatchmakingQueue.user)).where(
            MatchmakingQueue.user_id != current_user.user_id,
            MatchmakingQueue.status == 'waiting',
            MatchmakingQueue.skill_rank >= my_rank - skill_range,
            MatchmakingQueue.skill_rank <= my_rank + skill_range
        ).order_by(
            func.abs(MatchmakingQueue.skill_rank - my_rank)
        ).limit(1)
    )
    opponent_entry = potential_matches.scalar_one_or_none()
    
    if opponent_entry:
        # Match found! Create game
        game = Game(
            id=str(uuid.uuid4()),
            player1_id=current_user.user_id,
            player2_id=opponent_entry.user_id,
            current_round=1,
            status='active',
            turn_player_id=current_user.user_id,
            is_bot_game=False,
            turn_started_at=datetime.now(timezone.utc)
        )
        db.add(game)
        
        # Mark both queue entries as matched
        my_entry.status = 'matched'
        opponent_entry.status = 'matched'
        
        await db.commit()
        await db.refresh(game)
        
        return {
            "status": "matched",
            "game_id": game.id,
            "opponent": {
                "user_id": opponent_entry.user.user_id,
                "username": opponent_entry.user.username,
                "avatar": opponent_entry.user.avatar,
                "skill_rank": opponent_entry.user.skill_rank
            },
            "skill_diff": abs(my_rank - opponent_entry.skill_rank)
        }
    
    # No match yet - check if should offer bot match
    if wait_time >= MATCHMAKING_TIMEOUT_SECONDS:
        return {
            "status": "waiting",
            "wait_time": int(wait_time),
            "skill_range": skill_range,
            "offer_bot_match": True,
            "message": f"No opponent found after {int(wait_time)}s. Play against bot?"
        }
    
    # Get queue stats
    queue_count = await db.execute(
        select(func.count()).select_from(MatchmakingQueue).where(
            MatchmakingQueue.status == 'waiting'
        )
    )
    total_waiting = queue_count.scalar() or 0
    
    return {
        "status": "waiting",
        "wait_time": int(wait_time),
        "skill_range": skill_range,
        "players_in_queue": total_waiting,
        "your_rank": my_rank
    }

@api_router.post("/matchmaking/bot-fallback")
async def matchmaking_bot_fallback(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Accept bot match when no human opponent is found"""
    # Remove from queue
    result = await db.execute(
        select(MatchmakingQueue).where(
            MatchmakingQueue.user_id == current_user.user_id,
            MatchmakingQueue.status == 'waiting'
        )
    )
    queue_entry = result.scalar_one_or_none()
    if queue_entry:
        await db.delete(queue_entry)
    
    # Create bot game
    bot = await get_or_create_bot(db)
    bot.skill_rank = current_user.skill_rank or 1000
    
    game = Game(
        id=str(uuid.uuid4()),
        player1_id=current_user.user_id,
        player2_id=bot.user_id,
        current_round=1,
        status='active',
        turn_player_id=current_user.user_id,
        is_bot_game=True,
        turn_started_at=datetime.now(timezone.utc)
    )
    db.add(game)
    await db.commit()
    await db.refresh(game)
    
    return {"game_id": game.id, "opponent": BOT_USERNAME, "is_bot": True}


# ========== ACHIEVEMENT ENDPOINTS ==========

@api_router.get("/achievements")
async def get_all_achievements():
    """Get list of all available achievements"""
    return [{"id": k, **v} for k, v in ACHIEVEMENTS.items()]

@api_router.get("/achievements/me")
async def get_my_achievements(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get current user's earned achievements"""
    result = await db.execute(
        select(UserAchievement).where(UserAchievement.user_id == current_user.user_id).order_by(UserAchievement.earned_at.desc())
    )
    earned = result.scalars().all()
    
    earned_list = []
    for ua in earned:
        if ua.achievement_id in ACHIEVEMENTS:
            earned_list.append({
                "id": ua.achievement_id,
                "earned_at": ua.earned_at.isoformat() if ua.earned_at else None,
                **ACHIEVEMENTS[ua.achievement_id]
            })
    
    return {
        "earned": earned_list,
        "total_earned": len(earned_list),
        "total_available": len(ACHIEVEMENTS)
    }

@api_router.get("/users/{user_id}/achievements")
async def get_user_achievements(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific user's earned achievements (public view)"""
    result = await db.execute(
        select(UserAchievement).where(UserAchievement.user_id == user_id).order_by(UserAchievement.earned_at.desc())
    )
    earned = result.scalars().all()
    
    earned_list = []
    for ua in earned:
        if ua.achievement_id in ACHIEVEMENTS:
            earned_list.append({
                "id": ua.achievement_id,
                "earned_at": ua.earned_at.isoformat() if ua.earned_at else None,
                **ACHIEVEMENTS[ua.achievement_id]
            })
    
    return {
        "earned": earned_list,
        "total_earned": len(earned_list)
    }


# ========== PRIZE DRAWS ENDPOINTS ==========

class PrizeDrawEntry(BaseModel):
    draw_id: str
    cost: int

@api_router.post("/prize-draws/enter")
async def enter_prize_draw(
    entry: PrizeDrawEntry,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enter a prize draw by spending credits"""
    # Validate user has enough credits
    if (current_user.credits or 0) < entry.cost:
        raise HTTPException(status_code=400, detail="Not enough credits")
    
    # Deduct credits
    current_user.credits = (current_user.credits or 0) - entry.cost
    await db.commit()
    
    # In a real implementation, we'd store the entry in a prize_draw_entries table
    # For now, just deduct credits and return success
    
    return {
        "success": True,
        "draw_id": entry.draw_id,
        "credits_spent": entry.cost,
        "remaining_credits": current_user.credits,
        "message": "Entry submitted successfully. Good luck!"
    }


app.include_router(api_router)

# Serve uploaded files
app.mount("/api/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)