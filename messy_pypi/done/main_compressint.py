#!/usr/bin/env python
# vim: set sw=4 sts=4 et fdm=marker:
# Permet de compresser une chaine un nombre par la moiter de sa longueur
# Fonctions
# - randomnombre(lenNb: int) -> str:  Renvoie un nombre aléatoire de longueur lenNb
# - owrite(stringNbRandom: str, outfile: str(file)) -> Compresse le str dans le fichier outfile
# - oread(file: str, outfile: str(file)) -> Compresse le str dans le fichier outfile
# HelpMenu
# Compression:
# 	compressint -x [file_output]
# 	Marche avec un input
# Deompression:
# 	compressint -X <file_compresser> [file_output]
import sys
import random
def randomnombre(lenNb):
    # Entree: lenNb: int
    # Sortie: str
    # Renvoi un nombre de longeur `lenNb` 
    stringNb = ""
    for _ in range(lenNb):
        stringNb += str(random.randint(0, 9))
    return stringNb
def owrite(stringNbRandom, outfile):
    """
    Entree: stringNbRandom: str, outfile: str(file name)
    Sortie: None
    """
    l = ""
    for i in range(len(stringNbRandom) // 2):
        a = stringNbRandom[i * 2:((i * 2) + 2)]
        if a == "13":
            l += chr(100)
        else:
            l += chr(int(a))
    if len(stringNbRandom) % 2 == 1:
        l += "e" + chr(int(stringNbRandom[-1]))
    with open(outfile, "w") as f:  # Write other thing
        f.write(l)
def oread(file, outfile):
    """
    Entree: file, outfile:str(file)
    Sortie: None
    """
    l = ""
    reachend = False
    with open(file, "r") as f:
        a = f.read()
    for i in a:
        if reachend:
            l += str(ord(i))
        elif ord(i) == 100:
            l += "13"
        elif ord(i) == 101:  # e
            reachend = True
        else:
            l += str(ord(i)).zfill(2)
    with open(outfile, "w") as f:
        f.write(l)
if __name__ == "__main__":
    if "--help" in sys.argv:
        print("Compression:")
        print("\tcompressint -x [file_output]")
        print("\tMarche avec un input")
        print("Deompression:")
        print("\tcompressint -X <file_compresser> [file_output]")
    elif len(sys.argv) >= 2:
        if sys.argv[1] == "-x":
            if len(sys.argv) >= 3:
                file_output = sys.argv[2]
            else:
                file_output = "out.txt"
            stringNombre = input("Input Nombre: ")
            if stringNombre.isdigit():
                owrite(stringNombre, file_output)
            else:
                raise Exception("Un nombre est attendu")
        if sys.argv[1] == "-X":
            if len(sys.argv) <= 4:
                file_output = sys.argv[3]
            elif len(sys.argv) <= 3:
                file_output = "in.txt"
            else:
                raise Exception("Pas le bon nombre d'arguement")
            oread(sys.argv[2], file_output)
