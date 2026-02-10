"""
Generate club-specific questions for each team in the database.
Categories will be like "Manchester United-History", "Bayern Munich-Players", etc.
"""
import asyncio
import sys
sys.path.append('/app/backend')

from database import AsyncSessionLocal
from models import Question
from clubs_data import CLUBS_BY_LEAGUE
import uuid
import random

# Club-specific historical data (major clubs with rich history)
CLUB_HISTORY = {
    # Premier League
    "Arsenal": {
        "trophies": {"league": 13, "fa_cup": 14, "champions_league": 0},
        "legends": ["Thierry Henry", "Dennis Bergkamp", "Patrick Vieira", "Tony Adams"],
        "managers": ["Arsene Wenger", "Mikel Arteta", "George Graham"],
        "facts": ["Unbeaten 2003-04 season (Invincibles)", "Record FA Cup wins", "Founded 1886 in Woolwich"],
        "rivals": ["Tottenham Hotspur", "Chelsea", "Manchester United"],
        "founded": 1886,
        "stadium": "Emirates Stadium",
        "capacity": 60704,
        "nickname": "The Gunners"
    },
    "Manchester United": {
        "trophies": {"league": 20, "fa_cup": 12, "champions_league": 3},
        "legends": ["George Best", "Bobby Charlton", "Eric Cantona", "Ryan Giggs", "Wayne Rooney"],
        "managers": ["Sir Alex Ferguson", "Matt Busby", "Jose Mourinho"],
        "facts": ["Most league titles in England", "Treble winners 1999", "Munich air disaster 1958"],
        "rivals": ["Liverpool", "Manchester City", "Leeds United"],
        "founded": 1878,
        "stadium": "Old Trafford",
        "capacity": 74879,
        "nickname": "The Red Devils"
    },
    "Liverpool": {
        "trophies": {"league": 19, "fa_cup": 8, "champions_league": 6},
        "legends": ["Steven Gerrard", "Kenny Dalglish", "Ian Rush", "Mohamed Salah"],
        "managers": ["Bill Shankly", "Bob Paisley", "Jurgen Klopp"],
        "facts": ["Istanbul miracle 2005", "You'll Never Walk Alone", "Six European Cups"],
        "rivals": ["Manchester United", "Everton", "Manchester City"],
        "founded": 1892,
        "stadium": "Anfield",
        "capacity": 61276,
        "nickname": "The Reds"
    },
    "Manchester City": {
        "trophies": {"league": 9, "fa_cup": 7, "champions_league": 1},
        "legends": ["Sergio Aguero", "Vincent Kompany", "David Silva", "Kevin De Bruyne"],
        "managers": ["Pep Guardiola", "Roberto Mancini", "Manuel Pellegrini"],
        "facts": ["Aguero 93:20 moment", "Treble winners 2023", "Most consecutive league wins"],
        "rivals": ["Manchester United", "Liverpool", "Chelsea"],
        "founded": 1880,
        "stadium": "Etihad Stadium",
        "capacity": 55097,
        "nickname": "The Citizens"
    },
    "Chelsea": {
        "trophies": {"league": 6, "fa_cup": 8, "champions_league": 2},
        "legends": ["Frank Lampard", "John Terry", "Didier Drogba", "Gianfranco Zola"],
        "managers": ["Jose Mourinho", "Carlo Ancelotti", "Thomas Tuchel"],
        "facts": ["First Champions League 2012", "Roman Abramovich era", "Most consecutive clean sheets"],
        "rivals": ["Arsenal", "Tottenham Hotspur", "Manchester United"],
        "founded": 1905,
        "stadium": "Stamford Bridge",
        "capacity": 40341,
        "nickname": "The Blues"
    },
    "Tottenham Hotspur": {
        "trophies": {"league": 2, "fa_cup": 8, "champions_league": 0},
        "legends": ["Harry Kane", "Jimmy Greaves", "Glenn Hoddle", "Ledley King"],
        "managers": ["Bill Nicholson", "Mauricio Pochettino", "Antonio Conte"],
        "facts": ["First British club to win European trophy", "1961 Double winners", "New stadium 2019"],
        "rivals": ["Arsenal", "Chelsea", "West Ham United"],
        "founded": 1882,
        "stadium": "Tottenham Hotspur Stadium",
        "capacity": 62850,
        "nickname": "Spurs"
    },
    
    # La Liga
    "Real Madrid": {
        "trophies": {"league": 36, "copa_del_rey": 20, "champions_league": 15},
        "legends": ["Cristiano Ronaldo", "Raul", "Alfredo Di Stefano", "Zinedine Zidane"],
        "managers": ["Zinedine Zidane", "Carlo Ancelotti", "Miguel Munoz"],
        "facts": ["Most Champions League titles (15)", "Galacticos era", "10 consecutive La Liga titles"],
        "rivals": ["FC Barcelona", "Atletico Madrid", "Sevilla FC"],
        "founded": 1902,
        "stadium": "Santiago Bernabeu",
        "capacity": 83000,
        "nickname": "Los Blancos"
    },
    "FC Barcelona": {
        "trophies": {"league": 27, "copa_del_rey": 31, "champions_league": 5},
        "legends": ["Lionel Messi", "Johan Cruyff", "Xavi", "Andres Iniesta"],
        "managers": ["Johan Cruyff", "Pep Guardiola", "Frank Rijkaard"],
        "facts": ["La Masia academy", "Tiki-taka style", "Sextuple 2009"],
        "rivals": ["Real Madrid", "Espanyol", "Atletico Madrid"],
        "founded": 1899,
        "stadium": "Camp Nou",
        "capacity": 99354,
        "nickname": "Blaugrana"
    },
    "Atletico Madrid": {
        "trophies": {"league": 11, "copa_del_rey": 10, "champions_league": 0},
        "legends": ["Fernando Torres", "Diego Forlan", "Antoine Griezmann", "Diego Costa"],
        "managers": ["Diego Simeone", "Luis Aragones", "Radomir Antic"],
        "facts": ["La Liga 2014 title", "Two Champions League finals", "Famous defense under Simeone"],
        "rivals": ["Real Madrid", "FC Barcelona", "Sevilla FC"],
        "founded": 1903,
        "stadium": "Wanda Metropolitano",
        "capacity": 68456,
        "nickname": "Los Colchoneros"
    },
    
    # Bundesliga
    "Bayern Munich": {
        "trophies": {"league": 33, "dfb_pokal": 20, "champions_league": 6},
        "legends": ["Franz Beckenbauer", "Gerd Muller", "Oliver Kahn", "Robert Lewandowski"],
        "managers": ["Pep Guardiola", "Jupp Heynckes", "Hansi Flick"],
        "facts": ["Most Bundesliga titles", "Treble 2013 and 2020", "Bayern Tax transfers"],
        "rivals": ["Borussia Dortmund", "RB Leipzig", "1860 Munich"],
        "founded": 1900,
        "stadium": "Allianz Arena",
        "capacity": 75024,
        "nickname": "Der FCB"
    },
    "Borussia Dortmund": {
        "trophies": {"league": 8, "dfb_pokal": 5, "champions_league": 1},
        "legends": ["Marco Reus", "Michael Zorc", "Jurgen Kohler", "Lars Ricken"],
        "managers": ["Jurgen Klopp", "Thomas Tuchel", "Ottmar Hitzfeld"],
        "facts": ["Yellow Wall (Gelbe Wand)", "Champions League 1997", "Famous youth development"],
        "rivals": ["Bayern Munich", "Schalke 04", "Bayer Leverkusen"],
        "founded": 1909,
        "stadium": "Signal Iduna Park",
        "capacity": 81365,
        "nickname": "BVB"
    },
    
    # Serie A
    "Juventus": {
        "trophies": {"league": 36, "coppa_italia": 14, "champions_league": 2},
        "legends": ["Alessandro Del Piero", "Gianluigi Buffon", "Michel Platini", "Roberto Baggio"],
        "managers": ["Marcello Lippi", "Antonio Conte", "Massimiliano Allegri"],
        "facts": ["Most Serie A titles", "9 consecutive league titles", "Calciopoli scandal"],
        "rivals": ["Inter Milan", "AC Milan", "Torino FC"],
        "founded": 1897,
        "stadium": "Allianz Stadium",
        "capacity": 41507,
        "nickname": "La Vecchia Signora"
    },
    "AC Milan": {
        "trophies": {"league": 19, "coppa_italia": 5, "champions_league": 7},
        "legends": ["Paolo Maldini", "Franco Baresi", "Kaka", "Marco van Basten"],
        "managers": ["Arrigo Sacchi", "Carlo Ancelotti", "Fabio Capello"],
        "facts": ["7 Champions League titles", "Legendary defense", "San Siro shared with Inter"],
        "rivals": ["Inter Milan", "Juventus", "Napoli"],
        "founded": 1899,
        "stadium": "San Siro",
        "capacity": 75923,
        "nickname": "Rossoneri"
    },
    "Inter Milan": {
        "trophies": {"league": 20, "coppa_italia": 9, "champions_league": 3},
        "legends": ["Javier Zanetti", "Ronaldo", "Giuseppe Meazza", "Lothar Matthaus"],
        "managers": ["Jose Mourinho", "Helenio Herrera", "Simone Inzaghi"],
        "facts": ["Treble 2010 under Mourinho", "Derby della Madonnina", "Grande Inter era"],
        "rivals": ["AC Milan", "Juventus", "Roma"],
        "founded": 1908,
        "stadium": "San Siro",
        "capacity": 75923,
        "nickname": "Nerazzurri"
    },
    "SSC Napoli": {
        "trophies": {"league": 3, "coppa_italia": 6, "champions_league": 0},
        "legends": ["Diego Maradona", "Dries Mertens", "Lorenzo Insigne", "Ciro Ferrara"],
        "managers": ["Luciano Spalletti", "Maurizio Sarri", "Rafa Benitez"],
        "facts": ["Maradona era 1984-1991", "Serie A 2023", "Diego Armando Maradona Stadium"],
        "rivals": ["AS Roma", "Juventus", "AC Milan"],
        "founded": 1926,
        "stadium": "Diego Armando Maradona Stadium",
        "capacity": 54726,
        "nickname": "I Partenopei"
    },
    
    # Ligue 1
    "Paris Saint-Germain": {
        "trophies": {"league": 11, "coupe_de_france": 14, "champions_league": 0},
        "legends": ["Zlatan Ibrahimovic", "Ronaldinho", "David Beckham", "Kylian Mbappe"],
        "managers": ["Carlo Ancelotti", "Laurent Blanc", "Mauricio Pochettino"],
        "facts": ["QSI takeover 2011", "Neymar record transfer", "Ligue 1 dominance"],
        "rivals": ["Olympique de Marseille", "AS Monaco", "Olympique Lyonnais"],
        "founded": 1970,
        "stadium": "Parc des Princes",
        "capacity": 47929,
        "nickname": "Les Parisiens"
    },
    "Olympique de Marseille": {
        "trophies": {"league": 10, "coupe_de_france": 10, "champions_league": 1},
        "legends": ["Didier Deschamps", "Jean-Pierre Papin", "Chris Waddle", "Rudi Voller"],
        "managers": ["Franz Beckenbauer", "Marcelo Bielsa", "Jorge Sampaoli"],
        "facts": ["Only French Champions League winner", "Le Classique rivalry", "Velodrome atmosphere"],
        "rivals": ["Paris Saint-Germain", "Olympique Lyonnais", "AS Saint-Etienne"],
        "founded": 1899,
        "stadium": "Stade Velodrome",
        "capacity": 67394,
        "nickname": "OM"
    }
}

def generate_club_questions():
    """Generate club-specific questions"""
    questions = []
    
    for club_name, data in CLUB_HISTORY.items():
        # Determine category prefix
        category_prefix = club_name
        
        # === HISTORY QUESTIONS ===
        
        # 1. Founded year
        wrong_years = [data['founded'] + 12, data['founded'] - 8, data['founded'] + 20]
        questions.append({
            "text": f"When was {club_name} founded?",
            "options": [str(data['founded']), str(wrong_years[0]), str(wrong_years[1]), str(wrong_years[2])],
            "correct": "A",
            "category": f"{category_prefix}-History",
            "difficulty": 2
        })
        
        # 2. Stadium name
        other_clubs = [c for c in CLUB_HISTORY.keys() if c != club_name]
        wrong_stadiums = random.sample([CLUB_HISTORY[c]['stadium'] for c in other_clubs], 3)
        questions.append({
            "text": f"What is the home stadium of {club_name}?",
            "options": [data['stadium'], wrong_stadiums[0], wrong_stadiums[1], wrong_stadiums[2]],
            "correct": "A",
            "category": f"{category_prefix}-History",
            "difficulty": 1
        })
        
        # 3. Nickname
        wrong_nicknames = random.sample([CLUB_HISTORY[c]['nickname'] for c in other_clubs], 3)
        questions.append({
            "text": f"What is the nickname of {club_name}?",
            "options": [data['nickname'], wrong_nicknames[0], wrong_nicknames[1], wrong_nicknames[2]],
            "correct": "A",
            "category": f"{category_prefix}-History",
            "difficulty": 1
        })
        
        # 4. Stadium capacity
        capacity = data['capacity']
        wrong_capacities = [capacity + 15000, capacity - 10000, capacity + 8000]
        questions.append({
            "text": f"What is the approximate capacity of {data['stadium']}?",
            "options": [f"{capacity:,}", f"{wrong_capacities[0]:,}", f"{wrong_capacities[1]:,}", f"{wrong_capacities[2]:,}"],
            "correct": "A",
            "category": f"{category_prefix}-History",
            "difficulty": 2
        })
        
        # 5. Main rival
        rivals = data.get('rivals', [])
        if rivals:
            other_clubs_list = [c for c in CLUB_HISTORY.keys() if c != club_name and c not in rivals]
            wrong_rivals = random.sample(other_clubs_list, min(3, len(other_clubs_list)))
            questions.append({
                "text": f"Which club is considered {club_name}'s main rival?",
                "options": [rivals[0], wrong_rivals[0], wrong_rivals[1] if len(wrong_rivals) > 1 else rivals[1] if len(rivals) > 1 else "Unknown", wrong_rivals[2] if len(wrong_rivals) > 2 else "Other"],
                "correct": "A",
                "category": f"{category_prefix}-History",
                "difficulty": 2
            })
        
        # 6. Historical fact question
        facts = data.get('facts', [])
        if facts:
            for fact in facts[:2]:
                questions.append({
                    "text": f"Which club is known for: '{fact}'?",
                    "options": [club_name] + random.sample(other_clubs, 3),
                    "correct": "A",
                    "category": f"{category_prefix}-History",
                    "difficulty": 3
                })
        
        # === LEGENDS/PLAYERS QUESTIONS ===
        legends = data.get('legends', [])
        if legends:
            # Question about club legends
            for legend in legends[:3]:
                wrong_legends = []
                for c in other_clubs:
                    wrong_legends.extend(CLUB_HISTORY[c].get('legends', [])[:1])
                wrong_legends = random.sample([l for l in wrong_legends if l != legend], min(3, len(wrong_legends)))
                
                if len(wrong_legends) >= 3:
                    questions.append({
                        "text": f"Which club did {legend} become a legend at?",
                        "options": [club_name] + random.sample(other_clubs, 3),
                        "correct": "A",
                        "category": f"{category_prefix}-Players",
                        "difficulty": 2
                    })
                    
                    questions.append({
                        "text": f"Who is a legendary player for {club_name}?",
                        "options": [legend] + wrong_legends[:3],
                        "correct": "A",
                        "category": f"{category_prefix}-Players",
                        "difficulty": 2
                    })
        
        # === MANAGERS QUESTIONS ===
        managers = data.get('managers', [])
        if managers:
            for manager in managers[:2]:
                wrong_managers = []
                for c in other_clubs:
                    wrong_managers.extend(CLUB_HISTORY[c].get('managers', [])[:1])
                wrong_managers = random.sample([m for m in wrong_managers if m != manager], min(3, len(wrong_managers)))
                
                if len(wrong_managers) >= 3:
                    questions.append({
                        "text": f"Which club did {manager} manage?",
                        "options": [club_name] + random.sample(other_clubs, 3),
                        "correct": "A",
                        "category": f"{category_prefix}-Managers",
                        "difficulty": 2
                    })
        
        # === TROPHIES QUESTIONS ===
        trophies = data.get('trophies', {})
        if trophies:
            # League titles
            league_titles = trophies.get('league', 0)
            if league_titles > 0:
                wrong_counts = [league_titles + 3, league_titles - 2, league_titles + 7]
                questions.append({
                    "text": f"How many domestic league titles has {club_name} won?",
                    "options": [str(league_titles), str(wrong_counts[0]), str(wrong_counts[1]), str(wrong_counts[2])],
                    "correct": "A",
                    "category": f"{category_prefix}-Trophies",
                    "difficulty": 3
                })
            
            # Champions League
            cl_titles = trophies.get('champions_league', 0)
            if cl_titles > 0:
                wrong_cl = [cl_titles + 1, cl_titles - 1, cl_titles + 3]
                questions.append({
                    "text": f"How many Champions League/European Cup titles has {club_name} won?",
                    "options": [str(cl_titles), str(wrong_cl[0]), str(wrong_cl[1] if wrong_cl[1] >= 0 else 0), str(wrong_cl[2])],
                    "correct": "A",
                    "category": f"{category_prefix}-Trophies",
                    "difficulty": 2
                })
    
    return questions

async def insert_club_questions():
    """Insert club-specific questions into the database"""
    questions_data = generate_club_questions()
    
    print(f"Generated {len(questions_data)} club-specific questions")
    
    questions_to_insert = []
    for q in questions_data:
        questions_to_insert.append(Question(
            id=str(uuid.uuid4()),
            question_text=q['text'],
            option_a=q['options'][0],
            option_b=q['options'][1],
            option_c=q['options'][2],
            option_d=q['options'][3],
            correct_option=q['correct'],
            category=q['category'],
            difficulty=q['difficulty']
        ))
    
    print(f"Inserting {len(questions_to_insert)} questions...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Insert in batches
            batch_size = 100
            for i in range(0, len(questions_to_insert), batch_size):
                batch = questions_to_insert[i:i+batch_size]
                session.add_all(batch)
                await session.commit()
                print(f"Inserted batch {i//batch_size + 1}")
            
            print(f"✓ Successfully inserted {len(questions_to_insert)} club-specific questions!")
        except Exception as e:
            print(f"Error: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(insert_club_questions())
