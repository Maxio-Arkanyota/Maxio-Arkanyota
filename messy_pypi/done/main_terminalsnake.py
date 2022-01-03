#!/usr/bin/env python3
import fcntl
import signal
import sys
import threading
import os
import termios
import time
import tty
import types
from select import select
from random import randint

# ["BORDURE", ["Snake directions", ,,,,,], "Apple", "Réactualise snake directions"]
Themes = {
    "Normal": ["\u2588", ['←', '↑', '→', '↓'], "X", "\u00B7"],
    "Full": ["=", ["\u2588", "\u2588", "\u2588", "\u2588"], "\u2600", "?"],
    "Custom": ["\u2588", ['←', '↑', '→', '↓'], "X", "\u00B7"],
}


# TODO:
# - Windows Adaptations
# - Cleanup

# --- BUGS
# - Bug: Apple spawn inside snake
# - Fix bug: redessiner la queue quand le menu s'enlève

# --- NOT URGENT
# - Keyboard Option
# - CustomTheme
# - Theme Head
# - --help menu
# - Save Config

def sigint_quit(s, f):
    exit_event.set()


def clean_quit(errcode: int = 0):
    exit_event.set()
    print("Fin du programme")
    Key.stop()
    Draw.stop()
    raise SystemExit(errcode)


escape = {
    "\n": "enter",
    ("\x7f", "\x08"): "backspace",
    ("[A", "OA"): "up",
    ("[B", "OB"): "down",
    ("[D", "OD"): "left",
    ("[C", "OC"): "right",
    "[2~": "insert",
    "[3~": "delete",
    "[H": "home",
    "[F": "end",
    "[5~": "page_up",
    "[6~": "page_down",
    "\t": "tab",
    "[Z": "shift_tab",
    "OP": "f1",
    "OQ": "f2",
    "OR": "f3",
    "OS": "f4",
    "[15": "f5",
    "[17": "f6",
    "[18": "f7",
    "[19": "f8",
    "[20": "f9",
    "[21": "f10",
    "[23": "f11",
    "[24": "f12"
}
mouse_state = {
    # Changer le cls.snake_pos[1]regex si supérieur a la key  \033[<100;: passer le {1,2} à {1,3}ou+
    # mouse_.._click
    "\033[<0;": "mouse_left_click",
    "\033[<1;": "mouse_middle_click",
    "\033[<2;": "mouse_right_click",
    # mouse_..alt_click
    "\033[<8;": "mouse_left_alt_click",
    "\033[<9;": "mouse_left_alt_click",
    "\033[<10;": "mouse_left_alt_click",
    # mouse_..ctrl_click
    "\033[<16;": "mouse_left_ctrl_click",
    "\033[<17;": "mouse_middle_ctrl_click",
    "\033[<18;": "mouse_right_ctrl_click",
    # mouse_..altctrl_click
    "\033[<24;": "mouse_left_ctrlalt_click",
    "\033[<25;": "mouse_middle_ctrlalt_click",
    "\033[<26;": "mouse_right_ctrlalt_click",
    # mouse_drag_.._click
    "\033[<32;": "mouse_drag_left_click",
    "\033[<33;": "mouse_drag_middle_click",
    "\033[<34;": "mouse_drad_right_click",
    # mouse_drag_..alt_click
    "\033[<40;": "mouse_left_alt_click",
    "\033[<41;": "mouse_left_alt_click",
    "\033[<42;": "mouse_left_alt_click",
    # mouse_drag_..ctrl_click
    "\033[<48;": "mouse_left_ctrl_click",
    "\033[<49;": "mouse_middle_ctrl_click",
    "\033[<50;": "mouse_right_ctrl_click",
    # mouse_drag_..ctrlalt_click
    "\033[<56;": "mouse_left_ctrlalt_click",
    "\033[<57;": "mouse_middle_ctrlalt_click",
    "\033[<58;": "mouse_right_ctrlalt_click",
    # mouse_scroll..
    "\033[<64;": "mouse_scroll_up",
    "\033[<65;": "mouse_scroll_down",
    # mouse_scroll_alt..
    "\033[<72;": "mouse_scroll_alt_up",
    "\033[<73;": "mouse_scroll_alt_down",
    # mouse_scroll_ctrl..
    "\033[<80;": "mouse_scroll_ctrl_up",
    "\033[<81;": "mouse_scroll_ctrl_down",
    # mouse_scroll_ctrlalt..
    "\033[<88;": "mouse_scroll_ctrl_up",
    "\033[<89;": "mouse_scroll_ctrl_down",
}


class Actions:
    # mouse_pos=mouse_pos,             click_state=click_state, clean_key=clean_key             ,input_save=input_save
    # Pos mouse type: (x, y), up or down            , key du type: escape ou mouse_..., key du type: \033[..

    dico_actions = {}

    @classmethod
    def set_action(cls):
        cls.dico_actions = {
            "z": cls.change_direction,
            "s": cls.change_direction,
            "d": cls.change_direction,
            "q": cls.change_direction,
            "\x1b[A": cls.change_direction,
            "\x1b[B": cls.change_direction,
            "\x1b[C": cls.change_direction,
            "\x1b[D": cls.change_direction,
            "m": Draw.show_menu,
            "escape": Draw.show_menu,
            "r": Draw.restart,
        }

    @classmethod
    def change_option_dead(cls, **kwargs):
        if kwargs["clean_key"] in ["z", "\x1b[A"]:
            Draw.dead_option_number = (Draw.dead_option_number - 1)
        if kwargs["clean_key"] in ["s", "\x1b[B"]:
            Draw.dead_option_number = (Draw.dead_option_number + 1)
        Draw.dead_option_number %= 2  # CAR y a 2 options Quit, Restart
        Draw.draw_dead_options()

    @classmethod
    def set_dead_action(cls):
        cls.dico_actions = {
            "r": Draw.restart,  # restart
            "escape": Draw.show_menu,  # restart
            "z": cls.change_option_dead,
            "\x1b[A": cls.change_option_dead,
            "s": cls.change_option_dead,
            "\x1b[B": cls.change_option_dead,
            "\n": cls.do_dead_option_action,
        }

    @classmethod
    def do_dead_option_action(cls, **kwargs):
        if Draw.dead_option_number == 0:
            Draw.restart()
        if Draw.dead_option_number == 1:
            sigint_quit(0, None)

    @classmethod
    def set_menu_action(cls):
        cls.dico_actions = {
            "r": Draw.restart,
            "m": Draw.show_menu,
            "escape": Draw.show_menu,
            "z": cls.change_option_menu,
            "\x1b[A": cls.change_option_menu,
            "s": cls.change_option_menu,
            "\x1b[B": cls.change_option_menu,
            "\n": cls.do_option_action,
            "q": cls.do_option_action,
            "\x1b[D": cls.do_option_action,
            "d": cls.do_option_action,
            "\x1b[C": cls.do_option_action,
        }

    @classmethod
    def change_direction(cls, **kwargs):
        directions = {
            "z": 1,
            "\x1b[A": 1,
            "q": 0,
            "\x1b[D": 0,
            "d": 2,
            "\x1b[C": 2,
            "s": 3,
            "\x1b[B": 3,
        }
        if not Draw.lock:
            if directions[kwargs["clean_key"]] % 2 != Draw.facing % 2:
                Draw.facing = directions[kwargs["clean_key"]]
                Draw.lock = True

    @classmethod
    def change_option_menu(cls, **kwargs):
        if kwargs["clean_key"] in ["z", "\x1b[A"]:
            Draw.option_number = (Draw.option_number - 1)
        if kwargs["clean_key"] in ["s", "\x1b[B"]:
            Draw.option_number = (Draw.option_number + 1)
        Draw.option_number %= len(Draw.menu_options)
        Draw.draw_options()

    @classmethod
    def do_option_action(cls, **kwargs):
        option = tuple(Draw.menu_options.keys())[Draw.option_number]
        func = Draw.menu_options[option]
        if isinstance(func, types.FunctionType) and kwargs["clean_key"] == "\n":
            if option == "Quit":
                func(0, None)
            else:
                func()
        elif isinstance(func, list):
            if kwargs["clean_key"] in ["q", "\x1b[C", "\n"]:
                func[0] += 1
            elif kwargs["clean_key"] in ["d", "\x1b[D"]:
                func[0] -= 1
            func[0] = func[0] % len(func[1])
            # TODO Actualiser la valeur
            # Avec FPS = func[1][func[0]
            Draw.draw_options()


def game_restart(**kwargs):
    Draw.menu = False
    Draw.snake_pos = [(Draw.size // 2, Draw.size // 2)]
    Draw.facing = 0  # 0 right, 1: up, 2: left 3: down
    Draw.snake_long = 10
    # back position -> Head
    Draw.points = 0
    Draw.draw_box()
    Draw.set_a_apple()
    Draw.dead = False
    Actions.set_action()


def show_shortcuts():  # TODO ou a remove
    pass


def quit_menu():
    Draw.show_menu()


class Draw:
    lock = False  # Pour éviter le double action sur la meme frame
    menu = False
    dead = False
    size = 32 + 2  # 2 pour les bordures
    facing = 0  # 0 right, 1: up, 2: left 3: down
    snake_long = 10
    # back position -> Head
    snake_pos = [(size // 2, size // 2)]
    random_pos = ()
    points = 0
    logo_menu = (
        "███ █   █ ████ █  █ ████",
        "█   ██  █ █  █ █ █  █   ",
        "███ █ █ █ ████ ██   ███ ",
        "  █ █  ██ █  █ █ █  █   ",
        "███ █   █ █  █ █  █ ████",
    )

    @classmethod
    def restart(cls, **kwargs):
        cls.menu = False
        cls.snake_pos = [(cls.size // 2, cls.size // 2)]
        cls.facing = 0  # 0 right, 1: up, 2: left 3: down
        cls.snake_long = 10
        # back position -> Head
        cls.points = 0
        cls.draw_box()
        cls.dead = False
        Actions.set_action()
        cls.set_a_apple()

    @classmethod
    def show_menu(cls, **kwargs):
        if cls.menu:
            cls.menu = False
            Actions.set_action()
            # print("\033[2J\033[1;1H")  # CLEAR SCREEN
            cls.draw_box()
            print(f"\033[{cls.random_pos[1] + 1};{cls.random_pos[0] + 1}H{Themes[cls.current_theme][2]}")
            cls.redraw_queue()
        else:
            cls.menu = True
            Actions.set_menu_action()
            for i in range(len(cls.logo_menu)):
                print(f"\033[{i + 5};5H{cls.logo_menu[i]}")
            cls.option_number = 0
            cls.draw_options()

    menu_options = {
        # OPTION: [Curent_option(Default_option), [selectable options]]
        # "FPS": [0, [10, 15, 24, 30, 60, 120]],
        "Speed": [1, [.03, .05, .1, .3, .5, 1]],
        "Size": [1, [16 + 2, 32 + 2, 64 + 2]],  # NEED TO RESTART
        "Themes": [0, ["Normal", "Full"]],      #, "Custom"]],
        # "Show Shortcut": show_shortcuts,
        "Continue": quit_menu,
        "Restart": game_restart,
        "Quit": sigint_quit,
    }
    option_number: int = 0
    dead_option_number: int = 0
    speed: float = menu_options["Speed"][1][menu_options["Speed"][0]]
    current_theme: str = str(menu_options["Themes"][1][menu_options["Themes"][0]])
    dead_options: tuple = ("Restart", "Quit")

    @classmethod
    def set_a_apple(cls):
        pos_of_point = randint(1, (cls.size - 2) ** 2 - cls.snake_long)
        current_point = 0
        for i in range(1, cls.size - 1):
            for j in range(1, cls.size - 1):
                if (i, j) in cls.snake_pos:
                    pass
                else:
                    current_point += 1
                if current_point == pos_of_point:
                    cls.random_pos = (i, j)
                    print(f"\033[{cls.random_pos[1] + 1};{cls.random_pos[0] + 1}H{Themes[cls.current_theme][2]}")

    @classmethod
    def draw_options(cls):
        for i in range(len(cls.menu_options.keys())):
            # : ← {func[1][func[0]]} →
            if cls.option_number == i:
                message = f"\033[33m\033[{i * 2 + 11};8H{tuple(cls.menu_options.keys())[i]}\033[0m"
            else:
                message = f"\033[{i * 2 + 11};8H{tuple(cls.menu_options.keys())[i]}"

            option = tuple(Draw.menu_options.keys())[i]
            func = Draw.menu_options[option]
            # replace func[1] by menu_option
            if isinstance(func, list):
                message += f": ← {func[1][func[0]]} →    "
            print(message)
            if option == "Themes":
                Draw.current_theme = func[1][func[0]]
            if option == "Size":
                Draw.size = func[1][func[0]]
                # Restart
            if option == "Speed":
                Draw.speed = func[1][func[0]]

    @classmethod
    def draw_dead_options(cls):
        cls.logo_dead = (
            "████ ████ █   █ ███  ████ █   █ ███ ███  ",
            "█    █  █ ██ ██ █    █  █ █   █ █   █ █  ",
            "█ ██ ████ █ █ █ ██   █  █  █ █  ██  ██   ",
            "█  █ █  █ █   █ █    █  █  █ █  █   █ █  ",
            "████ █  █ █   █ ███  ████   █   ███ █  █ ",
        )
        for j in range(len(cls.logo_dead)):
            print(f"\033[{j + 5};5H{cls.logo_dead[j]}")
        for i in range(2):
            # Draw Gameover
            # : ← {func[1][func[0]]}
            if cls.dead_option_number == i:
                message = f"\033[33m\033[{i * 2 + 11};8H{cls.dead_options[i]}\033[0m"
            else:
                message = f"\033[{i * 2 + 11};8H{cls.dead_options[i]}"
            print(message)

    @classmethod
    def draw_box(cls):
        print("\033[2J\033[1;1H")  # CLEAR SCREEN
        print(f"\033[1;1H" + Themes[cls.current_theme][0] * cls.size)
        print(f"\033[{cls.size};1H" + Themes[cls.current_theme][0] * cls.size)
        for i in range(2, cls.size):
            print(f"\033[{i};1H{Themes[cls.current_theme][0]}")
            print(f"\033[{i};{cls.size}H{Themes[cls.current_theme][0]}")

    @classmethod
    def redraw_queue(cls):
        for i, j in cls.snake_pos:
            print(f"\033[{j};{i}H{Themes[cls.current_theme][3]}")

    @classmethod
    def set_dead(cls):
        # Set dead menu option
        # Reset points
        cls.dead = True
        cls.draw_dead_options()
        Actions.set_dead_action()

        pass

    @classmethod
    def _do_draw(cls):
        cls.draw_box()
        cls.set_a_apple()
        while not cls.stopping:
            if exit_event.is_set():
                break

            if cls.menu or cls.dead:
                pass
            else:
                # SET CODE HERE: ne pas metre de code bloquant: code qui nécessite une action de l'utilisateur
                # Affiche la tête du snake
                print(f"\033[{cls.snake_pos[-1][1]};{cls.snake_pos[-1][0]}H{Themes[cls.current_theme][1][cls.facing]}")

                # Déplacement f(facing)
                if cls.facing == 0:
                    cls.snake_pos += [(cls.snake_pos[-1][0] - 1, cls.snake_pos[-1][1])]
                elif cls.facing == 1:
                    cls.snake_pos += [(cls.snake_pos[-1][0], cls.snake_pos[-1][1] - 1)]
                elif cls.facing == 2:
                    cls.snake_pos += [(cls.snake_pos[-1][0] + 1, cls.snake_pos[-1][1])]
                elif cls.facing == 3:
                    cls.snake_pos += [(cls.snake_pos[-1][0], cls.snake_pos[-1][1] + 1)]

                if True:  # A remove Condition gameover
                    if 1 < cls.snake_pos[-1][0] <= cls.size - 1 and 1 < cls.snake_pos[-1][1] <= cls.size - 1:
                        pass
                    else:
                        # Si bord et touché
                        cls.set_dead()
                    if (cls.snake_pos[-1][0], cls.snake_pos[-1][1]) in cls.snake_pos[:-1]:
                        # Vérifier si il se touche la queue
                        # tuple((cls.snake_pos[i][0], cls.snake_pos[i][1]) for i in range(len(cls.snake_pos)-1)):
                        cls.set_dead()

                if True:  # Si la tête du serpent touche une pomme
                    if (cls.random_pos[0] + 1, cls.random_pos[1] + 1) == cls.snake_pos[-1]:
                        cls.set_a_apple()
                        cls.snake_long += 1
                        cls.points += 1

                # Supprime le queue qui disparait
                if len(cls.snake_pos) > cls.snake_long:
                    print(f"\033[{cls.snake_pos[0][1]};{cls.snake_pos[0][0]}H ")
                    cls.snake_pos.pop(0)

            if "--debug" in sys.argv:  # DEBUG VAR
                # print(f"\033[40;1HSnake = {cls.snake_pos}")
                print(f"\033[2;35HRandom Apple= {cls.random_pos}")
                print(f"\033[3;35HPoints= {cls.points}")
                print(f"\033[4;35H{cls.current_theme=}")
            cls.lock = False
            time.sleep(cls.speed)

    # ---------------------------------------
    stopping: bool = False
    started: bool = False
    reader: threading.Thread

    @classmethod
    def start(cls):
        cls.stopping = False
        cls.reader = threading.Thread(target=cls._do_draw)
        cls.reader.start()
        cls.started = True

    @classmethod
    def stop(cls):
        if cls.started and cls.reader.is_alive():
            cls.stopping = True
            try:
                cls.reader.join()
            except RuntimeError:
                pass


class Key:
    list = None
    stopping: bool = False
    started: bool = False
    reader: threading.Thread

    @classmethod
    def start(cls):
        cls.stopping = False
        cls.reader = threading.Thread(target=cls._get_key)
        cls.reader.start()
        cls.started = True

    @classmethod
    def stop(cls):
        if cls.started and cls.reader.is_alive():
            cls.stopping = True
            try:
                cls.reader.join()
            except RuntimeError:
                pass

    @classmethod
    def last(cls) -> str:
        if cls.list:
            return cls.list.pop()
        else:
            return ""

    @classmethod
    def get(cls) -> str:
        if cls.list:
            return cls.list.pop(0)
        else:
            return ""

    @classmethod
    def has_key(cls) -> bool:
        return bool(cls.list)

    @classmethod
    def clear(cls):
        cls.list = []

    @classmethod
    def _get_key(cls):
        input_key = ""
        mouse_pos = None
        while not cls.stopping:
            with Raw(sys.stdin):
                if exit_event.is_set():
                    break
                if not select([sys.stdin], [], [], 0.1)[0]:
                    continue
                input_key += sys.stdin.read(1)
                if input_key == "\033":
                    with Nonblocking(sys.stdin):
                        input_key += sys.stdin.read(20)
                        if input_key.startswith("\033[<"):
                            _ = sys.stdin.read(1000)
                click_state = ""
                if input_key == "\033":
                    clean_key = "escape"
                elif input_key == "\\":
                    clean_key = "\\"
                else:
                    clean_key = input_key
                input_save = input_key
                input_key = ""

            if clean_key in Actions.dico_actions.keys():
                Actions.dico_actions[clean_key](clean_key=clean_key, input_save=input_save)
        clean_quit()


# Ne pas toucher: code pris de bpytop
class Raw(object):
    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()

    def __enter__(self):
        self.original_stty = termios.tcgetattr(self.stream)
        tty.setcbreak(self.stream)

    def __exit__(self, type_, value, traceback):
        termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)


class Nonblocking(object):
    """Set nonblocking mode for device"""

    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()

    def __enter__(self):
        self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)

    def __exit__(self, *args):
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)


def main():
    if "--debug" in sys.argv:
        debug = True
    else:
        debug = False
    if "--help" in sys.argv:
        print("--debug : affiche le arguments des keys")
        print("--help : affiche cd message")
    # https://blog.miguelgrinberg.com/post/how-to-kill-a-python-thread
    global exit_event
    exit_event = threading.Event()
    # Signaux Events
    signal.signal(signal.SIGINT, sigint_quit)
    # Define Initial Actions:
    Actions.set_action()

    # Set config

    # Start Program
    def run():
        Key.start()
        Draw.start()

    run()


if __name__ == "__main__":
    main()
