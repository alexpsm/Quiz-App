"""
QuizBall API Tests - Iteration 4
Testing 3 new features:
1. Avatar image upload (POST /api/users/avatar)
2. My Rank endpoint (GET /api/users/my-rank)
3. Full League system (CRUD + join/leave)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ball-knowledge.preview.emergentagent.com')
TEST_USER_EMAIL = "testuser@quizball.com"
TEST_USER_PASSWORD = "Test12345"


@pytest.fixture(scope="module")
def session():
    """Create requests session with cookies"""
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def auth_session(session):
    """Authenticate test user and return session"""
    login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    return session


@pytest.fixture(scope="module")
def secondary_auth_session():
    """Create a second authenticated user for league tests"""
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    
    secondary_email = f"test_league_user_{uuid.uuid4().hex[:8]}@quizball.com"
    
    # Register new user
    reg_resp = s.post(f"{BASE_URL}/api/auth/register", json={
        "email": secondary_email,
        "password": TEST_USER_PASSWORD,
        "name": "League Test User"
    })
    
    if reg_resp.status_code != 200:
        # Try login if already exists
        login_resp = s.post(f"{BASE_URL}/api/auth/login", json={
            "email": secondary_email,
            "password": TEST_USER_PASSWORD
        })
        if login_resp.status_code != 200:
            pytest.skip("Could not create secondary user for league tests")
    
    # Update profile with username
    s.put(f"{BASE_URL}/api/users/me", json={
        "username": f"test_league_{uuid.uuid4().hex[:6]}",
        "favorite_club": "Arsenal"
    })
    
    return s


# ==================== AVATAR UPLOAD TESTS ====================

class TestAvatarUpload:
    """Test POST /api/users/avatar endpoint"""
    
    def test_avatar_upload_accepts_image(self, auth_session):
        """Test that avatar upload accepts image and returns avatar URL"""
        import base64
        png_1x1 = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        
        # Create a fresh session for file uploads (Content-Type must not be preset)
        upload_session = requests.Session()
        upload_session.cookies.update(auth_session.cookies)
        
        files = {"file": ("test_avatar.png", png_1x1, "image/png")}
        response = upload_session.post(f"{BASE_URL}/api/users/avatar", files=files)
        
        assert response.status_code == 200, f"Avatar upload failed: {response.text}"
        data = response.json()
        assert "avatar" in data, "Response missing 'avatar' field"
        assert data["avatar"].startswith("/api/uploads/"), f"Avatar URL should start with /api/uploads/, got: {data['avatar']}"
        
        print(f"✅ Avatar uploaded successfully: {data['avatar']}")
    
    def test_avatar_upload_rejects_non_image(self, auth_session):
        """Test that avatar upload rejects non-image files"""
        upload_session = requests.Session()
        upload_session.cookies.update(auth_session.cookies)
        
        files = {"file": ("test.txt", b"This is not an image", "text/plain")}
        response = upload_session.post(f"{BASE_URL}/api/users/avatar", files=files)
        
        assert response.status_code == 400, f"Expected 400 for non-image file, got {response.status_code}"
        print("✅ Non-image file correctly rejected")
    
    def test_avatar_upload_updates_user_profile(self, auth_session):
        """Test that uploaded avatar is reflected in user profile"""
        import base64
        png_1x1 = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        
        upload_session = requests.Session()
        upload_session.cookies.update(auth_session.cookies)
        
        files = {"file": ("profile_avatar.png", png_1x1, "image/png")}
        upload_resp = upload_session.post(f"{BASE_URL}/api/users/avatar", files=files)
        assert upload_resp.status_code == 200, f"Upload failed: {upload_resp.text}"
        
        uploaded_avatar_url = upload_resp.json()["avatar"]
        
        # Verify user profile reflects new avatar
        me_resp = auth_session.get(f"{BASE_URL}/api/auth/me")
        assert me_resp.status_code == 200
        user_data = me_resp.json()
        
        assert user_data.get("avatar") == uploaded_avatar_url, \
            f"Profile avatar mismatch. Expected: {uploaded_avatar_url}, Got: {user_data.get('avatar')}"
        
        print(f"✅ User profile avatar updated to: {uploaded_avatar_url}")
    
    def test_avatar_upload_requires_auth(self):
        """Test that avatar upload requires authentication"""
        # Use a fresh session without auth
        fresh_session = requests.Session()
        import base64
        png_1x1 = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        
        files = {"file": ("test.png", png_1x1, "image/png")}
        response = fresh_session.post(f"{BASE_URL}/api/users/avatar", files=files)
        
        assert response.status_code == 401, f"Expected 401 for unauthenticated upload, got {response.status_code}"
        print("✅ Avatar upload correctly requires authentication")


# ==================== MY RANK TESTS ====================

class TestMyRank:
    """Test GET /api/users/my-rank endpoint"""
    
    def test_my_rank_returns_global_rank(self, auth_session):
        """Test that my-rank returns global ranking"""
        response = auth_session.get(f"{BASE_URL}/api/users/my-rank")
        assert response.status_code == 200, f"My rank failed: {response.text}"
        
        data = response.json()
        assert "global" in data, "Response missing 'global' rank"
        assert "rank" in data["global"], "Global rank missing 'rank' field"
        assert "total" in data["global"], "Global rank missing 'total' field"
        assert isinstance(data["global"]["rank"], int), "Rank should be integer"
        assert isinstance(data["global"]["total"], int), "Total should be integer"
        assert data["global"]["rank"] >= 1, "Rank should be at least 1"
        
        print(f"✅ Global rank: #{data['global']['rank']} of {data['global']['total']}")
    
    def test_my_rank_returns_club_rank_when_set(self, auth_session):
        """Test that my-rank returns club ranking when favorite_club is set"""
        # First ensure user has favorite_club
        auth_session.put(f"{BASE_URL}/api/users/me", json={"favorite_club": "Manchester United"})
        
        response = auth_session.get(f"{BASE_URL}/api/users/my-rank")
        assert response.status_code == 200
        
        data = response.json()
        assert "club" in data, "Response missing 'club' rank when favorite_club is set"
        assert "rank" in data["club"], "Club rank missing 'rank' field"
        assert "total" in data["club"], "Club rank missing 'total' field"
        assert "name" in data["club"], "Club rank missing 'name' field"
        assert data["club"]["name"] == "Manchester United", f"Club name mismatch: {data['club']['name']}"
        
        print(f"✅ Club rank ({data['club']['name']}): #{data['club']['rank']} of {data['club']['total']}")
    
    def test_my_rank_returns_country_rank_when_set(self, auth_session):
        """Test that my-rank returns country ranking when country is set"""
        # First ensure user has country
        auth_session.put(f"{BASE_URL}/api/users/me", json={"country": "United Kingdom"})
        
        response = auth_session.get(f"{BASE_URL}/api/users/my-rank")
        assert response.status_code == 200
        
        data = response.json()
        assert "country" in data, "Response missing 'country' rank when country is set"
        assert "rank" in data["country"], "Country rank missing 'rank' field"
        assert "total" in data["country"], "Country rank missing 'total' field"
        assert "name" in data["country"], "Country rank missing 'name' field"
        
        print(f"✅ Country rank ({data['country']['name']}): #{data['country']['rank']} of {data['country']['total']}")
    
    def test_my_rank_returns_league_ranks(self, auth_session):
        """Test that my-rank returns league rankings"""
        response = auth_session.get(f"{BASE_URL}/api/users/my-rank")
        assert response.status_code == 200
        
        data = response.json()
        assert "leagues" in data, "Response missing 'leagues' field"
        assert isinstance(data["leagues"], list), "Leagues should be a list"
        
        # If user is in leagues, verify structure
        if len(data["leagues"]) > 0:
            league = data["leagues"][0]
            assert "league_id" in league, "League rank missing 'league_id'"
            assert "league_name" in league, "League rank missing 'league_name'"
            assert "rank" in league, "League rank missing 'rank'"
            assert "total" in league, "League rank missing 'total'"
            print(f"✅ League ranks: {len(data['leagues'])} leagues - e.g., {league['league_name']} #{league['rank']}/{league['total']}")
        else:
            print("✅ League ranks: User not in any leagues (empty list)")
    
    def test_my_rank_requires_auth(self):
        """Test that my-rank requires authentication"""
        fresh_session = requests.Session()
        response = fresh_session.get(f"{BASE_URL}/api/users/my-rank")
        
        assert response.status_code == 401, f"Expected 401 for unauthenticated my-rank, got {response.status_code}"
        print("✅ My rank correctly requires authentication")


# ==================== LEAGUE SYSTEM TESTS ====================

class TestLeagueSystem:
    """Test full league CRUD system"""
    
    def test_create_public_league(self, auth_session):
        """Test creating a public league"""
        league_name = f"TEST_Public_League_{uuid.uuid4().hex[:6]}"
        
        response = auth_session.post(f"{BASE_URL}/api/leagues", json={
            "name": league_name,
            "league_type": "public"
        })
        
        assert response.status_code == 200, f"Create league failed: {response.text}"
        data = response.json()
        
        assert "id" in data, "Response missing 'id'"
        assert "name" in data, "Response missing 'name'"
        assert data["name"] == league_name, f"Name mismatch: {data['name']}"
        assert data["league_type"] == "public", f"League type should be 'public', got: {data['league_type']}"
        assert "invite_code" in data, "Response missing 'invite_code'"
        assert "member_count" in data, "Response missing 'member_count'"
        assert data["member_count"] == 1, "Creator should be auto-joined (member_count=1)"
        
        print(f"✅ Public league created: {data['name']} (ID: {data['id']})")
        return data["id"]
    
    def test_create_private_league(self, auth_session):
        """Test creating a private league"""
        league_name = f"TEST_Private_League_{uuid.uuid4().hex[:6]}"
        
        response = auth_session.post(f"{BASE_URL}/api/leagues", json={
            "name": league_name,
            "league_type": "private"
        })
        
        assert response.status_code == 200, f"Create private league failed: {response.text}"
        data = response.json()
        
        assert data["league_type"] == "private", f"League type should be 'private', got: {data['league_type']}"
        assert "invite_code" in data and data["invite_code"], "Private league should have invite_code"
        
        print(f"✅ Private league created: {data['name']} with invite code: {data['invite_code']}")
        return data["id"], data["invite_code"]
    
    def test_list_leagues(self, auth_session):
        """Test listing leagues with membership status"""
        response = auth_session.get(f"{BASE_URL}/api/leagues")
        
        assert response.status_code == 200, f"List leagues failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Response should be a list"
        
        if len(data) > 0:
            league = data[0]
            assert "id" in league, "League missing 'id'"
            assert "name" in league, "League missing 'name'"
            assert "league_type" in league, "League missing 'league_type'"
            assert "member_count" in league, "League missing 'member_count'"
            assert "is_member" in league, "League missing 'is_member'"
            assert "is_creator" in league, "League missing 'is_creator'"
            
        print(f"✅ List leagues returns {len(data)} leagues")
    
    def test_list_public_leagues_only(self, auth_session):
        """Test filtering to public leagues only"""
        response = auth_session.get(f"{BASE_URL}/api/leagues?league_type=public")
        
        assert response.status_code == 200
        data = response.json()
        
        for league in data:
            assert league["league_type"] == "public", f"Expected public league, got {league['league_type']}"
        
        print(f"✅ Public leagues filter returns {len(data)} public leagues")
    
    def test_join_league(self, auth_session, secondary_auth_session):
        """Test joining a league by ID"""
        # Create a public league with primary user
        league_name = f"TEST_Joinable_League_{uuid.uuid4().hex[:6]}"
        create_resp = auth_session.post(f"{BASE_URL}/api/leagues", json={
            "name": league_name,
            "league_type": "public"
        })
        assert create_resp.status_code == 200
        league_id = create_resp.json()["id"]
        
        # Join with secondary user
        join_resp = secondary_auth_session.post(f"{BASE_URL}/api/leagues/{league_id}/join")
        assert join_resp.status_code == 200, f"Join league failed: {join_resp.text}"
        
        data = join_resp.json()
        assert "message" in data, "Response missing 'message'"
        
        print(f"✅ Secondary user joined league {league_id}")
    
    def test_join_league_by_invite_code(self, auth_session, secondary_auth_session):
        """Test joining a private league by invite code"""
        # Create a private league
        league_name = f"TEST_Private_Code_League_{uuid.uuid4().hex[:6]}"
        create_resp = auth_session.post(f"{BASE_URL}/api/leagues", json={
            "name": league_name,
            "league_type": "private"
        })
        assert create_resp.status_code == 200
        league_data = create_resp.json()
        invite_code = league_data["invite_code"]
        
        # Join with secondary user via code
        join_resp = secondary_auth_session.post(f"{BASE_URL}/api/leagues/join-code/{invite_code}")
        assert join_resp.status_code == 200, f"Join by code failed: {join_resp.text}"
        
        data = join_resp.json()
        assert "league_id" in data, "Response missing 'league_id'"
        assert "league_name" in data, "Response missing 'league_name'"
        assert data["league_name"] == league_name
        
        print(f"✅ Joined private league via code: {invite_code}")
    
    def test_join_league_already_member(self, auth_session):
        """Test that joining a league twice returns error"""
        # Create and try to join again (creator is auto-joined)
        league_name = f"TEST_Double_Join_{uuid.uuid4().hex[:6]}"
        create_resp = auth_session.post(f"{BASE_URL}/api/leagues", json={
            "name": league_name,
            "league_type": "public"
        })
        league_id = create_resp.json()["id"]
        
        # Try to join again
        join_resp = auth_session.post(f"{BASE_URL}/api/leagues/{league_id}/join")
        assert join_resp.status_code == 400, f"Expected 400 for double join, got {join_resp.status_code}"
        
        print("✅ Double join correctly rejected")
    
    def test_leave_league(self, auth_session, secondary_auth_session):
        """Test leaving a league"""
        # Create a league and have secondary user join
        league_name = f"TEST_Leave_League_{uuid.uuid4().hex[:6]}"
        create_resp = auth_session.post(f"{BASE_URL}/api/leagues", json={
            "name": league_name,
            "league_type": "public"
        })
        league_id = create_resp.json()["id"]
        
        # Secondary user joins
        secondary_auth_session.post(f"{BASE_URL}/api/leagues/{league_id}/join")
        
        # Secondary user leaves
        leave_resp = secondary_auth_session.post(f"{BASE_URL}/api/leagues/{league_id}/leave")
        assert leave_resp.status_code == 200, f"Leave league failed: {leave_resp.text}"
        
        data = leave_resp.json()
        assert "message" in data
        
        print(f"✅ User left league {league_id}")
    
    def test_leave_league_not_member(self, auth_session):
        """Test leaving a league user is not a member of"""
        # Create a league with secondary user (different session needed)
        # For simplicity, try to leave a non-existent league
        fake_league_id = str(uuid.uuid4())
        
        leave_resp = auth_session.post(f"{BASE_URL}/api/leagues/{fake_league_id}/leave")
        assert leave_resp.status_code == 404, f"Expected 404 for leaving non-member league, got {leave_resp.status_code}"
        
        print("✅ Leave non-member league correctly rejected")
    
    def test_get_league_details_with_leaderboard(self, auth_session):
        """Test getting league details with leaderboard"""
        # Create a league
        league_name = f"TEST_Leaderboard_League_{uuid.uuid4().hex[:6]}"
        create_resp = auth_session.post(f"{BASE_URL}/api/leagues", json={
            "name": league_name,
            "league_type": "public"
        })
        league_id = create_resp.json()["id"]
        
        # Get league details
        details_resp = auth_session.get(f"{BASE_URL}/api/leagues/{league_id}")
        assert details_resp.status_code == 200, f"Get league details failed: {details_resp.text}"
        
        data = details_resp.json()
        assert "id" in data, "Response missing 'id'"
        assert "name" in data, "Response missing 'name'"
        assert "league_type" in data, "Response missing 'league_type'"
        assert "invite_code" in data, "Response missing 'invite_code'"
        assert "member_count" in data, "Response missing 'member_count'"
        assert "leaderboard" in data, "Response missing 'leaderboard'"
        
        # Check leaderboard structure
        assert isinstance(data["leaderboard"], list), "Leaderboard should be a list"
        if len(data["leaderboard"]) > 0:
            member = data["leaderboard"][0]
            assert "rank" in member, "Leaderboard member missing 'rank'"
            assert "user_id" in member, "Leaderboard member missing 'user_id'"
            assert "username" in member, "Leaderboard member missing 'username'"
            assert "skill_rank" in member, "Leaderboard member missing 'skill_rank'"
            assert "is_current_user" in member, "Leaderboard member missing 'is_current_user'"
        
        print(f"✅ League details with leaderboard: {len(data['leaderboard'])} members")
    
    def test_get_nonexistent_league(self, auth_session):
        """Test getting a non-existent league returns 404"""
        fake_id = str(uuid.uuid4())
        response = auth_session.get(f"{BASE_URL}/api/leagues/{fake_id}")
        
        assert response.status_code == 404, f"Expected 404 for non-existent league, got {response.status_code}"
        print("✅ Non-existent league correctly returns 404")
    
    def test_join_invalid_invite_code(self, auth_session):
        """Test joining with invalid invite code returns 404"""
        response = auth_session.post(f"{BASE_URL}/api/leagues/join-code/INVALID1")
        
        assert response.status_code == 404, f"Expected 404 for invalid code, got {response.status_code}"
        print("✅ Invalid invite code correctly returns 404")


# ==================== INTEGRATION TESTS ====================

class TestIntegration:
    """Integration tests combining features"""
    
    def test_league_rank_appears_in_my_rank(self, auth_session):
        """Test that after joining a league, it appears in my-rank response"""
        # Create and verify league appears in my-rank
        league_name = f"TEST_MyRank_League_{uuid.uuid4().hex[:6]}"
        create_resp = auth_session.post(f"{BASE_URL}/api/leagues", json={
            "name": league_name,
            "league_type": "public"
        })
        assert create_resp.status_code == 200
        league_id = create_resp.json()["id"]
        
        # Check my-rank
        rank_resp = auth_session.get(f"{BASE_URL}/api/users/my-rank")
        assert rank_resp.status_code == 200
        
        data = rank_resp.json()
        league_ids = [l["league_id"] for l in data.get("leagues", [])]
        assert league_id in league_ids, f"Newly joined league {league_id} not found in my-rank leagues: {league_ids}"
        
        print(f"✅ Created league {league_id} appears in my-rank")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
