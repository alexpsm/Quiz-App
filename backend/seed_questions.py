import asyncio
import sys
sys.path.append('/app/backend')

from database import AsyncSessionLocal
from models import Question
import uuid

SEED_QUESTIONS = [
    {
        "question_text": "Which player won the Ballon d'Or in 2023?",
        "option_a": "Lionel Messi",
        "option_b": "Erling Haaland",
        "option_c": "Kylian Mbappé",
        "option_d": "Kevin De Bruyne",
        "correct_option": "A",
        "category": "Players",
        "difficulty": 1
    },
    {
        "question_text": "Which team won the UEFA Champions League in 2023?",
        "option_a": "Manchester City",
        "option_b": "Real Madrid",
        "option_c": "Inter Milan",
        "option_d": "Bayern Munich",
        "correct_option": "A",
        "category": "League",
        "difficulty": 1
    },
    {
        "question_text": "What is the maximum capacity of the Camp Nou stadium?",
        "option_a": "75,000",
        "option_b": "85,000",
        "option_c": "99,354",
        "option_d": "110,000",
        "correct_option": "C",
        "category": "Stadiums",
        "difficulty": 2
    },
    {
        "question_text": "Which country won the 2022 FIFA World Cup?",
        "option_a": "Brazil",
        "option_b": "France",
        "option_c": "Argentina",
        "option_d": "Germany",
        "correct_option": "C",
        "category": "Country",
        "difficulty": 1
    },
    {
        "question_text": "Which club has won the most UEFA Champions League titles?",
        "option_a": "AC Milan",
        "option_b": "Barcelona",
        "option_c": "Bayern Munich",
        "option_d": "Real Madrid",
        "correct_option": "D",
        "category": "Club",
        "difficulty": 1
    },
    {
        "question_text": "What is Liverpool FC's famous anthem?",
        "option_a": "Blue Moon",
        "option_b": "You'll Never Walk Alone",
        "option_c": "Glory Glory Man United",
        "option_d": "Sweet Caroline",
        "correct_option": "B",
        "category": "Fan Culture",
        "difficulty": 1
    },
    {
        "question_text": "Who is the all-time top scorer in Premier League history?",
        "option_a": "Wayne Rooney",
        "option_b": "Thierry Henry",
        "option_c": "Alan Shearer",
        "option_d": "Harry Kane",
        "correct_option": "C",
        "category": "Players",
        "difficulty": 2
    },
    {
        "question_text": "In which year was the first FIFA World Cup held?",
        "option_a": "1928",
        "option_b": "1930",
        "option_c": "1934",
        "option_d": "1938",
        "correct_option": "B",
        "category": "History",
        "difficulty": 2
    },
    {
        "question_text": "Which player has won the most Champions League titles?",
        "option_a": "Cristiano Ronaldo",
        "option_b": "Lionel Messi",
        "option_c": "Dani Carvajal",
        "option_d": "Andrés Iniesta",
        "correct_option": "A",
        "category": "Players",
        "difficulty": 2
    },
    {
        "question_text": "What is the nickname of Argentina's national team?",
        "option_a": "La Roja",
        "option_b": "La Albiceleste",
        "option_c": "Os Canarinhos",
        "option_d": "Les Bleus",
        "correct_option": "B",
        "category": "Country",
        "difficulty": 1
    },
    {
        "question_text": "Which stadium is known as 'The Theatre of Dreams'?",
        "option_a": "Anfield",
        "option_b": "Old Trafford",
        "option_c": "Stamford Bridge",
        "option_d": "Emirates Stadium",
        "correct_option": "B",
        "category": "Stadiums",
        "difficulty": 1
    },
    {
        "question_text": "Which club is known as 'The Red Devils'?",
        "option_a": "Liverpool",
        "option_b": "Arsenal",
        "option_c": "Manchester United",
        "option_d": "AC Milan",
        "correct_option": "C",
        "category": "Club",
        "difficulty": 1
    },
    {
        "question_text": "Who scored the 'Hand of God' goal?",
        "option_a": "Pelé",
        "option_b": "Diego Maradona",
        "option_c": "Ronaldinho",
        "option_d": "Zinedine Zidane",
        "correct_option": "B",
        "category": "History",
        "difficulty": 1
    },
    {
        "question_text": "Which league is known as 'La Liga'?",
        "option_a": "English Premier League",
        "option_b": "Italian Serie A",
        "option_c": "Spanish League",
        "option_d": "German Bundesliga",
        "correct_option": "C",
        "category": "League",
        "difficulty": 1
    },
    {
        "question_text": "What color card results in a player being sent off?",
        "option_a": "Yellow",
        "option_b": "Red",
        "option_c": "Orange",
        "option_d": "Blue",
        "correct_option": "B",
        "category": "Fan Culture",
        "difficulty": 1
    },
]

async def seed_questions():
    async with AsyncSessionLocal() as session:
        try:
            for q_data in SEED_QUESTIONS:
                question = Question(
                    id=str(uuid.uuid4()),
                    **q_data
                )
                session.add(question)
            
            await session.commit()
            print(f"Successfully seeded {len(SEED_QUESTIONS)} questions!")
        except Exception as e:
            print(f"Error seeding questions: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(seed_questions())
