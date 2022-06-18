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
def terminal_dico(table, name_bar=("name", "ligne")):
	len_of_each_elements = [0]*len(name_bar)
	for i in range(len(len_of_each_elements)):
		for j in range(len(table)):
			len_of_each_elements[i] = max(len_of_each_elements[i], len(str(list(table.items())[j][i])))
	for i in table:
		print(str(i).center(len_of_each_elements[0]) + " | "+ str(table[i]).center(len_of_each_elements[1]))
def getKey(debug: bool = False) -> str:
	"""
	Warning: Ne renvoie pas la même valeur entre Windows et Linux/MacOs
	Warning2: Sur Linux/MacOs, Il faut presser 2 foix le button Echap pour que il soit effectuer
	Pause le terminal jusqu'a la rentrer d'un input
	"""
	if platform[:3] == 'win':
		__keydict = {
			0x3b: 'f1',
			0x3c: 'f2',
			0x3d: 'f3',
			0x3e: 'f4',
			0x3f: 'f5',
			0x40: 'f6',
			0x41: 'f7',
			0x42: 'f8',
			0x43: 'f9',
			0x44: 'f10',
			0x68: 'altf1',
			0x69: 'altf2',
			0x6a: 'altf3',
			0x6b: 'altf4',
			0x6c: 'altf5',
			0x6d: 'altf6',
			0x6e: 'altf7',
			0x6f: 'altf8',
			0x70: 'altf9',
			0x71: 'altf10',
			0x5e: 'ctrlf1',
			0x5f: 'ctrlf2',
			0x60: 'ctrlf3',
			0x61: 'ctrlf4',
			0x62: 'ctrlf5',
			0x63: 'ctrlf6',
			0x64: 'ctrlf7',
			0x65: 'ctrlf8',
			0x66: 'ctrlf9',
			0x67: 'ctrlf10',
			0x54: 'shiftf1',
			0x55: 'shiftf2',
			0x56: 'shiftf3',
			0x57: 'shiftf4',
			0x58: 'shiftf5',
			0x59: 'shiftf6',
			0x5a: 'shiftf7',
			0x5b: 'shiftf8',
			0x5c: 'shiftf9',
			0x5d: 'shiftf10',
			0x52: 'ins',
			0x53: 'del',
			0x4f: 'end',
			0x50: 'down',
			0x51: 'pgdn',
			0x4b: 'left',
			0x4d: 'right',
			0x47: 'home',
			0x48: 'up',
			0x49: 'pgup',
			0xa2: 'altins',
			0xa3: 'altdel',
			0x9f: 'altend',
			0xa0: 'altdown',
			0xa1: 'altpgdn',
			0x9b: 'altleft',
			0x9d: 'altright',
			0x97: 'althome',
			0x98: 'altup',
			0x99: 'altpgup',
			0x92: 'ctrlins',
			0x93: 'ctrldel',
			0x75: 'ctrlend',
			0x91: 'ctrldown',
			0x76: 'ctrlpgdn',
			0x73: 'ctrlleft',
			0x74: 'ctrlright',
			0x77: 'ctrlhome',
			0x8d: 'ctrlup',
			0x84: 'ctrlpgup',
			3: 'ctrl2'
		}
		import ctypes
		import msvcrt
		def getch():
			n = ord(ctypes.c_char(msvcrt.getch()).value)
			try:
				c = chr(n)
			except:
				c = '\0'
			return n, c
		def getkey():
			n, c = getch()
			# 0xE0 is 'grey' keys.  change this if you don't like it, but I don't care what color the key is.  IMHO it just confuses the end-user if they need to know.
			if n == 0 or n == 0xE0:
				n, c = getch()
				if n in __keydict:
					return __keydict[n]
				return "key%x" % n
			return c
	elif platform[:3] == 'lin' or platform[:3] == 'dar':
		import tty
		import termios
		from sys import stdin
		def getch():
			fd = stdin.fileno()
			old_settings = termios.tcgetattr(fd)
			try:
				tty.setraw(stdin.fileno())
				ch = stdin.read(1)
			finally:
				termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
			return ch
		def getkey():
			getchar = getch
			c1 = getchar()
			if ord(c1) != 0x1b:
				return c1
			c2 = getchar()
			if ord(c2) != 0x5b:
				return c1 + c2
			c3 = getchar()
			if ord(c3) != 0x33:
				return c1 + c2 + c3
			c4 = getchar()
			return c1 + c2 + c3 + c4
	key = getkey()
	if debug and key == "\x03":
		exit()
	else:
		return key
def get_key_bytes(debug: bool = False) -> bytes:
	return getKey(debug=debug).encode()
# All {{{1
# Launch and import {{{2
# COMPRESSINT {{{3
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
class CompressInt:
	def randomnombre(self, lenNb):
		# Entree: lenNb: int
		# Sortie: str
		# Renvoi un nombre de longeur `lenNb`
		stringNb = ""
		for _ in range(lenNb):
			stringNb += str(random.randint(0, 9))
		return stringNb
	@staticmethod
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
	@staticmethod
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
	def main(self, is_compression=True):
		file_output = "out.txt"
		file_input = "in.txt"
		if is_compression:
			try:
				stringNombre = open(file_input, 'r').readline()
			except:
				return
			if stringNombre.isdigit():
				self.owrite(stringNombre, file_output)
			else:
				raise Exception("Un nombre est attendu")
		else:
			self.oread(sys.argv[2], file_output)
# Démineur Terminal {{{3
def demineur():
	size = 10
	game_open = True
	drapeau_map = [
		[
			False for _ in range(size)
		]
		for _ in range(size)
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
			print_char(1, 1, "Vous avez gagné\n" + "restart: Enter\n" + "exit: CtrlC")
			key = getKey(debug=True)
			if key == "\r":
				demineur()
		elif ligne:
			clear()
			print_char(1, 1, "Vous avez perdu\n" +"restart: Enter\n" + "exit: CtrlC")
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
# Minesweeper Démienur graphique pygame {{{3
class MineSweeperMain:
	@staticmethod
	def start():
		pygame.font.init()
		os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (400, 100)
		surface = pygame.display.set_mode((1200, 900))
		pygame.display.set_caption('Minesweeper')
		state = MineSweeperStates.running
		player = MineSweeperPlayer()
		grid = MineSweeperGrid(player)
		run