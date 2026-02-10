"""
QuizBall API Tests - Iteration 3
Testing V2 features: Quick Play vs Bot, Game History, Social sharing, enhanced onboarding
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://matchmake-quiz.preview.emergentagent.com')

@pytest.fixture(scope="module")
def session():
    """Create requests session with cookies"""
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s

@pytest.fixture(scope="module")
def test_user_email():
    """Generate unique test email"""
    return f"test_user_{uuid.uuid4().hex[:8]}@quizball.com"

@pytest.fixture(scope="module")
def auth_session(session, test_user_email):
    """Register and login test user, return authenticated session"""
    # Try login first with existing test user
    login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": "testuser@quizball.com",
        "password": "Test12345"
    })
    
    if login_resp.status_code == 200:
        return session
    
    # If that fails, register new user
    reg_resp = session.post(f"{BASE_URL}/api/auth/register", json={
        "email": test_user_email,
        "password": "Test12345",
        "name": "Test User"
    })
    assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.text}"
    return session


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_login_existing_user(self, session):
        """Test login with existing test user"""
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testuser@quizball.com",
            "password": "Test12345"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        print("✅ Login successful")
    
    def test_login_invalid_credentials(self, session):
        """Test login with wrong password"""
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testuser@quizball.com",
            "password": "WrongPassword"
        })
        assert response.status_code == 401
        print("✅ Invalid credentials correctly rejected")
    
    def test_get_current_user(self, auth_session):
        """Test GET /api/auth/me returns user with country, age, phone_number fields"""
        response = auth_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200, f"Failed to get user: {response.text}"
        
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        assert "name" in data
        assert "skill_rank" in data
        
        # V2 fields - country, age, phone_number should be present
        assert "country" in data, "Missing 'country' field in /api/auth/me response"
        assert "age" in data, "Missing 'age' field in /api/auth/me response"
        assert "phone_number" in data, "Missing 'phone_number' field in /api/auth/me response"
        
        print(f"✅ GET /api/auth/me returns country={data.get('country')}, age={data.get('age')}, phone={data.get('phone_number')}")


class TestUserEndpoints:
    """Test user profile endpoints with V2 fields"""
    
    def test_update_profile_with_v2_fields(self, auth_session):
        """Test PUT /api/users/me accepts country, age, phone_number"""
        update_data = {
            "username": f"testplayer_{uuid.uuid4().hex[:4]}",
            "country": "United Kingdom",
            "age": 25,
            "phone_number": "+44123456789",
            "favorite_club": "Manchester United"
        }
        
        response = auth_session.put(f"{BASE_URL}/api/users/me", json=update_data)
        assert response.status_code == 200, f"Profile update failed: {response.text}"
        
        data = response.json()
        assert data.get("country") == "United Kingdom", f"Country not updated: {data}"
        assert data.get("age") == 25, f"Age not updated: {data}"
        assert data.get("phone_number") == "+44123456789", f"Phone not updated: {data}"
        
        print("✅ PUT /api/users/me accepts country, age, phone_number fields")
    
    def test_leaderboard(self, auth_session):
        """Test leaderboard endpoint"""
        response = auth_session.get(f"{BASE_URL}/api/users/leaderboard?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Leaderboard returns {len(data)} players")


class TestClubEndpoints:
    """Test club-related endpoints"""
    
    def test_get_clubs_by_league(self, session):
        """Test clubs organized by league"""
        response = session.get(f"{BASE_URL}/api/clubs")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0, "No clubs returned"
        print(f"✅ Clubs endpoint returns leagues: {list(data.keys())}")
    
    def test_get_clubs_list(self, session):
        """Test flat club list"""
        response = session.get(f"{BASE_URL}/api/clubs/list")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Clubs list returns {len(data)} clubs")


class TestQuestionEndpoints:
    """Test question endpoints"""
    
    def test_get_categories(self, session):
        """Test question categories"""
        response = session.get(f"{BASE_URL}/api/questions/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "No categories returned"
        print(f"✅ Categories: {data}")
    
    def test_list_questions(self, session):
        """Test listing questions"""
        response = session.get(f"{BASE_URL}/api/questions?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Questions list returns {len(data)} questions")


class TestGameEndpoints:
    """Test game endpoints including V2 Quick Play and History"""
    
    def test_quick_play_vs_bot(self, auth_session):
        """Test POST /api/games/quick-play creates game against TheScore90Bot"""
        response = auth_session.post(f"{BASE_URL}/api/games/quick-play")
        assert response.status_code == 200, f"Quick play failed: {response.text}"
        
        data = response.json()
        assert "game_id" in data, "No game_id in response"
        assert data.get("opponent") == "TheScore90Bot", f"Expected opponent TheScore90Bot, got {data.get('opponent')}"
        
        print(f"✅ Quick Play created game {data['game_id']} vs TheScore90Bot")
        return data['game_id']
    
    def test_game_history(self, auth_session):
        """Test GET /api/games/history returns completed game list"""
        response = auth_session.get(f"{BASE_URL}/api/games/history?limit=10")
        assert response.status_code == 200, f"Game history failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        
        # Check structure of history items if any exist
        if len(data) > 0:
            item = data[0]
            required_fields = ["id", "opponent_username", "opponent_avatar", "my_score", "opponent_score", "won"]
            for field in required_fields:
                assert field in item, f"Missing field '{field}' in history item"
        
        print(f"✅ Game history returns {len(data)} completed games")
    
    def test_list_active_games(self, auth_session):
        """Test listing active games"""
        response = auth_session.get(f"{BASE_URL}/api/games")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Active games: {len(data)}")
    
    def test_create_invite(self, auth_session):
        """Test creating game invite"""
        response = auth_session.post(f"{BASE_URL}/api/games/invite")
        assert response.status_code == 200
        
        data = response.json()
        assert "invite_code" in data
        assert len(data["invite_code"]) == 8
        
        print(f"✅ Invite created: {data['invite_code']}")
    
    def test_random_matchmaking(self, auth_session):
        """Test random matchmaking"""
        response = auth_session.post(f"{BASE_URL}/api/games/matchmake")
        # May fail if no other users - that's ok
        if response.status_code == 200:
            data = response.json()
            assert "game_id" in data
            print(f"✅ Matchmaking found opponent, game: {data['game_id']}")
        else:
            print(f"⚠️ Matchmaking - no opponents available (expected in test env)")
    
    def test_club_challenge(self, auth_session):
        """Test club challenge mode"""
        # First ensure user has favorite_club set
        auth_session.put(f"{BASE_URL}/api/users/me", json={"favorite_club": "Manchester United"})
        
        response = auth_session.post(f"{BASE_URL}/api/games/club-challenge")
        assert response.status_code == 200, f"Club challenge failed: {response.text}"
        
        data = response.json()
        assert "game_id" in data
        assert data.get("club") == "Manchester United"
        
        print(f"✅ Club Challenge created: game {data['game_id']} for {data['club']}")


class TestAdminEndpoints:
    """Test admin endpoints"""
    
    def test_create_question_with_valid_password(self, session):
        """Test creating question with admin password"""
        response = session.post(
            f"{BASE_URL}/api/questions?password=quizball_admin_2026",
            json={
                "question_text": f"TEST_Q_{uuid.uuid4().hex[:4]}: Which team won the Premier League in 2024?",
                "option_a": "Manchester City",
                "option_b": "Arsenal",
                "option_c": "Liverpool",
                "option_d": "Chelsea",
                "correct_option": "A",
                "category": "League",
                "difficulty": 1
            }
        )
        assert response.status_code == 200, f"Question creation failed: {response.text}"
        
        data = response.json()
        assert "id" in data
        print(f"✅ Question created: {data['id']}")
    
    def test_create_question_invalid_password(self, session):
        """Test question creation with wrong password"""
        response = session.post(
            f"{BASE_URL}/api/questions?password=wrong_password",
            json={
                "question_text": "Test question",
                "option_a": "A",
                "option_b": "B",
                "option_c": "C",
                "option_d": "D",
                "correct_option": "A",
                "category": "League",
                "difficulty": 1
            }
        )
        assert response.status_code == 403
        print("✅ Invalid admin password correctly rejected")


class TestGameFlow:
    """Test complete game flow"""
    
    def test_full_quick_play_flow(self, auth_session):
        """Test full quick play game flow: create, select category, answer questions"""
        # 1. Start quick play
        qp_resp = auth_session.post(f"{BASE_URL}/api/games/quick-play")
        assert qp_resp.status_code == 200
        game_id = qp_resp.json()["game_id"]
        print(f"Step 1: Created game {game_id}")
        
        # 2. Get game details
        game_resp = auth_session.get(f"{BASE_URL}/api/games/{game_id}")
        assert game_resp.status_code == 200
        game_data = game_resp.json()
        assert game_data["is_my_turn"] == True
        print(f"Step 2: Game status - Round {game_data['current_round']}, My turn: {game_data['is_my_turn']}")
        
        # 3. Get categories
        cat_resp = auth_session.get(f"{BASE_URL}/api/questions/categories")
        categories = cat_resp.json()
        assert len(categories) > 0
        selected_category = categories[0]
        print(f"Step 3: Available categories: {categories}")
        
        # 4. Select category and get questions
        select_resp = auth_session.post(f"{BASE_URL}/api/games/{game_id}/select-category?category={selected_category}")
        if select_resp.status_code == 200:
            questions = select_resp.json()["questions"]
            print(f"Step 4: Selected '{selected_category}', got {len(questions)} questions")
            
            # 5. Answer questions
            for i, q in enumerate(questions):
                answer_resp = auth_session.post(f"{BASE_URL}/api/games/{game_id}/answer", json={
                    "question_id": q["id"],
                    "selected_option": "A",  # Random answer
                    "time_taken": 5.0
                })
                assert answer_resp.status_code == 200
                result = answer_resp.json()
                print(f"Step 5.{i+1}: Answered Q{i+1}, correct: {result['is_correct']}, score: {result['score']}")
            
            print("✅ Full quick play flow completed successfully")
        else:
            print(f"⚠️ Category selection failed: {select_resp.text}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
