#!/usr/bin/env python3
import os
import re


def count_number_of_lines_in_file(file: str) -> int:
    """
    Entrée: file: str
    Sortie: int
    
    Compte le nombre de lignes dans un fichier
    """
    with open(file, "r", encoding="latin-1") as f:
        text = f.readlines()
        text = [e for e in text if e.strip() not in {""}]
        return len(text)


def count_number_of_lines_in_folder(folder: str, match: str = "(.py$|.md$)") -> int:
    """
    Info: You can set "../../Here"
    Info: C'est le fichier a partir du dossier de ce fichier
    """
    nombres_lignes = 0
    for root, directories, files in os.walk(folder, topdown=False):
        for name in files:
            if re.search(match, name):
                nombres_lignes += count_number_of_lines_in_file(os.path.join(root, name))
    return nombres_lignes


def count_number_of_lines_in_folder_verbose(folder: str, match: str = "(.py$|.md$)", otherinfo=False) -> int:
    """
    Info: You can set "../../Here"
    Info: C'est le fichier a partir du dossier de ce fichier
    """
    dico_otherinfo = {}
    nombres_lignes = 0
    for root, directories, files in os.walk(folder, topdown=False):
        print("\033[31mroot:\033[0m " + root)
        print("\033[32mdirectories:\033[0m " + str(directories))
        print("\033[33mfiles:\033[0m " + str(files))
        for name in files:
            if re.search(match, name):
                print("\033[31m---\033[0m")
                print("\033[36mname:\033[0m " + str(name))
                print("\033[34mpath:\033[0m " + str(os.path.join(root, name)))
                ligne = count_number_of_lines_in_file(os.path.join(root, name))
                print("\033[35mlignes:\033[0m " + str(ligne))
                if otherinfo:
                    if name in dico_otherinfo:
                        if isinstance(dico_otherinfo[name], list):
                            dico_otherinfo[name] = dico_otherinfo[name] + [ligne]
                        else:
                            dico_otherinfo[name] = [dico_otherinfo[name], ligne]
                    else:
                        dico_otherinfo[name] = ligne

                nombres_lignes += ligne
        try:
            print("\n" + "=" * (os.get_terminal_size()[0]) + "\n")
        except:
            print("\n" + "=" * 25 + "\n")

    if otherinfo:
        print(dico_otherinfo)
        max_len = 0
        info_byext = {}
        for i in dico_otherinfo.keys():
            max_len = max(len(i), max_len)
        for i, j in dico_otherinfo.items():
            l = 0
            if isinstance(j, list):
                for k in j:
                    l += k
            else:
                l = j
            print("name: " + str(i.center(max_len)) + "\t list: " + str(j) + "\t ligne: " + str(l) + "\t ext:" + str(
                i.split('.')[-1]))
            if i.split('.')[-1] in info_byext:
                info_byext[i.split('.')[-1]] += l
            else:
                info_byext[i.split('.')[-1]] = l
        print("==-==-==-==-==-==")
        for i, j in info_byext.items():
            print(str(i) + "\t: " + str(j))

        try:
            print("\n" + "=" * (os.get_terminal_size()[0]) + "\n")
        except:
            print("\n" + "=" * 25 + "\n")
        return nombres_lignes
    else:
        return nombres_lignes


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("use: python3.10 main_countlines.py [match]")
            exit()
        match = sys.argv[1]
    else:
        match = "\.py$|\.md$|\.html$|\.css$|\.txt$|LICENCE$|\.cfg$|\.json$"
    print("nombre de lignes: " + str(count_number_of_lines_in_folder_verbose(".", match, otherinfo=True)))
    print("match: " + match)
    print("fichier courant: " + str(os.getcwd()))
    print(sys.argv)
