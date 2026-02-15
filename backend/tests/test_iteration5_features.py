"""
Iteration 5 Feature Tests
========================
Tests for 3 new features:
1. Social auth buttons (Facebook, X/Twitter, Apple) - UI placeholders
2. Stripe payment integration for credit packages
3. Weekly Club Wars - club vs club competition

Test user: testuser@quizball.com / Test12345
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture(scope="module")
def authenticated_session():
    """Login and return authenticated session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    # Login
    response = session.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "testuser@quizball.com", "password": "Test12345"}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return session


class TestStripePaymentCheckout:
    """Tests for POST /api/payments/checkout - Stripe checkout session creation"""
    
    def test_checkout_credits_100_returns_url(self, authenticated_session):
        """POST /api/payments/checkout with credits_100 creates checkout URL"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/payments/checkout",
            json={"package_id": "credits_100", "origin_url": "https://football-quizzer-1.preview.emergentagent.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "session_id" in data
        assert "stripe.com" in data["url"]
        assert data["session_id"].startswith("cs_test_")
    
    def test_checkout_credits_500_returns_url(self, authenticated_session):
        """POST /api/payments/checkout with credits_500 creates checkout URL"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/payments/checkout",
            json={"package_id": "credits_500", "origin_url": "https://football-quizzer-1.preview.emergentagent.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "session_id" in data
    
    def test_checkout_credits_1000_returns_url(self, authenticated_session):
        """POST /api/payments/checkout with credits_1000 creates checkout URL"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/payments/checkout",
            json={"package_id": "credits_1000", "origin_url": "https://football-quizzer-1.preview.emergentagent.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "session_id" in data
    
    def test_checkout_premium_returns_url(self, authenticated_session):
        """POST /api/payments/checkout with premium creates checkout URL"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/payments/checkout",
            json={"package_id": "premium", "origin_url": "https://football-quizzer-1.preview.emergentagent.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "session_id" in data
    
    def test_checkout_invalid_package_returns_400(self, authenticated_session):
        """POST /api/payments/checkout with invalid package_id returns 400"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/payments/checkout",
            json={"package_id": "invalid_package", "origin_url": "https://football-quizzer-1.preview.emergentagent.com"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "Invalid package" in data.get("detail", "")
    
    def test_checkout_requires_auth(self):
        """POST /api/payments/checkout returns 401 when not authenticated"""
        response = requests.post(
            f"{BASE_URL}/api/payments/checkout",
            json={"package_id": "credits_100", "origin_url": "https://example.com"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 401


class TestStripePaymentStatus:
    """Tests for GET /api/payments/status/{session_id}"""
    
    def test_payment_status_returns_correct_fields(self, authenticated_session):
        """GET /api/payments/status returns status, payment_status, amount_total, currency"""
        # First create a checkout session
        checkout_response = authenticated_session.post(
            f"{BASE_URL}/api/payments/checkout",
            json={"package_id": "credits_100", "origin_url": "https://football-quizzer-1.preview.emergentagent.com"}
        )
        session_id = checkout_response.json()["session_id"]
        
        # Check status
        response = authenticated_session.get(f"{BASE_URL}/api/payments/status/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "payment_status" in data
        assert "amount_total" in data
        assert "currency" in data
    
    def test_payment_status_shows_unpaid_for_new_session(self, authenticated_session):
        """GET /api/payments/status shows payment_status='unpaid' for new sessions"""
        # Create a checkout session
        checkout_response = authenticated_session.post(
            f"{BASE_URL}/api/payments/checkout",
            json={"package_id": "credits_500", "origin_url": "https://football-quizzer-1.preview.emergentagent.com"}
        )
        session_id = checkout_response.json()["session_id"]
        
        # Check status
        response = authenticated_session.get(f"{BASE_URL}/api/payments/status/{session_id}")
        data = response.json()
        assert data["payment_status"] == "unpaid"
        assert data["status"] == "open"
    
    def test_payment_status_amount_matches_package(self, authenticated_session):
        """GET /api/payments/status returns correct amount for package"""
        # credits_100 is $0.99 = 99 cents
        checkout_response = authenticated_session.post(
            f"{BASE_URL}/api/payments/checkout",
            json={"package_id": "credits_100", "origin_url": "https://football-quizzer-1.preview.emergentagent.com"}
        )
        session_id = checkout_response.json()["session_id"]
        
        response = authenticated_session.get(f"{BASE_URL}/api/payments/status/{session_id}")
        data = response.json()
        assert data["amount_total"] == 99  # 99 cents
        assert data["currency"] == "usd"
    
    def test_payment_status_requires_auth(self):
        """GET /api/payments/status returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/payments/status/cs_test_fake_session")
        assert response.status_code == 401


class TestClubWarsCurrent:
    """Tests for GET /api/club-wars/current"""
    
    def test_current_war_returns_structure(self, authenticated_session):
        """GET /api/club-wars/current returns war with standings"""
        response = authenticated_session.get(f"{BASE_URL}/api/club-wars/current")
        assert response.status_code == 200
        data = response.json()
        assert "war_id" in data
        assert "week_start" in data
        assert "week_end" in data
        assert "standings" in data
        assert "my_club" in data
    
    def test_current_war_week_bounds_correct(self, authenticated_session):
        """GET /api/club-wars/current returns Monday-Sunday week bounds"""
        response = authenticated_session.get(f"{BASE_URL}/api/club-wars/current")
        data = response.json()
        
        from datetime import datetime
        week_start = datetime.fromisoformat(data["week_start"].replace('Z', '+00:00'))
        week_end = datetime.fromisoformat(data["week_end"].replace('Z', '+00:00'))
        
        # Week start should be Monday (weekday 0)
        assert week_start.weekday() == 0
        # Week end should be 7 days after start
        assert (week_end - week_start).days == 7
    
    def test_current_war_standings_structure(self, authenticated_session):
        """GET /api/club-wars/current standings have rank, club_name, points, games, members"""
        response = authenticated_session.get(f"{BASE_URL}/api/club-wars/current")
        data = response.json()
        
        if data["standings"]:
            standing = data["standings"][0]
            assert "rank" in standing
            assert "club_name" in standing
            assert "total_points" in standing
            assert "total_games" in standing
            assert "member_count" in standing
    
    def test_current_war_shows_my_contribution(self, authenticated_session):
        """GET /api/club-wars/current shows my_contribution if user has contributed"""
        response = authenticated_session.get(f"{BASE_URL}/api/club-wars/current")
        data = response.json()
        
        # User should have my_club set
        assert data.get("my_club") is not None
        
        # my_contribution may or may not be set depending on games played
        if data.get("my_contribution"):
            assert "points" in data["my_contribution"]
            assert "games_played" in data["my_contribution"]
    
    def test_current_war_requires_auth(self):
        """GET /api/club-wars/current returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/club-wars/current")
        assert response.status_code == 401


class TestClubWarsContribute:
    """Tests for POST /api/club-wars/contribute"""
    
    def test_contribute_creates_game(self, authenticated_session):
        """POST /api/club-wars/contribute creates a game and returns game_id"""
        response = authenticated_session.post(f"{BASE_URL}/api/club-wars/contribute")
        assert response.status_code == 200
        data = response.json()
        assert "game_id" in data
        assert "war_id" in data
    
    def test_contribute_increments_games_played(self, authenticated_session):
        """POST /api/club-wars/contribute increments games_played count"""
        # Get initial count
        initial_response = authenticated_session.get(f"{BASE_URL}/api/club-wars/current")
        initial_games = 0
        if initial_response.json().get("my_contribution"):
            initial_games = initial_response.json()["my_contribution"]["games_played"]
        
        # Contribute
        authenticated_session.post(f"{BASE_URL}/api/club-wars/contribute")
        
        # Check count increased
        final_response = authenticated_session.get(f"{BASE_URL}/api/club-wars/current")
        final_games = final_response.json()["my_contribution"]["games_played"]
        assert final_games > initial_games
    
    def test_contribute_returns_game_that_exists(self, authenticated_session):
        """POST /api/club-wars/contribute game_id is valid and can be fetched"""
        response = authenticated_session.post(f"{BASE_URL}/api/club-wars/contribute")
        game_id = response.json()["game_id"]
        
        # Verify game exists
        game_response = authenticated_session.get(f"{BASE_URL}/api/games/{game_id}")
        assert game_response.status_code == 200
        game_data = game_response.json()
        assert game_data["status"] == "active"
    
    def test_contribute_requires_auth(self):
        """POST /api/club-wars/contribute returns 401 without auth"""
        response = requests.post(f"{BASE_URL}/api/club-wars/contribute")
        assert response.status_code == 401


class TestExistingFeatures:
    """Verify existing features still work (Quick Play, Club Challenge, Profile, etc.)"""
    
    def test_quick_play_still_works(self, authenticated_session):
        """POST /api/games/quick-play still creates a game"""
        response = authenticated_session.post(f"{BASE_URL}/api/games/quick-play")
        assert response.status_code == 200
        data = response.json()
        assert "game_id" in data
        assert "opponent" in data
    
    def test_game_invite_still_works(self, authenticated_session):
        """POST /api/games/invite still creates invite code"""
        response = authenticated_session.post(f"{BASE_URL}/api/games/invite")
        assert response.status_code == 200
        data = response.json()
        assert "invite_code" in data
        assert "game_id" in data
    
    def test_my_rank_still_works(self, authenticated_session):
        """GET /api/users/my-rank still returns ranks"""
        response = authenticated_session.get(f"{BASE_URL}/api/users/my-rank")
        assert response.status_code == 200
        data = response.json()
        assert "global" in data
    
    def test_auth_me_still_works(self, authenticated_session):
        """GET /api/auth/me still returns user profile"""
        response = authenticated_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        assert "credits" in data
    
    def test_leagues_still_work(self, authenticated_session):
        """GET /api/leagues still returns leagues"""
        response = authenticated_session.get(f"{BASE_URL}/api/leagues")
        assert response.status_code == 200
        # Returns a list
        assert isinstance(response.json(), list)
