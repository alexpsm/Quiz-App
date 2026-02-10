"""
Iteration 6 Gameplay Feature Tests
==================================
Tests for gameplay improvements:
1. Bot games with is_bot_game=true and turn_started_at
2. Game GET returns is_bot_game, turn_started_at, turn_deadline fields
3. Rounds with opponent_answers for completed rounds
4. Bot-play endpoint simulates bot answers with question details
5. Answer endpoint properly switches turn after 3 answers
6. Bot-play advances game round after bot finishes

Test user: testuser@quizball.com / Test12345
"""
import pytest
import requests
import os
import time

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


class TestQuickPlayBotGame:
    """Tests for POST /api/games/quick-play - Bot game creation"""
    
    def test_quick_play_creates_bot_game(self, authenticated_session):
        """POST /api/games/quick-play creates a game with is_bot_game=true"""
        response = authenticated_session.post(f"{BASE_URL}/api/games/quick-play")
        assert response.status_code == 200
        data = response.json()
        assert "game_id" in data
        assert data["opponent"] == "TheScore90Bot"
    
    def test_quick_play_game_get_has_bot_fields(self, authenticated_session):
        """GET /api/games/{id} returns is_bot_game, turn_started_at, turn_deadline"""
        # Create game
        create_response = authenticated_session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = create_response.json()["game_id"]
        
        # Get game
        response = authenticated_session.get(f"{BASE_URL}/api/games/{game_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify bot game fields
        assert "is_bot_game" in data
        assert data["is_bot_game"] == True
        assert "turn_started_at" in data
        assert data["turn_started_at"] is not None
        assert "turn_deadline" in data
        assert data["turn_deadline"] is not None
    
    def test_turn_deadline_is_3_hours_after_start(self, authenticated_session):
        """turn_deadline should be approximately 3 hours after turn_started_at"""
        # Create game
        create_response = authenticated_session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = create_response.json()["game_id"]
        
        # Get game
        response = authenticated_session.get(f"{BASE_URL}/api/games/{game_id}")
        data = response.json()
        
        from datetime import datetime
        turn_started = datetime.fromisoformat(data["turn_started_at"].replace('Z', '+00:00'))
        turn_deadline = datetime.fromisoformat(data["turn_deadline"].replace('Z', '+00:00'))
        
        # Deadline should be ~3 hours after start
        delta = turn_deadline - turn_started
        assert 10799 <= delta.total_seconds() <= 10801, f"Expected ~3 hours, got {delta.total_seconds()} seconds"


class TestGameRoundsAndAnswers:
    """Tests for answering questions and round progression"""
    
    @pytest.fixture
    def game_with_category(self, authenticated_session):
        """Create a game and select category, return game_id and questions"""
        # Create game
        create_response = authenticated_session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = create_response.json()["game_id"]
        
        # Use 'League' category which always has enough questions
        category = "League"
        
        # Select category
        select_response = authenticated_session.post(
            f"{BASE_URL}/api/games/{game_id}/select-category",
            params={"category": category}
        )
        assert select_response.status_code == 200, f"Select category failed: {select_response.text}"
        questions = select_response.json()["questions"]
        
        return {"game_id": game_id, "questions": questions}
    
    def test_select_category_returns_questions(self, authenticated_session, game_with_category):
        """Selecting category returns 3 questions"""
        questions = game_with_category["questions"]
        assert len(questions) == 3
        for q in questions:
            assert "id" in q
            assert "question_text" in q
            assert "option_a" in q
            assert "option_b" in q
            assert "option_c" in q
            assert "option_d" in q
    
    def test_submit_answer_returns_score(self, authenticated_session, game_with_category):
        """Submitting answer returns is_correct and score"""
        game_id = game_with_category["game_id"]
        question = game_with_category["questions"][0]
        
        response = authenticated_session.post(
            f"{BASE_URL}/api/games/{game_id}/answer",
            json={
                "question_id": question["id"],
                "selected_option": "A",
                "time_taken": 5.0
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "is_correct" in data
        assert "score" in data
        assert isinstance(data["score"], int)
    
    def test_answering_3_questions_switches_turn(self, authenticated_session):
        """After answering 3 questions, turn switches to bot (player2)"""
        # Create game
        create_response = authenticated_session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = create_response.json()["game_id"]
        
        # Use 'League' category which always has enough questions
        category = "League"
        
        select_response = authenticated_session.post(
            f"{BASE_URL}/api/games/{game_id}/select-category",
            params={"category": category}
        )
        assert select_response.status_code == 200, f"Select category failed: {select_response.text}"
        questions = select_response.json()["questions"]
        
        # Verify it's player's turn initially
        game_before = authenticated_session.get(f"{BASE_URL}/api/games/{game_id}").json()
        assert game_before["is_my_turn"] == True
        
        # Answer all 3 questions
        for q in questions:
            authenticated_session.post(
                f"{BASE_URL}/api/games/{game_id}/answer",
                json={
                    "question_id": q["id"],
                    "selected_option": "A",
                    "time_taken": 3.0
                }
            )
        
        # Verify turn switched to bot
        game_after = authenticated_session.get(f"{BASE_URL}/api/games/{game_id}").json()
        assert game_after["is_my_turn"] == False, "Turn should switch to bot after 3 answers"


class TestBotPlayEndpoint:
    """Tests for POST /api/games/{id}/bot-play - Bot answering simulation"""
    
    def test_bot_play_returns_answers_with_question_details(self, authenticated_session):
        """Bot-play returns bot_answers with question_text, options, correct_option, score"""
        # Create game
        create_response = authenticated_session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = create_response.json()["game_id"]
        
        # Use 'League' category which always has enough questions
        category = "League"
        
        select_response = authenticated_session.post(
            f"{BASE_URL}/api/games/{game_id}/select-category",
            params={"category": category}
        )
        assert select_response.status_code == 200, f"Select category failed: {select_response.text}"
        questions = select_response.json()["questions"]
        
        # Answer all 3 questions to switch turn to bot
        for q in questions:
            authenticated_session.post(
                f"{BASE_URL}/api/games/{game_id}/answer",
                json={
                    "question_id": q["id"],
                    "selected_option": "A",
                    "time_taken": 3.0
                }
            )
        
        # Trigger bot play
        bot_response = authenticated_session.post(f"{BASE_URL}/api/games/{game_id}/bot-play")
        assert bot_response.status_code == 200
        data = bot_response.json()
        
        # Verify bot_answers structure
        assert "bot_answers" in data
        assert len(data["bot_answers"]) == 3
        
        for answer in data["bot_answers"]:
            assert "question_id" in answer
            assert "selected_option" in answer
            assert "correct_option" in answer
            assert "is_correct" in answer
            assert "time_taken" in answer
            assert "score" in answer
            assert "question_text" in answer
            assert "option_a" in answer
            assert "option_b" in answer
            assert "option_c" in answer
            assert "option_d" in answer
    
    def test_bot_play_advances_round(self, authenticated_session):
        """Bot-play advances game to next round"""
        # Create game
        create_response = authenticated_session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = create_response.json()["game_id"]
        
        # Use 'League' category which always has enough questions
        category = "League"
        
        select_response = authenticated_session.post(
            f"{BASE_URL}/api/games/{game_id}/select-category",
            params={"category": category}
        )
        assert select_response.status_code == 200, f"Select category failed: {select_response.text}"
        questions = select_response.json()["questions"]
        
        # Get initial round
        game_before = authenticated_session.get(f"{BASE_URL}/api/games/{game_id}").json()
        initial_round = game_before["current_round"]
        
        # Answer all 3 questions
        for q in questions:
            authenticated_session.post(
                f"{BASE_URL}/api/games/{game_id}/answer",
                json={
                    "question_id": q["id"],
                    "selected_option": "A",
                    "time_taken": 3.0
                }
            )
        
        # Trigger bot play
        bot_response = authenticated_session.post(f"{BASE_URL}/api/games/{game_id}/bot-play")
        assert bot_response.status_code == 200
        
        # Check round advanced
        game_after = authenticated_session.get(f"{BASE_URL}/api/games/{game_id}").json()
        
        # If not finished, round should advance
        if game_after["status"] == "active":
            assert game_after["current_round"] == initial_round + 1, "Round should advance after bot plays"
            assert game_after["is_my_turn"] == True, "Turn should be back to player"
    
    def test_bot_play_fails_if_not_bot_turn(self, authenticated_session):
        """Bot-play returns error if it's not the bot's turn"""
        # Create game
        create_response = authenticated_session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = create_response.json()["game_id"]
        
        # Don't answer any questions - it's still player's turn
        bot_response = authenticated_session.post(f"{BASE_URL}/api/games/{game_id}/bot-play")
        assert bot_response.status_code == 400
        assert "Not the bot's turn" in bot_response.json().get("detail", "")


class TestOpponentAnswersPlayback:
    """Tests for opponent_answers in game rounds"""
    
    def test_game_rounds_have_opponent_answers_after_completion(self, authenticated_session):
        """Completed rounds include opponent_answers for playback"""
        # Create game
        create_response = authenticated_session.post(f"{BASE_URL}/api/games/quick-play")
        game_id = create_response.json()["game_id"]
        
        # Use 'League' category which always has enough questions
        category = "League"
        
        select_response = authenticated_session.post(
            f"{BASE_URL}/api/games/{game_id}/select-category",
            params={"category": category}
        )
        assert select_response.status_code == 200, f"Select category failed: {select_response.text}"
        questions = select_response.json()["questions"]
        
        # Answer all 3 questions
        for q in questions:
            authenticated_session.post(
                f"{BASE_URL}/api/games/{game_id}/answer",
                json={
                    "question_id": q["id"],
                    "selected_option": "A",
                    "time_taken": 3.0
                }
            )
        
        # Trigger bot play
        authenticated_session.post(f"{BASE_URL}/api/games/{game_id}/bot-play")
        
        # Get game with rounds
        game = authenticated_session.get(f"{BASE_URL}/api/games/{game_id}").json()
        
        # Check that round 1 has opponent_answers (completed round)
        round1 = next((r for r in game["rounds"] if r["round_number"] == 1), None)
        assert round1 is not None
        assert "opponent_answers" in round1
        assert "my_answers" in round1
        assert len(round1["my_answers"]) == 3
        # After bot played, opponent_answers should be populated
        assert len(round1["opponent_answers"]) == 3


class TestFullGameFlow:
    """End-to-end test of the complete game flow"""
    
    def test_full_game_flow_quick_play(self, authenticated_session):
        """Test: quick-play -> select-category -> answer x3 -> bot-play -> verify"""
        # 1. Create quick-play game
        create_response = authenticated_session.post(f"{BASE_URL}/api/games/quick-play")
        assert create_response.status_code == 200
        game_id = create_response.json()["game_id"]
        opponent = create_response.json()["opponent"]
        print(f"Created game {game_id} vs {opponent}")
        
        # 2. Verify game state
        game = authenticated_session.get(f"{BASE_URL}/api/games/{game_id}").json()
        assert game["is_bot_game"] == True
        assert game["is_my_turn"] == True
        assert game["current_round"] == 1
        assert game["turn_deadline"] is not None
        print(f"Game state: round {game['current_round']}, is_my_turn={game['is_my_turn']}")
        
        # 3. Select category (use 'League' which has enough questions)
        category = "League"
        
        select_response = authenticated_session.post(
            f"{BASE_URL}/api/games/{game_id}/select-category",
            params={"category": category}
        )
        assert select_response.status_code == 200, f"Select category failed: {select_response.text}"
        questions = select_response.json()["questions"]
        assert len(questions) == 3
        print(f"Selected category: {category}, got {len(questions)} questions")
        
        # 4. Answer all 3 questions
        for i, q in enumerate(questions):
            answer_response = authenticated_session.post(
                f"{BASE_URL}/api/games/{game_id}/answer",
                json={
                    "question_id": q["id"],
                    "selected_option": "A",
                    "time_taken": 5.0
                }
            )
            assert answer_response.status_code == 200
            print(f"Answered Q{i+1}: is_correct={answer_response.json()['is_correct']}, score={answer_response.json()['score']}")
        
        # 5. Verify turn switched
        game_after_answers = authenticated_session.get(f"{BASE_URL}/api/games/{game_id}").json()
        assert game_after_answers["is_my_turn"] == False
        print("Turn switched to bot")
        
        # 6. Trigger bot play
        bot_response = authenticated_session.post(f"{BASE_URL}/api/games/{game_id}/bot-play")
        assert bot_response.status_code == 200
        bot_data = bot_response.json()
        assert len(bot_data["bot_answers"]) == 3
        print(f"Bot answered: score={bot_data['bot_score']}")
        
        # 7. Verify game advanced
        final_game = authenticated_session.get(f"{BASE_URL}/api/games/{game_id}").json()
        if final_game["status"] == "active":
            assert final_game["current_round"] == 2
            assert final_game["is_my_turn"] == True
            print(f"Round advanced to {final_game['current_round']}, is_my_turn=True")
        else:
            print(f"Game finished: status={final_game['status']}")
        
        # 8. Verify opponent_answers in round 1
        round1 = next((r for r in final_game["rounds"] if r["round_number"] == 1), None)
        assert round1 is not None
        assert len(round1["opponent_answers"]) == 3
        print(f"Round 1 opponent_answers: {len(round1['opponent_answers'])} answers")
        
        print("Full game flow test PASSED")


class TestDashboardFeatures:
    """Verify dashboard-related APIs still work"""
    
    def test_quick_play_still_works(self, authenticated_session):
        """POST /api/games/quick-play works"""
        response = authenticated_session.post(f"{BASE_URL}/api/games/quick-play")
        assert response.status_code == 200
    
    def test_invite_still_works(self, authenticated_session):
        """POST /api/games/invite works"""
        response = authenticated_session.post(f"{BASE_URL}/api/games/invite")
        assert response.status_code == 200
    
    def test_club_wars_still_works(self, authenticated_session):
        """GET /api/club-wars/current works"""
        response = authenticated_session.get(f"{BASE_URL}/api/club-wars/current")
        assert response.status_code == 200
    
    def test_my_rank_still_works(self, authenticated_session):
        """GET /api/users/my-rank works"""
        response = authenticated_session.get(f"{BASE_URL}/api/users/my-rank")
        assert response.status_code == 200
