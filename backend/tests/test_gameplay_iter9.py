"""
Iteration 9: Full Gameplay Mechanics Testing
Tests:
1. Full Quick Play game flow (6 rounds, bot game)
2. Full Club Challenge game flow (6 rounds, solo mode)
3. correct_option always returned in answer response
4. Round number increments correctly
5. Bot play endpoint works after player answers
6. Game over shows correct scores and winner
7. Category selection page functionality
8. Answer feedback shows correct answer when wrong
9. Game history endpoint
10. No duplicate GameRound entries
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_EMAIL = "testuser@quizball.com"
TEST_USER_PASSWORD = "Test12345"

class TestGameplayMechanics:
    """Full gameplay mechanics testing for iteration 9"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        # Login
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        
    def test_01_login_and_auth(self):
        """Test login works and /auth/me returns user data"""
        me_resp = self.session.get(f"{BASE_URL}/api/auth/me")
        assert me_resp.status_code == 200, f"Auth/me failed: {me_resp.text}"
        user = me_resp.json()
        assert "user_id" in user
        assert "skill_rank" in user
        assert "favorite_club" in user
        print(f"✓ User logged in: {user.get('username')} (rank: {user.get('skill_rank')})")
        
    def test_02_categories_available(self):
        """Test categories endpoint returns categories"""
        resp = self.session.get(f"{BASE_URL}/api/questions/categories")
        assert resp.status_code == 200
        categories = resp.json()
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "Club" in categories, "Club category should exist"
        print(f"✓ Categories available: {len(categories)} categories")
        
    def test_03_quick_play_start(self):
        """Test starting a Quick Play game"""
        resp = self.session.post(f"{BASE_URL}/api/games/quick-play")
        assert resp.status_code == 200, f"Quick play failed: {resp.text}"
        data = resp.json()
        assert "game_id" in data
        assert "opponent" in data
        assert data["opponent"] == "TheScore90Bot"
        print(f"✓ Quick Play started: {data['game_id']}")
        return data["game_id"]
        
    def test_04_club_challenge_start(self):
        """Test starting a Club Challenge game"""
        resp = self.session.post(f"{BASE_URL}/api/games/club-challenge")
        assert resp.status_code == 200, f"Club challenge failed: {resp.text}"
        data = resp.json()
        assert "game_id" in data
        assert "club" in data  # Should return user's favorite club
        print(f"✓ Club Challenge started: {data['game_id']} for club: {data['club']}")
        return data["game_id"]
        
    def test_05_get_game_state(self):
        """Test getting game state returns correct fields"""
        # Create a new game
        resp = self.session.post(f"{BASE_URL}/api/games/quick-play")
        assert resp.status_code == 200
        game_id = resp.json()["game_id"]
        
        # Get game state
        game_resp = self.session.get(f"{BASE_URL}/api/games/{game_id}")
        assert game_resp.status_code == 200
        game = game_resp.json()
        
        assert game["id"] == game_id
        assert game["current_round"] == 1
        assert game["status"] == "active"
        assert game["is_my_turn"] == True
        assert game["is_bot_game"] == True
        assert "player1" in game
        assert "player2" in game
        assert "my_score" in game
        assert "opponent_score" in game
        assert "rounds" in game
        print(f"✓ Game state retrieved: round {game['current_round']}, status: {game['status']}")
        
    def test_06_select_category(self):
        """Test selecting a category creates a round with questions"""
        # Create game
        resp = self.session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = resp.json()["game_id"]
        
        # Select category
        cat_resp = self.session.post(f"{BASE_URL}/api/games/{game_id}/select-category", params={"category": "Club"})
        assert cat_resp.status_code == 200, f"Category select failed: {cat_resp.text}"
        data = cat_resp.json()
        
        assert "questions" in data
        assert len(data["questions"]) == 3, "Should receive 3 questions"
        
        # Verify question structure
        for q in data["questions"]:
            assert "id" in q
            assert "question_text" in q
            assert "option_a" in q
            assert "option_b" in q
            assert "option_c" in q
            assert "option_d" in q
            # correct_option should NOT be in questions (only in answer response)
            
        print(f"✓ Category selected, received {len(data['questions'])} questions")
        return game_id, data["questions"]
        
    def test_07_answer_submission_correct_option_returned(self):
        """Test that correct_option is ALWAYS returned in answer response (critical bug fix test)"""
        # Create game and get questions
        resp = self.session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = resp.json()["game_id"]
        
        cat_resp = self.session.post(f"{BASE_URL}/api/games/{game_id}/select-category", params={"category": "Club"})
        questions = cat_resp.json()["questions"]
        
        # Submit a WRONG answer to verify correct_option is returned
        ans_resp = self.session.post(f"{BASE_URL}/api/games/{game_id}/answer", json={
            "question_id": questions[0]["id"],
            "selected_option": "X",  # Intentionally wrong
            "time_taken": 5.0
        })
        assert ans_resp.status_code == 200, f"Answer submit failed: {ans_resp.text}"
        data = ans_resp.json()
        
        assert "is_correct" in data
        assert "score" in data
        assert "correct_option" in data, "correct_option MUST be returned (bug fix verification)"
        assert data["correct_option"] in ["A", "B", "C", "D"], f"correct_option should be A/B/C/D, got: {data['correct_option']}"
        
        print(f"✓ Answer response includes correct_option: {data['correct_option']} (is_correct: {data['is_correct']}, score: {data['score']})")
        
    def test_08_full_quick_play_round(self):
        """Test completing all 3 questions in a round for Quick Play"""
        # Create game
        resp = self.session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = resp.json()["game_id"]
        
        # Select category
        cat_resp = self.session.post(f"{BASE_URL}/api/games/{game_id}/select-category", params={"category": "Club"})
        questions = cat_resp.json()["questions"]
        
        # Answer all 3 questions
        for i, q in enumerate(questions):
            ans_resp = self.session.post(f"{BASE_URL}/api/games/{game_id}/answer", json={
                "question_id": q["id"],
                "selected_option": "A",  # Just pick A for each
                "time_taken": 3.0
            })
            assert ans_resp.status_code == 200, f"Answer {i+1} failed: {ans_resp.text}"
            data = ans_resp.json()
            assert "correct_option" in data
            print(f"  - Q{i+1}: selected=A, correct={data['correct_option']}, score={data['score']}")
            
        # After 3 answers, turn should switch to bot (player2)
        game_resp = self.session.get(f"{BASE_URL}/api/games/{game_id}")
        game = game_resp.json()
        
        # In a bot game after player answers, it's bot's turn
        # But we need to trigger bot-play
        assert game["is_bot_game"] == True
        print(f"✓ Round 1 completed, turn_player: {game['turn_player_id']}")
        
        return game_id
        
    def test_09_bot_play_endpoint(self):
        """Test bot play endpoint works correctly"""
        # Create game and complete player's turn
        resp = self.session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = resp.json()["game_id"]
        
        # Select category and answer all questions
        cat_resp = self.session.post(f"{BASE_URL}/api/games/{game_id}/select-category", params={"category": "Club"})
        questions = cat_resp.json()["questions"]
        
        for q in questions:
            self.session.post(f"{BASE_URL}/api/games/{game_id}/answer", json={
                "question_id": q["id"],
                "selected_option": "B",
                "time_taken": 4.0
            })
        
        # Now trigger bot play
        bot_resp = self.session.post(f"{BASE_URL}/api/games/{game_id}/bot-play")
        assert bot_resp.status_code == 200, f"Bot play failed: {bot_resp.text}"
        data = bot_resp.json()
        
        assert "bot_answers" in data
        assert "bot_score" in data
        assert "round_complete" in data
        assert "game_status" in data
        assert len(data["bot_answers"]) == 3, "Bot should answer 3 questions"
        
        # Verify bot answer structure
        for ba in data["bot_answers"]:
            assert "question_id" in ba
            assert "selected_option" in ba
            assert "correct_option" in ba
            assert "is_correct" in ba
            assert "time_taken" in ba
            assert "score" in ba
            
        print(f"✓ Bot play completed: bot_score={data['bot_score']}, status={data['game_status']}")
        return game_id
        
    def test_10_round_advancement(self):
        """Test that rounds advance correctly after both players answer"""
        resp = self.session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = resp.json()["game_id"]
        
        # Complete round 1
        cat_resp = self.session.post(f"{BASE_URL}/api/games/{game_id}/select-category", params={"category": "Club"})
        questions = cat_resp.json()["questions"]
        for q in questions:
            self.session.post(f"{BASE_URL}/api/games/{game_id}/answer", json={
                "question_id": q["id"],
                "selected_option": "C",
                "time_taken": 2.5
            })
        
        # Bot plays
        self.session.post(f"{BASE_URL}/api/games/{game_id}/bot-play")
        
        # Check game state - should be round 2 now
        game_resp = self.session.get(f"{BASE_URL}/api/games/{game_id}")
        game = game_resp.json()
        
        assert game["current_round"] == 2, f"Expected round 2, got {game['current_round']}"
        assert game["is_my_turn"] == True, "Should be player's turn again"
        
        print(f"✓ Round advanced to {game['current_round']}, is_my_turn: {game['is_my_turn']}")
        
    def test_11_full_quick_play_game_6_rounds(self):
        """Test complete Quick Play game through all 6 rounds"""
        resp = self.session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = resp.json()["game_id"]
        
        for round_num in range(1, 7):
            # Get game state
            game_resp = self.session.get(f"{BASE_URL}/api/games/{game_id}")
            game = game_resp.json()
            
            if game["status"] == "finished":
                break
                
            assert game["current_round"] == round_num, f"Expected round {round_num}, got {game['current_round']}"
            
            # Select category
            cat_resp = self.session.post(f"{BASE_URL}/api/games/{game_id}/select-category", params={"category": "Club"})
            if cat_resp.status_code != 200:
                print(f"  Warning: Category select returned {cat_resp.status_code}: {cat_resp.text}")
                break
            questions = cat_resp.json()["questions"]
            
            # Answer all 3 questions
            for q in questions:
                self.session.post(f"{BASE_URL}/api/games/{game_id}/answer", json={
                    "question_id": q["id"],
                    "selected_option": "D",
                    "time_taken": 5.0
                })
            
            # Bot plays
            bot_resp = self.session.post(f"{BASE_URL}/api/games/{game_id}/bot-play")
            if bot_resp.status_code != 200:
                print(f"  Warning: Bot play returned {bot_resp.status_code}: {bot_resp.text}")
            
            print(f"  - Round {round_num} completed")
        
        # Verify game is finished
        final_resp = self.session.get(f"{BASE_URL}/api/games/{game_id}")
        final_game = final_resp.json()
        
        assert final_game["status"] == "finished", f"Expected finished, got {final_game['status']}"
        assert final_game["winner_id"] is not None, "Winner should be set"
        print(f"✓ Full game completed: my_score={final_game['my_score']}, opponent_score={final_game['opponent_score']}, winner_id={final_game['winner_id']}")
        
    def test_12_club_challenge_full_game_6_rounds(self):
        """Test complete Club Challenge game (solo mode) through all 6 rounds"""
        resp = self.session.post(f"{BASE_URL}/api/games/club-challenge")
        assert resp.status_code == 200, f"Club challenge start failed: {resp.text}"
        game_id = resp.json()["game_id"]
        
        for round_num in range(1, 7):
            # Get game state
            game_resp = self.session.get(f"{BASE_URL}/api/games/{game_id}")
            game = game_resp.json()
            
            if game["status"] == "finished":
                break
                
            assert game["current_round"] == round_num, f"Expected round {round_num}, got {game['current_round']}"
            
            # In Club Challenge, category is auto-selected to "Club" by frontend
            # But backend still needs select-category call
            cat_resp = self.session.post(f"{BASE_URL}/api/games/{game_id}/select-category", params={"category": "Club"})
            if cat_resp.status_code != 200:
                print(f"  Warning R{round_num}: Category select returned {cat_resp.status_code}: {cat_resp.text}")
                break
            questions = cat_resp.json()["questions"]
            
            # Answer all 3 questions
            for i, q in enumerate(questions):
                ans_resp = self.session.post(f"{BASE_URL}/api/games/{game_id}/answer", json={
                    "question_id": q["id"],
                    "selected_option": "A",
                    "time_taken": 4.0
                })
                if ans_resp.status_code != 200:
                    print(f"  Warning R{round_num} Q{i+1}: Answer submit returned {ans_resp.status_code}: {ans_resp.text}")
                    
            print(f"  - Round {round_num} completed (solo)")
        
        # Verify game is finished
        final_resp = self.session.get(f"{BASE_URL}/api/games/{game_id}")
        final_game = final_resp.json()
        
        assert final_game["status"] == "finished", f"Expected finished, got {final_game['status']}"
        assert final_game["winner_id"] is not None, "Winner should be set for solo game"
        print(f"✓ Club Challenge completed: my_score={final_game['my_score']}, status={final_game['status']}")
        
    def test_13_game_history_endpoint(self):
        """Test game history endpoint returns finished games"""
        # First complete a quick game
        resp = self.session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = resp.json()["game_id"]
        
        # Complete all 6 rounds quickly
        for _ in range(6):
            cat_resp = self.session.post(f"{BASE_URL}/api/games/{game_id}/select-category", params={"category": "Club"})
            if cat_resp.status_code != 200:
                break
            questions = cat_resp.json()["questions"]
            for q in questions:
                self.session.post(f"{BASE_URL}/api/games/{game_id}/answer", json={
                    "question_id": q["id"],
                    "selected_option": "A",
                    "time_taken": 1.0
                })
            self.session.post(f"{BASE_URL}/api/games/{game_id}/bot-play")
        
        # Now check history
        history_resp = self.session.get(f"{BASE_URL}/api/games/history")
        assert history_resp.status_code == 200, f"History failed: {history_resp.text}"
        history = history_resp.json()
        
        assert isinstance(history, list)
        if len(history) > 0:
            game = history[0]
            assert "id" in game
            assert "opponent_username" in game
            assert "my_score" in game
            assert "opponent_score" in game
            assert "won" in game
            assert "date" in game
            print(f"✓ Game history: {len(history)} games, most recent: {game['opponent_username']} - won: {game['won']}")
        else:
            print(f"✓ Game history endpoint works (0 games)")
            
    def test_14_no_duplicate_rounds(self):
        """Test that selecting category multiple times doesn't create duplicate rounds"""
        resp = self.session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = resp.json()["game_id"]
        
        # Select category multiple times
        for _ in range(3):
            self.session.post(f"{BASE_URL}/api/games/{game_id}/select-category", params={"category": "Club"})
        
        # Check game state
        game_resp = self.session.get(f"{BASE_URL}/api/games/{game_id}")
        game = game_resp.json()
        
        # Should only have 1 round for round_number=1
        round_1_count = sum(1 for r in game["rounds"] if r["round_number"] == 1)
        assert round_1_count <= 1, f"Expected max 1 round for round_number=1, got {round_1_count}"
        print(f"✓ No duplicate rounds: {len(game['rounds'])} total rounds in game state")
        
    def test_15_timeout_answer_x(self):
        """Test that timeout sends 'X' as answer (not empty string)"""
        resp = self.session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = resp.json()["game_id"]
        
        cat_resp = self.session.post(f"{BASE_URL}/api/games/{game_id}/select-category", params={"category": "Club"})
        questions = cat_resp.json()["questions"]
        
        # Submit 'X' as timeout answer
        ans_resp = self.session.post(f"{BASE_URL}/api/games/{game_id}/answer", json={
            "question_id": questions[0]["id"],
            "selected_option": "X",  # Timeout value
            "time_taken": 15.0
        })
        assert ans_resp.status_code == 200, f"Timeout answer failed: {ans_resp.text}"
        data = ans_resp.json()
        
        assert data["is_correct"] == False, "X should always be wrong"
        assert data["score"] == 0, "X should give 0 points"
        assert "correct_option" in data, "correct_option should still be returned"
        print(f"✓ Timeout 'X' answer handled: is_correct=False, score=0, correct={data['correct_option']}")


class TestDashboardAndUI:
    """Test dashboard and UI endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert login_resp.status_code == 200
        
    def test_active_games_list(self):
        """Test listing active games"""
        resp = self.session.get(f"{BASE_URL}/api/games")
        assert resp.status_code == 200
        games = resp.json()
        assert isinstance(games, list)
        print(f"✓ Active games: {len(games)} games")
        
    def test_leaderboard(self):
        """Test leaderboard endpoint"""
        resp = self.session.get(f"{BASE_URL}/api/users/leaderboard")
        assert resp.status_code == 200
        leaderboard = resp.json()
        assert isinstance(leaderboard, list)
        if len(leaderboard) > 0:
            assert "username" in leaderboard[0]
            assert "skill_rank" in leaderboard[0]
        print(f"✓ Leaderboard: {len(leaderboard)} users")
        
    def test_my_rank(self):
        """Test my rank endpoint"""
        resp = self.session.get(f"{BASE_URL}/api/users/my-rank")
        assert resp.status_code == 200
        ranks = resp.json()
        assert "global" in ranks
        print(f"✓ My rank: global={ranks['global']}")
