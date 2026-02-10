import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class QuizBallAPITester:
    def __init__(self, base_url="https://ball-knowledge.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()  # Use session to handle cookies
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_password = "quizball_admin_2026"

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Optional[Dict] = None, headers: Optional[Dict] = None) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    return False, error_data
                except:
                    print(f"   Error: {response.text}")
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_auth_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_data = {
            "email": f"test_user_{timestamp}@example.com",
            "password": "TestPass123!",
            "name": f"Test User {timestamp}"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=test_data
        )
        
        if success:
            self.test_email = test_data["email"]
            self.test_password = test_data["password"]
            return True
        return False

    def test_auth_login(self):
        """Test user login"""
        if not hasattr(self, 'test_email'):
            print("❌ Cannot test login - no registered user")
            return False
            
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        return success

    def test_auth_me(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        
        if success:
            self.user_data = response
            print(f"   User ID: {response.get('user_id')}")
            print(f"   Email: {response.get('email')}")
            print(f"   Username: {response.get('username')}")
        
        return success

    def test_update_profile(self):
        """Test updating user profile"""
        timestamp = datetime.now().strftime('%H%M%S')
        update_data = {
            "username": f"testuser{timestamp}",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=test"
        }
        
        success, response = self.run_test(
            "Update Profile",
            "PUT",
            "users/me",
            200,
            data=update_data
        )
        
        if success:
            print(f"   Updated username: {response.get('username')}")
        
        return success

    def test_questions_categories(self):
        """Test getting question categories"""
        success, response = self.run_test(
            "Get Question Categories",
            "GET",
            "questions/categories",
            200
        )
        
        if success:
            print(f"   Categories: {response}")
            self.categories = response
        
        return success

    def test_questions_list(self):
        """Test listing questions"""
        success, response = self.run_test(
            "List Questions",
            "GET",
            "questions?limit=5",
            200
        )
        
        if success:
            print(f"   Found {len(response)} questions")
            if response:
                self.sample_questions = response[:3]
        
        return success

    def test_admin_create_question(self):
        """Test creating a question (admin)"""
        question_data = {
            "question_text": "Which team won the 2024 UEFA Champions League?",
            "option_a": "Real Madrid",
            "option_b": "Manchester City", 
            "option_c": "Bayern Munich",
            "option_d": "Barcelona",
            "correct_option": "A",
            "category": "League",
            "difficulty": 2
        }
        
        success, response = self.run_test(
            "Create Question (Admin)",
            "POST",
            f"questions?password={self.admin_password}",
            200,
            data=question_data
        )
        
        if success:
            print(f"   Created question ID: {response.get('id')}")
            self.test_question_id = response.get('id')
        
        return success

    def test_matchmaking(self):
        """Test random matchmaking"""
        success, response = self.run_test(
            "Random Matchmaking",
            "POST",
            "games/matchmake",
            200
        )
        
        if success:
            print(f"   Game ID: {response.get('game_id')}")
            self.game_id = response.get('game_id')
        
        return success

    def test_create_invite(self):
        """Test creating game invite"""
        success, response = self.run_test(
            "Create Game Invite",
            "POST",
            "games/invite",
            200
        )
        
        if success:
            print(f"   Invite code: {response.get('invite_code')}")
            self.invite_code = response.get('invite_code')
        
        return success

    def test_list_games(self):
        """Test listing user's games"""
        success, response = self.run_test(
            "List User Games",
            "GET",
            "games",
            200
        )
        
        if success:
            print(f"   Found {len(response)} games")
            if response:
                print(f"   First game status: {response[0].get('status')}")
        
        return success

    def test_get_game_details(self):
        """Test getting specific game details"""
        if not hasattr(self, 'game_id'):
            print("❌ Cannot test game details - no game created")
            return False
            
        success, response = self.run_test(
            "Get Game Details",
            "GET",
            f"games/{self.game_id}",
            200
        )
        
        if success:
            print(f"   Game status: {response.get('status')}")
            print(f"   Current round: {response.get('current_round')}")
            print(f"   Is my turn: {response.get('is_my_turn')}")
        
        return success

    def test_select_category(self):
        """Test selecting category for game round"""
        if not hasattr(self, 'game_id') or not hasattr(self, 'categories'):
            print("❌ Cannot test category selection - missing game or categories")
            return False
            
        if not self.categories:
            print("❌ No categories available")
            return False
        
        # Try different categories until we find one with enough questions
        for category in self.categories:
            success, response = self.run_test(
                f"Select Game Category ({category})",
                "POST",
                f"games/{self.game_id}/select-category?category={category}",
                200
            )
            
            if success:
                questions = response.get('questions', [])
                print(f"   Selected category: {category}")
                print(f"   Got {len(questions)} questions")
                if questions:
                    self.round_questions = questions
                    return True
            else:
                print(f"   Category {category} failed, trying next...")
                continue
        
        print("❌ No categories have enough questions")
        return False

    def test_submit_answer(self):
        """Test submitting an answer"""
        if not hasattr(self, 'game_id') or not hasattr(self, 'round_questions'):
            print("❌ Cannot test answer submission - missing game or questions")
            return False
            
        if not self.round_questions:
            print("❌ No questions available")
            return False
            
        question = self.round_questions[0]
        answer_data = {
            "question_id": question['id'],
            "selected_option": "A",
            "time_taken": 5.5
        }
        
        success, response = self.run_test(
            "Submit Answer",
            "POST",
            f"games/{self.game_id}/answer",
            200,
            data=answer_data
        )
        
        if success:
            print(f"   Is correct: {response.get('is_correct')}")
            print(f"   Score: {response.get('score')}")
        
        return success

    def test_leaderboard(self):
        """Test getting leaderboard"""
        success, response = self.run_test(
            "Get Leaderboard",
            "GET",
            "users/leaderboard?limit=10",
            200
        )
        
        if success:
            print(f"   Leaderboard entries: {len(response)}")
            if response:
                print(f"   Top player: {response[0].get('username')} ({response[0].get('skill_rank')})")
        
        return success

    def test_logout(self):
        """Test user logout"""
        success, response = self.run_test(
            "User Logout",
            "POST",
            "auth/logout",
            200
        )
        
        if success:
            # Clear session cookies
            self.session.cookies.clear()
        
        return success

def main():
    print("🏈 QuizBall API Testing Suite")
    print("=" * 50)
    
    tester = QuizBallAPITester()
    
    # Test sequence
    test_sequence = [
        # Authentication tests
        ("Registration", tester.test_auth_registration),
        ("Login", tester.test_auth_login),
        ("Get Current User", tester.test_auth_me),
        ("Update Profile", tester.test_update_profile),
        
        # Question tests
        ("Get Categories", tester.test_questions_categories),
        ("List Questions", tester.test_questions_list),
        ("Create Question (Admin)", tester.test_admin_create_question),
        
        # Game tests
        ("Random Matchmaking", tester.test_matchmaking),
        ("Create Invite", tester.test_create_invite),
        ("List Games", tester.test_list_games),
        ("Get Game Details", tester.test_get_game_details),
        ("Select Category", tester.test_select_category),
        ("Submit Answer", tester.test_submit_answer),
        
        # User tests
        ("Get Leaderboard", tester.test_leaderboard),
        
        # Cleanup
        ("Logout", tester.test_logout),
    ]
    
    failed_tests = []
    
    for test_name, test_func in test_sequence:
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} - Exception: {str(e)}")
            failed_tests.append(test_name)
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print("\n✅ All tests passed!")
    
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())