"""
Test Suite for Iteration 8: Club Category Unification and Club Challenge Mode
Tests:
1. Unified 'Club' category with questions for all 96 clubs
2. Club Challenge mode returns club-specific questions based on user's favorite club
3. Categories reduced to 18 (no club-specific subcategories)
4. Quick Play still works with regular categories
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestClubCategoryUnification:
    """Tests for unified Club category with 96 clubs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_categories_count_reduced(self):
        """Verify categories are reduced to ~18 (no club-specific subcategories)"""
        response = self.session.get(f"{BASE_URL}/api/questions/categories")
        assert response.status_code == 200
        categories = response.json()
        
        # Should have around 18 categories, not 85+
        print(f"Total categories: {len(categories)}")
        print(f"Categories: {categories}")
        
        # Verify no club-specific subcategories like 'Arsenal-History', 'Manchester United-Players'
        club_subcategories = [c for c in categories if '-History' in c or '-Players' in c or '-Managers' in c or '-Trophies' in c]
        assert len(club_subcategories) == 0, f"Found club-specific subcategories: {club_subcategories}"
        
        # Should have 'Club' as a unified category
        assert 'Club' in categories, "Missing unified 'Club' category"
        
        # Should be around 18 categories (not 85+)
        assert len(categories) <= 25, f"Too many categories ({len(categories)}), expected ~18"
    
    def test_club_category_has_869_questions(self):
        """Verify Club category has ~869 questions covering all 96 clubs"""
        response = self.session.get(f"{BASE_URL}/api/questions?category=Club&limit=1000")
        assert response.status_code == 200
        questions = response.json()
        
        print(f"Total Club questions: {len(questions)}")
        
        # Should have around 869 questions (9 questions per club * 96 clubs)
        assert len(questions) >= 800, f"Expected ~869 Club questions, got {len(questions)}"
    
    def test_club_questions_cover_premier_league_clubs(self):
        """Verify questions exist for Premier League clubs"""
        response = self.session.get(f"{BASE_URL}/api/questions?category=Club&limit=1000")
        assert response.status_code == 200
        questions = response.json()
        
        premier_league_clubs = ['Arsenal', 'Liverpool', 'Manchester United', 'Chelsea', 'Manchester City', 
                                'Tottenham', 'Newcastle', 'Aston Villa', 'Brighton', 'West Ham']
        
        for club in premier_league_clubs:
            club_questions = [q for q in questions if club.lower() in q['question_text'].lower()]
            print(f"{club}: {len(club_questions)} questions")
            assert len(club_questions) >= 1, f"No questions found for {club}"
    
    def test_club_questions_cover_bundesliga_clubs(self):
        """Verify questions exist for Bundesliga clubs"""
        response = self.session.get(f"{BASE_URL}/api/questions?category=Club&limit=1000")
        assert response.status_code == 200
        questions = response.json()
        
        bundesliga_clubs = ['Bayern Munich', 'Borussia Dortmund', 'RB Leipzig', 'Bayer Leverkusen', 'Eintracht Frankfurt']
        
        for club in bundesliga_clubs:
            club_questions = [q for q in questions if club.lower() in q['question_text'].lower()]
            print(f"{club}: {len(club_questions)} questions")
            assert len(club_questions) >= 1, f"No questions found for {club}"
    
    def test_club_questions_cover_la_liga_clubs(self):
        """Verify questions exist for La Liga clubs"""
        response = self.session.get(f"{BASE_URL}/api/questions?category=Club&limit=1000")
        assert response.status_code == 200
        questions = response.json()
        
        la_liga_clubs = ['Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla', 'Real Sociedad']
        
        for club in la_liga_clubs:
            club_questions = [q for q in questions if club.lower() in q['question_text'].lower()]
            print(f"{club}: {len(club_questions)} questions")
            assert len(club_questions) >= 1, f"No questions found for {club}"
    
    def test_club_questions_cover_serie_a_clubs(self):
        """Verify questions exist for Serie A clubs"""
        response = self.session.get(f"{BASE_URL}/api/questions?category=Club&limit=1000")
        assert response.status_code == 200
        questions = response.json()
        
        serie_a_clubs = ['Juventus', 'Inter Milan', 'AC Milan', 'Napoli', 'Roma']
        
        for club in serie_a_clubs:
            club_questions = [q for q in questions if club.lower() in q['question_text'].lower()]
            print(f"{club}: {len(club_questions)} questions")
            assert len(club_questions) >= 1, f"No questions found for {club}"
    
    def test_club_questions_cover_ligue_1_clubs(self):
        """Verify questions exist for Ligue 1 clubs"""
        response = self.session.get(f"{BASE_URL}/api/questions?category=Club&limit=1000")
        assert response.status_code == 200
        questions = response.json()
        
        ligue_1_clubs = ['Paris Saint-Germain', 'Marseille', 'Monaco', 'Lyon', 'Lille']
        
        for club in ligue_1_clubs:
            club_questions = [q for q in questions if club.lower() in q['question_text'].lower()]
            print(f"{club}: {len(club_questions)} questions")
            assert len(club_questions) >= 1, f"No questions found for {club}"


class TestClubChallengeMode:
    """Tests for Club Challenge mode with favorite club filtering"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authenticated session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login with test user (favorite club: Arsenal)
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "matchtest@test.com", "password": "Test123456"}
        )
        if login_response.status_code != 200:
            pytest.skip("Could not login with test user")
    
    def test_club_challenge_returns_game_with_club(self):
        """POST /api/games/club-challenge returns game for user's favorite club"""
        response = self.session.post(f"{BASE_URL}/api/games/club-challenge")
        assert response.status_code == 200
        
        data = response.json()
        assert 'game_id' in data
        assert 'club' in data
        assert data['club'] == 'Arsenal', f"Expected Arsenal, got {data['club']}"
        
        print(f"Club Challenge game created: {data['game_id']} for club: {data['club']}")
    
    def test_club_challenge_game_has_correct_status(self):
        """Club Challenge game has status 'club_challenge'"""
        # Create club challenge game
        create_response = self.session.post(f"{BASE_URL}/api/games/club-challenge")
        assert create_response.status_code == 200
        game_id = create_response.json()['game_id']
        
        # Get game details
        game_response = self.session.get(f"{BASE_URL}/api/games/{game_id}")
        assert game_response.status_code == 200
        
        game = game_response.json()
        assert game['status'] == 'club_challenge', f"Expected status 'club_challenge', got {game['status']}"
    
    def test_club_challenge_questions_filtered_by_favorite_club(self):
        """Club Challenge mode returns questions about user's favorite club (Arsenal)"""
        # Create club challenge game
        create_response = self.session.post(f"{BASE_URL}/api/games/club-challenge")
        assert create_response.status_code == 200
        game_id = create_response.json()['game_id']
        
        # Select Club category
        category_response = self.session.post(f"{BASE_URL}/api/games/{game_id}/select-category?category=Club")
        assert category_response.status_code == 200
        
        data = category_response.json()
        questions = data.get('questions', [])
        
        assert len(questions) == 3, f"Expected 3 questions, got {len(questions)}"
        
        # All questions should mention Arsenal
        arsenal_questions = [q for q in questions if 'arsenal' in q['question_text'].lower()]
        print(f"Questions returned:")
        for q in questions:
            print(f"  - {q['question_text']}")
        
        assert len(arsenal_questions) == 3, f"Expected all 3 questions about Arsenal, got {len(arsenal_questions)}"


class TestQuickPlayMode:
    """Tests for Quick Play mode (regular categories)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authenticated session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login with test user
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "matchtest@test.com", "password": "Test123456"}
        )
        if login_response.status_code != 200:
            pytest.skip("Could not login with test user")
    
    def test_quick_play_creates_bot_game(self):
        """POST /api/games/quick-play creates game against bot"""
        response = self.session.post(f"{BASE_URL}/api/games/quick-play")
        assert response.status_code == 200
        
        data = response.json()
        assert 'game_id' in data
        assert data.get('opponent') == 'TheScore90Bot'
        
        print(f"Quick Play game created: {data['game_id']}")
    
    def test_quick_play_game_has_active_status(self):
        """Quick Play game has status 'active' (not 'club_challenge')"""
        # Create quick play game
        create_response = self.session.post(f"{BASE_URL}/api/games/quick-play")
        assert create_response.status_code == 200
        game_id = create_response.json()['game_id']
        
        # Get game details
        game_response = self.session.get(f"{BASE_URL}/api/games/{game_id}")
        assert game_response.status_code == 200
        
        game = game_response.json()
        assert game['status'] == 'active', f"Expected status 'active', got {game['status']}"
    
    def test_quick_play_can_select_any_category(self):
        """Quick Play allows selecting any category (not filtered by club)"""
        # Create quick play game
        create_response = self.session.post(f"{BASE_URL}/api/games/quick-play")
        assert create_response.status_code == 200
        game_id = create_response.json()['game_id']
        
        # Select a non-Club category (e.g., History)
        category_response = self.session.post(f"{BASE_URL}/api/games/{game_id}/select-category?category=History")
        assert category_response.status_code == 200
        
        data = category_response.json()
        questions = data.get('questions', [])
        
        assert len(questions) == 3, f"Expected 3 questions, got {len(questions)}"
        print(f"History questions returned:")
        for q in questions:
            print(f"  - {q['question_text']}")


class TestCategoryList:
    """Tests for category list endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_categories_include_expected_types(self):
        """Verify expected category types exist"""
        response = self.session.get(f"{BASE_URL}/api/questions/categories")
        assert response.status_code == 200
        categories = response.json()
        
        expected_categories = ['Club', 'History', 'Players', 'League', 'Stadiums', 'Rules']
        
        for expected in expected_categories:
            assert expected in categories, f"Missing expected category: {expected}"
        
        print(f"All categories: {categories}")
    
    def test_no_club_specific_subcategories(self):
        """Verify no club-specific subcategories like 'Arsenal-History'"""
        response = self.session.get(f"{BASE_URL}/api/questions/categories")
        assert response.status_code == 200
        categories = response.json()
        
        # Check for patterns like 'ClubName-SubCategory'
        problematic = []
        for cat in categories:
            if '-History' in cat or '-Players' in cat or '-Managers' in cat or '-Trophies' in cat:
                # Allow generic ones like 'Players - History'
                if cat.startswith('Players') or cat.startswith('Club'):
                    continue
                problematic.append(cat)
        
        assert len(problematic) == 0, f"Found club-specific subcategories: {problematic}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
