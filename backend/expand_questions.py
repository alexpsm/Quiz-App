"""
Comprehensive question expansion script for QuizBall.
Generates questions for all thin categories.
"""
import asyncio
import uuid
import random
from database import engine
from sqlalchemy import text

def q(question_text, a, b, c, d, correct):
    return (str(uuid.uuid4()), question_text, a, b, c, d, correct)

def generate_stadiums():
    """Generate Stadiums category questions"""
    questions = []
    data = [
        ("What is the capacity of Wembley Stadium?", "90,000", "75,000", "80,000", "85,000", "A"),
        ("Which stadium is known as 'The Theatre of Dreams'?", "Old Trafford", "Anfield", "Stamford Bridge", "Emirates Stadium", "A"),
        ("In which city is the Santiago Bernabeu located?", "Madrid", "Barcelona", "Seville", "Valencia", "A"),
        ("What is the name of Barcelona's stadium?", "Camp Nou", "Mestalla", "San Siro", "Allianz Arena", "A"),
        ("Which stadium hosted the 2014 World Cup final?", "Maracana", "Wembley", "Luzhniki", "Lusail", "A"),
        ("What is the home ground of Liverpool FC?", "Anfield", "Goodison Park", "Old Trafford", "Etihad Stadium", "A"),
        ("Which country is the Allianz Arena located in?", "Germany", "Italy", "Spain", "France", "A"),
        ("What is the largest football stadium in the world by capacity?", "Rungrado 1st of May Stadium", "Camp Nou", "Wembley", "Maracana", "A"),
        ("Which stadium is home to AC Milan and Inter Milan?", "San Siro", "Stadio Olimpico", "Allianz Stadium", "Diego Armando Maradona", "A"),
        ("What is the home stadium of Borussia Dortmund?", "Signal Iduna Park", "Allianz Arena", "Olympiastadion", "Volksparkstadion", "A"),
        ("Which stadium hosted the 2022 World Cup final?", "Lusail Stadium", "Al Bayt Stadium", "Khalifa International", "Ahmad bin Ali", "A"),
        ("What is the capacity of the Etihad Stadium?", "53,400", "75,000", "60,000", "45,000", "A"),
        ("Which stadium is known as 'The Kop'?", "Anfield", "Old Trafford", "Highbury", "White Hart Lane", "A"),
        ("In which city is the Stadio Olimpico located?", "Rome", "Milan", "Naples", "Turin", "A"),
        ("What is the name of Arsenal's current home ground?", "Emirates Stadium", "Highbury", "Wembley", "London Stadium", "A"),
        ("Which stadium is the home of Juventus?", "Allianz Stadium", "San Siro", "Stadio Olimpico", "Diego Armando Maradona", "A"),
        ("What is the home ground of Celtic FC?", "Celtic Park", "Ibrox Stadium", "Hampden Park", "Murrayfield", "A"),
        ("Which stadium hosted the first ever World Cup final in 1930?", "Estadio Centenario", "Maracana", "Wembley", "Azteca", "A"),
        ("What is the home stadium of Paris Saint-Germain?", "Parc des Princes", "Stade de France", "Stade Velodrome", "Groupama Stadium", "A"),
        ("Which English stadium has the 'Stretford End'?", "Old Trafford", "Anfield", "Stamford Bridge", "Emirates Stadium", "A"),
        ("What is the name of Tottenham's stadium?", "Tottenham Hotspur Stadium", "White Hart Lane", "Wembley", "London Stadium", "A"),
        ("In which city is the Azteca Stadium?", "Mexico City", "Buenos Aires", "Rio de Janeiro", "Lima", "A"),
        ("What is the home ground of Bayern Munich?", "Allianz Arena", "Signal Iduna Park", "Olympiastadion", "Volksparkstadion", "A"),
        ("Which stadium is known as 'The Nou Camp'?", "Camp Nou", "Santiago Bernabeu", "Mestalla", "Wanda Metropolitano", "A"),
        ("What is the capacity of Anfield after recent expansion?", "61,000", "54,000", "45,000", "70,000", "A"),
        ("Which stadium hosted Euro 2020 final?", "Wembley", "Olympiastadion", "Allianz Arena", "Stade de France", "A"),
        ("What is the name of Atletico Madrid's stadium?", "Civitas Metropolitano", "Santiago Bernabeu", "Camp Nou", "Mestalla", "A"),
        ("Where do Everton currently play their home games?", "Goodison Park", "Anfield", "Bramall Lane", "Elland Road", "A"),
        ("Which stadium is known as 'Fortress Anfield'?", "Anfield", "Old Trafford", "Stamford Bridge", "Etihad Stadium", "A"),
        ("What is the home ground of Real Betis?", "Estadio Benito Villamarin", "Ramon Sanchez-Pizjuan", "Mestalla", "Camp Nou", "A"),
        ("Which stadium has the famous 'Yellow Wall'?", "Signal Iduna Park", "Allianz Arena", "Camp Nou", "Wembley", "A"),
        ("What is the home stadium of Napoli?", "Stadio Diego Armando Maradona", "San Siro", "Stadio Olimpico", "Allianz Stadium", "A"),
        ("In which country is the Puskas Arena?", "Hungary", "Germany", "Poland", "Romania", "A"),
        ("What is the home ground of West Ham United?", "London Stadium", "Upton Park", "Stamford Bridge", "The Valley", "A"),
        ("Which stadium is known as 'El Monumental'?", "Estadio Monumental", "La Bombonera", "Maracana", "Azteca", "A"),
        ("What is the name of Benfica's stadium?", "Estadio da Luz", "Estadio Jose Alvalade", "Estadio do Dragao", "Estadio Nacional", "A"),
        ("Where do Aston Villa play?", "Villa Park", "St Andrew's", "The Hawthorns", "Molineux", "A"),
        ("What is the home stadium of Marseille?", "Stade Velodrome", "Parc des Princes", "Stade de France", "Groupama Stadium", "A"),
        ("Which stadium hosted the 2006 World Cup final?", "Olympiastadion Berlin", "Allianz Arena", "Signal Iduna Park", "Volksparkstadion", "A"),
        ("What is Leicester City's home ground called?", "King Power Stadium", "Walkers Stadium", "Filbert Street", "Ewood Park", "A"),
        ("Which is the oldest football ground still in use in England?", "Bramall Lane", "Anfield", "Goodison Park", "Old Trafford", "A"),
        ("What is the home ground of Rangers FC?", "Ibrox Stadium", "Celtic Park", "Hampden Park", "Tynecastle", "A"),
        ("Where does Wolverhampton Wanderers play?", "Molineux", "Villa Park", "The Hawthorns", "St Andrew's", "A"),
        ("What is the capacity of the Santiago Bernabeu?", "81,044", "60,000", "90,000", "75,000", "A"),
        ("Which stadium is home to the Italian national team?", "Stadio Olimpico", "San Siro", "Allianz Stadium", "Stadio Diego Armando Maradona", "A"),
        ("What is the name of Porto's stadium?", "Estadio do Dragao", "Estadio da Luz", "Estadio Jose Alvalade", "Estadio Bessa", "A"),
        ("Where do Newcastle United play?", "St James' Park", "Stadium of Light", "Riverside Stadium", "Elland Road", "A"),
        ("What is the home ground of Ajax?", "Johan Cruyff Arena", "De Kuip", "Philips Stadion", "Abe Lenstra Stadion", "A"),
        ("Which stadium hosted the 2010 World Cup final?", "Soccer City", "Moses Mabhida", "Cape Town Stadium", "Ellis Park", "A"),
        ("What is the name of Crystal Palace's ground?", "Selhurst Park", "The Valley", "Loftus Road", "Craven Cottage", "A"),
        ("Where does Feyenoord play?", "De Kuip", "Johan Cruyff Arena", "Philips Stadion", "Abe Lenstra Stadion", "A"),
        ("What is the home stadium of Sporting Lisbon?", "Estadio Jose Alvalade", "Estadio da Luz", "Estadio do Dragao", "Estadio Nacional", "A"),
        ("Which stadium is home to the German national team?", "Olympiastadion Berlin", "Allianz Arena", "Signal Iduna Park", "Volksparkstadion", "A"),
        ("What is the name of Fulham's ground?", "Craven Cottage", "Loftus Road", "Selhurst Park", "The Valley", "A"),
        ("Where do Leeds United play?", "Elland Road", "Hillsborough", "Bramall Lane", "Valley Parade", "A"),
        ("What is the home ground of PSV Eindhoven?", "Philips Stadion", "Johan Cruyff Arena", "De Kuip", "Abe Lenstra Stadion", "A"),
        ("Which stadium has the 'Holte End'?", "Villa Park", "Anfield", "Old Trafford", "Stamford Bridge", "A"),
        ("What is the capacity of Camp Nou?", "99,354", "80,000", "75,000", "85,000", "A"),
        ("Where does Nottingham Forest play?", "City Ground", "Meadow Lane", "Pride Park", "Bramall Lane", "A"),
        ("What is the name of Brighton's stadium?", "Amex Stadium", "Withdean Stadium", "Goldstone Ground", "Priestfield Stadium", "A"),
        ("Which stadium is home to Boca Juniors?", "La Bombonera", "El Monumental", "Estadio Azteca", "Maracana", "A"),
        ("What is the home ground of Southampton?", "St Mary's Stadium", "The Dell", "Fratton Park", "Dean Court", "A"),
        ("Where does Sevilla FC play?", "Ramon Sanchez-Pizjuan", "Estadio Benito Villamarin", "Estadio de la Ceramica", "Mestalla", "A"),
        ("What is the name of Burnley's stadium?", "Turf Moor", "Ewood Park", "Deepdale", "Bloomfield Road", "A"),
        ("Which stadium hosted the 2018 World Cup final?", "Luzhniki Stadium", "Saint Petersburg Stadium", "Spartak Stadium", "Kazan Arena", "A"),
        ("What is the home ground of Valencia CF?", "Mestalla", "Camp Nou", "Santiago Bernabeu", "Ramon Sanchez-Pizjuan", "A"),
        ("Where does Galatasaray play?", "RAMS Park", "Sukru Saracoglu", "Ataturk Olympic", "Vodafone Park", "A"),
        ("What is the capacity of Signal Iduna Park?", "81,365", "60,000", "90,000", "75,000", "A"),
        ("Which stadium is known as 'The Bridge'?", "Stamford Bridge", "Anfield", "Old Trafford", "Emirates Stadium", "A"),
        ("What is the home ground of Bayer Leverkusen?", "BayArena", "Allianz Arena", "Signal Iduna Park", "Volksparkstadion", "A"),
        ("Where does Real Sociedad play?", "Reale Arena", "San Mames", "Mestalla", "El Sadar", "A"),
        ("What is the name of Sheffield United's ground?", "Bramall Lane", "Hillsborough", "Elland Road", "Valley Parade", "A"),
        ("Which stadium has the 'Matthew Harding Stand'?", "Stamford Bridge", "Anfield", "Old Trafford", "Emirates Stadium", "A"),
        ("What is the home stadium of Lyon?", "Groupama Stadium", "Parc des Princes", "Stade Velodrome", "Stade de France", "A"),
        ("Where does Athletic Bilbao play?", "San Mames", "Mestalla", "Reale Arena", "El Sadar", "A"),
        ("What is the name of Ipswich Town's ground?", "Portman Road", "Carrow Road", "The Den", "Loftus Road", "A"),
        ("Which stadium is the largest in Africa?", "FNB Stadium", "Borg El Arab", "Cairo International", "Stade des Martyrs", "A"),
        ("What is the home ground of RB Leipzig?", "Red Bull Arena", "Signal Iduna Park", "Allianz Arena", "Olympiastadion", "A"),
        ("Where does Lazio play?", "Stadio Olimpico", "San Siro", "Allianz Stadium", "Stadio Diego Armando Maradona", "A"),
        ("What is the name of Bournemouth's stadium?", "Vitality Stadium", "St Mary's Stadium", "The Dell", "Fratton Park", "A"),
        ("Which stadium hosted the Champions League final in 2023?", "Ataturk Olympic Stadium", "Wembley", "Stade de France", "Estadio da Luz", "A"),
        ("What is the home ground of Fenerbahce?", "Sukru Saracoglu Stadium", "RAMS Park", "Vodafone Park", "Ataturk Olympic", "A"),
        ("Where does Villarreal play?", "Estadio de la Ceramica", "Mestalla", "Camp Nou", "Ramon Sanchez-Pizjuan", "A"),
        ("What is the capacity of Old Trafford?", "74,310", "60,000", "80,000", "55,000", "A"),
        ("Which stadium has the 'Curva Sud'?", "San Siro", "Stadio Olimpico", "Allianz Stadium", "Stadio Diego Armando Maradona", "A"),
        ("What is the name of Wolves' ground?", "Molineux", "Villa Park", "The Hawthorns", "St Andrew's", "A"),
        ("Where does Monaco play?", "Stade Louis II", "Parc des Princes", "Stade Velodrome", "Stade de France", "A"),
        ("What was Arsenal's stadium before the Emirates?", "Highbury", "White Hart Lane", "Wembley", "Upton Park", "A"),
        ("Which stadium is nicknamed 'The Caldron'?", "La Bombonera", "Anfield", "Signal Iduna Park", "Maracana", "A"),
        ("What is the home ground of Eintracht Frankfurt?", "Deutsche Bank Park", "Signal Iduna Park", "Allianz Arena", "Volksparkstadion", "A"),
        ("Where does Besiktas play?", "Vodafone Park", "RAMS Park", "Sukru Saracoglu", "Ataturk Olympic", "A"),
        ("What is the name of Brentford's stadium?", "Gtech Community Stadium", "Griffin Park", "Loftus Road", "Craven Cottage", "A"),
        ("Which country has the Estadio Azteca?", "Mexico", "Argentina", "Brazil", "Colombia", "A"),
        ("What is the home ground of Atalanta?", "Gewiss Stadium", "San Siro", "Stadio Olimpico", "Allianz Stadium", "A"),
        ("Where does Lille play?", "Stade Pierre-Mauroy", "Parc des Princes", "Stade Velodrome", "Groupama Stadium", "A"),
        ("What is the home stadium of Flamengo?", "Maracana", "Estadio Monumental", "La Bombonera", "Estadio Azteca", "A"),
    ]
    for d in data:
        # Shuffle options for each question
        opts = list(d[1:5])
        correct_text = d[1]  # correct is always option A in the data
        random.shuffle(opts)
        correct_letter = chr(65 + opts.index(correct_text))
        questions.append(q(d[0], opts[0], opts[1], opts[2], opts[3], correct_letter))
    return questions

def generate_champions_league():
    """Generate Champions League questions"""
    questions = []
    data = [
        ("Who has won the most Champions League titles?", "Real Madrid", "AC Milan", "Bayern Munich", "Liverpool", "A"),
        ("Which player has scored the most Champions League goals?", "Cristiano Ronaldo", "Lionel Messi", "Robert Lewandowski", "Raul", "A"),
        ("In what year was the Champions League rebranded from the European Cup?", "1992", "1990", "1995", "1988", "A"),
        ("Which team won the first ever European Cup in 1956?", "Real Madrid", "AC Milan", "Benfica", "Barcelona", "A"),
        ("Who scored the winning goal in the 2005 Champions League final for Liverpool?", "Penalty shootout (Dudek saves)", "Steven Gerrard", "Xabi Alonso", "Vladimir Smicer", "A"),
        ("Which club has lost the most Champions League finals?", "Juventus", "Bayern Munich", "Benfica", "Atletico Madrid", "A"),
        ("Who was the Champions League top scorer in 2021-22?", "Karim Benzema", "Robert Lewandowski", "Mohamed Salah", "Kylian Mbappe", "A"),
        ("Which city hosted the 2019 Champions League final?", "Madrid", "Istanbul", "Lisbon", "Cardiff", "A"),
        ("Who scored a hat-trick in the 1999 Champions League final?", "No one scored a hat-trick", "Ole Gunnar Solskjaer", "Teddy Sheringham", "Mario Basler", "A"),
        ("How many consecutive Champions League titles did Real Madrid win from 2016-2018?", "3", "2", "4", "5", "A"),
        ("Which team completed the treble in 2023?", "Manchester City", "Real Madrid", "Bayern Munich", "Barcelona", "A"),
        ("Who scored the fastest Champions League goal?", "Roy Makaay", "Lionel Messi", "Kylian Mbappe", "Usain Bolt", "A"),
        ("Which English club won the 2012 Champions League?", "Chelsea", "Manchester United", "Liverpool", "Arsenal", "A"),
        ("Who managed Inter Milan to Champions League glory in 2010?", "Jose Mourinho", "Carlo Ancelotti", "Antonio Conte", "Rafa Benitez", "A"),
        ("Which player has made the most Champions League appearances?", "Cristiano Ronaldo", "Iker Casillas", "Xavi", "Lionel Messi", "A"),
        ("In which year did Liverpool win their fifth Champions League?", "2005", "2019", "2001", "2007", "A"),
        ("Who scored the winning penalty in the 2008 Champions League final?", "Edwin van der Sar saved it", "Cristiano Ronaldo", "John Terry", "Nicolas Anelka", "A"),
        ("Which team did Manchester City beat in the 2023 Champions League final?", "Inter Milan", "Real Madrid", "Bayern Munich", "AC Milan", "A"),
        ("Who holds the record for most Champions League titles as a manager?", "Carlo Ancelotti", "Bob Paisley", "Zinedine Zidane", "Alex Ferguson", "A"),
        ("Which group stage format change was introduced in 2024-25?", "Swiss model league phase", "Expanded group stage", "Knockout playoffs", "Mini tournament", "A"),
        ("Who scored Barcelona's winner in the 2009 Champions League final?", "Lionel Messi", "Samuel Eto'o", "Xavi", "Andres Iniesta", "A"),
        ("Which team has won the Champions League the most times in England?", "Liverpool", "Manchester United", "Chelsea", "Nottingham Forest", "A"),
        ("Who was the youngest Champions League goalscorer?", "Ansu Fati", "Kylian Mbappe", "Bojan Krkic", "Cesc Fabregas", "A"),
        ("Which stadium hosted the 2020 Champions League final?", "Estadio da Luz", "Ataturk Olympic", "Wembley", "Stade de France", "A"),
        ("Who managed Chelsea to their first Champions League title?", "Roberto Di Matteo", "Andre Villas-Boas", "Carlo Ancelotti", "Jose Mourinho", "A"),
        ("Which player scored in three consecutive Champions League finals?", "Cristiano Ronaldo", "Gareth Bale", "Sergio Ramos", "Karim Benzema", "A"),
        ("How many Champions League titles has AC Milan won?", "7", "5", "6", "8", "A"),
        ("Which team knocked out Barcelona in the 2019 semi-finals?", "Liverpool", "Ajax", "Tottenham", "Manchester City", "A"),
        ("Who scored the 'ghost goal' in the 2010 Champions League semi-final?", "No ghost goal in CL 2010", "Fernando Torres", "Didier Drogba", "Lionel Messi", "A"),
        ("Which German team won the Champions League in 2013?", "Bayern Munich", "Borussia Dortmund", "Schalke 04", "Bayer Leverkusen", "A"),
        ("Who won the Champions League Player of the Season in 2022?", "Karim Benzema", "Thibaut Courtois", "Vinicius Jr", "Luka Modric", "A"),
        ("Which team has appeared in the most Champions League finals without winning?", "Juventus", "Atletico Madrid", "Benfica", "Bayer Leverkusen", "A"),
        ("In what year did Ajax win the Champions League with a young squad?", "1995", "1992", "1997", "2000", "A"),
        ("Who scored Bayern Munich's winning goal in the 2013 CL final?", "Arjen Robben", "Thomas Muller", "Franck Ribery", "Mario Mandzukic", "A"),
        ("Which team won the Champions League in 2004?", "Porto", "Monaco", "AC Milan", "Real Madrid", "A"),
        ("Who managed Porto to the 2004 Champions League title?", "Jose Mourinho", "Carlos Queiroz", "Andre Villas-Boas", "Luiz Felipe Scolari", "A"),
        ("What was the score in the 2005 Champions League final at half-time?", "3-0 to AC Milan", "2-0 to AC Milan", "1-0 to AC Milan", "0-0", "A"),
        ("Which player has won the Champions League with three different clubs?", "Clarence Seedorf", "Cristiano Ronaldo", "David Beckham", "Zlatan Ibrahimovic", "A"),
        ("Who scored Real Madrid's winner in the 2022 Champions League final?", "Vinicius Jr", "Karim Benzema", "Luka Modric", "Rodrygo", "A"),
        ("In which year did Marseille win the Champions League?", "1993", "1991", "1995", "1989", "A"),
        ("Which team did Tottenham lose to in the 2019 CL final?", "Liverpool", "Ajax", "Barcelona", "Manchester City", "A"),
        ("Who scored a bicycle kick in the 2018 Champions League quarter-final?", "Cristiano Ronaldo", "Gareth Bale", "Neymar", "Zlatan Ibrahimovic", "A"),
        ("How many teams compete in the Champions League group stage (pre-2024)?", "32", "16", "24", "48", "A"),
        ("Which country has produced the most Champions League winners?", "Spain", "England", "Italy", "Germany", "A"),
        ("Who scored the winning goal in the 2021 Champions League final?", "Kai Havertz", "Timo Werner", "Mason Mount", "N'Golo Kante", "A"),
        ("Which team won back-to-back Champions League titles in 1989 and 1990?", "AC Milan", "Real Madrid", "Barcelona", "Bayern Munich", "A"),
        ("Who was the Champions League's all-time assist leader?", "Cristiano Ronaldo", "Lionel Messi", "Ryan Giggs", "Angel Di Maria", "A"),
        ("In which city was the 2017 Champions League final played?", "Cardiff", "Milan", "Berlin", "Madrid", "A"),
        ("Which team eliminated PSG in the 2017 Champions League round of 16?", "Barcelona", "Real Madrid", "Bayern Munich", "Juventus", "A"),
        ("Who scored a hat-trick for Real Madrid vs Atletico in the 2017 CL semi?", "Cristiano Ronaldo", "Karim Benzema", "Gareth Bale", "Isco", "A"),
        ("What was unique about the 2020 Champions League tournament?", "Single-leg knockouts in Lisbon", "Played behind closed doors only", "Extended to 64 teams", "Two-year format", "A"),
        ("Which team has the most consecutive Champions League appearances?", "Real Madrid", "Bayern Munich", "Barcelona", "Manchester United", "A"),
        ("Who saved Arjen Robben's penalty in the 2012 Champions League final?", "Petr Cech", "Manuel Neuer", "Iker Casillas", "Gianluigi Buffon", "A"),
        ("What is the Champions League anthem based on?", "Handel's Zadok the Priest", "Beethoven's 9th", "Mozart's Requiem", "Bach's Toccata", "A"),
        ("Which team won the Champions League in 2003?", "AC Milan", "Juventus", "Real Madrid", "Inter Milan", "A"),
        ("Who was the top scorer in the 2023-24 Champions League?", "Kylian Mbappe", "Erling Haaland", "Harry Kane", "Vinicius Jr", "A"),
        ("Which team has the record for most goals in a single CL campaign?", "Barcelona (2011-12)", "Real Madrid (2013-14)", "Bayern Munich (2019-20)", "Liverpool (2017-18)", "A"),
        ("In which year did Nottingham Forest win the European Cup?", "1979 and 1980", "1977 and 1978", "1981 and 1982", "1975 and 1976", "A"),
        ("Who managed Liverpool to the 2019 Champions League title?", "Jurgen Klopp", "Rafa Benitez", "Brendan Rodgers", "Arne Slot", "A"),
        ("Which team beat Barcelona 8-2 in the 2020 CL quarter-final?", "Bayern Munich", "Manchester City", "Liverpool", "PSG", "A"),
        ("Who is the youngest manager to win the Champions League?", "Andre Villas-Boas never won it", "Pep Guardiola", "Jose Mourinho", "Julian Nagelsmann", "A"),
    ]
    for d in data:
        opts = list(d[1:5])
        correct_text = d[1]
        random.shuffle(opts)
        correct_letter = chr(65 + opts.index(correct_text))
        questions.append(q(d[0], opts[0], opts[1], opts[2], opts[3], correct_letter))
    return questions

def generate_history():
    """Generate football History questions"""
    questions = []
    data = [
        ("In what year was the first FIFA World Cup held?", "1930", "1928", "1934", "1926", "A"),
        ("Which country hosted the first World Cup?", "Uruguay", "Brazil", "Italy", "France", "A"),
        ("Who won the first ever World Cup?", "Uruguay", "Argentina", "Brazil", "Italy", "A"),
        ("When was FIFA founded?", "1904", "1900", "1910", "1920", "A"),
        ("Which country has won the most World Cups?", "Brazil", "Germany", "Italy", "Argentina", "A"),
        ("In what year did the English Premier League start?", "1992", "1990", "1988", "1995", "A"),
        ("When was the offside rule first introduced?", "1863", "1870", "1880", "1900", "A"),
        ("Which club is considered the oldest football club in the world?", "Sheffield FC", "Notts County", "Stoke City", "Aston Villa", "A"),
        ("In what year was the first international football match played?", "1872", "1870", "1875", "1880", "A"),
        ("Between which two teams was the first international match?", "Scotland and England", "England and Wales", "France and Belgium", "Germany and Austria", "A"),
        ("When was the Ballon d'Or first awarded?", "1956", "1950", "1960", "1970", "A"),
        ("Who won the first ever Ballon d'Or?", "Stanley Matthews", "Alfredo Di Stefano", "Raymond Kopa", "Lev Yashin", "A"),
        ("In what year was the European Championship first held?", "1960", "1958", "1964", "1956", "A"),
        ("Which country won the first European Championship?", "Soviet Union", "Spain", "West Germany", "France", "A"),
        ("When were red and yellow cards introduced in football?", "1970", "1966", "1974", "1960", "A"),
        ("In which World Cup were red and yellow cards first used?", "1970 Mexico", "1966 England", "1974 West Germany", "1978 Argentina", "A"),
        ("When was the back-pass rule changed in football?", "1992", "1990", "1994", "1988", "A"),
        ("Who scored the 'Hand of God' goal?", "Diego Maradona", "Pele", "Johan Cruyff", "Michel Platini", "A"),
        ("In which World Cup did the 'Hand of God' occur?", "1986", "1982", "1990", "1978", "A"),
        ("When was the Champions League anthem first played?", "1992", "1990", "1995", "1988", "A"),
        ("Which team won the first Premier League title?", "Manchester United", "Blackburn Rovers", "Arsenal", "Liverpool", "A"),
        ("In what year was the golden goal rule introduced?", "1993", "1990", "1996", "1998", "A"),
        ("When was VAR first used in a World Cup?", "2018", "2014", "2022", "2010", "A"),
        ("Which was the first World Cup to use goal-line technology?", "2014 Brazil", "2010 South Africa", "2018 Russia", "2022 Qatar", "A"),
        ("When was the FIFA Women's World Cup first held?", "1991", "1989", "1995", "1999", "A"),
        ("Which country won the first Women's World Cup?", "United States", "Norway", "Germany", "Sweden", "A"),
        ("In what year was the Bosman ruling?", "1995", "1990", "1998", "1992", "A"),
        ("What did the Bosman ruling change?", "Free transfers at end of contract", "Salary caps", "Transfer windows", "Squad size limits", "A"),
        ("When was the first televised football match?", "1937", "1940", "1950", "1930", "A"),
        ("Which was the first World Cup shown on television?", "1954 Switzerland", "1950 Brazil", "1958 Sweden", "1962 Chile", "A"),
        ("When was the penalty kick rule introduced?", "1891", "1870", "1900", "1880", "A"),
        ("In what year did professional football become legal in England?", "1885", "1880", "1890", "1875", "A"),
        ("Which year saw the Hillsborough disaster?", "1989", "1985", "1991", "1987", "A"),
        ("When did the Heysel Stadium disaster occur?", "1985", "1989", "1983", "1987", "A"),
        ("Which was the first club to win the European Cup?", "Real Madrid", "AC Milan", "Benfica", "Barcelona", "A"),
        ("In what year was the Africa Cup of Nations first held?", "1957", "1960", "1955", "1962", "A"),
        ("When was the Copa America first held?", "1916", "1920", "1930", "1910", "A"),
        ("Which team won the first Copa America?", "Uruguay", "Argentina", "Brazil", "Chile", "A"),
        ("In what year was the Football League founded in England?", "1888", "1885", "1890", "1892", "A"),
        ("Who was the first ever $100 million transfer?", "Gareth Bale", "Cristiano Ronaldo", "Neymar", "Kaka", "A"),
        ("Which year saw the first ever World Cup hat-trick?", "1930", "1934", "1938", "1950", "A"),
        ("When was the 'three points for a win' system introduced in England?", "1981", "1990", "1992", "1985", "A"),
        ("In what year did Argentina host the World Cup for the first time?", "1978", "1930", "1986", "1962", "A"),
        ("When was the first night match played under floodlights?", "1878", "1890", "1900", "1920", "A"),
        ("Which club won the first ever FA Cup?", "Wanderers FC", "Royal Engineers", "Oxford University", "Old Etonians", "A"),
        ("In what year was the FA Cup first held?", "1871", "1870", "1875", "1880", "A"),
        ("When was the Laws of the Game first codified?", "1863", "1860", "1870", "1850", "A"),
        ("Which organization wrote the first Laws of the Game?", "The Football Association", "FIFA", "IFAB", "The FA Premier League", "A"),
        ("In what year did substitutes first become allowed in football?", "1958", "1960", "1965", "1970", "A"),
        ("When was the first intercontinental club competition?", "1960", "1955", "1965", "1970", "A"),
        ("Which was the first Asian country to host a World Cup?", "Japan/South Korea (2002)", "China", "Qatar", "India", "A"),
        ("In what year was the Community Shield first played?", "1908", "1900", "1920", "1930", "A"),
        ("When was the League Cup (EFL Cup) first played in England?", "1960", "1955", "1965", "1970", "A"),
        ("Which year saw England's famous 1966 World Cup victory?", "1966", "1962", "1970", "1958", "A"),
        ("Where was the 1966 World Cup final played?", "Wembley", "Old Trafford", "Highbury", "Stamford Bridge", "A"),
        ("Who scored a hat-trick in the 1966 World Cup final?", "Geoff Hurst", "Bobby Charlton", "Bobby Moore", "Gordon Banks", "A"),
        ("In what year did Pele win his first World Cup?", "1958", "1962", "1970", "1966", "A"),
        ("How old was Pele when he won his first World Cup?", "17", "19", "21", "15", "A"),
        ("Which year did the Bundesliga start?", "1963", "1960", "1965", "1970", "A"),
        ("When was Serie A officially founded?", "1929", "1920", "1935", "1940", "A"),
        ("In what year was La Liga founded?", "1929", "1920", "1935", "1940", "A"),
        ("When was Ligue 1 established?", "1932", "1930", "1935", "1928", "A"),
    ]
    for d in data:
        opts = list(d[1:5])
        correct_text = d[1]
        random.shuffle(opts)
        correct_letter = chr(65 + opts.index(correct_text))
        questions.append(q(d[0], opts[0], opts[1], opts[2], opts[3], correct_letter))
    return questions

def generate_players():
    """Generate Players category questions"""
    questions = []
    data = [
        ("Who is the all-time top scorer in football history?", "Cristiano Ronaldo", "Lionel Messi", "Pele", "Josef Bican", "A"),
        ("Which player has won the most Ballon d'Or awards?", "Lionel Messi", "Cristiano Ronaldo", "Johan Cruyff", "Michel Platini", "A"),
        ("Who holds the record for most goals in a calendar year?", "Lionel Messi (91 in 2012)", "Cristiano Ronaldo", "Gerd Muller", "Pele", "A"),
        ("Which goalkeeper has the most clean sheets in Premier League history?", "Petr Cech", "David De Gea", "Edwin van der Sar", "Peter Schmeichel", "A"),
        ("Who is the youngest player to score in a World Cup?", "Pele", "Kylian Mbappe", "Michael Owen", "Lionel Messi", "A"),
        ("Which player has made the most Premier League appearances?", "Gareth Barry", "Ryan Giggs", "Frank Lampard", "David James", "A"),
        ("Who holds the record for most assists in Premier League history?", "Ryan Giggs", "Cesc Fabregas", "Frank Lampard", "David Beckham", "A"),
        ("Which player scored the fastest hat-trick in Premier League history?", "Sadio Mane", "Robbie Fowler", "Alan Shearer", "Sergio Aguero", "A"),
        ("Who is the all-time top scorer in La Liga?", "Lionel Messi", "Cristiano Ronaldo", "Raul", "Telmo Zarra", "A"),
        ("Which defender has scored the most Premier League goals?", "David Unsworth", "John Terry", "Rio Ferdinand", "Virgil van Dijk", "A"),
        ("Who was the first player to score 100 Premier League goals?", "Alan Shearer", "Robbie Fowler", "Andy Cole", "Les Ferdinand", "A"),
        ("Which player has the most red cards in Premier League history?", "Richard Dunne", "Patrick Vieira", "Roy Keane", "Vinnie Jones", "A"),
        ("Who is the youngest player to play in the Premier League?", "Ethan Nwaneri", "Harvey Elliott", "Matthew Briggs", "Jack Wilshere", "A"),
        ("Which player scored in six consecutive World Cups?", "No player has done this", "Cristiano Ronaldo", "Lionel Messi", "Miroslav Klose", "A"),
        ("Who holds the record for most goals in a single World Cup?", "Just Fontaine (13 in 1958)", "Gerd Muller", "Ronaldo", "Kylian Mbappe", "A"),
        ("Which player has scored the most international goals?", "Cristiano Ronaldo", "Ali Daei", "Lionel Messi", "Sunil Chhetri", "A"),
        ("Who was FIFA's first ever World Player of the Year?", "Lothar Matthaus", "Marco van Basten", "Roberto Baggio", "Romario", "A"),
        ("Which player has won the most league titles in Europe?", "Lionel Messi", "Ryan Giggs", "Dani Alves", "Maxwell", "A"),
        ("Who scored the 'Goal of the Century'?", "Diego Maradona", "Pele", "Johan Cruyff", "Lionel Messi", "A"),
        ("Which goalkeeper won the Ballon d'Or?", "Lev Yashin", "Gianluigi Buffon", "Manuel Neuer", "Oliver Kahn", "A"),
        ("Who is the Premier League's all-time top scorer?", "Alan Shearer", "Wayne Rooney", "Andrew Cole", "Sergio Aguero", "A"),
        ("Which player has scored the most free kicks in football history?", "Juninho Pernambucano", "David Beckham", "Lionel Messi", "Cristiano Ronaldo", "A"),
        ("Who holds the record for fastest goal in World Cup history?", "Hakan Sukur (11 seconds)", "Christian Eriksen", "Clint Dempsey", "Tim Cahill", "A"),
        ("Which player has won the most Champions League titles?", "Francisco Gento", "Cristiano Ronaldo", "Alfredo Di Stefano", "Paolo Maldini", "A"),
        ("Who was the first African to win the Ballon d'Or?", "George Weah", "Samuel Eto'o", "Didier Drogba", "Jay-Jay Okocha", "A"),
        ("Which player has played for the most clubs in their career?", "Sebastian Abreu", "Zlatan Ibrahimovic", "Nicolas Anelka", "Rivaldo", "A"),
        ("Who holds the record for oldest player to score in the Premier League?", "Teddy Sheringham", "Ryan Giggs", "Graham Alexander", "Dean Windass", "A"),
        ("Which player scored in every minute of a football match?", "No single player", "Cristiano Ronaldo", "Lionel Messi", "Zlatan Ibrahimovic", "A"),
        ("Who is the most capped player in international football history?", "Bader Al-Mutawa", "Ahmed Hassan", "Cristiano Ronaldo", "Sergio Ramos", "A"),
        ("Which player has won the most domestic league titles?", "Hossam Hassan", "Ryan Giggs", "Lionel Messi", "Dani Alves", "A"),
        ("Who scored the winner in the 2010 World Cup final?", "Andres Iniesta", "David Villa", "Xavi", "Fernando Torres", "A"),
        ("Which English player has scored the most World Cup goals?", "Gary Lineker", "Geoff Hurst", "Bobby Charlton", "Michael Owen", "A"),
        ("Who was the first player to score 50 Premier League goals?", "Alan Shearer", "Andy Cole", "Les Ferdinand", "Robbie Fowler", "A"),
        ("Which player is known as 'The Phenomenon'?", "Ronaldo Nazario", "Cristiano Ronaldo", "Ronaldinho", "Romario", "A"),
        ("Who is the youngest player to win a World Cup?", "Pele", "Kylian Mbappe", "Giuseppe Bergomi", "Norman Whiteside", "A"),
        ("Which player has the most assists in World Cup history?", "Pele", "Diego Maradona", "Lionel Messi", "Thomas Muller", "A"),
        ("Who scored the 'Scorpion Kick' in international football?", "Rene Higuita", "Zlatan Ibrahimovic", "Wayne Rooney", "Olivier Giroud", "A"),
        ("Which player holds the record for most Serie A goals?", "Silvio Piola", "Gabriel Batistuta", "Francesco Totti", "Alessandro Del Piero", "A"),
        ("Who was the first woman to win the Ballon d'Or Feminin?", "Ada Hegerberg", "Megan Rapinoe", "Marta", "Alexia Putellas", "A"),
        ("Which player has scored the most goals in a single Premier League season?", "Mohamed Salah and Erling Haaland (36)", "Andy Cole", "Alan Shearer", "Thierry Henry", "A"),
        ("Who holds the record for most Bundesliga goals?", "Gerd Muller", "Robert Lewandowski", "Klaus Fischer", "Karl-Heinz Rummenigge", "A"),
        ("Which player won the Golden Boot at the 2022 World Cup?", "Kylian Mbappe", "Lionel Messi", "Olivier Giroud", "Julian Alvarez", "A"),
        ("Who is known as 'The Egyptian King'?", "Mohamed Salah", "Ahmed Hassan", "Mohamed Aboutrika", "Essam El-Hadary", "A"),
        ("Which player scored in consecutive World Cup finals?", "Kylian Mbappe", "Pele", "Zinedine Zidane", "Ronaldo", "A"),
        ("Who holds the record for most career hat-tricks?", "Cristiano Ronaldo", "Lionel Messi", "Pele", "Gerd Muller", "A"),
        ("Which player has won the Copa America the most times?", "Lionel Messi", "Dani Alves", "Neymar", "Luis Suarez", "A"),
        ("Who was the first player transferred for over 1 million pounds?", "Trevor Francis", "Johan Cruyff", "Diego Maradona", "Kevin Keegan", "A"),
        ("Which player has scored the most goals from outside the box in PL history?", "Frank Lampard", "Steven Gerrard", "Paul Scholes", "David Beckham", "A"),
    ]
    for d in data:
        opts = list(d[1:5])
        correct_text = d[1]
        random.shuffle(opts)
        correct_letter = chr(65 + opts.index(correct_text))
        questions.append(q(d[0], opts[0], opts[1], opts[2], opts[3], correct_letter))
    return questions

def generate_country():
    """Generate Country / national team questions"""
    questions = []
    data = [
        ("Which country has won the most World Cups?", "Brazil", "Germany", "Italy", "Argentina", "A"),
        ("How many World Cups has Brazil won?", "5", "4", "6", "3", "A"),
        ("Which country won the 2022 World Cup?", "Argentina", "France", "Croatia", "Brazil", "A"),
        ("Which European country has won the most European Championships?", "Germany and Spain (3 each)", "France", "Italy", "Netherlands", "A"),
        ("What is the national football team of the Netherlands known as?", "Oranje", "Les Bleus", "La Roja", "Azzurri", "A"),
        ("Which country is known as 'La Roja'?", "Spain", "Chile", "Portugal", "Colombia", "A"),
        ("What nickname is given to the Italian national team?", "Azzurri", "La Roja", "Die Mannschaft", "Les Bleus", "A"),
        ("Which African nation has won the most Africa Cup of Nations titles?", "Egypt", "Cameroon", "Ghana", "Nigeria", "A"),
        ("How many World Cups has Germany won?", "4", "3", "5", "2", "A"),
        ("Which country won Euro 2020 (played in 2021)?", "Italy", "England", "Spain", "Denmark", "A"),
        ("Which is the only country to have played in every World Cup?", "Brazil", "Germany", "Italy", "Argentina", "A"),
        ("Who is the all-time top scorer for Brazil?", "Neymar", "Pele", "Ronaldo", "Romario", "A"),
        ("Which country did NOT win the 2018 World Cup?", "Croatia", "France", "Belgium", "England", "A"),
        ("What is the name of the French national team?", "Les Bleus", "La Roja", "Azzurri", "Oranje", "A"),
        ("Which South American country has won the most Copa Americas?", "Uruguay", "Argentina", "Brazil", "Chile", "A"),
        ("How many Copa Americas has Uruguay won?", "15", "9", "12", "7", "A"),
        ("Which country won the first European Championship in 1960?", "Soviet Union", "West Germany", "France", "Spain", "A"),
        ("What is Germany's national team known as?", "Die Mannschaft", "Azzurri", "Les Bleus", "Oranje", "A"),
        ("Which Asian country has qualified for the most World Cups?", "Japan/South Korea", "Saudi Arabia", "Iran", "Australia", "A"),
        ("Which country has never won a World Cup despite multiple finals?", "Netherlands", "Hungary", "Sweden", "Czech Republic", "A"),
        ("How many times has France won the World Cup?", "2", "1", "3", "0", "A"),
        ("Which country won the 2019 Women's World Cup?", "United States", "Netherlands", "Sweden", "England", "A"),
        ("What is Portugal's national team nickname?", "Selecao das Quinas", "La Roja", "Azzurri", "Die Mannschaft", "A"),
        ("Which country has won the most Olympic gold medals in football?", "Great Britain (early) / Hungary", "Brazil", "Argentina", "Uruguay", "A"),
        ("How many World Cups has Argentina won?", "3", "2", "4", "1", "A"),
        ("Which country hosted the 2010 World Cup?", "South Africa", "Brazil", "Germany", "Russia", "A"),
        ("What is the nickname of the Nigerian national team?", "Super Eagles", "Indomitable Lions", "Black Stars", "Pharaohs", "A"),
        ("Which country is home to the 'Indomitable Lions'?", "Cameroon", "Nigeria", "Ghana", "Ivory Coast", "A"),
        ("What is the nickname of the South Korean national team?", "Taegeuk Warriors", "Samurai Blue", "Socceroos", "All Whites", "A"),
        ("Which country won the 2023 Women's World Cup?", "Spain", "England", "United States", "Sweden", "A"),
        ("How many times has England won the World Cup?", "1", "2", "0", "3", "A"),
        ("Which Central American country is the most successful in World Cups?", "Mexico", "Costa Rica", "Honduras", "Panama", "A"),
        ("What is the nickname of the Ivory Coast national team?", "Les Elephants", "Super Eagles", "Indomitable Lions", "Black Stars", "A"),
        ("Which country hosted Euro 2024?", "Germany", "France", "England", "Spain", "A"),
        ("What is Japan's national team known as?", "Samurai Blue", "Taegeuk Warriors", "Socceroos", "Red Devils", "A"),
        ("Which country won the 2021 Copa America?", "Argentina", "Brazil", "Colombia", "Uruguay", "A"),
        ("How many times has Italy won the World Cup?", "4", "3", "5", "2", "A"),
        ("Which Nordic country has the best World Cup record?", "Sweden", "Denmark", "Norway", "Finland", "A"),
        ("What is the nickname of the Croatian national team?", "Vatreni (The Blazers)", "The White Eagles", "Red Devils", "Les Bleus", "A"),
        ("Which country won the 2022 Africa Cup of Nations?", "Senegal", "Egypt", "Cameroon", "Algeria", "A"),
        ("How many World Cup titles does Uruguay have?", "2", "1", "3", "0", "A"),
        ("Which country has the 'All Whites' as their national team?", "New Zealand", "Australia", "England", "Wales", "A"),
        ("What is the Belgian national team nickname?", "Red Devils", "Les Bleus", "Oranje", "Die Mannschaft", "A"),
        ("Which country hosted the 2014 World Cup?", "Brazil", "South Africa", "Russia", "Qatar", "A"),
        ("Which country has won the most Asian Cups?", "Japan", "Saudi Arabia", "Iran", "South Korea", "A"),
        ("What is the Ghanaian national team called?", "Black Stars", "Super Eagles", "Les Elephants", "Indomitable Lions", "A"),
        ("Which country won Euro 2016?", "Portugal", "France", "Germany", "Spain", "A"),
        ("How many consecutive World Cup finals has Croatia reached (as of 2022)?", "2", "1", "3", "0", "A"),
    ]
    for d in data:
        opts = list(d[1:5])
        correct_text = d[1]
        random.shuffle(opts)
        correct_letter = chr(65 + opts.index(correct_text))
        questions.append(q(d[0], opts[0], opts[1], opts[2], opts[3], correct_letter))
    return questions

def generate_fan_culture():
    """Generate Fan Culture questions"""
    questions = []
    data = [
        ("What song do Liverpool fans sing before matches?", "You'll Never Walk Alone", "Hey Jude", "Don't Look Back in Anger", "Sweet Caroline", "A"),
        ("Which team's fans are known as 'The Kop'?", "Liverpool", "Everton", "Manchester United", "Leeds United", "A"),
        ("What is the name of the ultras group at Borussia Dortmund?", "The Unity", "Yellow Wall", "Suedtribuene", "BVB Ultras", "A"),
        ("Which club's fans wave the 'Poznan'?", "Lech Poznan / Manchester City", "Arsenal", "Chelsea", "Tottenham", "A"),
        ("What colour card do fans wave at Real Madrid?", "White handkerchiefs", "Red scarves", "Blue flags", "Green banners", "A"),
        ("Which derby is known as 'El Clasico'?", "Real Madrid vs Barcelona", "AC Milan vs Inter", "River Plate vs Boca Juniors", "Celtic vs Rangers", "A"),
        ("What is the 'Old Firm' derby?", "Celtic vs Rangers", "Liverpool vs Everton", "Arsenal vs Tottenham", "AC Milan vs Inter", "A"),
        ("Which city hosts the 'Derby della Madonnina'?", "Milan", "Rome", "Madrid", "Buenos Aires", "A"),
        ("What is the name of the Buenos Aires derby between River Plate and Boca?", "Superclasico", "El Clasico", "Derby della Madonnina", "Old Firm", "A"),
        ("Which fan movement started the 'tifo' tradition?", "Italian ultras", "English hooligans", "South American barras bravas", "German supporters", "A"),
        ("What does 'tifo' refer to in football?", "Choreographed fan displays", "A type of chant", "A supporters club", "A fan token", "A"),
        ("Which English derby is called the 'North London Derby'?", "Arsenal vs Tottenham", "Chelsea vs Fulham", "West Ham vs Millwall", "QPR vs Brentford", "A"),
        ("What do Barcelona fans throw onto the pitch during El Clasico?", "Pig heads (historically)", "Oranges", "Toilet rolls", "Coins", "A"),
        ("Which team's supporters are known as 'Gooners'?", "Arsenal", "Chelsea", "Tottenham", "West Ham", "A"),
        ("What is the 'Merseyside Derby'?", "Liverpool vs Everton", "Manchester United vs Manchester City", "Arsenal vs Tottenham", "Chelsea vs West Ham", "A"),
        ("Which team's fans sing 'Blue Moon'?", "Manchester City", "Chelsea", "Everton", "Leicester City", "A"),
        ("What is the Manchester derby?", "Manchester United vs Manchester City", "Liverpool vs Everton", "Arsenal vs Tottenham", "Chelsea vs Fulham", "A"),
        ("Which country's fans are known for the 'Icelandic clap' (Viking Thunder Clap)?", "Iceland", "Norway", "Sweden", "Denmark", "A"),
        ("What is the name of the wall of fans at Dortmund's Signal Iduna Park?", "Yellow Wall (Sudtribune)", "The Kop", "The Stretford End", "The Holte End", "A"),
        ("Which club's anthem is 'Hala Madrid'?", "Real Madrid", "Atletico Madrid", "Barcelona", "Valencia", "A"),
        ("What do Celtic fans call their stadium atmosphere?", "The Green Hell", "The Jungle", "Paradise", "The Caldron", "A"),
        ("Which derby is known as the 'Revierderby'?", "Borussia Dortmund vs Schalke 04", "Bayern vs Dortmund", "Hamburg vs St Pauli", "Hertha vs Union Berlin", "A"),
        ("What is the 'Steel City Derby'?", "Sheffield United vs Sheffield Wednesday", "Birmingham vs Aston Villa", "Bristol City vs Bristol Rovers", "Nottingham Forest vs Notts County", "A"),
        ("Which fans are famous for the 'Allez Allez Allez' chant?", "Liverpool", "PSG", "Napoli", "Marseille", "A"),
        ("What is the name of Napoli's most famous ultras?", "Curva A and Curva B", "The Yellow Wall", "The Kop", "Brigate", "A"),
        ("Which South American fan group is known as 'La 12'?", "Boca Juniors", "River Plate", "Flamengo", "Sao Paulo", "A"),
        ("What does 'Barra Brava' mean?", "Brave Gang (ultras group)", "Red Bar", "Strong Stand", "Fight Club", "A"),
        ("Which Premier League team has 'Bubbles' as their anthem?", "West Ham United", "Burnley", "Crystal Palace", "Leicester City", "A"),
        ("What song is associated with West Ham United?", "I'm Forever Blowing Bubbles", "Blue Moon", "You'll Never Walk Alone", "Glory Glory", "A"),
        ("Which team's fans are known as 'The Toon Army'?", "Newcastle United", "Sunderland", "Middlesbrough", "Leeds United", "A"),
        ("What is the 'Tyne-Wear Derby'?", "Newcastle vs Sunderland", "Sheffield Utd vs Sheffield Wed", "Liverpool vs Everton", "Bristol City vs Bristol Rovers", "A"),
        ("Which country's league has the most passionate atmosphere in South America?", "Argentina", "Brazil", "Colombia", "Uruguay", "A"),
        ("What is the 'Superga tragedy' related to?", "Torino FC plane crash (1949)", "Munich air disaster", "Hillsborough", "Heysel", "A"),
        ("Which club's fans famously sing 'Sweet Caroline'?", "England national team", "Newcastle United", "West Ham", "Liverpool", "A"),
        ("What is the name of the rivalry between Roma and Lazio?", "Derby della Capitale", "Derby della Madonnina", "Superclasico", "El Clasico", "A"),
        ("Which English club has 'Gladiator' as their entrance music?", "Tottenham Hotspur", "Arsenal", "Chelsea", "Manchester United", "A"),
        ("What is a 'double-decker' in fan culture?", "A two-tier choreography display", "Two consecutive wins", "A large banner", "A type of scarf", "A"),
        ("Which club's supporters group is called 'The Shed'?", "Chelsea", "Arsenal", "Liverpool", "Manchester City", "A"),
        ("What is the 'Seattle Sounders' fan group called?", "Emerald City Supporters", "Green Brigade", "Section 8", "District Ultras", "A"),
        ("Which tradition involves fans throwing a ball into the crowd before kickoff?", "Ball toss tradition (various)", "The Poznan", "The Viking Clap", "The Mexican Wave", "A"),
    ]
    for d in data:
        opts = list(d[1:5])
        correct_text = d[1]
        random.shuffle(opts)
        correct_letter = chr(65 + opts.index(correct_text))
        questions.append(q(d[0], opts[0], opts[1], opts[2], opts[3], correct_letter))
    return questions

def generate_league():
    """Generate League knowledge questions"""
    questions = []
    data = [
        ("How many teams play in the English Premier League?", "20", "18", "22", "16", "A"),
        ("Which league is known as the 'best league in the world'?", "Premier League", "La Liga", "Bundesliga", "Serie A", "A"),
        ("How many teams are promoted to the Premier League each season?", "3", "2", "4", "1", "A"),
        ("Which league has the most global TV viewers?", "Premier League", "La Liga", "Serie A", "Bundesliga", "A"),
        ("How many teams play in La Liga?", "20", "18", "22", "16", "A"),
        ("Which German league is known for its 50+1 ownership rule?", "Bundesliga", "Premier League", "Serie A", "Ligue 1", "A"),
        ("How many teams play in the Bundesliga?", "18", "20", "16", "22", "A"),
        ("Which Italian league is the top division?", "Serie A", "Serie B", "Serie C", "Calcio A", "A"),
        ("How many teams play in Serie A?", "20", "18", "22", "16", "A"),
        ("What is the top division of French football?", "Ligue 1", "Ligue 2", "Division 1", "Championnat", "A"),
        ("Which league does the MLS belong to?", "United States and Canada", "Mexico", "Brazil", "Argentina", "A"),
        ("How many teams are relegated from the Premier League each season?", "3", "2", "4", "1", "A"),
        ("What is the name of the Portuguese top division?", "Primeira Liga", "Super Liga", "Liga NOS", "Liga Portugal", "A"),
        ("Which league has had the most different champions in the last 20 years?", "Ligue 1", "Premier League", "La Liga", "Serie A", "A"),
        ("How many teams play in the Scottish Premiership?", "12", "10", "16", "20", "A"),
        ("Which league uses a winter break?", "Bundesliga", "Premier League", "MLS", "A-League", "A"),
        ("What is the second tier of English football called?", "Championship", "League One", "League Two", "National League", "A"),
        ("Which country's league is called the 'Eredivisie'?", "Netherlands", "Belgium", "Denmark", "Sweden", "A"),
        ("How many teams play in the Eredivisie?", "18", "20", "16", "14", "A"),
        ("What is the Turkish top division called?", "Super Lig", "Turkiye Ligi", "Birinci Lig", "Premier Lig", "A"),
        ("Which league was dominated by Celtic and Rangers?", "Scottish Premiership", "Irish Premier", "Welsh Premier", "Northern Irish", "A"),
        ("How many matchdays are in a Premier League season?", "38", "34", "36", "40", "A"),
        ("Which league has the highest average attendance in the world?", "Bundesliga", "Premier League", "La Liga", "Serie A", "A"),
        ("What is the Brazilian top division called?", "Serie A (Brasileirao)", "La Liga", "Premier League", "Super Liga", "A"),
        ("Which league does not have promotion and relegation?", "MLS", "Premier League", "Bundesliga", "La Liga", "A"),
        ("How many league titles has Manchester United won?", "20", "18", "13", "22", "A"),
        ("Which team has won the most Premier League titles?", "Manchester United", "Manchester City", "Chelsea", "Arsenal", "A"),
        ("How many La Liga titles has Real Madrid won?", "36", "30", "25", "34", "A"),
        ("Which team has won the most Serie A titles?", "Juventus", "AC Milan", "Inter Milan", "AS Roma", "A"),
        ("How many Bundesliga titles has Bayern Munich won?", "33", "25", "30", "20", "A"),
        ("Which team has won the most Ligue 1 titles?", "Paris Saint-Germain", "Marseille", "Saint-Etienne", "Lyon", "A"),
        ("What year did Leicester City win the Premier League?", "2016", "2015", "2017", "2014", "A"),
        ("Which was the last team outside the top 4 to win La Liga?", "Atletico Madrid", "Valencia", "Deportivo", "Real Sociedad", "A"),
        ("How many points for a win in most European leagues?", "3", "2", "1", "4", "A"),
        ("Which English club has been relegated the most times from the top flight?", "Birmingham City", "Sunderland", "Norwich City", "West Brom", "A"),
        ("What is the promotion playoff in English football?", "Championship playoff final", "Relegation battle", "Cup match", "League decider", "A"),
        ("Which league introduced the 'luxury tax'?", "MLS", "Premier League", "Ligue 1", "Bundesliga", "A"),
        ("How many teams are in the J-League (Japan)?", "18", "20", "16", "14", "A"),
        ("What is the Argentine top division called?", "Liga Profesional", "Primera Division", "Super Liga", "Nacional B", "A"),
        ("Which league had the 'Calciopoli' scandal?", "Serie A", "La Liga", "Ligue 1", "Bundesliga", "A"),
        ("How many matchdays are in a Bundesliga season?", "34", "38", "36", "30", "A"),
        ("Which Premier League team went unbeaten in 2003-04?", "Arsenal", "Manchester United", "Chelsea", "Liverpool", "A"),
        ("What nickname was given to Arsenal's unbeaten season?", "The Invincibles", "The Unstoppables", "The Immortals", "The Unbeatable", "A"),
        ("Which team won the first three Premier League titles?", "Manchester United", "Blackburn Rovers", "Arsenal", "Liverpool", "A"),
        ("How many teams are in Mexico's Liga MX?", "18", "20", "16", "22", "A"),
    ]
    for d in data:
        opts = list(d[1:5])
        correct_text = d[1]
        random.shuffle(opts)
        correct_letter = chr(65 + opts.index(correct_text))
        questions.append(q(d[0], opts[0], opts[1], opts[2], opts[3], correct_letter))
    return questions

async def insert_all():
    all_questions = []
    
    print("Generating Stadiums...")
    all_questions.extend([(cat, *q_data) for q_data in generate_stadiums() for cat in ["Stadiums"]])
    
    print("Generating Champions League...")
    all_questions.extend([(cat, *q_data) for q_data in generate_champions_league() for cat in ["Champions League"]])
    
    print("Generating History...")
    all_questions.extend([(cat, *q_data) for q_data in generate_history() for cat in ["History"]])
    
    print("Generating Players...")
    all_questions.extend([(cat, *q_data) for q_data in generate_players() for cat in ["Players"]])
    
    print("Generating Country...")
    all_questions.extend([(cat, *q_data) for q_data in generate_country() for cat in ["Country"]])
    
    print("Generating Fan Culture...")
    all_questions.extend([(cat, *q_data) for q_data in generate_fan_culture() for cat in ["Fan Culture"]])
    
    print("Generating League...")
    all_questions.extend([(cat, *q_data) for q_data in generate_league() for cat in ["League"]])
    
    print(f"\nTotal new questions: {len(all_questions)}")
    
    async with engine.begin() as conn:
        for cat, qid, qt, oa, ob, oc, od, correct in all_questions:
            await conn.execute(text(
                "INSERT INTO questions (id, question_text, option_a, option_b, option_c, option_d, correct_option, category) "
                "VALUES (:id, :qt, :oa, :ob, :oc, :od, :co, :cat)"
            ), {"id": qid, "qt": qt, "oa": oa, "ob": ob, "oc": oc, "od": od, "co": correct, "cat": cat})
        
        # Verify
        r = await conn.execute(text("SELECT category, COUNT(*) FROM questions GROUP BY category ORDER BY COUNT(*) DESC"))
        print("\nFinal category counts:")
        for cat, count in r.fetchall():
            print(f"  {cat}: {count}")

asyncio.run(insert_all())
