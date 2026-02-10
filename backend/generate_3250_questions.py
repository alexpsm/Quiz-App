"""Generate 3250+ club questions covering all 96 clubs"""
import asyncio
import sys
import random
import uuid
sys.path.append('/app/backend')

from database import AsyncSessionLocal
from models import Question
from sqlalchemy import text
from comprehensive_club_data import COMPREHENSIVE_CLUB_DATA

def get_random_clubs(exclude, count=3):
    clubs = [c for c in COMPREHENSIVE_CLUB_DATA.keys() if c != exclude]
    return random.sample(clubs, min(count, len(clubs)))

def get_random_values(data_list, exclude_val, count=3):
    filtered = [v for v in data_list if v != exclude_val]
    return random.sample(filtered, min(count, len(filtered))) if filtered else []

def generate_all_questions():
    questions = []
    all_clubs = list(COMPREHENSIVE_CLUB_DATA.keys())
    
    # Collect all values for wrong answers
    all_nicknames = [d.get('nickname','') for d in COMPREHENSIVE_CLUB_DATA.values() if d.get('nickname')]
    all_stadiums = [d.get('stadium','') for d in COMPREHENSIVE_CLUB_DATA.values() if d.get('stadium')]
    all_cities = [d.get('city','') for d in COMPREHENSIVE_CLUB_DATA.values() if d.get('city')]
    all_colors = [d.get('colors','') for d in COMPREHENSIVE_CLUB_DATA.values() if d.get('colors')]
    all_players = []
    all_managers = []
    for d in COMPREHENSIVE_CLUB_DATA.values():
        all_players.extend(d.get('legendary_players', []))
        all_players.extend(d.get('current_players', []))
        all_managers.extend(d.get('managers', []))
    all_players = list(set(all_players))
    all_managers = list(set(all_managers))
    
    for club, data in COMPREHENSIVE_CLUB_DATA.items():
        other_clubs = get_random_clubs(club)
        league = data.get('league', 'Unknown')
        
        # 1. Nickname
        if data.get('nickname'):
            wrong = get_random_values(all_nicknames, data['nickname'])
            if len(wrong) >= 3:
                questions.append({"text": f"What is the nickname of {club}?", "options": [data['nickname']] + wrong[:3], "club": club, "diff": 1})
                questions.append({"text": f"Which club is known as '{data['nickname']}'?", "options": [club] + other_clubs, "club": club, "diff": 2})
        
        # 2. Stadium
        if data.get('stadium'):
            wrong = get_random_values(all_stadiums, data['stadium'])
            if len(wrong) >= 3:
                questions.append({"text": f"What is the home stadium of {club}?", "options": [data['stadium']] + wrong[:3], "club": club, "diff": 1})
                questions.append({"text": f"Which club plays at {data['stadium']}?", "options": [club] + other_clubs, "club": club, "diff": 2})
        
        # 3. City
        if data.get('city'):
            wrong = get_random_values(all_cities, data['city'])
            if len(wrong) >= 3:
                questions.append({"text": f"In which city is {club} based?", "options": [data['city']] + wrong[:3], "club": club, "diff": 1})
                questions.append({"text": f"Which club is based in {data['city']}?", "options": [club] + other_clubs, "club": club, "diff": 2})
        
        # 4. Founded
        if data.get('founded'):
            yr = data['founded']
            questions.append({"text": f"When was {club} founded?", "options": [str(yr), str(yr+12), str(yr-8), str(yr+20)], "club": club, "diff": 2})
        
        # 5. Colors
        if data.get('colors'):
            wrong = get_random_values(all_colors, data['colors'])
            if len(wrong) >= 3:
                questions.append({"text": f"What are the colors of {club}?", "options": [data['colors']] + wrong[:3], "club": club, "diff": 1})
        
        # 6. League
        leagues = ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"]
        wrong_leagues = [l for l in leagues if l != league][:3]
        if len(wrong_leagues) >= 3:
            questions.append({"text": f"Which league does {club} play in?", "options": [league] + wrong_leagues, "club": club, "diff": 1})
        
        # 7. Country
        if data.get('country'):
            countries = ["England", "Spain", "Germany", "Italy", "France"]
            wrong_countries = [c for c in countries if c != data['country']][:3]
            questions.append({"text": f"In which country is {club} located?", "options": [data['country']] + wrong_countries, "club": club, "diff": 1})
        
        # 8-12. Legendary Players (5 questions per club)
        legends = data.get('legendary_players', [])
        for player in legends[:5]:
            wrong_players = get_random_values(all_players, player)
            if len(wrong_players) >= 3:
                questions.append({"text": f"Which club did {player} become a legend at?", "options": [club] + other_clubs, "club": club, "diff": 2})
                questions.append({"text": f"Who is a legendary player for {club}?", "options": [player] + wrong_players[:3], "club": club, "diff": 2})
        
        # 13-17. Current Players (5 questions per club)
        current = data.get('current_players', [])
        for player in current[:5]:
            wrong_players = get_random_values(all_players, player)
            if len(wrong_players) >= 3:
                questions.append({"text": f"Which club does {player} currently play for?", "options": [club] + other_clubs, "club": club, "diff": 1})
                questions.append({"text": f"Who is a current player at {club}?", "options": [player] + wrong_players[:3], "club": club, "diff": 1})
        
        # 18-20. Managers (3 questions per club)
        managers = data.get('managers', [])
        for manager in managers[:3]:
            wrong_mgrs = get_random_values(all_managers, manager)
            if len(wrong_mgrs) >= 3:
                questions.append({"text": f"Which club did {manager} manage?", "options": [club] + other_clubs, "club": club, "diff": 2})
                questions.append({"text": f"Who has managed {club}?", "options": [manager] + wrong_mgrs[:3], "club": club, "diff": 2})
        
        # 21. Rivals
        rivals = data.get('rivals', [])
        if rivals:
            non_rivals = [c for c in all_clubs if c != club and c not in rivals][:3]
            questions.append({"text": f"Who is {club}'s main rival?", "options": [rivals[0]] + non_rivals, "club": club, "diff": 2})
        
        # 22. Derby name
        if data.get('derby_name') and data['derby_name'] != 'None Traditional':
            questions.append({"text": f"What is the name of {club}'s local derby?", "options": [data['derby_name'], "City Derby", "Regional Derby", "Local Classic"], "club": club, "diff": 3})
        
        # 23. Top scorer
        if data.get('top_scorer'):
            wrong = get_random_values(all_players, data['top_scorer'])
            if len(wrong) >= 3:
                questions.append({"text": f"Who is {club}'s all-time top scorer?", "options": [data['top_scorer']] + wrong[:3], "club": club, "diff": 3})
        
        # 24. Top scorer goals
        if data.get('top_scorer_goals'):
            g = data['top_scorer_goals']
            questions.append({"text": f"How many goals did {club}'s top scorer score?", "options": [str(g), str(g+50), str(g-30), str(g+100)], "club": club, "diff": 3})
        
        # 25. Record signing
        if data.get('record_signing'):
            wrong = get_random_values(all_players, data['record_signing'])
            if len(wrong) >= 3:
                questions.append({"text": f"Who is {club}'s record signing?", "options": [data['record_signing']] + wrong[:3], "club": club, "diff": 3})
        
        # 26. Trophies - League titles
        trophies = data.get('trophies', {})
        if trophies.get('league_titles', 0) > 0:
            lt = trophies['league_titles']
            questions.append({"text": f"How many league titles has {club} won?", "options": [str(lt), str(lt+3), str(lt-2), str(lt+7)], "club": club, "diff": 3})
        
        # 27. European trophies
        if trophies.get('european_trophies', 0) > 0:
            et = trophies['european_trophies']
            questions.append({"text": f"How many European trophies has {club} won?", "options": [str(et), str(et+2), str(et-1) if et > 1 else "0", str(et+4)], "club": club, "diff": 3})
        
        # 28-30. Kit and sponsors
        if data.get('kit_manufacturer'):
            kits = ["Adidas", "Nike", "Puma", "Umbro", "New Balance", "Joma", "Hummel", "Castore"]
            wrong_kits = [k for k in kits if k != data['kit_manufacturer']][:3]
            questions.append({"text": f"Who manufactures {club}'s kit?", "options": [data['kit_manufacturer']] + wrong_kits, "club": club, "diff": 2})
        
        if data.get('shirt_sponsor'):
            questions.append({"text": f"Which club is sponsored by {data['shirt_sponsor']}?", "options": [club] + other_clubs, "club": club, "diff": 3})
        
        # 31. Captain
        if data.get('captain'):
            wrong = get_random_values(all_players, data['captain'])
            if len(wrong) >= 3:
                questions.append({"text": f"Who is the captain of {club}?", "options": [data['captain']] + wrong[:3], "club": club, "diff": 2})
        
        # 32-34. Historical facts
        notable = data.get('notable_seasons', [])
        for season in notable[:2]:
            questions.append({"text": f"Which club achieved: {season}?", "options": [club] + other_clubs, "club": club, "diff": 3})
    
    return questions

async def insert_questions():
    # Clear old Club questions
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM questions WHERE category = 'Club'"))
        await session.commit()
        print("Cleared old Club questions")
    
    all_q = generate_all_questions()
    print(f"Generated {len(all_q)} questions")
    
    to_insert = []
    for q in all_q:
        opts = q['options'][:]
        correct = opts[0]
        random.shuffle(opts)
        correct_idx = opts.index(correct)
        correct_letter = ['A','B','C','D'][correct_idx]
        
        to_insert.append(Question(
            id=str(uuid.uuid4()),
            question_text=q['text'],
            option_a=opts[0],
            option_b=opts[1],
            option_c=opts[2],
            option_d=opts[3],
            correct_option=correct_letter,
            category="Club",
            difficulty=q['diff']
        ))
    
    async with AsyncSessionLocal() as session:
        batch = 200
        for i in range(0, len(to_insert), batch):
            session.add_all(to_insert[i:i+batch])
            await session.commit()
            print(f"Inserted {min(i+batch, len(to_insert))}/{len(to_insert)}")
        
        result = await session.execute(text("SELECT COUNT(*) FROM questions WHERE category = 'Club'"))
        print(f"\n✓ Total Club questions: {result.scalar()}")

if __name__ == "__main__":
    asyncio.run(insert_questions())
