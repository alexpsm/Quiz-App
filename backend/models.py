from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    username = Column(String(100), unique=True, index=True)
    picture = Column(String(500))
    avatar = Column(String(500))
    skill_rank = Column(Integer, default=1000)
    credits = Column(Integer, default=100)
    password_hash = Column(String(255))
    is_admin = Column(Boolean, default=False)
    favorite_club = Column(String(100), index=True)
    club_knowledge_score = Column(Integer, default=0)
    country = Column(String(100), index=True)
    age = Column(Integer)
    phone_number = Column(String(20))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    sessions = relationship('UserSession', back_populates='user', cascade='all, delete-orphan')
    games_as_player1 = relationship('Game', foreign_keys='Game.player1_id', back_populates='player1')
    games_as_player2 = relationship('Game', foreign_keys='Game.player2_id', back_populates='player2')
    league_memberships = relationship('LeagueMembership', back_populates='user', cascade='all, delete-orphan')

class UserSession(Base):
    __tablename__ = 'user_sessions'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    session_token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    user = relationship('User', back_populates='sessions')

class Question(Base):
    __tablename__ = 'questions'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_text = Column(Text, nullable=False)
    option_a = Column(String(500), nullable=False)
    option_b = Column(String(500), nullable=False)
    option_c = Column(String(500), nullable=False)
    option_d = Column(String(500), nullable=False)
    correct_option = Column(String(1), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    difficulty = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_category_difficulty', 'category', 'difficulty'),
    )

class Game(Base):
    __tablename__ = 'games'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    player1_id = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    player2_id = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    current_round = Column(Integer, default=1)
    status = Column(String(20), default='active', index=True)
    turn_player_id = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'))
    winner_id = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'))
    invite_code = Column(String(20), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    player1 = relationship('User', foreign_keys=[player1_id], back_populates='games_as_player1')
    player2 = relationship('User', foreign_keys=[player2_id], back_populates='games_as_player2')
    rounds = relationship('GameRound', back_populates='game', cascade='all, delete-orphan')

class GameRound(Base):
    __tablename__ = 'game_rounds'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    game_id = Column(String(36), ForeignKey('games.id', ondelete='CASCADE'), nullable=False, index=True)
    round_number = Column(Integer, nullable=False)
    category_selected = Column(String(100))
    player1_answers = Column(JSON, default=list)
    player2_answers = Column(JSON, default=list)
    player1_score = Column(Integer, default=0)
    player2_score = Column(Integer, default=0)
    questions = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    game = relationship('Game', back_populates='rounds')
    
    __table_args__ = (
        Index('idx_game_round', 'game_id', 'round_number'),
    )


class League(Base):
    __tablename__ = 'leagues'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    league_type = Column(String(20), nullable=False, index=True)  # 'public' or 'private'
    invite_code = Column(String(20), unique=True, index=True)
    created_by = Column(String(36), ForeignKey('users.user_id'))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    memberships = relationship('LeagueMembership', back_populates='league', cascade='all, delete-orphan')

class LeagueMembership(Base):
    __tablename__ = 'league_memberships'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    league_id = Column(String(36), ForeignKey('leagues.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    league = relationship('League', back_populates='memberships')
    user = relationship('User', back_populates='league_memberships')
    
    __table_args__ = (
        Index('idx_league_user', 'league_id', 'user_id'),
    )

class PaymentTransaction(Base):
    __tablename__ = 'payment_transactions'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    session_id = Column(String(255), unique=True, index=True)
    package_id = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='usd')
    credits_to_add = Column(Integer, default=0)
    is_premium = Column(Boolean, default=False)
    payment_status = Column(String(50), default='pending')
    status = Column(String(50), default='initiated')
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class ClubWar(Base):
    __tablename__ = 'club_wars'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    week_start = Column(DateTime(timezone=True), nullable=False, index=True)
    week_end = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default='active')  # 'active' or 'completed'
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class ClubWarContribution(Base):
    __tablename__ = 'club_war_contributions'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    club_war_id = Column(String(36), ForeignKey('club_wars.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    club_name = Column(String(100), nullable=False, index=True)
    points = Column(Integer, default=0)
    games_played = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_clubwar_user', 'club_war_id', 'user_id'),
        Index('idx_clubwar_club', 'club_war_id', 'club_name'),
    )
