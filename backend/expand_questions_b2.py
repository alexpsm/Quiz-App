"""Batch 2: Expand Rules, Terminology, International Tournaments + more for all thin categories"""
import asyncio
import uuid
import random
from database import engine
from sqlalchemy import text

def q(question_text, a, b, c, d, correct):
    return (str(uuid.uuid4()), question_text, a, b, c, d, correct)

def shuffle_q(data_list):
    questions = []
    for d in data_list:
        opts = list(d[1:5])
        correct_text = d[1]
        random.shuffle(opts)
        correct_letter = chr(65 + opts.index(correct_text))
        questions.append(q(d[0], opts[0], opts[1], opts[2], opts[3], correct_letter))
    return questions

def gen_rules():
    data = [
        ("How many players are on the field for each team at the start?", "11", "10", "12", "9", "A"),
        ("How long is a standard football match?", "90 minutes", "80 minutes", "100 minutes", "120 minutes", "A"),
        ("What does VAR stand for?", "Video Assistant Referee", "Visual Aid Replay", "Video Analysis Review", "Virtual Assistant Referee", "A"),
        ("What colour card results in a player being sent off?", "Red", "Yellow", "Green", "Blue", "A"),
        ("How many substitutions are allowed in most competitions?", "5", "3", "4", "6", "A"),
        ("What is the penalty area distance from the goal line?", "18 yards", "16 yards", "20 yards", "12 yards", "A"),
        ("How far is the penalty spot from the goal?", "12 yards", "10 yards", "11 yards", "14 yards", "A"),
        ("What is the maximum number of players on a matchday squad?", "Depends on competition", "18", "20", "16", "A"),
        ("What happens if a match ends in a draw in a knockout competition?", "Extra time then penalties", "Replay", "Coin toss", "Golden goal", "A"),
        ("How wide is a standard football goal?", "8 yards (7.32m)", "7 yards", "9 yards", "10 yards", "A"),
        ("How tall is a standard football goal?", "8 feet (2.44m)", "7 feet", "9 feet", "10 feet", "A"),
        ("What is the circumference of a regulation football?", "68-70 cm", "60-62 cm", "72-74 cm", "65-67 cm", "A"),
        ("What is the radius of the centre circle?", "10 yards", "8 yards", "12 yards", "15 yards", "A"),
        ("Can a goalkeeper handle the ball outside their penalty area?", "No", "Yes", "Only in their half", "Only from a throw-in", "A"),
        ("What is a direct free kick?", "A kick where you can score directly", "A kick that must be passed first", "A kick from the corner", "A goal kick", "A"),
        ("When is an indirect free kick awarded?", "For non-contact fouls", "For every foul", "Only in the box", "For handballs", "A"),
        ("What must happen before a corner kick is taken?", "Ball must be in the corner arc", "All players must be in the box", "Ref must blow whistle", "Opposition must be 5 yards away", "A"),
        ("How far must defenders stand from a free kick?", "10 yards (9.15m)", "8 yards", "12 yards", "15 yards", "A"),
        ("Can a player be offside from a goal kick?", "No", "Yes", "Only if in the box", "Only in extra time", "A"),
        ("Can a player be offside from a throw-in?", "No", "Yes", "Only in the opponent's half", "Only if behind the ball", "A"),
        ("What is the 'advantage rule'?", "Play continues if fouled team benefits", "The winning team gets advantages", "Extra time for the leading team", "Goal difference tiebreaker", "A"),
        ("What happens if a player receives two yellow cards?", "They are shown a red card and sent off", "They get a warning", "They miss the next game only", "Nothing until third yellow", "A"),
        ("Can an outfield player switch with the goalkeeper during play?", "Yes, with referee's permission", "No, never", "Only at half time", "Only during substitution", "A"),
        ("What is ABBA penalty format?", "Alternating order (1-2, 2-1, 1-2...)", "Sudden death from start", "Five penalties each", "Best of three", "A"),
        ("How long is each half of extra time?", "15 minutes", "10 minutes", "20 minutes", "30 minutes", "A"),
        ("What is the 'six-second rule' for goalkeepers?", "Must release ball within 6 seconds", "Must stay in box for 6 seconds", "Must wait 6 seconds after save", "Must not move for 6 seconds", "A"),
        ("Can a penalty be passed to a teammate?", "Yes", "No", "Only in friendlies", "Only in cup matches", "A"),
        ("What is 'simulation' in football?", "Diving to win a foul", "Running fast", "Tactical play", "Defensive block", "A"),
        ("When was the back-pass rule introduced?", "1992", "1990", "1994", "1988", "A"),
        ("What is the purpose of added time (stoppage time)?", "Compensate for stoppages during play", "Add excitement", "Give trailing team a chance", "TV scheduling", "A"),
        ("How many officials are there in a standard match?", "4 (referee, 2 assistants, 4th official)", "3", "5", "2", "A"),
        ("What does the fourth official do?", "Manages substitutions, displays added time", "Watches for offsides", "Takes penalties", "Coaches both teams", "A"),
        ("Can a goal be scored directly from a kick-off?", "Yes", "No", "Only in the first half", "Only after half time", "A"),
        ("What is the 'DOGSO' rule?", "Denial of obvious goal-scoring opportunity (red card)", "Direct offensive goal scoring option", "Defensive offside gets sent off", "Dangerous opponent gets stopped", "A"),
        ("Can a substitute be given a red card while on the bench?", "Yes", "No", "Only yellow cards", "Only warnings", "A"),
        ("What is a 'professional foul'?", "A deliberate foul to stop an attack", "A foul by a professional player", "A foul in the penalty area", "An accidental foul", "A"),
        ("How many players must a team have to continue a match?", "7", "8", "9", "6", "A"),
        ("Can a goal kick be taken from anywhere in the goal area?", "Yes", "No, only from the 6-yard line", "Only from the goal line", "Only from the centre of the area", "A"),
        ("What is 'encroachment' at a penalty kick?", "Players entering the box before the kick", "Goalkeeper moving off line", "Kicker stuttering", "Ball not on the spot", "A"),
        ("When is a drop ball used?", "When play stops for no foul", "After every goal", "At half time", "For injuries only", "A"),
        ("Can a player score an own goal from a throw-in?", "No (corner kick awarded)", "Yes", "Only in extra time", "Only if keeper handles it", "A"),
        ("What is the 'triple punishment' rule change?", "Penalty fouls no longer automatic red card", "Three yellows equal a ban", "Three goals win automatically", "Three subs allowed", "A"),
        ("Can VAR overturn a yellow card to a red?", "Yes", "No", "Only for violent conduct", "Only the referee decides", "A"),
        ("What is the handball rule regarding arm position?", "Arm must be in unnatural position", "Any touch is handball", "Only intentional is handball", "Goalkeeper rules only", "A"),
        ("Can a team make a substitution during a penalty shootout?", "Only for injured goalkeeper", "Yes, any player", "No, never", "Only one sub", "A"),
        ("What is concussion substitution protocol?", "Extra permanent sub for head injury", "Temporary sub for assessment", "No sub needed", "Player must leave field 10 mins", "A"),
    ]
    return shuffle_q(data)

def gen_terminology():
    data = [
        ("What is a hat-trick?", "Three goals by one player in a match", "Three wins in a row", "Three saves in a row", "Three assists in a match", "A"),
        ("What does 'nutmeg' mean?", "Passing the ball between an opponent's legs", "A type of free kick", "A defensive move", "Scoring from distance", "A"),
        ("What is a 'brace'?", "Two goals by one player in a match", "A leg injury", "A defensive formation", "A goal from a corner", "A"),
        ("What does 'parking the bus' mean?", "Playing very defensively", "Driving to the stadium", "Attacking with all players", "Playing with 10 men", "A"),
        ("What is 'tiki-taka'?", "Short passing possession style", "Long ball style", "Counter-attack style", "High pressing", "A"),
        ("What does 'clean sheet' mean?", "Not conceding a goal", "Winning by 3+ goals", "No cards received", "Perfect passing", "A"),
        ("What is a 'false nine'?", "A striker who drops deep into midfield", "A defender who plays up front", "A substitute striker", "A number 9 jersey without a player", "A"),
        ("What is 'gegenpressing'?", "Immediate counter-pressing after losing the ball", "Slow build-up play", "Defensive deep block", "Long ball strategy", "A"),
        ("What does 'catenaccio' mean?", "Italian defensive system (chain/lock)", "Chain of passes", "Goal celebration", "A type of dribble", "A"),
        ("What is a 'sweeper keeper'?", "Goalkeeper who plays outside the box", "A cleaner at the stadium", "A substitute goalkeeper", "A defender who sweeps", "A"),
        ("What does 'total football' refer to?", "Any player can play any position", "Scoring the most goals", "Playing all 90 minutes", "Using all substitutions", "A"),
        ("What is a 'box-to-box midfielder'?", "A midfielder who covers the full length of the pitch", "A midfielder who stays in the box", "A defensive midfielder only", "An attacking midfielder only", "A"),
        ("What is the 'Panenka' penalty?", "A chipped penalty down the middle", "A powerful penalty to the corner", "A penalty off the post", "A saved penalty", "A"),
        ("What does 'El Clasico' mean?", "The Classic (Real Madrid vs Barcelona)", "The Derby", "The Cup Final", "The Championship", "A"),
        ("What is a 'Rabona'?", "Kicking ball with leg crossed behind standing leg", "A bicycle kick", "A header", "A backpass", "A"),
        ("What is a 'bicycle kick'?", "An overhead kick while airborne", "Kicking with both feet", "A spinning kick", "A penalty technique", "A"),
        ("What does 'aggregate' mean?", "Total score over two legs", "Goal difference", "Points total", "Average score", "A"),
        ("What is 'injury time'?", "Added time for stoppages during the half", "Time when players are injured", "Break for medical treatment", "Post-match recovery", "A"),
        ("What does 'on the counter' mean?", "Counter-attacking quickly", "Defending near the goal", "Taking a corner", "Counting passes", "A"),
        ("What is a 'wondergoal'?", "An exceptional or spectacular goal", "A lucky goal", "An own goal", "A penalty", "A"),
        ("What does 'route one' football mean?", "Long ball from defence to attack", "Passing through the centre", "Playing down the flanks", "Slow build-up play", "A"),
        ("What is a 'derby'?", "A match between local rival teams", "A championship match", "A cup final", "A friendly match", "A"),
        ("What is 'pressing'?", "Pressuring opponents high up the pitch", "Ironing jerseys", "Passing accurately", "Defending deep", "A"),
        ("What does 'the double' mean?", "Winning the league and cup in one season", "Scoring twice", "Two consecutive wins", "A double save", "A"),
        ("What is 'the treble'?", "Winning league, domestic cup, and Champions League", "Three goals", "Three consecutive wins", "Three trophies in a career", "A"),
        ("What is a 'target man'?", "A tall striker who holds up play", "A penalty taker", "A defensive midfielder", "A goalkeeper", "A"),
        ("What does 'through ball' mean?", "A pass played into space behind defenders", "A ball that goes through the goal", "A cross from the wing", "A backpass to the keeper", "A"),
        ("What is 'man marking'?", "Following a specific opponent wherever they go", "Marking the pitch", "Zonal defending", "Marking goal kicks", "A"),
        ("What does 'zonal marking' mean?", "Defending an area rather than a specific player", "Marking the zones on the pitch", "Playing in zones", "A substitution system", "A"),
        ("What is a 'long throw'?", "A throw-in that reaches the penalty area", "A normal throw", "A goal kick", "A free kick from distance", "A"),
        ("What is 'time wasting'?", "Deliberately slowing down play", "Playing extra time", "Running out the clock legally", "Taking too many substitutions", "A"),
        ("What does 'the wall' refer to in football?", "Line of defenders at a free kick", "The stadium wall", "A defensive formation", "The goal frame", "A"),
        ("What is a 'dead ball situation'?", "Free kick, corner, penalty, throw-in", "When the ball is flat", "End of the match", "Ball out of play", "A"),
        ("What is 'pressing trigger'?", "A signal to start pressing the opponent", "A foul that causes pressing", "A referee's whistle", "A tactical timeout", "A"),
        ("What does 'inverted winger' mean?", "A winger who cuts inside onto stronger foot", "A winger who stays wide", "A defender playing as winger", "A winger who plays backwards", "A"),
        ("What is a 'regista'?", "A deep-lying playmaker", "A striker", "A winger", "A centre-back", "A"),
        ("What does 'mezzala' mean in football tactics?", "A central midfielder who drifts wide", "A defensive midfielder", "A striker", "A wing-back", "A"),
        ("What is 'gegenpressing' associated with?", "Jurgen Klopp", "Pep Guardiola", "Jose Mourinho", "Carlo Ancelotti", "A"),
        ("What does 'second balls' refer to?", "Loose balls after an aerial duel", "Reserve match balls", "Practice balls", "Half-time balls", "A"),
        ("What is a 'half-volley'?", "Striking ball just after it bounces", "Kicking ball in mid-air", "A weak shot", "A header", "A"),
        ("What does 'overload' mean tactically?", "Having numerical advantage in an area", "Too many players on the pitch", "Too many substitutions", "Playing extra time", "A"),
    ]
    return shuffle_q(data)

def gen_intl_tournaments():
    data = [
        ("Which country has won the most FIFA World Cups?", "Brazil (5)", "Germany (4)", "Italy (4)", "Argentina (3)", "A"),
        ("Where was the 2022 World Cup held?", "Qatar", "Russia", "Brazil", "South Africa", "A"),
        ("Who won the Golden Ball at the 2022 World Cup?", "Lionel Messi", "Kylian Mbappe", "Luka Modric", "Emiliano Martinez", "A"),
        ("Which team won Euro 2020?", "Italy", "England", "Spain", "Denmark", "A"),
        ("How often is the World Cup held?", "Every 4 years", "Every 2 years", "Every year", "Every 3 years", "A"),
        ("Which was the first World Cup held in Asia?", "2002 (Japan/South Korea)", "2022 (Qatar)", "2010 (South Africa)", "1994 (USA)", "A"),
        ("Who scored the most goals in World Cup history?", "Miroslav Klose", "Ronaldo (Brazil)", "Gerd Muller", "Just Fontaine", "A"),
        ("Which country won the first Women's World Cup in 1991?", "United States", "Norway", "Germany", "Sweden", "A"),
        ("Where was the 2018 World Cup held?", "Russia", "Brazil", "Qatar", "South Africa", "A"),
        ("Which nation won Euro 2024?", "Spain", "England", "France", "Germany", "A"),
        ("How many teams compete in the World Cup finals?", "32 (48 from 2026)", "24", "16", "64", "A"),
        ("Which country has hosted the most World Cups?", "Brazil, France, Italy, Germany, Mexico (2 each)", "Brazil", "Germany", "France", "A"),
        ("Who won the 2019 Copa America?", "Brazil", "Argentina", "Peru", "Chile", "A"),
        ("Which African nation won AFCON 2023?", "Ivory Coast", "Nigeria", "South Africa", "DR Congo", "A"),
        ("Where will the 2026 World Cup be held?", "USA, Canada, Mexico", "Saudi Arabia", "Australia", "Morocco", "A"),
        ("Who won the 2023 FIFA Club World Cup?", "Manchester City", "Real Madrid", "Flamengo", "Al Ahly", "A"),
        ("Which tournament is the oldest in football?", "FA Cup (1871)", "World Cup", "Copa America", "European Championship", "A"),
        ("What is the Nations League?", "UEFA national team competition", "A club competition", "A youth tournament", "A friendly series", "A"),
        ("Who won the first UEFA Nations League?", "Portugal", "Netherlands", "England", "Switzerland", "A"),
        ("Which country has won the most Copa Americas?", "Uruguay (15)", "Argentina (16)", "Brazil (9)", "Chile (2)", "A"),
        ("Where was Euro 2024 held?", "Germany", "England", "France", "Spain", "A"),
        ("Who was top scorer at the 2022 World Cup?", "Kylian Mbappe", "Lionel Messi", "Julian Alvarez", "Olivier Giroud", "A"),
        ("Which team won the Confederations Cup the most times?", "Brazil", "France", "Mexico", "Argentina", "A"),
        ("What year was the last Confederations Cup?", "2017", "2019", "2021", "2015", "A"),
        ("Which player has appeared in the most World Cups?", "Lionel Messi (5)", "Cristiano Ronaldo", "Antonio Carbajal", "Lothar Matthaus", "A"),
        ("Who won the Golden Boot at Euro 2020?", "Cristiano Ronaldo and Patrik Schick (5 goals each)", "Harry Kane", "Raheem Sterling", "Romelu Lukaku", "A"),
        ("Which country has won the most AFCON titles?", "Egypt (7)", "Cameroon (5)", "Ghana (4)", "Nigeria (3)", "A"),
        ("Where was the 2019 Women's World Cup held?", "France", "Canada", "Australia", "Japan", "A"),
        ("Who won the 2023 Women's World Cup?", "Spain", "England", "Sweden", "Japan", "A"),
        ("What is the penalty shootout record in World Cup finals?", "Argentina won most (3)", "Germany", "Brazil", "Italy", "A"),
        ("Which was the first World Cup with VAR?", "2018 Russia", "2014 Brazil", "2022 Qatar", "2010 South Africa", "A"),
        ("Who managed Spain to their 2010 World Cup victory?", "Vicente del Bosque", "Luis Enrique", "Xavi", "Luis Aragones", "A"),
        ("Which country has the most World Cup final appearances?", "Germany (8)", "Brazil (7)", "Argentina (6)", "Italy (6)", "A"),
        ("Who won the 2021 Copa America?", "Argentina", "Brazil", "Colombia", "Uruguay", "A"),
        ("What is the CONCACAF Gold Cup?", "North/Central American championship", "South American championship", "European championship", "African championship", "A"),
        ("Which Asian country has won the most Asian Cups?", "Japan (4)", "Saudi Arabia (3)", "Iran (3)", "South Korea (2)", "A"),
        ("What was the biggest margin of victory in World Cup history?", "Hungary 10-1 El Salvador (1982)", "Germany 8-0 Saudi Arabia", "Australia 31-0 American Samoa", "Brazil 7-1 over host (not WC)", "A"),
        ("Which World Cup had the 'Group of Death' with Germany, Spain, and Japan?", "2022 Qatar", "2018 Russia", "2014 Brazil", "2010 South Africa", "A"),
        ("Who scored the fastest goal in World Cup history?", "Hakan Sukur (11 seconds, 2002)", "Clint Dempsey", "Tim Cahill", "Valon Behrami", "A"),
        ("Which country hosted and won the 1998 World Cup?", "France", "Brazil", "Germany", "Italy", "A"),
    ]
    return shuffle_q(data)

async def insert_batch2():
    all_qs = []
    
    rules = gen_rules()
    print(f"Rules: {len(rules)}")
    all_qs.extend([("Rules", *q_data) for q_data in rules])
    
    term = gen_terminology()
    print(f"Terminology: {len(term)}")
    all_qs.extend([("Terminology", *q_data) for q_data in term])
    
    intl = gen_intl_tournaments()
    print(f"International Tournaments: {len(intl)}")
    all_qs.extend([("International Tournaments", *q_data) for q_data in intl])
    
    print(f"\nTotal batch 2: {len(all_qs)}")
    
    async with engine.begin() as conn:
        for cat, qid, qt, oa, ob, oc, od, correct in all_qs:
            await conn.execute(text(
                "INSERT INTO questions (id, question_text, option_a, option_b, option_c, option_d, correct_option, category) "
                "VALUES (:id, :qt, :oa, :ob, :oc, :od, :co, :cat)"
            ), {"id": qid, "qt": qt, "oa": oa, "ob": ob, "oc": oc, "od": od, "co": correct, "cat": cat})
        
        r = await conn.execute(text("SELECT category, COUNT(*) FROM questions GROUP BY category ORDER BY COUNT(*) DESC"))
        total = 0
        print("\nFinal counts:")
        for cat, count in r.fetchall():
            print(f"  {cat}: {count}")
            total += count
        print(f"\nGrand total: {total}")

asyncio.run(insert_batch2())
