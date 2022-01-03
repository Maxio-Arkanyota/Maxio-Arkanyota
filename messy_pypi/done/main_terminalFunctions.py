import os
import time


SUBSCRIPT: tuple[str, ...] = ("₀", "₁", "₂", "₃", "₄", "₅", "₆", "₇", "₈", "₉")
SUPERSCRIPT: tuple[str, ...] = ("⁰", "¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹")

def print_char(x: int, y: int, char: str) -> None:
    """
    x: >
    y: \\/
    """
    print(f"\033[{y};{x}H{char}")


def clear() -> None:
    # os.system("cls||clear")
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def terminal_size(item: str = None) -> (tuple[int, int] or int):
    """
    X: >
    Y: \\/
    """
    size = os.get_terminal_size()
    if item is None:
        return size[0], size[1]
    elif item == "X":
        return size[0]
    elif item == "Y":
        return size[1]


def message_page_trop_petite(sizex, sizey) -> bool:
    """
    sizex, sizey: int
    """
    if sizex > terminal_size("X") or sizey > terminal_size("Y"):
        print("Trop petit")
        time.sleep(.50)
        return True
    return False

def terminal_dico(table, name_bar=["name", "ligne"]):
    len_of_each_elements = [0]*len(name_bar)
    for i in range(len(len_of_each_elements)):
        for j in range(len(table)):
            len_of_each_elements[i] = max(len_of_each_elements[i], len(str(list(table.items())[j][i])))
    for i in table:
        print(str(i).center(len_of_each_elements[0]) + " | "+ str(table[i]).center(len_of_each_elements[1]))

if __name__ == "__main__":
    terminal_dico({'RM.md': 139, 'scores.txt': 1, 'keyboard_dico.txt': 1, 'keyboard_dico.py': 1297, 'keyboard_config.txt': 1, 'test_gmt.html': 62, 'index.html': [65, 124], 'main_terminalGetKey.html': 355, 'app_launch.html': 143, 'main_gamemakerterminal.html': 115, 'main_tetris.html': 1139, 'main_minesweeper.html': 914, 'main_demineur.html': 394, 'main_terminalFunctions.html': 183, 'main_customElement.html': 754, 'main_countlignes.html': 136, 'main_duplicateFile.html': 221, 'main_messy.html': 468, '__init__.html': 64, 'main_autoreadme.py': 17, 'main_demineur.py': 154, 'main_countlignes.py': 87, 'main_tetris.py': 334, 'main_customElement.py': 155, 'main_duplicateFile.py': 65, 'main_terminalFunctions.py': 35, 'main_minesweeper.py': 194, 'main_keyboardGenerator.py': 89, 'app_launch.py': 95, 'main_terminalGetKey.py': 132, 'main_compressint.py': 64, '__init__.py': 12, 'main_readmereader.py': 86, 'test_keyboard_gen.py': 11})

