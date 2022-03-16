#!/usr/bin/env python
# vim: set fdm=marker:
# Imports {{{1
from __future__ import print_function, annotations
from collections import defaultdict
from enum import Enum, auto
from select import select
from typing import Iterator
threading 	= globals()['__builtins__'].__dict__['__import__']("threading")
hashlib 	= globals()['__builtins__'].__dict__['__import__']("hashlib")
random 		= globals()['__builtins__'].__dict__['__import__']("random")
signal 		= globals()['__builtins__'].__dict__['__import__']("signal")
types 		= globals()['__builtins__'].__dict__['__import__']("types")
time 		= globals()['__builtins__'].__dict__['__import__']("time")
sys 		= globals()['__builtins__'].__dict__['__import__']("sys")
re 			= globals()['__builtins__'].__dict__['__import__']("re")
os 			= globals()['__builtins__'].__dict__['__import__']("os")
if os.name != "nt":
	termios = globals()['__builtins__'].__dict__['__import__']("termios")
	fcntl 	= globals()['__builtins__'].__dict__['__import__']("fcntl")
	tty 	= globals()['__builtins__'].__dict__['__import__']("tty")
try:
	pygame = globals()['__builtins__'].__dict__['__import__']("pygame")
except ImportError:
	pass
from random import randint
from sys import platform

# Global {{{1
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
	# mouse_drag_..ctrlalt_cl