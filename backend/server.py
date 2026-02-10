from fastapi import FastAPI, APIRouter, Depends, HTTPException, Response, Cookie, Header, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from database import get_db
from models import User, UserSession, Question, Game, GameRound, League, LeagueMembership, PaymentTransaction, ClubWar, ClubWarContribution, MatchmakingQueue
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
        
        return {
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
        }
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
        "skill_rank": user.skill_rank
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

# Game Endpoints
BOT_USERNAME = "TheScore90Bot"

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
            avatar="https://api.dicebear.com/7.x/bottts/svg?seed=Score90Bot",
            skill_rank=1000,
            is_admin=False,
        )
        db.add(bot)
        await db.commit()
        await db.refresh(bot)
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
            "skill_rank": game.player1.skill_rank
        },
        "player2": {
            "user_id": game.player2.user_id,
            "username": game.player2.username,
            "avatar": game.player2.avatar,
            "skill_rank": game.player2.skill_rank
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
        "rounds": rounds_data
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
    
    # Get current round
    round_result = await db.execute(
        select(GameRound).where(
            GameRound.game_id == game_id,
            GameRound.round_number == game.current_round
        )
    )
    game_round = round_result.scalar_one_or_none()
    
    if not game_round or not game_round.questions:
        raise HTTPException(status_code=400, detail="Round not set up")
    
    # Load the questions for this round
    q_ids = game_round.questions
    q_result = await db.execute(select(Question).where(Question.id.in_(q_ids)))
    questions_map = {q.id: q for q in q_result.scalars().all()}
    
    # Simulate bot answers based on user's skill rank
    # Higher user rank = smarter bot (50-85% accuracy)
    user_rank = current_user.skill_rank or 1000
    bot_accuracy = min(0.85, max(0.50, user_rank / 2000))
    
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
    if game.current_round >= 6:
        total_p1 = sum(r.player1_score for r in game.rounds)
        total_p2 = sum(r.player2_score for r in game.rounds)
        game.winner_id = game.player1_id if total_p1 >= total_p2 else game.player2_id
        game.status = 'finished'
    else:
        game.current_round += 1
        game.turn_player_id = game.player1_id
        game.turn_started_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return {
        "bot_answers": bot_answers,
        "bot_score": bot_score,
        "round_complete": True,
        "game_status": game.status
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
    
    # Get 3 random questions from the selected category
    q_result = await db.execute(
        select(Question).where(Question.category == category).order_by(func.random()).limit(3)
    )
    questions = q_result.scalars().all()
    
    if len(questions) < 3:
        raise HTTPException(status_code=400, detail="Not enough questions in this category")
    
    # Create or update round
    round_result = await db.execute(
        select(GameRound).where(
            GameRound.game_id == game_id,
            GameRound.round_number == game.current_round
        )
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
    
    # Get current round
    round_result = await db.execute(
        select(GameRound).where(
            GameRound.game_id == game_id,
            GameRound.round_number == game.current_round
        )
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
    is_player1 = game.player1_id == current_user.user_id
    
    if is_player1:
        answers = list(game_round.player1_answers or [])
        answers.append({
            "question_id": data.question_id,
            "selected_option": data.selected_option,
            "is_correct": is_correct,
            "time_taken": data.time_taken,
            "score": score
        })
        game_round.player1_answers = answers
        game_round.player1_score += score
        
        # Check if player1 completed all 3 questions
        if len(answers) >= 3:
            # Switch turn to player2
            game.turn_player_id = game.player2_id
            game.turn_started_at = datetime.now(timezone.utc)
    else:
        answers = list(game_round.player2_answers or [])
        answers.append({
            "question_id": data.question_id,
            "selected_option": data.selected_option,
            "is_correct": is_correct,
            "time_taken": data.time_taken,
            "score": score
        })
        game_round.player2_answers = answers
        game_round.player2_score += score
        
        # Check if player2 completed all 3 questions
        if len(answers) >= 3:
            # Round complete, move to next round
            if game.current_round >= 6:
                # Game finished
                total_p1 = sum(r.player1_score for r in game.rounds)
                total_p2 = sum(r.player2_score for r in game.rounds)
                game.winner_id = game.player1_id if total_p1 > total_p2 else game.player2_id
                game.status = 'finished'
                
                # Update skill rankings (ELO-like system) for non-bot, non-self games
                if not game.is_bot_game and game.player1_id != game.player2_id:
                    # Get both players
                    p1_result = await db.execute(select(User).where(User.user_id == game.player1_id))
                    p2_result = await db.execute(select(User).where(User.user_id == game.player2_id))
                    player1 = p1_result.scalar_one_or_none()
                    player2 = p2_result.scalar_one_or_none()
                    
                    if player1 and player2:
                        p1_rank = player1.skill_rank or 1000
                        p2_rank = player2.skill_rank or 1000
                        
                        # Calculate ELO changes
                        p1_delta, p2_delta = calculate_elo_change(
                            p1_rank, p2_rank,
                            winner_is_p1=(game.winner_id == game.player1_id),
                            score_diff=abs(total_p1 - total_p2)
                        )
                        
                        player1.skill_rank = max(100, p1_rank + p1_delta)
                        player2.skill_rank = max(100, p2_rank + p2_delta)
                
                # Update club knowledge score for club challenge mode
                if game.status == 'club_challenge' or (game.player1_id == game.player2_id):
                    current_user.club_knowledge_score = (current_user.club_knowledge_score or 0) + total_p1
            else:
                game.current_round += 1
                game.turn_player_id = game.player1_id
                game.turn_started_at = datetime.now(timezone.utc)
    
    # Special handling for club challenge single-player mode
    if game.player1_id == game.player2_id and is_correct:
        current_user.club_knowledge_score = (current_user.club_knowledge_score or 0) + score
    
    await db.commit()
    
    return {
        "is_correct": is_correct,
        "score": score,
        "correct_option": question.correct_option if is_correct else None
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
    "premium": {"amount": 4.99, "credits": 0, "label": "Premium (Ad-Free)", "is_premium": True},
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

async def get_or_create_current_war(db: AsyncSession):
    """Get or create the current week's club war"""
    week_start, week_end = get_current_week_bounds()
    
    result = await db.execute(
        select(ClubWar).where(
            ClubWar.week_start == week_start,
            ClubWar.status == 'active'
        )
    )
    war = result.scalar_one_or_none()
    
    if not war:
        war = ClubWar(
            id=str(uuid.uuid4()),
            week_start=week_start,
            week_end=week_end,
            status='active'
        )
        db.add(war)
        await db.commit()
        await db.refresh(war)
    
    return war

@api_router.get("/club-wars/current")
async def get_current_club_war(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get the current week's club war leaderboard"""
    war = await get_or_create_current_war(db)
    
    # Aggregate club scores
    result = await db.execute(
        select(
            ClubWarContribution.club_name,
            func.sum(ClubWarContribution.points).label('total_points'),
            func.sum(ClubWarContribution.games_played).label('total_games'),
            func.count(ClubWarContribution.user_id.distinct()).label('member_count')
        ).where(
            ClubWarContribution.club_war_id == war.id
        ).group_by(ClubWarContribution.club_name).order_by(func.sum(ClubWarContribution.points).desc())
    )
    club_standings = result.all()
    
    # Get user's contribution
    user_contrib = None
    if current_user.favorite_club:
        user_result = await db.execute(
            select(ClubWarContribution).where(
                ClubWarContribution.club_war_id == war.id,
                ClubWarContribution.user_id == current_user.user_id
            )
        )
        user_contrib_obj = user_result.scalar_one_or_none()
        if user_contrib_obj:
            user_contrib = {
                "points": user_contrib_obj.points,
                "games_played": user_contrib_obj.games_played
            }
    
    return {
        "war_id": war.id,
        "week_start": war.week_start.isoformat(),
        "week_end": war.week_end.isoformat(),
        "standings": [{
            "rank": idx + 1,
            "club_name": row.club_name,
            "total_points": row.total_points or 0,
            "total_games": row.total_games or 0,
            "member_count": row.member_count or 0
        } for idx, row in enumerate(club_standings)],
        "my_contribution": user_contrib,
        "my_club": current_user.favorite_club
    }

@api_router.post("/club-wars/contribute")
async def contribute_to_club_war(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Start a quick play game that contributes to the club war"""
    if not current_user.favorite_club:
        raise HTTPException(status_code=400, detail="Select a club first to join Club Wars")
    
    # Create a bot game for contribution
    bot = await get_or_create_bot(db)
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
    
    # Create or update contribution
    war = await get_or_create_current_war(db)
    
    result = await db.execute(
        select(ClubWarContribution).where(
            ClubWarContribution.club_war_id == war.id,
            ClubWarContribution.user_id == current_user.user_id
        )
    )
    contrib = result.scalar_one_or_none()
    
    if not contrib:
        contrib = ClubWarContribution(
            id=str(uuid.uuid4()),
            club_war_id=war.id,
            user_id=current_user.user_id,
            club_name=current_user.favorite_club,
            games_played=1
        )
        db.add(contrib)
    else:
        contrib.games_played += 1
    
    await db.commit()
    await db.refresh(game)
    
    return {"game_id": game.id, "war_id": war.id}

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