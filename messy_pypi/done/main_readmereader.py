from collections import deque  # Implement Mathematiques Stacks
# from main_terminalFunctions import
from os import get_terminal_size
from main_terminalGetKey import getKey


def readfile(file):
    #       Gras, Italique,             Strike, code, Mcode, Hilight
    #      0**    1*     2__    3_     4~~    5`     6```   7==
    etat = [False, False, False, False, False, False, False, False]
    to_printfile = []
    with open(file, "r") as f:
        a = f.readlines()
    for i in a:
        current_ligne = i.rstrip()  # Fro keep \t
        if current_ligne == "---" or current_ligne == "___" or current_ligne == "***":
            current_ligne = get_terminal_size()[0] * "─"
        elif current_ligne[0:6] == "######":
            current_ligne = "\033[33mh6\u2588\u2588\u2588\u2588" + current_ligne[6:] + "\033[0m"
        elif current_ligne[0:5] == "#####":
            current_ligne = "\033[33mh5\u2588\u2588\u2588" + current_ligne[5:] + "\033[0m"
        elif current_ligne[0:4] == "####":
            current_ligne = "\033[33mH4\u2588\u2588" + current_ligne[4:] + "\033[0m"
        elif current_ligne[0:3] == "###":
            current_ligne = "\033[32m\033[1m" + (' ' + current_ligne[3:] + " ").center(get_terminal_size()[0],
                                                                                       ".") + "\033[0m"  # "\033[32m\033[3m3\u2588\u2588"+ current_ligne[3:] +"\033[0m"
        elif current_ligne[0:2] == "##":
            current_ligne = "\033[34m\033[1m" + (' ' + current_ligne[2:] + " ").center(get_terminal_size()[0],
                                                                                       "─") + "\033[0m"
        elif current_ligne[0:1] == "#":
            current_ligne = "\033[31m\033[1m\033[4m" + (' ' + current_ligne[1:] + " ").center(get_terminal_size()[0],
                                                                                              "\u2588") + "\033[0m"
        # While "**" or "~~" or "*" or "==" or "__" not i current line
        if "**" in current_ligne and not etat[0]:
            etat[0] = True
            current_ligne = current_ligne.replace("**", "\033[1m\033[91m", 1)
        if "**" in current_ligne and etat[0]:
            etat[0] = False
            current_ligne = current_ligne.replace("**", "\033[0m", 1)
        if "__" in current_ligne and not etat[2]:
            etat[2] = True
            current_ligne = current_ligne.replace("__", "\033[1m", 1)
        if "__" in current_ligne and etat[2]:
            etat[2] = False
            current_ligne = current_ligne.replace("__", "\033[0m", 1)
        if "==" in current_ligne and not etat[7]:
            etat[7] = True
            current_ligne = current_ligne.replace("==", "\033[103m\033[30m", 1)
        if "==" in current_ligne and etat[7]:
            etat[7] = False
            current_ligne = current_ligne.replace("==", "\033[0m", 1)

        to_printfile.append(current_ligne)
    return to_printfile


def printontermnal(to_printfile, boucle=True):
    ShowLines = False
    Firstline = 0
    ChosedLink = 0
    Reapet = True
    while Reapet:
        for i in to_printfile:
            print(i)
        if boucle:
            key = getKey(debug=True)
            if key == "l":
                ShowLines = not ShowLines
            if key == "j":  # DOWN
                Firstline = Firstline + 1  # min(Firstline+1, len(to_printfile))
            if key == "k":  # Up
                Firstline = Firstline - 1  # max(Firstline-1, 0)
            if key == "Tab":
                ChosedLink = ChosedLink + 1  # min(ChosedLink+1, len(alllink))
            if key == "ShiftTab":
                ChosedLink = ChosedLink - 1  # min(ChosedLink-1, 0)
            if key == "\r":  # ENTER
                pass  # TODO: Open browser with current link

        else:
            Reapet = False


if __name__ == "__main__":  # Si tu le lance avec python3.10 main_readmereader.py
    import sys

    args = sys.argv  # Recuperer les arguments du terminal
    if "--help" in args or "-h" in args:
        print("""
        -l, --lines: Affiches le numero des lignes avec
        -h, --help: affiche ceci
        -c, --config: Fichier config (Feature)
        -i, --image : Affiche les images en Assci with `https://dev.to/natamacm/terminal-image-with-python-44mh`
        -b, -blockcode : Hilight code blocks
        -s, --size : definir la taille de l'output
        """)
    if "--exec" in args:
        printontermnal(readfile("resources/Readmereader/RM.md"), boucle=False)
