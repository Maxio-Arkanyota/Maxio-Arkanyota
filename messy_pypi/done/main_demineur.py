from main_terminalGetKey import getKey
from main_terminalFunctions import print_char, clear, terminal_size, message_page_trop_petite
from random import randint


def demineur(size: int = 10):
    game_open = True
    drapeau_map = [
        [
            False for j in range(size)
        ]
        for i in range(size)
    ]
    plateau = []
    for i in range(size):
        ligne = []
        for j in range(size):
            if randint(1, 10) >= 3:
                ligne += [10]
            else:
                ligne += [9]
        plateau += [ligne]
    nouveau_plateau = []
    for i in range(len(plateau)):
        ligne = []
        for j in range(len(plateau[i])):
            if plateau[i][j] == 9:
                ligne += [9]
            else:
                somme = 0
                for k in range(-1, 2):
                    for l in range(-1, 2):
                        if not (k == 0 and l == 0):
                            if 0 <= i + k < 10 and 0 <= j + l < 10:
                                if plateau[i + k][j + l] == 9:
                                    somme += 1
                if somme == 0:
                    ligne += [10]
                else:
                    ligne += [-somme]
        nouveau_plateau += [ligne]
    del ligne
    plateau = nouveau_plateau
    # Plateau = [[0 if randint(1,10) >= 2 else -1 for j in range(size)] for i in range(size)]
    # Cache = [[1 for j in range(size)] for i in range(size)]
    x, y = size // 2, size // 2
    player_a_gagner = False
    ligne = False
    while game_open:
        if player_a_gagner:
            clear()
            print_char(1, 1,
                       "Vous avez gagné\n" +
                       "restart: Enter\n" +
                       "exit: CtrlC"
                       )
            key = getKey(debug=True)
            if key == "\r":
                demineur()
        elif ligne:
            clear()
            print_char(1, 1,
                       "Vous avez perdu\n" +
                       "restart: Enter\n" +
                       "exit: CtrlC"
                       )
            for i in range(len(plateau)):
                print("\n ", end="")
                for j in range(len(plateau[i])):
                    if plateau[i][j] == 0:
                        char_item = " "
                    elif 1 <= plateau[i][j] <= 8:
                        char_item = plateau[i][j]
                    elif -1 >= plateau[i][j] >= -8:
                        char_item = "\u2588"
                    elif plateau[i][j] == 10:
                        char_item = "\u2588"
                    elif plateau[i][j] == 9:
                        char_item = "\033[31m☭\033[0m"
                    elif plateau[i][j] == 12:
                        char_item = "\033[31m☭\033[0m"
                    else:
                        char_item = "?"
                    print_char(
                        ((terminal_size("X") - size) // 2) + i,
                        ((terminal_size("Y") - size) // 2) + j,
                        char_item
                    )
            key = getKey(debug=True)
            if key == "\r":
                demineur()
        else:
            print_char(1, 1,
                       "left: q ou ← \n" +
                       "up: z ou ↑ \n" +
                       "right: d ou → \n" +
                       "down: s ou ↓ \n" +
                       "click: a ou Enter \n" +
                       "flag: e"
                       )
            size_trop_petit = message_page_trop_petite(size + 2, size + 2)
            if not size_trop_petit:
                # print(Plateau)
                player_a_gagner = True
                for i in range(len(plateau)):
                    print("\n ", end="")
                    for j in range(len(plateau[i])):
                        if plateau[i][j] == 0:
                            char_item = " "
                        elif 1 <= plateau[i][j] <= 8:
                            char_item = plateau[i][j]
                        elif -1 >= plateau[i][j] >= -8:
                            char_item = "\u2588"
                            player_a_gagner = False
                        elif plateau[i][j] == 10:
                            char_item = "\u2588"
                            player_a_gagner = False
                        elif plateau[i][j] == 9:
                            char_item = "\u2588"
                        elif plateau[i][j] == 12:
                            char_item = "\033[31m☭\033[0m"
                        else:
                            char_item = "?"
                        print_char(
                            ((terminal_size("X") - size) // 2) + i,
                            ((terminal_size("Y") - size) // 2) + j,
                            (lambda elem, char_item_lambda:
                             "⚑" if elem  # ⚐⚑
                             else char_item_lambda)(drapeau_map[i][j], char_item)
                        )
                print_char(((terminal_size("X") - size) // 2) + x, ((terminal_size("Y") - size) // 2) + y, "X")
                key = getKey(debug=True)
                clear()
                if key == "q" or key == "\x1b[D":
                    x = max(0, x - 1)
                if key == "d" or key == "\x1b[C":
                    x = min(size - 1, x + 1)
                if key == "z" or key == "\x1b[A":
                    y = max(0, y - 1)
                if key == "s" or key == "\x1b[B":
                    y = min(size - 1, y + 1)
                if key == "a" or key == "\r":
                    if plateau[x][y] == 9:
                        ligne = True
                    if plateau[x][y] < 0:
                        plateau[x][y] = -plateau[x][y]
                    if plateau[x][y] == 10:
                        plateau[x][y] = 0
                if key == "e":
                    drapeau_map[x][y] = not drapeau_map[x][y]
                # DrawChar((TerminalSize("Y")//2), 10, "Y")
            # ⓪①②③④⑤⑥⑦⑧ ⓵⓶⓷⓸⓹⓺⓻⓼⓽⓾

if __name__ == "__main__":
    import sys
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Affichier le message d'aide: (Celui ci)")
        print("\tdemineur --help")
        print("Jouer:")
        print("\tdemineur [size]")
    elif len(sys.argv) > 1 and sys.argv[1].isdigit():
        demineur(int(sys.argv[1]))
    else:
        demineur()
