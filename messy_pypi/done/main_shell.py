import re

from main_terminalGetKey import getKey, get_key_bytes
from main_terminalFunctions import print_char, clear, terminal_size, message_page_trop_petite
from random import randint
from re import search
import os


class ShellFunctions:
    @classmethod
    def auto_complete(cls, command, list_of_command):
        """
        This function is used to auto-complete the command.
        """
        command_list = []
        for i in list_of_command:
            if i.startswith(command):
                command_list.append(i)
        return command_list

    @classmethod
    def reset_tabulationIndex(cls):
        ShellDraw.reload_all()
        ShellInfos.tabulationIndex = -1


class ShellDraw:
    @classmethod
    def draw_footer(cls):
        x = os.get_terminal_size()[0]
        y = os.get_terminal_size()[1]
        sys.stdout.write(f"\033[{y - 1};0H" + "-" * x)
        sys.stdout.write(f"\033[{y - 1};6H" + ShellModes.get_mode_name())
        sys.stdout.write(f"\033[{y - 1};20H" + ShellInfos.stack_key)
        sys.stdout.flush()

    @classmethod
    def cursor_key(cls):
        sys.stdout.write(
            f"\033[{ShellInfos.cursor_pos // os.get_terminal_size()[0] + 1};{ShellInfos.cursor_pos % os.get_terminal_size()[0]}H")

    @classmethod
    def actulise_input(cls):
        sys.stdout.write("\033[0;0H" + ShellInfos.input_string + " ")

    @classmethod
    def clear_input(cls):
        sys.stdout.write("\033[0;0H" + " " * os.get_terminal_size()[0])

    @classmethod
    def reload_all(cls):
        clear()
        cls.draw_footer()
        cls.actulise_input()
        cls.cursor_key()


class ShellConfig:
    @classmethod
    def load_config(cls):
        """
        This function is used to load the configuration file.
        """
        try:
            with open("config.txt", "r") as f:
                config = f.readlines()
            return config
        except FileNotFoundError:
            print("ShellConfiguration file not found.")
            return False

    @classmethod
    def get_history(cls):
        """
        This function is used to get the history of commands.
        """
        try:
            with open("history.txt", "r") as f:
                history = [i.lstrip() for i in f.readlines()]
            return history
        except FileNotFoundError:
            return []

    @classmethod
    def write_history(cls, command):
        """
        This function is used to write the history of commands.
        """
        with open("history.txt", "a") as f:
            f.write(command + "\n")


class ShellInfos:
    stack_key = ""
    input_string = ""
    cursor_pos = 1
    tabulationIndex = -1
    history = ShellConfig.get_history()
    history_index = 0


class ShellModes:
    allShellModes = []
    currentMode = 0

    def __init__(self, id, name, commands):
        self.modId = id
        self.modName = name
        self.command = commands
        self.allShellModes.append(self)

    @staticmethod
    def change_mode(new_mode: int):
        if new_mode == 0:
            ShellModes.currentMode = 0
            ShellInfos.stack_key = ""
        elif new_mode == 1:
            ShellModes.currentMode = 1
            ShellFunctions.reset_tabulationIndex()
        elif new_mode == 2:
            ShellModes.currentMode = 2
        elif new_mode == 3:
            ShellModes.currentMode = 3
        ShellDraw.draw_footer()

    def normal_insert_mode(key: str):
        if re.match('\\x1b\\[[A-D]', key):
            if key == "\x1b[C":
                ShellInfos.cursor_pos = min(ShellInfos.cursor_pos + 1, len(ShellInfos.input_string) + 1)
            elif key == "\x1b[D":
                ShellInfos.cursor_pos = max(0, ShellInfos.cursor_pos - 1)
            elif key == "\x1b[A":  # Up
                if ShellInfos.history_index > -len(ShellInfos.history):
                    ShellInfos.history_index = max(ShellInfos.history_index - 1, 0-len(ShellInfos.history))
                    ShellInfos.input_string = ShellInfos.history[ShellInfos.history_index]
                    ShellInfos.cursor_pos = len(ShellInfos.input_string) + 1
                ShellDraw.clear_input()
                ShellDraw.actulise_input()
            elif key == "\x1b[B":  # Down
                if ShellInfos.history_index < -1:
                    ShellInfos.history_index += 1
                    ShellInfos.input_string = ShellInfos.history[ShellInfos.history_index]
                    ShellInfos.cursor_pos = len(ShellInfos.input_string) + 1
                elif ShellInfos.history_index == -1:
                    ShellInfos.history_index = 0
                    ShellInfos.input_string = ""
                    ShellInfos.cursor_pos = 1
                ShellDraw.clear_input()
                ShellDraw.actulise_input()


    def normal_mode(key: str):
        if re.match('^[0-9d hjklwb]$', key) or key in ["\x01", "\x7f"]:
            ShellInfos.stack_key += key
        elif key == "i":
            ShellModes.change_mode(1)
            return
        elif key == "a":
            ShellModes.change_mode(1)
            if ShellInfos.cursor_pos < len(ShellInfos.input_string) + 1:
                ShellInfos.cursor_pos += 1
            return
        elif key == "r":
            ShellModes.change_mode(2)
            return
        elif key == ":":
            ShellModes.change_mode(3)
            return

        if ShellInfos.stack_key[-2:] == "dd":
            ShellInfos.input_string = ""
            ShellInfos.cursor_pos = 1
            ShellInfos.stack_key = ""
            ShellDraw.clear_input()
        elif ShellInfos.stack_key[-1:] == " ":
            if ShellInfos.stack_key[:-1].isdigit():
                ShellInfos.cursor_pos += int(ShellInfos.stack_key[:-1])
            else:
                ShellInfos.cursor_pos += 1
            ShellInfos.cursor_pos = min(ShellInfos.cursor_pos, len(ShellInfos.input_string) + 1)
            ShellInfos.stack_key = ""
        elif ShellInfos.stack_key[-1:] == "\x7f":
            if ShellInfos.stack_key[:-1].isdigit():
                ShellInfos.cursor_pos -= int(ShellInfos.stack_key[:-1])
            else:
                ShellInfos.cursor_pos -= 1
            ShellInfos.cursor_pos = max(ShellInfos.cursor_pos, 1)
            ShellInfos.stack_key = ""
        ShellDraw.actulise_input()
        ShellDraw.draw_footer()

    def insert_mode(key: str):
        if key == "\x7f":
            ShellInfos.input_string = ShellInfos.input_string[:-1]
            ShellInfos.cursor_pos = max(1, ShellInfos.cursor_pos - 1)
            ShellFunctions.reset_tabulationIndex()
        elif key == "\r":
            if ShellInfos.tabulationIndex == -1:
                sys.stdout.write(f"\033[2J\033[0;0H{ShellInfos.input_string}\r\n")
                os.system(ShellInfos.input_string)
                ShellDraw.draw_footer()
                ShellConfig.write_history(ShellInfos.input_string)
                ShellInfos.history_index = 0
                ShellInfos.history.append(ShellInfos.input_string)
                ShellInfos.input_string = ""
                ShellInfos.cursor_pos = 1
            else:
                ShellInfos.input_string = " ".join(ShellInfos.input_string.split(" ")[:-1]) + " " + \
                                     ShellFunctions.auto_complete(ShellInfos.input_string.split(" ")[-1], os.listdir("."))[
                                         ShellInfos.tabulationIndex]
                ShellInfos.cursor_pos = len(ShellInfos.input_string) + 1
                ShellFunctions.reset_tabulationIndex()
        elif key == "\t":
            list_autocomplete = ShellFunctions.auto_complete(ShellInfos.input_string.split(" ")[-1], os.listdir("."))
            ShellInfos.tabulationIndex += 1
            for ind, i in enumerate(list_autocomplete):
                if ind == ShellInfos.tabulationIndex:
                    sys.stdout.write(f"\033[33m\033[{ind + 2};1H{i}\033[0m")
                else:
                    sys.stdout.write(f"\033[{ind + 2};1H{i}")
        else:
            if ShellInfos.input_string == "":
                ShellDraw.clear_input()
            ShellInfos.input_string = ShellInfos.input_string[:ShellInfos.cursor_pos - 1] + key + ShellInfos.input_string[
                                                                                   ShellInfos.cursor_pos - 1:]
            ShellInfos.cursor_pos += 1
            ShellFunctions.reset_tabulationIndex()
        ShellDraw.actulise_input()

    def all_mode(key: str):
        if key == "\x1b\x1b":
            ShellModes.change_mode(0)
            return

    @classmethod
    def get_mode_name(self):
        return self.allShellModes[self.currentMode].modName


def Shellmain():
    normalMode = ShellModes(0, "Normal", [])
    insertMode = ShellModes(1, "Insert", [])
    ReplaceMode = ShellModes(2, "Replace", [])
    CommandMode = ShellModes(3, "Command", [])
    clear()
    ShellDraw.reload_all()
    while True:
        key = getKey(debug=True)
        sys.stdout.write("\033[0;0H")
        # print(get_key_bytes(True))
        if ShellModes.currentMode == 0:  # Normal Mode
            ShellModes.all_mode(key)
            ShellModes.normal_mode(key)
            ShellModes.normal_insert_mode(key)
        elif ShellModes.currentMode == 1:
            ShellModes.all_mode(key)
            ShellModes.insert_mode(key)
            ShellModes.normal_insert_mode(key)
        elif ShellModes.currentMode == 2:
            ShellModes.all_mode(key)
        elif ShellModes.currentMode == 3:
            ShellModes.all_mode(key)
        ShellDraw.cursor_key()
        sys.stdout.flush()


if __name__ == "__main__":
    import sys

    if "--help" in sys.argv or "-h" in sys.argv:
        print("TODO")

    main()
