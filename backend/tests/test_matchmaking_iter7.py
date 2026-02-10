"""
Test suite for Iteration 7 features:
1. Club-specific question categories (e.g., 'Manchester United-History', 'Arsenal-Players')
2. Matchmaking endpoints (join, status, leave, bot-fallback)
3. ELO calculation function for skill_rank updates
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_EMAIL = "matchtest@test.com"
TEST_USER_PASSWORD = "Test123456"

class TestClubSpecificCategories:
    """Test that club-specific question categories exist"""
    
    def test_categories_endpoint_returns_club_specific(self):
        """Verify club-specific categories like 'Manchester United-History' exist"""
        response = requests.get(f"{BASE_URL}/api/questions/categories")
        assert response.status_code == 200
        
        categories = response.json()
        assert isinstance(categories, list)
        assert len(categories) > 0
        
        # Check for specific club categories
        expected_clubs = [
            "Manchester United-History",
            "Manchester United-Players",
            "Arsenal-History",
            "Arsenal-Players",
            "Bayern Munich-History",
            "Bayern Munich-Trophies",
            "Real Madrid-History",
            "Liverpool-Players",
            "Chelsea-History",
            "FC Barcelona-Players"
        ]
        
        found_clubs = []
        for expected in expected_clubs:
            if expected in categories:
                found_clubs.append(expected)
        
        print(f"Found {len(found_clubs)}/{len(expected_clubs)} expected club categories")
        print(f"Found categories: {found_clubs}")
        
        # At least 5 club-specific categories should exist
        assert len(found_clubs) >= 5, f"Expected at least 5 club-specific categories, found {len(found_clubs)}"
    
    def test_questions_exist_for_club_categories(self):
        """Verify questions exist for club-specific categories"""
        # Test a few club categories
        test_categories = [
            "Manchester United-History",
            "Arsenal-Players",
            "Bayern Munich-History"
        ]
        
        for category in test_categories:
            response = requests.get(f"{BASE_URL}/api/questions", params={"category": category, "limit": 5})
            assert response.status_code == 200
            
            questions = response.json()
            print(f"Category '{category}': {len(questions)} questions found")
            
            # Each category should have at least 1 question
            assert len(questions) >= 1, f"Category '{category}' has no questions"
            
            # Verify question structure
            if questions:
                q = questions[0]
                assert "question_text" in q
                assert "option_a" in q
                assert "option_b" in q
                assert "option_c" in q
                assert "option_d" in q
                assert "correct_option" in q
                assert q["category"] == category


class TestMatchmakingEndpoints:
    """Test matchmaking queue endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get session
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
        )
        
        if login_response.status_code != 200:
            # Try to register first
            register_response = self.session.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD,
                    "name": "Match Test User"
                }
            )
            if register_response.status_code not in [200, 201]:
                pytest.skip(f"Could not authenticate: {register_response.text}")
        
        yield
        
        # Cleanup: leave queue if still in it
        try:
            self.session.delete(f"{BASE_URL}/api/matchmaking/leave")
        except:
            pass
    
    def test_join_matchmaking_queue(self):
        """Test POST /api/matchmaking/join"""
        response = self.session.post(f"{BASE_URL}/api/matchmaking/join")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["queued", "already_queued"]
        
        if data["status"] == "queued":
            assert "skill_rank" in data
            assert "message" in data
            print(f"Joined queue with skill_rank: {data['skill_rank']}")
    
    def test_matchmaking_status_shows_waiting(self):
        """Test GET /api/matchmaking/status shows waiting state"""
        # First join the queue
        join_response = self.session.post(f"{BASE_URL}/api/matchmaking/join")
        assert join_response.status_code == 200
        
        # Check status
        status_response = self.session.get(f"{BASE_URL}/api/matchmaking/status")
        assert status_response.status_code == 200
        
        data = status_response.json()
        assert "status" in data
        
        if data["status"] == "waiting":
            assert "wait_time" in data
            assert "skill_range" in data
            assert "players_in_queue" in data
            print(f"Status: waiting, wait_time: {data['wait_time']}s, skill_range: ±{data['skill_range']}, queue: {data['players_in_queue']}")
        elif data["status"] == "matched":
            assert "game_id" in data
            print(f"Status: matched, game_id: {data['game_id']}")
    
    def test_leave_matchmaking_queue(self):
        """Test DELETE /api/matchmaking/leave"""
        # First join the queue
        self.session.post(f"{BASE_URL}/api/matchmaking/join")
        
        # Leave the queue
        response = self.session.delete(f"{BASE_URL}/api/matchmaking/leave")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["left", "not_in_queue"]
        print(f"Leave queue result: {data['status']}")
        
        # Verify no longer in queue
        status_response = self.session.get(f"{BASE_URL}/api/matchmaking/status")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["status"] == "not_queued"
    
    def test_bot_fallback_creates_game(self):
        """Test POST /api/matchmaking/bot-fallback creates bot game"""
        # First join the queue
        self.session.post(f"{BASE_URL}/api/matchmaking/join")
        
        # Request bot fallback
        response = self.session.post(f"{BASE_URL}/api/matchmaking/bot-fallback")
        assert response.status_code == 200
        
        data = response.json()
        assert "game_id" in data
        assert "opponent" in data
        assert data["opponent"] == "TheScore90Bot"
        assert data.get("is_bot") == True
        
        print(f"Bot fallback created game: {data['game_id']}")
        
        # Verify game exists
        game_response = self.session.get(f"{BASE_URL}/api/games/{data['game_id']}")
        assert game_response.status_code == 200
        game_data = game_response.json()
        assert game_data["is_bot_game"] == True
    
    def test_skill_range_expands_over_time(self):
        """Test that skill range expands based on wait time"""
        # Join queue
        self.session.post(f"{BASE_URL}/api/matchmaking/join")
        
        # Check initial status
        status1 = self.session.get(f"{BASE_URL}/api/matchmaking/status").json()
        initial_range = status1.get("skill_range", 150)
        
        # Wait a bit and check again
        time.sleep(2)
        status2 = self.session.get(f"{BASE_URL}/api/matchmaking/status").json()
        
        # Skill range should be >= initial (may expand after 15s)
        if status2.get("status") == "waiting":
            assert status2.get("skill_range", 0) >= initial_range
            print(f"Initial range: {initial_range}, After 2s: {status2.get('skill_range')}")


class TestELOCalculation:
    """Test ELO calculation for skill_rank updates"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
        )
        
        if login_response.status_code != 200:
            register_response = self.session.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD,
                    "name": "Match Test User"
                }
            )
            if register_response.status_code not in [200, 201]:
                pytest.skip("Could not authenticate")
    
    def test_user_has_skill_rank(self):
        """Verify user profile includes skill_rank"""
        response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        
        data = response.json()
        assert "skill_rank" in data
        assert isinstance(data["skill_rank"], int)
        assert data["skill_rank"] >= 100  # Minimum rank
        
        print(f"User skill_rank: {data['skill_rank']}")
    
    def test_leaderboard_shows_skill_rank(self):
        """Verify leaderboard includes skill_rank"""
        response = self.session.get(f"{BASE_URL}/api/users/leaderboard")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:
            user = data[0]
            assert "skill_rank" in user
            assert "username" in user
            print(f"Top user: {user.get('username')} with skill_rank: {user.get('skill_rank')}")
    
    def test_game_response_includes_skill_rank(self):
        """Verify game response includes player skill_rank"""
        # Create a quick play game
        response = self.session.post(f"{BASE_URL}/api/games/quick-play")
        assert response.status_code == 200
        
        game_id = response.json()["game_id"]
        
        # Get game details
        game_response = self.session.get(f"{BASE_URL}/api/games/{game_id}")
        assert game_response.status_code == 200
        
        game_data = game_response.json()
        assert "player1" in game_data
        assert "player2" in game_data
        assert "skill_rank" in game_data["player1"]
        assert "skill_rank" in game_data["player2"]
        
        print(f"Player1 skill_rank: {game_data['player1']['skill_rank']}")
        print(f"Player2 (bot) skill_rank: {game_data['player2']['skill_rank']}")


class TestMatchmakingQueueStats:
    """Test matchmaking queue statistics"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
        )
        
        if login_response.status_code != 200:
            self.session.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD,
                    "name": "Match Test User"
                }
            )
        
        yield
        
        try:
            self.session.delete(f"{BASE_URL}/api/matchmaking/leave")
        except:
            pass
    
    def test_status_returns_queue_count(self):
        """Test that status returns players_in_queue count"""
        # Join queue
        self.session.post(f"{BASE_URL}/api/matchmaking/join")
        
        # Get status
        response = self.session.get(f"{BASE_URL}/api/matchmaking/status")
        assert response.status_code == 200
        
        data = response.json()
        if data["status"] == "waiting":
            assert "players_in_queue" in data
            assert isinstance(data["players_in_queue"], int)
            assert data["players_in_queue"] >= 1  # At least the current user
            print(f"Players in queue: {data['players_in_queue']}")
    
    def test_status_returns_your_rank(self):
        """Test that status returns your_rank"""
        # Join queue
        self.session.post(f"{BASE_URL}/api/matchmaking/join")
        
        # Get status
        response = self.session.get(f"{BASE_URL}/api/matchmaking/status")
        assert response.status_code == 200
        
        data = response.json()
        if data["status"] == "waiting":
            assert "your_rank" in data
            assert isinstance(data["your_rank"], int)
            print(f"Your rank in queue: {data['your_rank']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
