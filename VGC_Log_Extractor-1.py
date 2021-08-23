from difflib import SequenceMatcher

with open('Logs/Log3.txt', "r") as file:
    content = file.readlines()

with open('Resources/PokemonList.txt', "r") as pokemones:
    pokemon_list = pokemones.readlines()
    my_pokemon_list = []
    for a in pokemon_list:
        my_pokemon_list.append(a.strip())

characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '


def similar(x, y):

    """ Takes 2 arguments: (string, string)
        Returns the percentage (0 to 1) of similarity between the 2 strings """

    return SequenceMatcher(None, x, y).ratio()

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
        line = content[a].rstrip()
        line = line.upper()

        if 'COMMUNICATING' in line:
            previous_line = content[a - 1].rstrip()
            previous_line = previous_line.upper()
            next_line = content[a + 1].rstrip()
            next_line = next_line.upper()

            if 'WENT BACK' in previous_line or 'SWITCHED OUT' in previous_line or 'GO! ' in next_line or 'SENT OUT' in next_line or 'CANCELED' in next_line or 'COMMUNICATING' in next_line:
                continue

            total_turns += 1
            turn_lines.append(a+1)
            # print('Linea: ' + str(a+1) + ' Turno: ' + str(turns))

    return total_turns, turn_lines

def get_pokes():

    """
    Takes:
        - content of log file
        - list of pokemon from txt file
        - characters string to purge Pokémon names
    Returns:
        - Dictionary for each player. Each player dictionary contains:
            - Dictionary with the purged names of each Pokémon picked.
            (if language not English, key is named UNKNOWN#). Each Pokémon dictionary contains:
                - Turn0 as key.
                - str(100) as value

        Example:
            player1 = {'APPLETUN':  {'Turn0': '100'}, 'SALAZZLE': {'Turn0': '100'}, 'MIMIKYU': {'Turn0': '100'}, 'ZACIAN':    {'Turn0': '100'}}
            player2 = {'DRAGAPULT': {'Turn0': '100'}, 'GROUDON':  {'Turn0': '100'}, 'ENTEI':   {'Turn0': '100'}, 'RILLABOOM': {'Turn0': '100'}}

    """

    global content
    global my_pokemon_list
    global characters

    temp_pokemon_player1 = []
    temp_pokemon_player2 = []
    real_pokemon_player1 = []
    real_pokemon_player2 = []
    final_pokemon_player1 = {}
    final_pokemon_player2 = {}

    # Take raw pokemon names from log file
    for a in range(len(content)):
        line = content[a].rstrip()
        line = line.upper()

        if 'SLOT1' in line or 'SLOT2' in line:
            limit = line.find('SLOT')
            pokemon = line[0:limit]
            my_pokemon = ''
            for letter in pokemon:
                if letter in characters:
                    my_pokemon += letter
            my_pokemon = my_pokemon.strip()

            if my_pokemon not in temp_pokemon_player1:
                temp_pokemon_player1.append(my_pokemon)

        if 'SLOT3' in line or 'SLOT4' in line:
            limit = line.find('SLOT')
            pokemon = line[0:limit]
            my_pokemon = ''
            for letter in pokemon:
                if letter in characters:
                    my_pokemon += letter
            my_pokemon = my_pokemon.strip()

            if my_pokemon not in temp_pokemon_player2:
                temp_pokemon_player2.append(my_pokemon)

    # Purge raw pokemon data comparing with my pokemon list
    for poke in temp_pokemon_player1:
        if poke in my_pokemon_list:
            if poke not in real_pokemon_player1:
                real_pokemon_player1.append(poke)
        else:
            final_poke = poke
            previous_similitud = 0
            for realpoke in my_pokemon_list:
                current_similitud = similar(poke, realpoke)
                if current_similitud > previous_similitud:
                    final_poke = realpoke
                    previous_similitud = current_similitud

            if previous_similitud >= 0.80:
                if final_poke not in real_pokemon_player1:
                    real_pokemon_player1.append(final_poke)

    if len(real_pokemon_player1) < 4:
        for a in range(4 - len(real_pokemon_player1)):
            real_pokemon_player1.append('UNKNOWN'+str(a+1))

    for poke in temp_pokemon_player2:
        if poke in my_pokemon_list:
            if poke not in real_pokemon_player2:
                real_pokemon_player2.append(poke)
        else:
            final_poke = poke
            previous_similitud = 0
            for realpoke in my_pokemon_list:
                current_similitud = similar(poke, realpoke)
                if current_similitud > previous_similitud:
                    final_poke = realpoke
                    previous_similitud = current_similitud

            if previous_similitud >= 0.80:
                if final_poke not in real_pokemon_player2:
                    real_pokemon_player2.append(final_poke)

    if len(real_pokemon_player2) < 4:
        for a in range(4 - len(real_pokemon_player2)):
            real_pokemon_player2.append('UNKNOWN'+str(a+1))

    # Create a dictionary with pokemon and turn0 hp
    for a in real_pokemon_player1:
        if 'UNKNOWN' in a:
            final_pokemon_player1[a] = {}
            final_pokemon_player1[a]['Turn0'] = 0
        else:
            final_pokemon_player1[a] = {}
            final_pokemon_player1[a]['Turn0'] = '100'

    for a in real_pokemon_player2:
        if 'UNKNOWN' in a:
            final_pokemon_player2[a] = {}
            final_pokemon_player2[a]['Turn0'] = 0
        else:
            final_pokemon_player2[a] = {}
            final_pokemon_player2[a]['Turn0'] = '100'

    return final_pokemon_player1, final_pokemon_player2


def get_hp():

    """
    Takes:
        - content of log file

    Returns:
        - Dictionary for each player.

    """

    global content

    turns, lines = get_turns()
    pokes_player1, pokes_player2 = get_pokes()

    # Get each turn hp PRESENT IN LOG FILE, for each pokemon of each player. And create a dictionary with the data
    for index in range(turns):
        start = lines[index]

        if index == len(lines)-1:
            end = len(content)
        else:
            end = lines[index+1]

        for poke in pokes_player1:
            final_hp = ''
            present = False
            for a in range(start, end):
                line = content[a].rstrip()
                line = line.upper()

                if 'SLOT1' in line or 'SLOT2' in line:
                    limit = line.find('SLOT')
                    pokemon = line[0:limit]
                    my_pokemon = ''
                    for letter in pokemon:
                        if letter in characters:
                            my_pokemon += letter
                    my_pokemon = my_pokemon.strip()

                    if similar(my_pokemon, poke) >=0.80:
                        present = True
                        hp = line[limit+9:len(line)]
                        my_hp = ''
                        for letter in hp:
                            if letter in characters:
                                my_hp += letter
                        my_hp = my_hp.strip()
                        final_hp = my_hp

            if present == True:
                pokes_player1[poke]['Turn' + str(index + 1)] = final_hp
                # print('Turn ' + str(index+1) + ' ' + str(poke) + ' ' +str(my_hp))

        for poke in pokes_player2:
            final_hp = ''
            present = False
            for a in range(start, end):
                line = content[a].rstrip()
                line = line.upper()

                if 'SLOT3' in line or 'SLOT4' in line:
                    limit = line.find('SLOT')
                    pokemon = line[0:limit]
                    my_pokemon = ''
                    for letter in pokemon:
                        if letter in characters:
                            my_pokemon += letter
                    my_pokemon = my_pokemon.strip()

                    if similar(my_pokemon, poke) >=0.80:
                        present = True
                        hp = line[limit+9:len(line)]
                        my_hp = ''
                        for letter in hp:
                            if letter in characters:
                                my_hp += letter
                        my_hp = my_hp.strip()
                        final_hp = my_hp

            if present == True:
                pokes_player2[poke]['Turn' + str(index + 1)] = final_hp
                # print('Turn ' + str(index+1) + ' ' + str(poke) + ' ' +str(my_hp))

    # Fill in the dictionary the empty turns NOT PRESENT in log file
    for a in pokes_player1:
        current_hp = '100'
        for b in range(turns):
            if 'Turn' + str(b+1) in pokes_player1[a]:
                current_hp = pokes_player1[a]['Turn' + str(b + 1)]
            else:
                pokes_player1[a]['Turn' + str(b + 1)] = current_hp

    for a in pokes_player2:
        current_hp = '100'
        for b in range(turns):
            if 'Turn' + str(b+1) in pokes_player2[a]:
                current_hp = pokes_player2[a]['Turn' + str(b + 1)]
            else:
                pokes_player2[a]['Turn' + str(b + 1)] = current_hp

    # Order turns in dictionary from 0 to final turn
    temp1 = {}
    for a in pokes_player1:
        temp1[a] = {}
        for b in range(len(pokes_player1[a])):
            temp1[a]['Turn' + str(b)] = pokes_player1[a]['Turn' + str(b)]
    pokes_player1 = temp1

    temp2 = {}
    for a in pokes_player2:
        temp2[a] = {}
        for b in range(len(pokes_player2[a])):
            temp2[a]['Turn' + str(b)] = pokes_player2[a]['Turn' + str(b)]
    pokes_player2 = temp2

    return pokes_player1, pokes_player2



def get_attacks():

    """
    - return atacks damage

    """

    global content

    turns, lines = get_turns()
    pokes_player1, pokes_player2 = get_pokes()

    for index in range(turns):
        start = lines[index]

        if index == len(lines)-1:
            end = len(content)
        else:
            end = lines[index+1]


        for a in range(start, end):
            line = content[a].rstrip()
            line = line.upper()

            if 'USED' in line:
                damage = False
                for my_word in range(a+1,end):
                    temp_line = content[my_word].rstrip()
                    temp_line = temp_line.upper()
                    if 'USED' in temp_line:
                        break
                    elif 'SLOT' in temp_line:
                        damage = True
                        break

                if damage = True:
                    if 'OPPOSING' in line:
                        limit1 = line.find('OPPOSING')
                        limit1 = limit1 + 9
                        limit2 = line.find('USED')
                        pokemon = line[limit1:limit2]
                        my_pokemon = ''
                        for letter in pokemon:
                            if letter in characters:
                                my_pokemon += letter
                        my_pokemon = my_pokemon.strip()

                        final_poke = ''
                        previous_similar = 0
                        for poke in pokes_player2:
                            current_similar = similar(my_pokemon, poke)
                            if current_similar > previous_similar:
                                final_poke = poke




                    else:




                limit = line.find('SLOT')
                pokemon = line[0:limit]
                my_pokemon = ''
                for letter in pokemon:
                    if letter in characters:
                        my_pokemon += letter
                my_pokemon = my_pokemon.strip()

                if similar(my_pokemon, poke) >=0.80:
                    present = True
                    hp = line[limit+9:len(line)]
                    my_hp = ''
                    for letter in hp:
                        if letter in characters:
                            my_hp += letter
                    my_hp = my_hp.strip()
                    final_hp = my_hp

        if present == True:
            pokes_player1[poke]['Turn' + str(index + 1)] = final_hp
            # print('Turn ' + str(index+1) + ' ' + str(poke) + ' ' +str(my_hp))
























remaining_hp1, remaining_hp2 = get_hp()

print(remaining_hp1)
print(remaining_hp2)

turnos, lineas = get_turns()

print(turnos)
print(lineas)