from difflib import SequenceMatcher

with open('Logs/LogV3.txt', "r") as file:
    content = file.readlines()

with open('Resources/PokemonList.txt', "r") as pokemones:
    pokemon_list = pokemones.readlines()
    my_pokemon_list = []
    for a in pokemon_list:
        my_pokemon_list.append(a.strip())

with open('Resources/MovesList.txt', "r") as movimientos:
    move_list = movimientos.readlines()
    my_move_list = []
    for a in move_list:
        my_move_list.append(a.strip())

characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '


def similar(x, y):

    """ Takes 2 arguments: (string, string)
        Returns the percentage (0 to 1) of similarity between the 2 strings """

    return SequenceMatcher(None, x, y).ratio()


def get_similar_from_list(my_string, my_list):

    """
    :param my_string: string to look for in my_list
    :param my_list: List of strings
    :return: One string from my_list which is the most similar to my_string
    """

    previous_similar = 0
    final_string = ''
    for item in my_list:
        current_similar = similar(my_string, item)
        if current_similar > previous_similar:
            final_string = item
            previous_similar = current_similar

    return final_string


def parse_string(line, start, end):
    """
    :param line: String to analyze
    :param start: String index starting point
    :param end: String index ending point
    :return: parsed string in base of global characters variable
    """
    global characters

    limit1 = None
    limit2 = None

    if type(start) == str:
        limit1 = line.find(start)
        limit1 = limit1 + len(start)
    elif type(start) == int:
        limit1 = start

    if type(end) == str:
        limit2 = line.find(end)
    elif type(end) == int:
        limit2 = end

    my_string = line[limit1:limit2]

    final_string = ''
    for letter in my_string:
        if letter in characters:
            final_string += letter

    final_string = final_string.strip()

    return final_string


def is_turn_finished(line_number):

    """
    Takes:
        - content of log file
    Returns:
        - Number of total turns
        - List of line number in the log file of the starting of each turn
    """

    global content

    current_line = content[line_number].rstrip()
    current_line = current_line.upper()

    if 'COMMUNICATING' in current_line:
        previous_line = content[line_number - 1].rstrip()
        previous_line = previous_line.upper()
        next_line = content[line_number + 1].rstrip()
        next_line = next_line.upper()

        if 'WENT BACK' in previous_line or 'SWITCHED OUT' in previous_line or 'GO! ' in next_line or 'SENT OUT' in next_line or 'CANCELED' in next_line or 'COMMUNICATING' in next_line:
            return False
        else:
            return True
    else:
        return False


def is_attacking(line_number):

    """
     Takes:
         - content of log file
     Returns:
         - Boolean if there is a pokemon attacking in the given line
    """

    global content

    current_line = content[line_number].rstrip()
    current_line = current_line.upper()

    if 'USED' in current_line:
        if 'OPPOSING' in line:
            return 'OPPONENT'
        else:
            return 'USER'
    else:
        return False


def get_turns():

    """
    Takes:
        - content of log file
    Returns:
        - Number of total turns
        - List of line number in the log file of the starting of each turn
    """

    global content

    total_turns = 0
    turn_lines = []

    for a in range(len(content)):
        if is_turn_finished(a) == True:
            total_turns += 1
            turn_lines.append(a)

    return total_turns, turn_lines


def get_attack_lines(turn):
    if turn == 0:
        return 'NO ATTACKS'

    global content
    turns, turn_lines = get_turns()
    attacks_lines = []

    start = turn_lines[turn-1]
    if turn_lines[-1] == turn_lines[turn-1]:
        end = len(content)
    else:
        end = turn_lines[turn]


    for a in range(start, end):
        my_line = content[a].rstrip()
        my_line = my_line.upper()
        if 'USED' in my_line:
            attacks_lines.append(a)

    return attacks_lines


def get_picks():

    """
    Takes:
        - content of log file
        - list of pokemon from txt file
        - characters string to purge Pokémon names
    Returns:
        - List of each player piked pokemon
    """

    global content
    global my_pokemon_list
    global characters

    pokes_player1 = []
    pokes_player2 = []

    for a in range(len(content)):
        line = content[a].rstrip()
        line = line.upper()

        if 'SLOT1' in line or 'SLOT2' in line:
            my_pick = parse_string(line, 0, 'SLOT')
            my_pick = get_similar_from_list(my_pick, my_pokemon_list)

            if my_pick not in pokes_player1:
                pokes_player1.append(my_pick)

        if 'SLOT3' in line or 'SLOT4' in line:
            my_pick = parse_string(line, 0, 'SLOT')
            my_pick = get_similar_from_list(my_pick, my_pokemon_list)

            if my_pick not in pokes_player2:
                pokes_player2.append(my_pick)

    return pokes_player1, pokes_player2


def get_attack(line_number):

    global content

    turns, turn_lines = get_turns()
    pokes_player1, pokes_player2 = get_picks()


    # # DETERMINAR EN QUE TURNO SE HA PRODUCIDO EL ATAQUE # #
    current_turn = ''
    for a in range(len(turn_lines)):
        if line_number < turn_lines[a]:
            current_turn = a
            break
        elif turn_lines[-1] < line_number <= len(content):
            current_turn = a+1

    print('This attack happened in: TURN ' + str(current_turn))


    # # DETEMRINAR EL POKEMON ATACANTE Y EL ATAQUE REALIZADO # #
    my_line = content[line_number].rstrip()
    my_line = my_line.upper()
    if 'OPPOSING' in my_line:
        attacker_poke = parse_string(my_line, 'OPPOSING', 'USED')
        attacker_poke = get_similar_from_list(attacker_poke, pokes_player2)
        move_used = parse_string(my_line, 'USED', len(my_line))
        move_used = get_similar_from_list(move_used, my_move_list)
        attacker_player = 'PLAYER2'
    else:
        attacker_poke = parse_string(my_line, 0, 'USED')
        attacker_poke = get_similar_from_list(attacker_poke, pokes_player1)
        move_used = parse_string(my_line, 'USED', len(my_line))
        move_used = get_similar_from_list(move_used, my_move_list)
        attacker_player = 'PLAYER1'

    print('The attacker player was: ' + str(attacker_player))
    print('The attacker pokémon was: ' + str(attacker_poke))
    print('The move used in the attack was: ' + str(move_used))


    # # DETERMINAR CUANTOS POKEMON RECIBEN DAÑO # #

    # Determinar la lineas de inicio y final del ataque
    attack_lines = get_attack_lines(current_turn)
    start_line = line_number

    index = attack_lines.index(line_number)
    if attack_lines[index] == attack_lines[-1]: # Si es el ultimo ataque
        if current_turn == len(turn_lines): # Si es el ultimo turno
            end_line = len(content)
            for a in reversed(range(line_number, len(content))):
                temp_line = content[a].strip()
                temp_line = temp_line.upper()
                if 'HAD ITS' in temp_line or 'WAS HURT' in temp_line:
                    end_line = a
        else:
            end_line = turn_lines[current_turn]
            for a in reversed(range(line_number, turn_lines[current_turn])):
                temp_line = content[a].strip()
                temp_line = temp_line.upper()
                if 'HAD ITS' in temp_line or 'WAS HURT' in temp_line:
                    end_line = a
    else:
        end_line = attack_lines[index+1]

    # Deterinar que pokemon reciben daño
    harm = False
    harmed_lines = []
    for b in range(start_line, end_line):
        previous_line = content[b - 1].strip()
        previous_line = previous_line.upper()
        current_line = content[b].strip()
        current_line = current_line.upper()
        next_line = content[b + 1].strip()
        next_line = next_line.upper()
        if 'SLOT' in current_line:
            if (
            'GO!' not in previous_line and
            'SENT OUT' not in previous_line and
            'HAD ITS' not in previous_line and
            'HAD ITS' not in next_line and
            'HURT BY ITS' not in previous_line):
                harm = True
                harmed_lines.append(b)

    harmed_player = ''
    if not harm:
        print('NO DAMAGE DEALT')
    else:
        for c in harmed_lines:
            current_line = content[c].strip()
            current_line = current_line.upper()
            previous_line = content[c-1].strip()
            previous_line = previous_line.upper()
            # if 'GO!' not in previous_line and 'SENT OUT' not in previous_line:
            if 'SLOT1' in current_line or 'SLOT2' in current_line:
                harmed_player = 'PLAYER1'
            elif 'SLOT3' in current_line or 'SLOT4' in current_line:
                harmed_player = 'PLAYER2'

            harmed_poke = parse_string(current_line, 0, 'SLOT')
            remain_hp = parse_string(current_line, 'HP:', len(current_line))
            if harmed_player == 'PLAYER1':
                harmed_poke = get_similar_from_list(harmed_poke, pokes_player1)
            elif harmed_player == 'PLAYER2':
                harmed_poke = get_similar_from_list(harmed_poke, pokes_player2)

            if attacker_player == harmed_player and harmed_poke == attacker_poke:
                print('Damaged pokemon: (' + str(harmed_player) + ') ' + str(harmed_poke) + ' Remaining HP: ' + str(remain_hp) + '% (SELF DAMAGE)')
            elif attacker_player == harmed_player and harmed_poke != attacker_poke:
                print('Damaged pokemon: (' + str(harmed_player) + ') ' + str(harmed_poke) + ' Remaining HP: ' + str(remain_hp) + '% (HARM PARTNER)' )
            elif attacker_player != harmed_player:
                print('Damaged pokemon: (' + str(harmed_player) + ') ' + str(harmed_poke) + ' Remaining HP: ' + str(remain_hp) + '%')


# Si ataco y muere alguien sale fainted
# justo despues del fainted, restore hp
# Si se han debilitado pokemon en el turno, Antes de terminar el turno saldría un go! tal o un sent out
# was hurt aparece como mensaje al terminar fase de ataque ()101
# Cuando actua el campo de rillaboom, "had its HP"  aparece en la linea de antes o en la linea de despues de un SLOT


# def stupid(a):
#     return a-1
# get_attack(stupid(16))


for a in range(len(content)):
    current_line = content[a].strip()
    current_line = current_line.upper()
    if 'USED' in current_line:
        get_attack(a)


#################################################################################

#

#
#
#
# def get_picks():
#
#     """
#     Takes:
#         - content of log file
#         - list of pokemon from txt file
#         - characters string to purge Pokémon names
#     Returns:
#         - Dictionary for each player. Each player dictionary contains:
#             - Dictionary with the purged names of each Pokémon picked.
#             (if language not English, key is named UNKNOWN#). Each Pokémon dictionary contains:
#                 - Turn0 as key.
#                 - str(100) as value
#
#         Example:
#             player1 = {'APPLETUN':  {'Turn0': '100'}, 'SALAZZLE': {'Turn0': '100'}, 'MIMIKYU': {'Turn0': '100'}, 'ZACIAN':    {'Turn0': '100'}}
#             player2 = {'DRAGAPULT': {'Turn0': '100'}, 'GROUDON':  {'Turn0': '100'}, 'ENTEI':   {'Turn0': '100'}, 'RILLABOOM': {'Turn0': '100'}}
#
#     """
#
#     global content
#     global my_pokemon_list
#     global characters
#
#     temp_pokemon_player1 = []
#     temp_pokemon_player2 = []
#     real_pokemon_player1 = []
#     real_pokemon_player2 = []
#     final_pokemon_player1 = {}
#     final_pokemon_player2 = {}
#
#     # Take raw pokemon names from log file
#     for a in range(len(content)):
#         line = content[a].rstrip()
#         line = line.upper()
#
#         if 'SLOT1' in line or 'SLOT2' in line:
#             limit = line.find('SLOT')
#             pokemon = line[0:limit]
#             my_pokemon = ''
#             for letter in pokemon:
#                 if letter in characters:
#                     my_pokemon += letter
#             my_pokemon = my_pokemon.strip()
#
#             if my_pokemon not in temp_pokemon_player1:
#                 temp_pokemon_player1.append(my_pokemon)
#
#         if 'SLOT3' in line or 'SLOT4' in line:
#             limit = line.find('SLOT')
#             pokemon = line[0:limit]
#             my_pokemon = ''
#             for letter in pokemon:
#                 if letter in characters:
#                     my_pokemon += letter
#             my_pokemon = my_pokemon.strip()
#
#             if my_pokemon not in temp_pokemon_player2:
#                 temp_pokemon_player2.append(my_pokemon)
#
#     # Purge raw pokemon data comparing with my pokemon list
#     for poke in temp_pokemon_player1:
#         if poke in my_pokemon_list:
#             if poke not in real_pokemon_player1:
#                 real_pokemon_player1.append(poke)
#         else:
#             final_poke = poke
#             previous_similitud = 0
#             for realpoke in my_pokemon_list:
#                 current_similitud = similar(poke, realpoke)
#                 if current_similitud > previous_similitud:
#                     final_poke = realpoke
#                     previous_similitud = current_similitud
#
#             if previous_similitud >= 0.80:
#                 if final_poke not in real_pokemon_player1:
#                     real_pokemon_player1.append(final_poke)
#
#     if len(real_pokemon_player1) < 4:
#         for a in range(4 - len(real_pokemon_player1)):
#             real_pokemon_player1.append('UNKNOWN'+str(a+1))
#
#     for poke in temp_pokemon_player2:
#         if poke in my_pokemon_list:
#             if poke not in real_pokemon_player2:
#                 real_pokemon_player2.append(poke)
#         else:
#             final_poke = poke
#             previous_similitud = 0
#             for realpoke in my_pokemon_list:
#                 current_similitud = similar(poke, realpoke)
#                 if current_similitud > previous_similitud:
#                     final_poke = realpoke
#                     previous_similitud = current_similitud
#
#             if previous_similitud >= 0.80:
#                 if final_poke not in real_pokemon_player2:
#                     real_pokemon_player2.append(final_poke)
#
#     if len(real_pokemon_player2) < 4:
#         for a in range(4 - len(real_pokemon_player2)):
#             real_pokemon_player2.append('UNKNOWN'+str(a+1))
#
#     # Create a dictionary with pokemon and turn0 hp
#     for a in real_pokemon_player1:
#         if 'UNKNOWN' in a:
#             final_pokemon_player1[a] = {}
#             final_pokemon_player1[a]['Turn0'] = 0
#         else:
#             final_pokemon_player1[a] = {}
#             final_pokemon_player1[a]['Turn0'] = '100'
#
#     for a in real_pokemon_player2:
#         if 'UNKNOWN' in a:
#             final_pokemon_player2[a] = {}
#             final_pokemon_player2[a]['Turn0'] = 0
#         else:
#             final_pokemon_player2[a] = {}
#             final_pokemon_player2[a]['Turn0'] = '100'
#
#     return final_pokemon_player1, final_pokemon_player2
#
#
# def get_hp_per_turn():
#
#     """
#     Takes:
#         - content of log file
#
#     Returns:
#         - Dictionary for each player.
#
#     """
#
#     global content
#
#     turns, lines = get_turns()
#     pokes_player1, pokes_player2 = get_picks()
#
#     # Get each turn hp PRESENT IN LOG FILE, for each pokemon of each player. And create a dictionary with the data
#     for index in range(turns):
#         start = lines[index]
#
#         if index == len(lines)-1:
#             end = len(content)
#         else:
#             end = lines[index+1]
#
#         for poke in pokes_player1:
#             final_hp = ''
#             present = False
#             for a in range(start, end):
#                 line = content[a].rstrip()
#                 line = line.upper()
#
#
#                 if 'SLOT1' in line or 'SLOT2' in line:
#                     limit = line.find('SLOT')
#                     pokemon = line[0:limit]
#                     my_pokemon = ''
#                     for letter in pokemon:
#                         if letter in characters:
#                             my_pokemon += letter
#                     my_pokemon = my_pokemon.strip()
#
#                     if similar(my_pokemon, poke) >=0.80:
#                         present = True
#                         hp = line[limit+9:len(line)]
#                         my_hp = ''
#                         for letter in hp:
#                             if letter in characters:
#                                 my_hp += letter
#                         my_hp = my_hp.strip()
#                         final_hp = my_hp
#
#             if present == True:
#                 pokes_player1[poke]['Turn' + str(index + 1)] = final_hp
#                 # print('Turn ' + str(index+1) + ' ' + str(poke) + ' ' +str(my_hp))
#
#         for poke in pokes_player2:
#             final_hp = ''
#             present = False
#             for a in range(start, end):
#                 line = content[a].rstrip()
#                 line = line.upper()
#
#                 if 'SLOT3' in line or 'SLOT4' in line:
#                     limit = line.find('SLOT')
#                     pokemon = line[0:limit]
#                     my_pokemon = ''
#                     for letter in pokemon:
#                         if letter in characters:
#                             my_pokemon += letter
#                     my_pokemon = my_pokemon.strip()
#
#                     if similar(my_pokemon, poke) >=0.80:
#                         present = True
#                         hp = line[limit+9:len(line)]
#                         my_hp = ''
#                         for letter in hp:
#                             if letter in characters:
#                                 my_hp += letter
#                         my_hp = my_hp.strip()
#                         final_hp = my_hp
#
#             if present == True:
#                 pokes_player2[poke]['Turn' + str(index + 1)] = final_hp
#                 # print('Turn ' + str(index+1) + ' ' + str(poke) + ' ' +str(my_hp))
#
#     # Fill in the dictionary the empty turns NOT PRESENT in log file
#     for a in pokes_player1:
#         current_hp = '100'
#         for b in range(turns):
#             if 'Turn' + str(b+1) in pokes_player1[a]:
#                 current_hp = pokes_player1[a]['Turn' + str(b + 1)]
#             else:
#                 pokes_player1[a]['Turn' + str(b + 1)] = current_hp
#
#     for a in pokes_player2:
#         current_hp = '100'
#         for b in range(turns):
#             if 'Turn' + str(b+1) in pokes_player2[a]:
#                 current_hp = pokes_player2[a]['Turn' + str(b + 1)]
#             else:
#                 pokes_player2[a]['Turn' + str(b + 1)] = current_hp
#
#     # Order turns in dictionary from 0 to final turn
#     temp1 = {}
#     for a in pokes_player1:
#         temp1[a] = {}
#         for b in range(len(pokes_player1[a])):
#             temp1[a]['Turn' + str(b)] = pokes_player1[a]['Turn' + str(b)]
#     pokes_player1 = temp1
#
#     temp2 = {}
#     for a in pokes_player2:
#         temp2[a] = {}
#         for b in range(len(pokes_player2[a])):
#             temp2[a]['Turn' + str(b)] = pokes_player2[a]['Turn' + str(b)]
#     pokes_player2 = temp2
#
#     return pokes_player1, pokes_player2
#
#
#
# def get_attacks():
#
#     """
#     - return atacks damage
#
#     """
#
#     global content
#
#     turns, lines = get_turns()
#     pokes_player1, pokes_player2 = get_picks()
#
#     # start a loop in range of battle turns
#     for index in range(turns):
#         start = lines[index]
#
#         if index == len(lines) - 1:
#             end = len(content) - 1
#         else:
#             end = (lines[index+1]) - 1
#
#         print('Turn START')
#
#         #for each turn, start a loop which reads each line of the turn
#         for a in range(start, end):
#             turn_line = content[a].rstrip()
#             turn_line = turn_line.upper()
#             # print('turn line: ' + str(a) + ' ' + str(turn_line))
#             harm = False
#             harmed = []
#             if 'USED' in turn_line:
#                 harm = True
#                 if 'OPPOSING' in turn_line:
#                     attacker_poke = parse_string(turn_line, 'OPPOSING', 'USED')
#                     attacker_poke = get_similar_from_list(attacker_poke, pokes_player2)
#                     # crear lista para adjuntar attacker
#                     print('(Turn' + str(index+1) + ') Player2 ' + str(attacker_poke) + ' ATTACKS')
#
#                     for my_index in range(a + 1, end):
#                         next_line = content[my_index].rstrip()
#                         next_line = next_line.upper()
#                         previous_line = content[my_index - 1].rstrip()
#                         previous_line = previous_line.upper()
#
#                         if 'USED' in next_line:
#                             if harm == False:
#                                 harmed.append('NO DEALS DAMAGE')
#                                 break
#                             else:
#                                 break
#                         elif 'AVOIDED' in next_line:
#                             over_next_line = content[my_index + 1].rstrip()
#                             over_next_line = over_next_line.upper()
#                             if 'SLOT' not in over_next_line:
#                                 harmed.append('NO DEALS DAMAGE')
#                                 break
#                         elif 'SLOT' in next_line:
#                             if 'USED' in previous_line or 'SLOT' in previous_line or 'AVOIDED' in previous_line:
#                                 harmed_poke = parse_string(next_line, 0, 'SLOT')
#                                 remain_hp = parse_string(next_line, 'HP:', len(next_line))
#                                 if 'SLOT1' in next_line or 'SLOT2' in next_line:
#                                     harmed_poke = get_similar_from_list(harmed_poke, pokes_player1)
#                                     if harmed_poke == attacker_poke:
#                                         harmed.append('RECOIL: ' + str(remain_hp))
#                                     else:
#                                         harmed.append(str(harmed_poke) + ': ' + str(remain_hp))
#                                 elif 'SLOT3' in next_line or 'SLOT4' in next_line:
#                                     harmed_poke = get_similar_from_list(harmed_poke, pokes_player2)
#                                     harmed.append(str(harmed_poke) + ': ' + str(remain_hp))
#                             elif 'LOST SOME' in previous_line:
#                                 harmed_poke = parse_string(next_line, 0, 'SLOT')
#                                 remain_hp = parse_string(next_line, 'HP:', len(next_line))
#                                 if 'SLOT1' in next_line or 'SLOT2' in next_line:
#                                     harmed_poke = get_similar_from_list(harmed_poke, pokes_player1)
#                                     if harmed_poke == attacker_poke:
#                                         harmed.append('RECOIL: ' + str(remain_hp))
#                                     else:
#                                         harmed.append(str(harmed_poke) + ': ' + str(remain_hp))
#                                 elif 'SLOT3' in next_line or 'SLOT4' in next_line:
#                                     harmed_poke = get_similar_from_list(harmed_poke, pokes_player2)
#                                     harmed.append(str(harmed_poke) + ': ' + str(remain_hp))
#
#                     print(harmed)
#
#                 else:
#                     attacker_poke = parse_string(turn_line, 0, 'USED')
#                     attacker_poke = get_similar_from_list(attacker_poke, pokes_player1)
#                     print('(Turn' + str(index + 1) + ') Player1 ' + str(attacker_poke) + ' ATTACKS')
#
#                     harmed = []
#                     for my_index in range(a + 1, end):
#                         next_line = content[my_index].rstrip()
#                         next_line = next_line.upper()
#                         previous_line = content[my_index - 1].rstrip()
#                         previous_line = previous_line.upper()
#
#                         if 'USED' in next_line:
#                             if harm == False:
#                                 harmed.append('NO DEALS DAMAGE')
#                                 break
#                             else:
#                                 break
#                         elif 'AVOIDED' in next_line:
#                             over_next_line = content[my_index+1].rstrip()
#                             over_next_line = over_next_line.upper()
#                             if 'SLOT' not in over_next_line:
#                                 harmed.append('NO DEALS DAMAGE')
#                                 break
#                         elif 'SLOT' in next_line:
#                             if 'USED' in previous_line or 'SLOT' in previous_line or 'AVOIDED' in previous_line:
#                                 harmed_poke = parse_string(next_line, 0, 'SLOT')
#                                 remain_hp = parse_string(next_line, 'HP:', len(next_line))
#                                 if 'SLOT1' in next_line or 'SLOT2' in next_line:
#                                     harmed_poke = get_similar_from_list(harmed_poke, pokes_player1)
#                                     if harmed_poke == attacker_poke:
#                                         harmed.append('RECOIL: ' + str(remain_hp))
#                                     else:
#                                         harmed.append(str(harmed_poke) + ': ' + str(remain_hp))
#                                 elif 'SLOT3' in next_line or 'SLOT4' in next_line:
#                                     harmed_poke = get_similar_from_list(harmed_poke, pokes_player2)
#                                     harmed.append(str(harmed_poke) + ': ' + str(remain_hp))
#                             elif 'LOST SOME' in previous_line:
#                                 harmed_poke = parse_string(next_line, 0, 'SLOT')
#                                 remain_hp = parse_string(next_line, 'HP:', len(next_line))
#                                 if 'SLOT1' in next_line or 'SLOT2' in next_line:
#                                     harmed_poke = get_similar_from_list(harmed_poke, pokes_player1)
#                                     if harmed_poke == attacker_poke:
#                                         harmed.append('RECOIL: ' + str(remain_hp))
#                                     else:
#                                         harmed.append(str(harmed_poke) + ': ' + str(remain_hp))
#                                 elif 'SLOT3' in next_line or 'SLOT4' in next_line:
#                                     harmed_poke = get_similar_from_list(harmed_poke, pokes_player2)
#                                     harmed.append(str(harmed_poke) + ': ' + str(remain_hp))
#                     print(harmed)
#
#         print('Turn END')
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# remaining_hp1, remaining_hp2 = get_hp_per_turn()
#
# print(remaining_hp1)
# print(remaining_hp2)
#
# turnos, lineas = get_turns()
#
# print(turnos)
# print(lineas)
#
# get_attacks()

