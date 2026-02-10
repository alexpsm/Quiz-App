# Comprehensive club list for QuizBall Club Challenge

CLUBS_BY_LEAGUE = {
    "Premier League": [
        "Arsenal", "Aston Villa", "AFC Bournemouth", "Brentford", "Brighton & Hove Albion",
        "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich Town",
        "Leicester City", "Liverpool", "Manchester City", "Manchester United",
        "Newcastle United", "Nottingham Forest", "Southampton", "Tottenham Hotspur",
        "West Ham United", "Wolverhampton Wanderers"
    ],
    "Bundesliga": [
        "Bayern Munich", "Borussia Dortmund", "Bayer Leverkusen", "RB Leipzig",
        "VfB Stuttgart", "Eintracht Frankfurt", "SC Freiburg", "VfL Wolfsburg",
        "TSG Hoffenheim", "1. FC Union Berlin", "Borussia Monchengladbach",
        "1. FSV Mainz 05", "SV Werder Bremen", "FC Augsburg", "VfL Bochum",
        "1. FC Heidenheim", "FC St. Pauli", "Holstein Kiel"
    ],
    "Ligue 1": [
        "Paris Saint-Germain", "AS Monaco", "Olympique de Marseille", "LOSC Lille",
        "Olympique Lyonnais", "RC Lens", "Stade Rennais", "OGC Nice",
        "Stade Brestois", "RC Strasbourg", "FC Nantes", "Toulouse FC",
        "Montpellier HSC", "AJ Auxerre", "Angers SCO", "Le Havre AC",
        "AS Saint-Etienne", "Stade de Reims"
    ],
    "Serie A": [
        "Inter Milan", "AC Milan", "Juventus", "SSC Napoli", "AS Roma",
        "SS Lazio", "Atalanta", "ACF Fiorentina", "Bologna FC", "Torino FC",
        "Udinese", "Genoa CFC", "Cagliari", "Empoli FC", "US Lecce",
        "Parma Calcio", "Hellas Verona", "Venezia FC", "AC Monza", "Como 1907"
    ],
    "La Liga": [
        "Real Madrid", "FC Barcelona", "Atletico Madrid", "Sevilla FC", "Real Sociedad",
        "Real Betis", "Villarreal CF", "Athletic Bilbao", "Valencia CF", "CA Osasuna",
        "RC Celta de Vigo", "Girona FC", "RCD Mallorca", "Getafe CF", "Deportivo Alaves",
        "UD Las Palmas", "Rayo Vallecano", "RCD Espanyol", "Real Valladolid", "CD Leganes"
    ],
}

def get_all_clubs():
    """Return flat list of all clubs"""
    all_clubs = []
    for league, clubs in CLUBS_BY_LEAGUE.items():
        all_clubs.extend(clubs)
    return sorted(all_clubs)

def get_club_league(club_name):
    """Get the league for a given club"""
    for league, clubs in CLUBS_BY_LEAGUE.items():
        if club_name in clubs:
            return league
    return None
