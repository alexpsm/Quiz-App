"""
Generate questions for ALL clubs in the dropdown menu.
All questions use category "Club" as a unified pool.
Each question is tagged with the specific club name for filtering in Club Challenge mode.
"""
import asyncio
import sys
sys.path.append('/app/backend')

from database import AsyncSessionLocal
from models import Question
from clubs_data import CLUBS_BY_LEAGUE, get_all_clubs, get_club_league
from sqlalchemy import text
import uuid
import random

# Comprehensive club data with details for question generation
CLUB_DETAILS = {
    # Premier League
    "Arsenal": {"nickname": "The Gunners", "colors": "Red and White", "stadium": "Emirates Stadium", "city": "London", "founded": 1886, "league": "Premier League"},
    "Aston Villa": {"nickname": "The Villans", "colors": "Claret and Blue", "stadium": "Villa Park", "city": "Birmingham", "founded": 1874, "league": "Premier League"},
    "AFC Bournemouth": {"nickname": "The Cherries", "colors": "Red and Black", "stadium": "Vitality Stadium", "city": "Bournemouth", "founded": 1899, "league": "Premier League"},
    "Brentford": {"nickname": "The Bees", "colors": "Red and White", "stadium": "Gtech Community Stadium", "city": "London", "founded": 1889, "league": "Premier League"},
    "Brighton & Hove Albion": {"nickname": "The Seagulls", "colors": "Blue and White", "stadium": "Amex Stadium", "city": "Brighton", "founded": 1901, "league": "Premier League"},
    "Chelsea": {"nickname": "The Blues", "colors": "Blue", "stadium": "Stamford Bridge", "city": "London", "founded": 1905, "league": "Premier League"},
    "Crystal Palace": {"nickname": "The Eagles", "colors": "Red and Blue", "stadium": "Selhurst Park", "city": "London", "founded": 1905, "league": "Premier League"},
    "Everton": {"nickname": "The Toffees", "colors": "Blue and White", "stadium": "Goodison Park", "city": "Liverpool", "founded": 1878, "league": "Premier League"},
    "Fulham": {"nickname": "The Cottagers", "colors": "White and Black", "stadium": "Craven Cottage", "city": "London", "founded": 1879, "league": "Premier League"},
    "Ipswich Town": {"nickname": "The Tractor Boys", "colors": "Blue and White", "stadium": "Portman Road", "city": "Ipswich", "founded": 1878, "league": "Premier League"},
    "Leicester City": {"nickname": "The Foxes", "colors": "Blue", "stadium": "King Power Stadium", "city": "Leicester", "founded": 1884, "league": "Premier League"},
    "Liverpool": {"nickname": "The Reds", "colors": "Red", "stadium": "Anfield", "city": "Liverpool", "founded": 1892, "league": "Premier League"},
    "Manchester City": {"nickname": "The Citizens", "colors": "Sky Blue", "stadium": "Etihad Stadium", "city": "Manchester", "founded": 1880, "league": "Premier League"},
    "Manchester United": {"nickname": "The Red Devils", "colors": "Red and White", "stadium": "Old Trafford", "city": "Manchester", "founded": 1878, "league": "Premier League"},
    "Newcastle United": {"nickname": "The Magpies", "colors": "Black and White", "stadium": "St James' Park", "city": "Newcastle", "founded": 1892, "league": "Premier League"},
    "Nottingham Forest": {"nickname": "The Reds", "colors": "Red and White", "stadium": "City Ground", "city": "Nottingham", "founded": 1865, "league": "Premier League"},
    "Southampton": {"nickname": "The Saints", "colors": "Red and White", "stadium": "St Mary's Stadium", "city": "Southampton", "founded": 1885, "league": "Premier League"},
    "Tottenham Hotspur": {"nickname": "Spurs", "colors": "White and Navy", "stadium": "Tottenham Hotspur Stadium", "city": "London", "founded": 1882, "league": "Premier League"},
    "West Ham United": {"nickname": "The Hammers", "colors": "Claret and Blue", "stadium": "London Stadium", "city": "London", "founded": 1895, "league": "Premier League"},
    "Wolverhampton Wanderers": {"nickname": "Wolves", "colors": "Gold and Black", "stadium": "Molineux Stadium", "city": "Wolverhampton", "founded": 1877, "league": "Premier League"},
    
    # Bundesliga
    "Bayern Munich": {"nickname": "Der FCB", "colors": "Red and White", "stadium": "Allianz Arena", "city": "Munich", "founded": 1900, "league": "Bundesliga"},
    "Borussia Dortmund": {"nickname": "BVB", "colors": "Yellow and Black", "stadium": "Signal Iduna Park", "city": "Dortmund", "founded": 1909, "league": "Bundesliga"},
    "Bayer Leverkusen": {"nickname": "Die Werkself", "colors": "Red and Black", "stadium": "BayArena", "city": "Leverkusen", "founded": 1904, "league": "Bundesliga"},
    "RB Leipzig": {"nickname": "Die Roten Bullen", "colors": "Red and White", "stadium": "Red Bull Arena", "city": "Leipzig", "founded": 2009, "league": "Bundesliga"},
    "VfB Stuttgart": {"nickname": "Die Schwaben", "colors": "White and Red", "stadium": "Mercedes-Benz Arena", "city": "Stuttgart", "founded": 1893, "league": "Bundesliga"},
    "Eintracht Frankfurt": {"nickname": "Die Adler", "colors": "Red, Black and White", "stadium": "Deutsche Bank Park", "city": "Frankfurt", "founded": 1899, "league": "Bundesliga"},
    "SC Freiburg": {"nickname": "Breisgau-Brasilianer", "colors": "Red and White", "stadium": "Europa-Park Stadion", "city": "Freiburg", "founded": 1904, "league": "Bundesliga"},
    "VfL Wolfsburg": {"nickname": "Die Wolfe", "colors": "Green and White", "stadium": "Volkswagen Arena", "city": "Wolfsburg", "founded": 1945, "league": "Bundesliga"},
    "TSG Hoffenheim": {"nickname": "Die Kraichgauer", "colors": "Blue and White", "stadium": "PreZero Arena", "city": "Sinsheim", "founded": 1899, "league": "Bundesliga"},
    "1. FC Union Berlin": {"nickname": "Die Eisernen", "colors": "Red and White", "stadium": "Stadion An der Alten Forsterei", "city": "Berlin", "founded": 1966, "league": "Bundesliga"},
    "Borussia Monchengladbach": {"nickname": "Die Fohlen", "colors": "White, Green and Black", "stadium": "Borussia-Park", "city": "Monchengladbach", "founded": 1900, "league": "Bundesliga"},
    "1. FSV Mainz 05": {"nickname": "Die Nullfunfer", "colors": "Red and White", "stadium": "Mewa Arena", "city": "Mainz", "founded": 1905, "league": "Bundesliga"},
    "SV Werder Bremen": {"nickname": "Die Werderaner", "colors": "Green and White", "stadium": "Weserstadion", "city": "Bremen", "founded": 1899, "league": "Bundesliga"},
    "FC Augsburg": {"nickname": "Die Fuggerstadter", "colors": "Red, Green and White", "stadium": "WWK Arena", "city": "Augsburg", "founded": 1907, "league": "Bundesliga"},
    "VfL Bochum": {"nickname": "Die Unabsteigbaren", "colors": "Blue and White", "stadium": "Vonovia Ruhrstadion", "city": "Bochum", "founded": 1848, "league": "Bundesliga"},
    "1. FC Heidenheim": {"nickname": "Die Brenz", "colors": "Red and Blue", "stadium": "Voith-Arena", "city": "Heidenheim", "founded": 1946, "league": "Bundesliga"},
    "FC St. Pauli": {"nickname": "Die Kiezkicker", "colors": "Brown and White", "stadium": "Millerntor-Stadion", "city": "Hamburg", "founded": 1910, "league": "Bundesliga"},
    "Holstein Kiel": {"nickname": "Die Storche", "colors": "Blue and White", "stadium": "Holstein-Stadion", "city": "Kiel", "founded": 1900, "league": "Bundesliga"},
    
    # Ligue 1
    "Paris Saint-Germain": {"nickname": "Les Parisiens", "colors": "Blue, Red and White", "stadium": "Parc des Princes", "city": "Paris", "founded": 1970, "league": "Ligue 1"},
    "AS Monaco": {"nickname": "Les Monegasques", "colors": "Red and White", "stadium": "Stade Louis II", "city": "Monaco", "founded": 1924, "league": "Ligue 1"},
    "Olympique de Marseille": {"nickname": "OM", "colors": "White and Blue", "stadium": "Stade Velodrome", "city": "Marseille", "founded": 1899, "league": "Ligue 1"},
    "LOSC Lille": {"nickname": "Les Dogues", "colors": "Red and White", "stadium": "Stade Pierre-Mauroy", "city": "Lille", "founded": 1944, "league": "Ligue 1"},
    "Olympique Lyonnais": {"nickname": "Les Gones", "colors": "White, Red and Blue", "stadium": "Groupama Stadium", "city": "Lyon", "founded": 1950, "league": "Ligue 1"},
    "RC Lens": {"nickname": "Les Sang et Or", "colors": "Red and Gold", "stadium": "Stade Bollaert-Delelis", "city": "Lens", "founded": 1906, "league": "Ligue 1"},
    "Stade Rennais": {"nickname": "Les Rouges et Noirs", "colors": "Red and Black", "stadium": "Roazhon Park", "city": "Rennes", "founded": 1901, "league": "Ligue 1"},
    "OGC Nice": {"nickname": "Les Aiglons", "colors": "Red and Black", "stadium": "Allianz Riviera", "city": "Nice", "founded": 1904, "league": "Ligue 1"},
    "Stade Brestois": {"nickname": "Les Pirates", "colors": "Red and White", "stadium": "Stade Francis-Le Ble", "city": "Brest", "founded": 1950, "league": "Ligue 1"},
    "RC Strasbourg": {"nickname": "Racing", "colors": "Blue and White", "stadium": "Stade de la Meinau", "city": "Strasbourg", "founded": 1906, "league": "Ligue 1"},
    "FC Nantes": {"nickname": "Les Canaris", "colors": "Yellow and Green", "stadium": "Stade de la Beaujoire", "city": "Nantes", "founded": 1943, "league": "Ligue 1"},
    "Toulouse FC": {"nickname": "Les Violets", "colors": "Violet and White", "stadium": "Stadium de Toulouse", "city": "Toulouse", "founded": 1970, "league": "Ligue 1"},
    "Montpellier HSC": {"nickname": "La Paillade", "colors": "Blue and Orange", "stadium": "Stade de la Mosson", "city": "Montpellier", "founded": 1974, "league": "Ligue 1"},
    "AJ Auxerre": {"nickname": "L'AJA", "colors": "White and Blue", "stadium": "Stade de l'Abbe-Deschamps", "city": "Auxerre", "founded": 1905, "league": "Ligue 1"},
    "Angers SCO": {"nickname": "Le SCO", "colors": "White and Black", "stadium": "Stade Raymond Kopa", "city": "Angers", "founded": 1919, "league": "Ligue 1"},
    "Le Havre AC": {"nickname": "Les Ciel et Marine", "colors": "Sky Blue and Navy", "stadium": "Stade Oceane", "city": "Le Havre", "founded": 1872, "league": "Ligue 1"},
    "AS Saint-Etienne": {"nickname": "Les Verts", "colors": "Green and White", "stadium": "Stade Geoffroy-Guichard", "city": "Saint-Etienne", "founded": 1919, "league": "Ligue 1"},
    "Stade de Reims": {"nickname": "Les Rouges et Blancs", "colors": "Red and White", "stadium": "Stade Auguste-Delaune", "city": "Reims", "founded": 1931, "league": "Ligue 1"},
    
    # Serie A
    "Inter Milan": {"nickname": "Nerazzurri", "colors": "Blue and Black", "stadium": "San Siro", "city": "Milan", "founded": 1908, "league": "Serie A"},
    "AC Milan": {"nickname": "Rossoneri", "colors": "Red and Black", "stadium": "San Siro", "city": "Milan", "founded": 1899, "league": "Serie A"},
    "Juventus": {"nickname": "La Vecchia Signora", "colors": "Black and White", "stadium": "Allianz Stadium", "city": "Turin", "founded": 1897, "league": "Serie A"},
    "SSC Napoli": {"nickname": "Gli Azzurri", "colors": "Blue and White", "stadium": "Diego Armando Maradona Stadium", "city": "Naples", "founded": 1926, "league": "Serie A"},
    "AS Roma": {"nickname": "I Giallorossi", "colors": "Maroon and Gold", "stadium": "Stadio Olimpico", "city": "Rome", "founded": 1927, "league": "Serie A"},
    "SS Lazio": {"nickname": "Le Aquile", "colors": "Sky Blue and White", "stadium": "Stadio Olimpico", "city": "Rome", "founded": 1900, "league": "Serie A"},
    "Atalanta": {"nickname": "La Dea", "colors": "Blue and Black", "stadium": "Gewiss Stadium", "city": "Bergamo", "founded": 1907, "league": "Serie A"},
    "ACF Fiorentina": {"nickname": "La Viola", "colors": "Purple and White", "stadium": "Stadio Artemio Franchi", "city": "Florence", "founded": 1926, "league": "Serie A"},
    "Bologna FC": {"nickname": "I Rossoblù", "colors": "Red and Blue", "stadium": "Stadio Renato Dall'Ara", "city": "Bologna", "founded": 1909, "league": "Serie A"},
    "Torino FC": {"nickname": "Il Toro", "colors": "Maroon", "stadium": "Stadio Olimpico Grande Torino", "city": "Turin", "founded": 1906, "league": "Serie A"},
    "Udinese": {"nickname": "I Friulani", "colors": "White and Black", "stadium": "Dacia Arena", "city": "Udine", "founded": 1896, "league": "Serie A"},
    "Genoa CFC": {"nickname": "Il Grifone", "colors": "Red and Blue", "stadium": "Stadio Luigi Ferraris", "city": "Genoa", "founded": 1893, "league": "Serie A"},
    "Cagliari": {"nickname": "I Rossoblù", "colors": "Red and Blue", "stadium": "Unipol Domus", "city": "Cagliari", "founded": 1920, "league": "Serie A"},
    "Empoli FC": {"nickname": "Gli Azzurri", "colors": "Blue and White", "stadium": "Stadio Carlo Castellani", "city": "Empoli", "founded": 1920, "league": "Serie A"},
    "US Lecce": {"nickname": "I Giallorossi", "colors": "Yellow and Red", "stadium": "Stadio Via del Mare", "city": "Lecce", "founded": 1908, "league": "Serie A"},
    "Parma Calcio": {"nickname": "I Crociati", "colors": "White and Blue", "stadium": "Stadio Ennio Tardini", "city": "Parma", "founded": 1913, "league": "Serie A"},
    "Hellas Verona": {"nickname": "I Gialloblu", "colors": "Yellow and Blue", "stadium": "Stadio Marcantonio Bentegodi", "city": "Verona", "founded": 1903, "league": "Serie A"},
    "Venezia FC": {"nickname": "I Lagunari", "colors": "Green, Orange and Black", "stadium": "Stadio Pier Luigi Penzo", "city": "Venice", "founded": 1907, "league": "Serie A"},
    "AC Monza": {"nickname": "I Biancorossi", "colors": "White and Red", "stadium": "U-Power Stadium", "city": "Monza", "founded": 1912, "league": "Serie A"},
    "Como 1907": {"nickname": "I Lariani", "colors": "Blue and White", "stadium": "Stadio Giuseppe Sinigaglia", "city": "Como", "founded": 1907, "league": "Serie A"},
    
    # La Liga
    "Real Madrid": {"nickname": "Los Blancos", "colors": "White", "stadium": "Santiago Bernabeu", "city": "Madrid", "founded": 1902, "league": "La Liga"},
    "FC Barcelona": {"nickname": "Blaugrana", "colors": "Blue and Red", "stadium": "Camp Nou", "city": "Barcelona", "founded": 1899, "league": "La Liga"},
    "Atletico Madrid": {"nickname": "Los Colchoneros", "colors": "Red and White", "stadium": "Civitas Metropolitano", "city": "Madrid", "founded": 1903, "league": "La Liga"},
    "Sevilla FC": {"nickname": "Los Nervionenses", "colors": "White and Red", "stadium": "Ramon Sanchez Pizjuan", "city": "Seville", "founded": 1890, "league": "La Liga"},
    "Real Sociedad": {"nickname": "Txuri-urdin", "colors": "Blue and White", "stadium": "Reale Arena", "city": "San Sebastian", "founded": 1909, "league": "La Liga"},
    "Real Betis": {"nickname": "Los Verdiblancos", "colors": "Green and White", "stadium": "Benito Villamarin", "city": "Seville", "founded": 1907, "league": "La Liga"},
    "Villarreal CF": {"nickname": "El Submarino Amarillo", "colors": "Yellow", "stadium": "Estadio de la Ceramica", "city": "Villarreal", "founded": 1923, "league": "La Liga"},
    "Athletic Bilbao": {"nickname": "Los Leones", "colors": "Red and White", "stadium": "San Mames", "city": "Bilbao", "founded": 1898, "league": "La Liga"},
    "Valencia CF": {"nickname": "Los Che", "colors": "White and Orange", "stadium": "Mestalla", "city": "Valencia", "founded": 1919, "league": "La Liga"},
    "CA Osasuna": {"nickname": "Los Rojillos", "colors": "Red and Navy", "stadium": "El Sadar", "city": "Pamplona", "founded": 1920, "league": "La Liga"},
    "RC Celta de Vigo": {"nickname": "Os Celestes", "colors": "Sky Blue and White", "stadium": "Abanca-Balaidos", "city": "Vigo", "founded": 1923, "league": "La Liga"},
    "Girona FC": {"nickname": "Els Gironins", "colors": "Red and White", "stadium": "Montilivi", "city": "Girona", "founded": 1930, "league": "La Liga"},
    "RCD Mallorca": {"nickname": "Los Bermellones", "colors": "Red and Black", "stadium": "Son Moix", "city": "Palma", "founded": 1916, "league": "La Liga"},
    "Getafe CF": {"nickname": "Azulones", "colors": "Blue", "stadium": "Coliseum Alfonso Perez", "city": "Getafe", "founded": 1983, "league": "La Liga"},
    "Deportivo Alaves": {"nickname": "El Glorioso", "colors": "Blue and White", "stadium": "Mendizorrotza", "city": "Vitoria-Gasteiz", "founded": 1921, "league": "La Liga"},
    "UD Las Palmas": {"nickname": "La Unión", "colors": "Yellow", "stadium": "Gran Canaria Stadium", "city": "Las Palmas", "founded": 1949, "league": "La Liga"},
    "Rayo Vallecano": {"nickname": "Los Franjirrojos", "colors": "White with Red Stripe", "stadium": "Estadio de Vallecas", "city": "Madrid", "founded": 1924, "league": "La Liga"},
    "RCD Espanyol": {"nickname": "Los Periquitos", "colors": "Blue and White", "stadium": "RCDE Stadium", "city": "Barcelona", "founded": 1900, "league": "La Liga"},
    "Real Valladolid": {"nickname": "Pucela", "colors": "Purple and White", "stadium": "Estadio Jose Zorrilla", "city": "Valladolid", "founded": 1928, "league": "La Liga"},
    "CD Leganes": {"nickname": "Los Pepineros", "colors": "Blue and White", "stadium": "Estadio Municipal de Butarque", "city": "Leganes", "founded": 1928, "league": "La Liga"},
}

def get_other_clubs(exclude_club, same_league_only=False, count=3):
    """Get random clubs excluding the specified one"""
    if same_league_only and exclude_club in CLUB_DETAILS:
        league = CLUB_DETAILS[exclude_club]['league']
        other_clubs = [c for c in CLUB_DETAILS.keys() if c != exclude_club and CLUB_DETAILS.get(c, {}).get('league') == league]
    else:
        other_clubs = [c for c in CLUB_DETAILS.keys() if c != exclude_club]
    return random.sample(other_clubs, min(count, len(other_clubs)))

def generate_questions_for_club(club_name, club_data):
    """Generate multiple questions for a single club"""
    questions = []
    other_clubs = get_other_clubs(club_name)
    league = club_data.get('league', 'Unknown')
    
    # 1. Nickname question
    wrong_nicknames = [CLUB_DETAILS.get(c, {}).get('nickname', 'Unknown') for c in other_clubs if CLUB_DETAILS.get(c, {}).get('nickname')]
    if len(wrong_nicknames) >= 3:
        questions.append({
            "text": f"What is the nickname of {club_name}?",
            "options": [club_data['nickname']] + wrong_nicknames[:3],
            "correct": "A",
            "club": club_name,
            "difficulty": 1
        })
    
    # 2. Stadium question
    wrong_stadiums = [CLUB_DETAILS.get(c, {}).get('stadium', 'Unknown') for c in other_clubs if CLUB_DETAILS.get(c, {}).get('stadium')]
    if len(wrong_stadiums) >= 3:
        questions.append({
            "text": f"What is the home stadium of {club_name}?",
            "options": [club_data['stadium']] + wrong_stadiums[:3],
            "correct": "A",
            "club": club_name,
            "difficulty": 1
        })
    
    # 3. City question
    wrong_cities = [CLUB_DETAILS.get(c, {}).get('city', 'Unknown') for c in other_clubs if CLUB_DETAILS.get(c, {}).get('city')]
    if len(wrong_cities) >= 3:
        questions.append({
            "text": f"In which city is {club_name} based?",
            "options": [club_data['city']] + wrong_cities[:3],
            "correct": "A",
            "club": club_name,
            "difficulty": 1
        })
    
    # 4. Founded year question
    founded = club_data.get('founded', 1900)
    wrong_years = [str(founded + 10), str(founded - 8), str(founded + 15)]
    questions.append({
        "text": f"In which year was {club_name} founded?",
        "options": [str(founded)] + wrong_years,
        "correct": "A",
        "club": club_name,
        "difficulty": 2
    })
    
    # 5. Colors question
    wrong_colors = [CLUB_DETAILS.get(c, {}).get('colors', 'Unknown') for c in other_clubs if CLUB_DETAILS.get(c, {}).get('colors')]
    if len(wrong_colors) >= 3:
        questions.append({
            "text": f"What are the primary colors of {club_name}?",
            "options": [club_data['colors']] + wrong_colors[:3],
            "correct": "A",
            "club": club_name,
            "difficulty": 1
        })
    
    # 6. League question
    other_leagues = ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"]
    wrong_leagues = [l for l in other_leagues if l != league][:3]
    if len(wrong_leagues) >= 3:
        questions.append({
            "text": f"Which league does {club_name} compete in?",
            "options": [league] + wrong_leagues,
            "correct": "A",
            "club": club_name,
            "difficulty": 1
        })
    
    # 7. Reverse nickname question (which club is known as...)
    questions.append({
        "text": f"Which club is known as '{club_data['nickname']}'?",
        "options": [club_name] + other_clubs[:3],
        "correct": "A",
        "club": club_name,
        "difficulty": 2
    })
    
    # 8. Reverse stadium question (which club plays at...)
    questions.append({
        "text": f"Which club plays their home games at {club_data['stadium']}?",
        "options": [club_name] + other_clubs[:3],
        "correct": "A",
        "club": club_name,
        "difficulty": 2
    })
    
    # 9. Reverse city question (which club is based in...)
    same_league_clubs = get_other_clubs(club_name, same_league_only=True, count=3)
    if len(same_league_clubs) >= 3:
        questions.append({
            "text": f"Which {league} club is based in {club_data['city']}?",
            "options": [club_name] + same_league_clubs[:3],
            "correct": "A",
            "club": club_name,
            "difficulty": 2
        })
    
    return questions

async def generate_and_insert_all_club_questions():
    """Generate questions for all 96 clubs and insert into database"""
    
    # First, delete old club-specific categories to avoid duplicates
    async with AsyncSessionLocal() as session:
        # Delete old club-specific questions (those with "-" in category that aren't generic)
        await session.execute(text("""
            DELETE FROM questions 
            WHERE category LIKE '%-%' 
            AND category NOT LIKE 'Club -%'
            AND category NOT LIKE 'Players -%'
        """))
        await session.commit()
        print("Cleaned up old club-specific questions")
    
    all_questions = []
    
    # Generate questions for all clubs in CLUB_DETAILS
    for club_name, club_data in CLUB_DETAILS.items():
        club_questions = generate_questions_for_club(club_name, club_data)
        all_questions.extend(club_questions)
        print(f"Generated {len(club_questions)} questions for {club_name}")
    
    print(f"\nTotal questions generated: {len(all_questions)}")
    
    # Convert to Question objects with "Club" category
    questions_to_insert = []
    for q in all_questions:
        # Shuffle options but track correct answer
        options = q['options'][:]
        correct_answer = options[0]  # First option is always correct
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        correct_letter = ['A', 'B', 'C', 'D'][correct_index]
        
        questions_to_insert.append(Question(
            id=str(uuid.uuid4()),
            question_text=q['text'],
            option_a=options[0],
            option_b=options[1],
            option_c=options[2],
            option_d=options[3],
            correct_option=correct_letter,
            category="Club",  # Single unified category
            difficulty=q['difficulty'],
            # Store club name in question text for filtering
        ))
    
    print(f"Inserting {len(questions_to_insert)} questions with 'Club' category...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Insert in batches
            batch_size = 100
            for i in range(0, len(questions_to_insert), batch_size):
                batch = questions_to_insert[i:i+batch_size]
                session.add_all(batch)
                await session.commit()
                print(f"Inserted batch {i//batch_size + 1}/{(len(questions_to_insert) + batch_size - 1)//batch_size}")
            
            print(f"\n✓ Successfully inserted {len(questions_to_insert)} club questions!")
            
            # Verify count
            result = await session.execute(text("SELECT COUNT(*) FROM questions WHERE category = 'Club'"))
            count = result.scalar()
            print(f"Total 'Club' category questions in database: {count}")
            
        except Exception as e:
            print(f"Error: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(generate_and_insert_all_club_questions())
