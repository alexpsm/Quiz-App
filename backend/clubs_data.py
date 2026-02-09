# Comprehensive club list for QuizBall Club Challenge

CLUBS_BY_LEAGUE = {
    "Premier League": [
        "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", 
        "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham",
        "Leeds United", "Liverpool", "Manchester City", "Manchester United",
        "Newcastle United", "Nottingham Forest", "Sunderland", "Tottenham",
        "West Ham", "Wolverhampton"
    ],
    "La Liga": [
        "Real Madrid", "Barcelona", "Atletico Madrid", "Sevilla", "Real Sociedad",
        "Real Betis", "Villarreal", "Athletic Bilbao", "Valencia", "Osasuna",
        "Celta Vigo", "Girona", "Mallorca", "Getafe", "Cadiz",
        "Rayo Vallecano", "Alaves", "Granada", "Almeria", "Las Palmas"
    ],
    "Bundesliga": [
        "Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Union Berlin",
        "Freiburg", "Bayer Leverkusen", "Eintracht Frankfurt", "Wolfsburg",
        "Mainz", "Borussia Monchengladbach", "Cologne", "Hoffenheim",
        "Werder Bremen", "Bochum", "Augsburg", "Stuttgart", "Hertha Berlin", "Schalke"
    ],
    "Serie A": [
        "Inter Milan", "AC Milan", "Juventus", "Napoli", "AS Roma",
        "Lazio", "Atalanta", "Fiorentina", "Bologna", "Torino",
        "Udinese", "Sassuolo", "Empoli", "Monza", "Lecce",
        "Verona", "Salernitana", "Spezia", "Cremonese", "Sampdoria"
    ],
    "Ligue 1": [
        "PSG", "Lens", "Lyon", "Marseille", "Lille",
        "Rennes", "Strasbourg", "Toulouse", "Angers", "Monaco",
        "Brest", "Le Havre", "Nice", "Paris FC", "Auxerre",
        "Nantes", "Metz", "Montpellier"
    ],
    "Championship": [
        "Leicester City", "Ipswich Town", "Southampton", "Leeds United",
        "West Brom", "Middlesbrough", "Norwich City", "Coventry City",
        "Hull City", "Preston North End", "Sheffield Wednesday", "Cardiff City",
        "Swansea City", "Bristol City", "Millwall", "Blackburn Rovers",
        "Stoke City", "Queens Park Rangers", "Birmingham City", "Plymouth Argyle"
    ],
    "South American": [
        "Boca Juniors", "River Plate", "Racing Club", "Independiente",
        "San Lorenzo", "Flamengo", "Palmeiras", "Corinthians", "Sao Paulo",
        "Santos", "Atletico Mineiro", "Penarol", "Nacional", "Colo-Colo",
        "Universidad de Chile", "Cerro Porteno", "Olimpia", "Barcelona SC",
        "LDU Quito", "Millonarios"
    ]
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
