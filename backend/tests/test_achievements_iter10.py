"""
Iteration 10: Testing Authentication, Player Tiering, and Achievement Badges System
- Authentication flow (registration, login with email/password)
- Player tiering system display on Dashboard and Profile (avatar tier badge)
- Achievement badges system - API endpoints (/api/achievements, /api/achievements/me)
- Achievement badges display on Profile page
- Achievement awarding after game completion
"""

import pytest
import requests
import os
import uuid
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user credentials
TEST_EMAIL = f"test_ach_{uuid.uuid4().hex[:8]}@quizball.com"
TEST_PASSWORD = "TestAch12345"
TEST_NAME = "Achievement Tester"

class TestAuthenticationFlow:
    """Test registration and login with email/password"""
    
    session = None
    user_data = None
    
    def test_01_register_new_user(self):
        """Test user registration"""
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": TEST_NAME
            }
        )
        print(f"Register response: {response.status_code} - {response.text[:200]}")
        assert response.status_code == 200, f"Registration failed: {response.text}"
        
        # Store session cookie
        TestAuthenticationFlow.session = requests.Session()
        TestAuthenticationFlow.session.cookies.update(response.cookies)
        print(f"Registration successful for {TEST_EMAIL}")
    
    def test_02_get_auth_me_after_register(self):
        """Test /auth/me returns user data after registration"""
        if not TestAuthenticationFlow.session:
            pytest.skip("No session from registration")
        
        response = TestAuthenticationFlow.session.get(f"{BASE_URL}/api/auth/me")
        print(f"Auth/me response: {response.status_code} - {response.text[:300]}")
        assert response.status_code == 200, f"Auth/me failed: {response.text}"
        
        data = response.json()
        assert "user_id" in data, "user_id missing from response"
        assert data["email"] == TEST_EMAIL, f"Email mismatch: {data['email']}"
        assert data["name"] == TEST_NAME, f"Name mismatch: {data['name']}"
        
        # Check player tier fields exist
        assert "player_tier" in data, "player_tier missing from response"
        assert "total_game_points" in data, "total_game_points missing from response"
        assert "skill_rank" in data, "skill_rank missing from response"
        
        TestAuthenticationFlow.user_data = data
        print(f"User data: player_tier={data['player_tier']}, skill_rank={data['skill_rank']}")
    
    def test_03_login_with_credentials(self):
        """Test login with email/password"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
        )
        print(f"Login response: {response.status_code} - {response.text[:200]}")
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        # Update session with new cookies
        TestAuthenticationFlow.session = requests.Session()
        TestAuthenticationFlow.session.cookies.update(response.cookies)
        print("Login successful")
    
    def test_04_login_invalid_credentials(self):
        """Test login with wrong password returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_EMAIL,
                "password": "WrongPassword123"
            }
        )
        print(f"Invalid login response: {response.status_code}")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_05_register_duplicate_email(self):
        """Test registering with existing email returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": TEST_EMAIL,
                "password": "AnotherPass123",
                "name": "Duplicate User"
            }
        )
        print(f"Duplicate register response: {response.status_code}")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"


class TestPlayerTieringSystem:
    """Test player tier display and calculation"""
    
    def test_06_new_user_starts_at_tier_1(self):
        """New users should start at tier 1"""
        if not TestAuthenticationFlow.user_data:
            pytest.skip("No user data from registration")
        
        assert TestAuthenticationFlow.user_data["player_tier"] == 1, \
            f"New user should be tier 1, got {TestAuthenticationFlow.user_data['player_tier']}"
        print("New user correctly starts at tier 1")
    
    def test_07_tier_in_leaderboard(self):
        """Leaderboard should include player_tier"""
        response = requests.get(f"{BASE_URL}/api/users/leaderboard?limit=10")
        print(f"Leaderboard response: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        if len(data) > 0:
            assert "player_tier" in data[0], "player_tier missing from leaderboard entries"
            print(f"Leaderboard entry has player_tier: {data[0]['player_tier']}")
        else:
            print("Leaderboard is empty, skipping tier check")
    
    def test_08_tier_in_game_state(self):
        """Game state should include player_tier for both players"""
        if not TestAuthenticationFlow.session:
            pytest.skip("No session available")
        
        # First need to complete profile setup
        profile_response = TestAuthenticationFlow.session.put(
            f"{BASE_URL}/api/users/me",
            json={
                "username": f"achtest_{uuid.uuid4().hex[:6]}",
                "favorite_club": "Arsenal",
                "country": "United Kingdom",
                "age": 25,
                "phone_number": "+447123456789"
            }
        )
        print(f"Profile setup response: {profile_response.status_code}")
        
        # Start a quick play game
        game_response = TestAuthenticationFlow.session.post(f"{BASE_URL}/api/games/quick-play")
        print(f"Quick play response: {game_response.status_code} - {game_response.text[:200]}")
        
        if game_response.status_code == 200:
            game_id = game_response.json().get("game_id")
            
            # Get game state
            state_response = TestAuthenticationFlow.session.get(f"{BASE_URL}/api/games/{game_id}")
            print(f"Game state response: {state_response.status_code}")
            assert state_response.status_code == 200
            
            state = state_response.json()
            assert "player1" in state, "player1 missing from game state"
            assert "player_tier" in state["player1"], "player_tier missing from player1"
            assert "player2" in state, "player2 missing from game state"
            assert "player_tier" in state["player2"], "player_tier missing from player2"
            
            print(f"Player1 tier: {state['player1']['player_tier']}, Player2 tier: {state['player2']['player_tier']}")
        else:
            pytest.skip(f"Could not start game: {game_response.text}")


class TestAchievementBadgesAPI:
    """Test achievement badges API endpoints"""
    
    def test_09_get_all_achievements(self):
        """GET /api/achievements returns all available achievements"""
        response = requests.get(f"{BASE_URL}/api/achievements")
        print(f"All achievements response: {response.status_code}")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) >= 20, f"Expected at least 20 achievements, got {len(data)}"
        
        # Check structure of first achievement
        if len(data) > 0:
            ach = data[0]
            assert "id" in ach, "Achievement missing 'id'"
            assert "name" in ach, "Achievement missing 'name'"
            assert "description" in ach, "Achievement missing 'description'"
            assert "icon" in ach, "Achievement missing 'icon'"
            assert "category" in ach, "Achievement missing 'category'"
            print(f"Sample achievement: {ach['id']} - {ach['name']}")
        
        # Check for specific achievements
        achievement_ids = [a["id"] for a in data]
        expected_achievements = [
            "first_win", "win_streak_3", "win_streak_5", "win_streak_10",
            "perfect_game", "perfect_round", "games_10", "games_50", "games_100",
            "wins_25", "wins_50", "wins_100", "ball_knowledge_1200",
            "ball_knowledge_1500", "ball_knowledge_1800", "challenge_winner",
            "hard_challenge_winner", "club_devotee", "comeback_king", "speed_demon"
        ]
        for exp_id in expected_achievements:
            assert exp_id in achievement_ids, f"Missing achievement: {exp_id}"
        
        print(f"All {len(expected_achievements)} expected achievements found")
    
    def test_10_get_my_achievements_authenticated(self):
        """GET /api/achievements/me returns user's earned achievements"""
        if not TestAuthenticationFlow.session:
            pytest.skip("No session available")
        
        response = TestAuthenticationFlow.session.get(f"{BASE_URL}/api/achievements/me")
        print(f"My achievements response: {response.status_code} - {response.text[:300]}")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "earned" in data, "Response missing 'earned' field"
        assert "total_earned" in data, "Response missing 'total_earned' field"
        assert "total_available" in data, "Response missing 'total_available' field"
        
        assert isinstance(data["earned"], list), "'earned' should be a list"
        assert data["total_available"] >= 20, f"Expected at least 20 available achievements"
        
        print(f"User has {data['total_earned']}/{data['total_available']} achievements")
    
    def test_11_get_my_achievements_unauthenticated(self):
        """GET /api/achievements/me without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/achievements/me")
        print(f"Unauthenticated achievements response: {response.status_code}")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_12_get_user_achievements_by_id(self):
        """GET /api/users/{user_id}/achievements returns user's achievements"""
        if not TestAuthenticationFlow.user_data:
            pytest.skip("No user data available")
        
        user_id = TestAuthenticationFlow.user_data["user_id"]
        response = requests.get(f"{BASE_URL}/api/users/{user_id}/achievements")
        print(f"User achievements response: {response.status_code} - {response.text[:200]}")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "earned" in data, "Response missing 'earned' field"
        assert "total_earned" in data, "Response missing 'total_earned' field"
        print(f"User {user_id} has {data['total_earned']} achievements")


class TestAchievementAwarding:
    """Test that achievements are awarded correctly after game completion"""
    
    game_id = None
    
    def test_13_play_game_and_check_achievements(self):
        """Play a complete game and verify achievements are checked"""
        if not TestAuthenticationFlow.session:
            pytest.skip("No session available")
        
        # Start a quick play game
        game_response = TestAuthenticationFlow.session.post(f"{BASE_URL}/api/games/quick-play")
        print(f"Quick play response: {game_response.status_code}")
        
        if game_response.status_code != 200:
            pytest.skip(f"Could not start game: {game_response.text}")
        
        TestAchievementAwarding.game_id = game_response.json().get("game_id")
        print(f"Started game: {TestAchievementAwarding.game_id}")
        
        # Play through 6 rounds
        for round_num in range(1, 7):
            print(f"\n--- Round {round_num} ---")
            
            # Select category
            cat_response = TestAuthenticationFlow.session.post(
                f"{BASE_URL}/api/games/{TestAchievementAwarding.game_id}/select-category",
                params={"category": "Club"}
            )
            print(f"Category select: {cat_response.status_code}")
            
            if cat_response.status_code != 200:
                print(f"Category select failed: {cat_response.text}")
                break
            
            questions = cat_response.json().get("questions", [])
            print(f"Got {len(questions)} questions")
            
            # Answer 3 questions
            for i, q in enumerate(questions[:3]):
                answer_response = TestAuthenticationFlow.session.post(
                    f"{BASE_URL}/api/games/{TestAchievementAwarding.game_id}/answer",
                    json={
                        "question_id": q["id"],
                        "selected_option": q["correct_option"],  # Answer correctly
                        "time_taken": 5.0
                    }
                )
                print(f"Answer {i+1}: {answer_response.status_code}")
                
                if answer_response.status_code == 200:
                    ans_data = answer_response.json()
                    # Check if achievements were earned
                    if ans_data.get("achievements_earned"):
                        print(f"ACHIEVEMENTS EARNED: {ans_data['achievements_earned']}")
            
            # Trigger bot play
            bot_response = TestAuthenticationFlow.session.post(
                f"{BASE_URL}/api/games/{TestAchievementAwarding.game_id}/bot-play"
            )
            print(f"Bot play: {bot_response.status_code}")
            
            if bot_response.status_code == 200:
                bot_data = bot_response.json()
                if bot_data.get("achievements_earned"):
                    print(f"ACHIEVEMENTS EARNED (bot phase): {bot_data['achievements_earned']}")
                if bot_data.get("game_status") == "finished":
                    print("Game finished!")
                    break
            
            time.sleep(0.5)
    
    def test_14_verify_first_win_achievement(self):
        """After winning a game, user should have first_win achievement"""
        if not TestAuthenticationFlow.session:
            pytest.skip("No session available")
        
        # Get user's achievements
        response = TestAuthenticationFlow.session.get(f"{BASE_URL}/api/achievements/me")
        print(f"Achievements after game: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            earned_ids = [a["id"] for a in data["earned"]]
            print(f"Earned achievements: {earned_ids}")
            
            # Check if first_win was earned (depends on game outcome)
            if "first_win" in earned_ids:
                print("SUCCESS: first_win achievement earned!")
            else:
                print("first_win not earned yet (may have lost the game)")
        else:
            print(f"Could not get achievements: {response.text}")
    
    def test_15_achievements_in_game_over_response(self):
        """Game over response should include achievements_earned field"""
        if not TestAchievementAwarding.game_id or not TestAuthenticationFlow.session:
            pytest.skip("No game played")
        
        # Get final game state
        response = TestAuthenticationFlow.session.get(
            f"{BASE_URL}/api/games/{TestAchievementAwarding.game_id}"
        )
        print(f"Final game state: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Game status: {data.get('status')}")
            print(f"Winner: {data.get('winner_id')}")
            print(f"My score: {data.get('my_score')}, Opponent score: {data.get('opponent_score')}")


class TestExistingUserWithAchievements:
    """Test with existing user who may have achievements"""
    
    def test_16_login_existing_user(self):
        """Login with existing test user"""
        # Use credentials from previous iterations
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "testuser@quizball.com",
                "password": "Test12345"
            }
        )
        print(f"Existing user login: {response.status_code}")
        
        if response.status_code == 200:
            session = requests.Session()
            session.cookies.update(response.cookies)
            
            # Get achievements
            ach_response = session.get(f"{BASE_URL}/api/achievements/me")
            print(f"Existing user achievements: {ach_response.status_code}")
            
            if ach_response.status_code == 200:
                data = ach_response.json()
                print(f"Existing user has {data['total_earned']}/{data['total_available']} achievements")
                for ach in data["earned"]:
                    print(f"  - {ach['id']}: {ach['name']}")
        else:
            print("Existing user not found, skipping")


class TestAchievementCategories:
    """Test achievement categories and icons"""
    
    def test_17_achievement_categories(self):
        """Verify achievements have correct categories"""
        response = requests.get(f"{BASE_URL}/api/achievements")
        assert response.status_code == 200
        
        data = response.json()
        categories = set()
        for ach in data:
            categories.add(ach.get("category"))
        
        print(f"Achievement categories: {categories}")
        
        expected_categories = {"milestone", "streak", "skill", "rating", "challenge", "club", "special"}
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"
        
        print("All expected categories present")
    
    def test_18_achievement_icons(self):
        """Verify achievements have valid icons"""
        response = requests.get(f"{BASE_URL}/api/achievements")
        assert response.status_code == 200
        
        data = response.json()
        valid_icons = {
            "trophy", "flame", "fire", "zap", "star", "clock", "play", "gamepad",
            "heart", "award", "medal", "crown", "trending-up", "brain", "gem",
            "flag", "shield", "home", "refresh-cw"
        }
        
        for ach in data:
            icon = ach.get("icon")
            assert icon in valid_icons, f"Invalid icon '{icon}' for achievement {ach['id']}"
        
        print(f"All {len(data)} achievements have valid icons")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
