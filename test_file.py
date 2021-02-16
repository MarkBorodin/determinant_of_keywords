with open('text.txt', 'r') as f:
    for line in f.readlines():
        if line != '':
            if line != '\n':
                if line != ' ':
                    print(line)
