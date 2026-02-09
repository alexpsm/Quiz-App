import asyncio
import sys
sys.path.append('/app/backend')

from database import AsyncSessionLocal
from models import Question
import uuid

ADDITIONAL_QUESTIONS = [
    # History category
    {
        "question_text": "Which player scored the fastest goal in World Cup history?",
        "option_a": "Hakan Şükür",
        "option_b": "Clint Dempsey",
        "option_c": "Bryan Robson",
        "option_d": "Emilio Butragueño",
        "correct_option": "A",
        "category": "History",
        "difficulty": 2
    },
    {
        "question_text": "Which country hosted the first-ever World Cup?",
        "option_a": "Brazil",
        "option_b": "Uruguay",
        "option_c": "Italy",
        "option_d": "England",
        "correct_option": "B",
        "category": "History",
        "difficulty": 1
    },
    {
        "question_text": "Who won the Golden Boot at the 2018 World Cup?",
        "option_a": "Cristiano Ronaldo",
        "option_b": "Harry Kane",
        "option_c": "Kylian Mbappé",
        "option_d": "Romelu Lukaku",
        "correct_option": "B",
        "category": "History",
        "difficulty": 2
    },
    # Club category
    {
        "question_text": "Which English club is known as 'The Gunners'?",
        "option_a": "Chelsea",
        "option_b": "Arsenal",
        "option_c": "Tottenham",
        "option_d": "West Ham",
        "correct_option": "B",
        "category": "Club",
        "difficulty": 1
    },
    {
        "question_text": "Which club won the treble in 1999 (Premier League, FA Cup, Champions League)?",
        "option_a": "Arsenal",
        "option_b": "Liverpool",
        "option_c": "Manchester United",
        "option_d": "Chelsea",
        "correct_option": "C",
        "category": "Club",
        "difficulty": 2
    },
    {
        "question_text": "What is the home stadium of Juventus?",
        "option_a": "San Siro",
        "option_b": "Allianz Stadium",
        "option_c": "Stadio Olimpico",
        "option_d": "Stadio San Paolo",
        "correct_option": "B",
        "category": "Club",
        "difficulty": 2
    },
    # Country category
    {
        "question_text": "Which country has won the most FIFA World Cups?",
        "option_a": "Germany",
        "option_b": "Italy",
        "option_c": "Brazil",
        "option_d": "Argentina",
        "correct_option": "C",
        "category": "Country",
        "difficulty": 1
    },
    {
        "question_text": "What is France's national team nickname?",
        "option_a": "Les Bleus",
        "option_b": "La Roja",
        "option_c": "Die Mannschaft",
        "option_d": "The Three Lions",
        "correct_option": "A",
        "category": "Country",
        "difficulty": 1
    },
    {
        "question_text": "Which country won the first European Championship in 1960?",
        "option_a": "France",
        "option_b": "Soviet Union",
        "option_c": "Spain",
        "option_d": "Italy",
        "correct_option": "B",
        "category": "Country",
        "difficulty": 3
    },
    # League category
    {
        "question_text": "Which team has won the most English Premier League titles?",
        "option_a": "Liverpool",
        "option_b": "Arsenal",
        "option_c": "Manchester United",
        "option_d": "Chelsea",
        "correct_option": "C",
        "category": "League",
        "difficulty": 1
    },
    {
        "question_text": "What is the top division of German football called?",
        "option_a": "Bundesliga",
        "option_b": "La Liga",
        "option_c": "Serie A",
        "option_d": "Ligue 1",
        "correct_option": "A",
        "category": "League",
        "difficulty": 1
    },
    {
        "question_text": "Which league is Lionel Messi currently playing in?",
        "option_a": "La Liga",
        "option_b": "MLS",
        "option_c": "Ligue 1",
        "option_d": "Serie A",
        "correct_option": "B",
        "category": "League",
        "difficulty": 1
    },
    # Fan Culture
    {
        "question_text": "What do Real Madrid fans call their club?",
        "option_a": "Los Blancos",
        "option_b": "Los Merengues",
        "option_c": "Both A and B",
        "option_d": "La Casa Blanca",
        "correct_option": "C",
        "category": "Fan Culture",
        "difficulty": 2
    },
    {
        "question_text": "What is the name of the derby between Barcelona and Real Madrid?",
        "option_a": "El Derbi",
        "option_b": "El Clásico",
        "option_c": "La Copa",
        "option_d": "El Grande",
        "correct_option": "B",
        "category": "Fan Culture",
        "difficulty": 1
    },
    {
        "question_text": "Which club's fans are known as 'Tifosi'?",
        "option_a": "AC Milan",
        "option_b": "Inter Milan",
        "option_c": "Italian clubs in general",
        "option_d": "Juventus",
        "correct_option": "C",
        "category": "Fan Culture",
        "difficulty": 2
    },
]

async def seed_additional_questions():
    async with AsyncSessionLocal() as session:
        try:
            for q_data in ADDITIONAL_QUESTIONS:
                question = Question(
                    id=str(uuid.uuid4()),
                    **q_data
                )
                session.add(question)
            
            await session.commit()
            print(f"Successfully seeded {len(ADDITIONAL_QUESTIONS)} additional questions!")
        except Exception as e:
            print(f"Error seeding questions: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(seed_additional_questions())
