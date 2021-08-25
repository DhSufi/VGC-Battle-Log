with open('Resources/RealMovesList.txt', "r") as file:
    content = file.readlines()

characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '


with open('Resources/MovesList.txt', "a+") as new_file:

    for line in range(len(content)):

        current_line = content[line].rstrip()
        current_line = current_line.upper()

        final_string = ''
        for letter in current_line:
            if letter in characters:
                final_string += letter

        new_file.write(final_string+'\n')
