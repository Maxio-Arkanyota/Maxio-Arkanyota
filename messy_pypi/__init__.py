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
		running = True
		clock = pygame.time.Clock()
		while running:
			clock.tick(30)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				if event.type == pygame.MOUSEBUTTONDOWN and state == MineSweeperStates.running:
					if pygame.mouse.get_pressed()[0]:
						pos = pygame.mouse.get_pos()
						grid.click(pos[0], pos[1])
					elif pygame.mouse.get_pressed()[2]:
						pos = pygame.mouse.get_pos()
						grid.mark_mine(pos[0] // 30, pos[1] // 30)
					if grid.check_if_win():
						state = MineSweeperStates.win
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE and (state == MineSweeperStates.game_over or state == MineSweeperStates.win):
						grid.reload()
						state = MineSweeperStates.running
					if event.key == pygame.K_b:
						grid.show_mines()
			surface.fill((0, 0, 0))
			if player.get_health() == 0:
				state = MineSweeperStates.game_over
			if state == MineSweeperStates.game_over:
				MineSweeperStats.draw(surface, 'Game over!', (970, 350))
				MineSweeperStats.draw(surface, 'Press Space to restart', (920, 400))
			elif state == MineSweeperStates.win:
				MineSweeperStats.draw(surface, 'You win!', (1000, 350))
				MineSweeperStats.draw(surface, 'Press Space to restart', (920, 400))
			grid.draw(surface)
			MineSweeperStats.draw(surface, 'Lives remaining', (950, 100))
			MineSweeperStats.draw(surface, str(player.get_health()), (1020, 200))
			pygame.display.flip()
class MineSweeperStates(Enum):
	running = auto()
	game_over = auto()
	win = auto()
class MineSweeperPlayer:
	def __init__(self):
		self.health = 5
	def sub_health(self):
		self.health -= 1
	def get_health(self):
		return self.health
class MineSweeperStats:
	@staticmethod
	def draw(surface, label, pos):
		textsurface = pygame.font.SysFont('Comic Sans MS', 24).render(label, False, (255, 255, 255))
		surface.blit(textsurface, (pos[0], pos[1]))
class MineSweeperCell:
	def __init__(self, pos, random_mine):
		self.visible = False
		self.mine = random_mine
		self.show_mine = False
		self.size = 30
		self.color = (200, 200, 200)
		self.pos = pos
		self.label = False
		self.mine_counter = 0
		self.font_color = (0, 0, 0)
		self.marked = False
		self.explosion = False
		self.img_flag = pygame.image.load('./resources/minesweeper/cell-flagged.png')
		self.img_flag = pygame.transform.scale(self.img_flag, (self.size, self.size))
		self.img_explode = pygame.image.load('./resources/minesweeper/mine-exploded.png')
		self.img_explode = pygame.transform.scale(self.img_explode, (self.size, self.size))
		self.img_mine = pygame.image.load('./resources/minesweeper/mine.png')
		self.img_mine = pygame.transform.scale(self.img_mine, (self.size, self.size))
		self.img_cell = []
		for i in range(9):
			_img = pygame.image.load(f'./resources/minesweeper/cell-{i}.png')
			_img = pygame.transform.scale(_img, (self.size, self.size))
			self.img_cell.append(_img)
	def draw(self, surface):
		if self.visible and not self.label and not (self.show_mine and self.mine):
			surface.blit(self.img_cell[0], (self.pos[0], self.pos[1]))
		elif self.label:
			self.show_label(surface, self.mine_counter, self.pos)
		elif self.marked:
			surface.blit(self.img_flag, (self.pos[0], self.pos[1]))
		elif self.show_mine and self.mine:
			surface.blit(self.img_mine, (self.pos[0], self.pos[1]))
		elif self.explosion:
			surface.blit(self.img_explode, (self.pos[0], self.pos[1]))
		else:
			pygame.draw.rect(surface, (50, 50, 50), (self.pos[0], self.pos[1], self.size, self.size))
	def show_label(self, surface, label, pos):
		# textsurface = pygame.font.SysFont('Comic Sans MS', 18).render(label, False, self.font_color)
		# surface.blit(textsurface, (pos[0] + 10, pos[1] + 4))
		surface.blit(self.img_cell[int(label)], (pos[0], pos[1]))
class MineSweeperGrid:
	def __init__(self, player):
		self.player = player
		self.cells = []
		self.search_dirs = [(0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1)]
		for y in range(30):
			self.cells.append([])
			for x in range(30):
				self.cells[y].append(MineSweeperCell((x * 30, y * 30), self.random_mines()))
		self.lines = []
		for y in range(1, 31, 1):
			temp = []
			temp.append((0, y * 30))
			temp.append((900, y * 30))
			self.lines.append(temp)
		for x in range(1, 31, 1):
			temp = []
			temp.append((x * 30, 0))
			temp.append((x * 30, 900))
			self.lines.append(temp)
	def random_mines(self):
		r = randint(0, 10)
		if r > 9:
			return True
		else:
			return False
	def draw(self, surface):
		for row in self.cells:
			for cell in row:
				cell.draw(surface)
		for line in self.lines:
			pygame.draw.line(surface, (0, 125, 0), line[0], line[1])
	def is_within_bounds(self, x, y):
		return x >= 0 and x < 30 and y >= 0 and y < 30
	def search(self, x, y):
		if not self.is_within_bounds(x, y):
			return
		cell = self.cells[y][x]
		if cell.visible:
			return
		if cell.mine:
			cell.explosion = True
			self.player.sub_health()
			return
		cell.visible = True
		num_mines = self.num_of_mines(x, y)
		if num_mines > 0:
			cell.label = True
			cell.mine_counter = str(num_mines)
			return
		for xx, yy in self.search_dirs:
			self.search(x + xx, y + yy)
	def num_of_mines(self, x, y):
		counter = 0
		for xx, yy in self.search_dirs:
			if self.is_within_bounds(x + xx, y + yy) and self.cells[y + yy][x + xx].mine:
				counter += 1
		return counter
	def click(self, x, y):
		grid_x, grid_y = x // 30, y // 30
		self.search(grid_x, grid_y)
	def reload(self):
		self.player.health = 5
		for row in self.cells:
			for cell in row:
				cell.visible = False
				cell.label = False
				cell.marked = False
				cell.show_mine = False
				cell.explosion = False
				cell.mine = self.random_mines()
	def check_if_win(self):
		if self.player.health < 1:
			return False
		for row in self.cells:
			for cell in row:
				if not cell.visible and not cell.mine:
					return False
		return True
	def show_mines(self):
		for row in self.cells:
			for cell in row:
				if not cell.show_mine:
					cell.show_mine = True
				else:
					cell.show_mine = False
	def mark_mine(self, x, y):
		self.cells[y][x].marked = True
# Snake Terminal {{{3
Themes = {
	"Normal": ["\u2588", ['←', '↑', '→', '↓'], "X", "\u00B7"],
	"Full": ["=", ["\u2588", "\u2588", "\u2588", "\u2588"], "\u2600", "?"],
	"Custom": ["\u2588", ['←', '↑', '→', '↓'], "X", "\u00B7"],
	"WindowsCompatibility": ["X", ['<', '^', '>', '!'], "*", "?"]
}
def sigint_quit(s, f):
	exit_event.set()
def clean_quit(errcode: int = 0):
	exit_event.set()
	print("Fin du programme")
	SnakeKey.stop()
	SnakeDraw.stop()
	raise SystemExit(errcode)
class SnakeActions:
	# mouse_pos=mouse_pos,			 click_state=click_state, clean_key=clean_key			 ,input_save=input_save
	# Pos mouse type: (x, y), up or down			, key du type: escape ou mouse_..., key du type: \033[..
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
			"m": SnakeDraw.show_menu,
			"escape": SnakeDraw.show_menu,
			"r": SnakeDraw.restart,
		}
	@classmethod
	def change_option_dead(cls, **kwargs):
		if kwargs["clean_key"] in ["z", "\x1b[A"]:
			SnakeDraw.dead_option_number = (SnakeDraw.dead_option_number - 1)
		if kwargs["clean_key"] in ["s", "\x1b[B"]:
			SnakeDraw.dead_option_number = (SnakeDraw.dead_option_number + 1)
		SnakeDraw.dead_option_number %= 2  # CAR y a 2 options Quit, Restart
		SnakeDraw.draw_dead_options()
	@classmethod
	def set_dead_action(cls):
		cls.dico_actions = {
			"r": SnakeDraw.restart,  # restart
			"escape": SnakeDraw.show_menu,  # restart
			"z": cls.change_option_dead,
			"\x1b[A": cls.change_option_dead,
			"s": cls.change_option_dead,
			"\x1b[B": cls.change_option_dead,
			"\n": cls.do_dead_option_action,
		}
	@classmethod
	def do_dead_option_action(cls, **kwargs):
		if SnakeDraw.dead_option_number == 0:
			SnakeDraw.restart()
		if SnakeDraw.dead_option_number == 1:
			sigint_quit(0, None)
	@classmethod
	def set_menu_action(cls):
		cls.dico_actions = {
			"r": SnakeDraw.restart,
			"m": SnakeDraw.show_menu,
			"escape": SnakeDraw.show_menu,
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
		if not SnakeDraw.lock:
			if directions[kwargs["clean_key"]] % 2 != SnakeDraw.facing % 2:
				SnakeDraw.facing = directions[kwargs["clean_key"]]
				SnakeDraw.lock = True
	@classmethod
	def change_option_menu(cls, **kwargs):
		if kwargs["clean_key"] in ["z", "\x1b[A"]:
			SnakeDraw.option_number = (SnakeDraw.option_number - 1)
		if kwargs["clean_key"] in ["s", "\x1b[B"]:
			SnakeDraw.option_number = (SnakeDraw.option_number + 1)
		SnakeDraw.option_number %= len(SnakeDraw.menu_options)
		SnakeDraw.draw_options()
	@classmethod
	def do_option_action(cls, **kwargs):
		option = tuple(SnakeDraw.menu_options.keys())[SnakeDraw.option_number]
		func = SnakeDraw.menu_options[option]
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
			SnakeDraw.draw_options()
def game_restart(**kwargs):
	SnakeDraw.menu = False
	SnakeDraw.snake_pos = [(SnakeDraw.size // 2, SnakeDraw.size // 2)]
	SnakeDraw.facing = 0  # 0 right, 1: up, 2: left 3: down
	SnakeDraw.snake_long = 10
	# back position -> Head
	SnakeDraw.points = 0
	SnakeDraw.draw_box()
	SnakeDraw.set_a_apple()
	SnakeDraw.dead = False
	SnakeActions.set_action()
def show_shortcuts():  # TODO ou a remove
	pass
def quit_menu():
	SnakeDraw.show_menu()
class SnakeDraw:
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
		SnakeActions.set_action()
		cls.set_a_apple()
	@classmethod
	def show_menu(cls, **kwargs):
		if cls.menu:
			cls.menu = False
			SnakeActions.set_action()
			# print("\033[2J\033[1;1H")  # CLEAR SCREEN
			cls.draw_box()
			print(f"\033[{cls.random_pos[1] + 1};{cls.random_pos[0] + 1}H{Themes[cls.current_theme][2]}")
			cls.redraw_queue()
		else:
			cls.menu = True
			SnakeActions.set_menu_action()
			for i in range(len(cls.logo_menu)):
				print(f"\033[{i + 5};5H{cls.logo_menu[i]}")
			cls.option_number = 0
			cls.draw_options()
	menu_options = {
		# OPTION: [Curent_option(Default_option), [selectable options]]
		# "FPS": [0, [10, 15, 24, 30, 60, 120]],
		"Speed": [1, [.03, .05, .1, .3, .5, 1]],
		"Size": [1, [16 + 2, 32 + 2, 64 + 2]],  # NEED TO RESTART
		"Themes": [0, ["Normal", "Full", "Custom", "WindowsCompatibility"]],
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
			option = tuple(SnakeDraw.menu_options.keys())[i]
			func = SnakeDraw.menu_options[option]
			# replace func[1] by menu_option
			if isinstance(func, list):
				message += f": ← {func[1][func[0]]} →   "
			print(message)
			if option == "Themes":
				SnakeDraw.current_theme = func[1][func[0]]
			if option == "Size":
				SnakeDraw.size = func[1][func[0]]
				# Restart
			if option == "Speed":
				SnakeDraw.speed = func[1][func[0]]
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
		SnakeActions.set_dead_action()
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
class SnakeKey:
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
			if clean_key in SnakeActions.dico_actions.keys():
				SnakeActions.dico_actions[clean_key](clean_key=clean_key, input_save=input_save)
		clean_quit()
def SnakeMain():
	if "--debug" in sys.argv:
		debug = True
	else:
		debug = False
	# https://blog.miguelgrinberg.com/post/how-to-kill-a-python-thread
	global exit_event
	exit_event = threading.Event()
	# Signaux Events
	signal.signal(signal.SIGINT, sigint_quit)
	# Define Initial Actions:
	SnakeActions.set_action()
	# Set config
	# Start Program
	def run():
		SnakeKey.start()
		SnakeDraw.start()
	run()
# Tetris Pygame{{{3
class tetris:
	def __init__(self):
		pygame.font.init()
		# GLOBALS VARS
		self.s_width = 800
		self.s_height = 700
		self.play_width = 300  # meaning 300 // 10 = 30 width per block
		self.play_height = 600  # meaning 600 // 20 = 30 height per block
		self.block_size = 30
		self.top_left_x = (self.s_width - self.play_width) // 2
		self.top_left_y = self.s_height - self.play_height
		# SHAPE FORMATS
		S = [['.....',
			  '.....',
			  '..00.',
			  '.00..',
			  '.....'],
			 ['.....',
			  '..0..',
			  '..00.',
			  '...0.',
			  '.....']]
		Z = [['.....',
			  '.....',
			  '.00..',
			  '..00.',
			  '.....'],
			 ['.....',
			  '..0..',
			  '.00..',
			  '.0...',
			  '.....']]
		I = [['..0..',
			  '..0..',
			  '..0..',
			  '..0..',
			  '.....'],
			 ['.....',
			  '0000.',
			  '.....',
			  '.....',
			  '.....']]
		O = [['.....',
			  '.....',
			  '.00..',
			  '.00..',
			  '.....']]
		J = [['.....',
			  '.0...',
			  '.000.',
			  '.....',
			  '.....'],
			 ['.....',
			  '..00.',
			  '..0..',
			  '..0..',
			  '.....'],
			 ['.....',
			  '.....',
			  '.000.',
			  '...0.',
			  '.....'],
			 ['.....',
			  '..0..',
			  '..0..',
			  '.00..',
			  '.....']]
		L = [['.....',
			  '...0.',
			  '.000.',
			  '.....',
			  '.....'],
			 ['.....',
			  '..0..',
			  '..0..',
			  '..00.',
			  '.....'],
			 ['.....',
			  '.....',
			  '.000.',
			  '.0...',
			  '.....'],
			 ['.....',
			  '.00..',
			  '..0..',
			  '..0..',
			  '.....']]
		T = [['.....',
			  '..0..',
			  '.000.',
			  '.....',
			  '.....'],
			 ['.....',
			  '..0..',
			  '..00.',
			  '..0..',
			  '.....'],
			 ['.....',
			  '.....',
			  '.000.',
			  '..0..',
			  '.....'],
			 ['.....',
			  '..0..',
			  '.00..',
			  '..0..',
			  '.....']]
		self.shapes = [S, Z, I, O, J, L, T]
		self.shape_colors = [(0, 255, 0),
							 (255, 0, 0),
							 (0, 255, 255),
							 (255, 255, 0),
							 (255, 165, 0),
							 (0, 0, 255),
							 (128, 0, 128)]
		self.win = pygame.display.set_mode((self.s_width, self.s_height))
		pygame.display.set_caption('Tetris')
	def create_grid(self, locked_pos={}):  # *
		grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
		for i in range(len(grid)):
			for j in range(len(grid[i])):
				if (j, i) in locked_pos:
					c = locked_pos[(j, i)]
					grid[i][j] = c
		return grid
	def convert_shape_format(self, shape):
		positions = []
		format = shape.shape[shape.rotation % len(shape.shape)]
		for i, line in enumerate(format):
			row = list(line)
			for j, column in enumerate(row):
				if column == '0':
					positions.append((shape.x + j, shape.y + i))
		for i, pos in enumerate(positions):
			positions[i] = (pos[0] - 2, pos[1] - 4)
		return positions
	def valid_space(self, shape, grid):
		accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
		accepted_pos = [j for sub in accepted_pos for j in sub]
		formatted = self.convert_shape_format(shape)
		for pos in formatted:
			if pos not in accepted_pos:
				if pos[1] > -1:
					return False
		return True
	def check_lost(self, positions):
		for pos in positions:
			x, y = pos
			if y < 1:
				return True
		return False
	def get_shape(self):
		return Piece(5, 0, random.choice(self.shapes), self.shapes, self.shape_colors)
	def draw_text_middle(self, surface, text, size, color):
		font = pygame.font.SysFont("comicsans", size, bold=True)
		label = font.render(text, 1, color)
		surface.blit(label, (
			self.top_left_x + self.play_width / 2 - (label.get_width() / 2),
			self.top_left_y + self.play_height / 2 - label.get_height() / 2))
	def draw_grid(self, surface, grid):
		sx = self.top_left_x
		sy = self.top_left_y
		for i in range(len(grid)):
			pygame.draw.line(surface, (128, 128, 128), (sx, sy + i * self.block_size),
							 (sx + self.play_width, sy + i * self.block_size))
			for j in range(len(grid[i])):
				pygame.draw.line(surface, (128, 128, 128), (sx + j * self.block_size, sy),
								 (sx + j * self.block_size, sy + self.play_height))
	def clear_rows(self, grid, locked):
		inc = 0
		for i in range(len(grid) - 1, -1, -1):
			row = grid[i]
			if (0, 0, 0) not in row:
				inc += 1
				ind = i
				for j in range(len(row)):
					try:
						del locked[(j, i)]
					except:
						continue
		if inc > 0:
			for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
				x, y = key
				if y < ind:
					newKey = (x, y + inc)
					locked[newKey] = locked.pop(key)
		return inc
	def draw_next_shape(self, shape, surface):
		font = pygame.font.SysFont('comicsans', 30)
		label = font.render('Next Shape', 1, (255, 255, 255))
		sx = self.top_left_x + self.play_width + 50
		sy = self.top_left_y + self.play_height / 2 - 100
		format = shape.shape[shape.rotation % len(shape.shape)]
		for i, line in enumerate(format):
			row = list(line)
			for j, column in enumerate(row):
				if column == '0':
					pygame.draw.rect(surface, shape.color, (sx + j * self.block_size, sy + i * self.block_size, self.block_size, self.block_size), 0)
		surface.blit(label, (sx + 10, sy - 30))
	def update_score(self, nscore):
		score = self.max_score()
		with open('resources/tetris/scores.txt', 'w') as f:
			if int(score) > nscore:
				f.write(str(score))
			else:
				f.write(str(nscore))
	def max_score(self):
		if os.path.exists('resources/tetris/scores.txt'):
			with open('resources/tetris/scores.txt', 'r') as f:
				lines = f.readlines()
				score = lines[0].strip()
		else:
			score = '0'
		return score
	def draw_window(self, surface, grid, score=0, last_score=0):
		surface.fill((0, 0, 0))
		pygame.font.init()
		font = pygame.font.SysFont('comicsans', 60)
		label = font.render('Tetris', 1, (255, 255, 255))
		surface.blit(label, (self.top_left_x + self.play_width / 2 - (label.get_width() / 2), 30))
		# current score
		font = pygame.font.SysFont('comicsans', 30)
		label = font.render('Score: ' + str(score), 1, (255, 255, 255))
		sx = self.top_left_x + self.play_width + 50
		sy = self.top_left_y + self.play_height / 2 - 100
		surface.blit(label, (sx + 20, sy + 160))
		# last score
		label = font.render('High Score: ' + last_score, 1, (255, 255, 255))
		sx = self.top_left_x - 200
		sy = self.top_left_y + 200
		surface.blit(label, (sx + 20, sy + 160))
		for i in range(len(grid)):
			for j in range(len(grid[i])):
				pygame.draw.rect(surface, grid[i][j],
								 (self.top_left_x + j * self.block_size, self.top_left_y + i * self.block_size,
								  self.block_size, self.block_size), 0)
		pygame.draw.rect(surface, (255, 0, 0), (self.top_left_x, self.top_left_y, self.play_width, self.play_height), 5)
		self.draw_grid(surface, grid)
		# pygame.display.update()
	def main(self):  # *
		last_score = self.max_score()
		locked_positions = {}
		grid = self.create_grid(locked_positions)
		change_piece = False
		run = True
		current_piece = self.get_shape()
		next_piece = self.get_shape()
		clock = pygame.time.Clock()
		fall_time = 0
		fall_speed = 0.27
		level_time = 0
		score = 0
		while run:
			grid = self.create_grid(locked_positions)
			fall_time += clock.get_rawtime()
			level_time += clock.get_rawtime()
			clock.tick()
			if level_time / 1000 > 5:
				level_time = 0
				if level_time > 0.12:
					level_time -= 0.005
			if fall_time / 1000 > fall_speed:
				fall_time = 0
				current_piece.y += 1
				if not (self.valid_space(current_piece, grid)) and current_piece.y > 0:
					current_piece.y -= 1
					change_piece = True
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False
					pygame.display.quit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_LEFT:
						current_piece.x -= 1
						if not (self.valid_space(current_piece, grid)):
							current_piece.x += 1
					if event.key == pygame.K_RIGHT:
						current_piece.x += 1
						if not (self.valid_space(current_piece, grid)):
							current_piece.x -= 1
					if event.key == pygame.K_DOWN:
						current_piece.y += 1
						if not (self.valid_space(current_piece, grid)):
							current_piece.y -= 1
					if event.key == pygame.K_UP:
						current_piece.rotation += 1
						if not (self.valid_space(current_piece, grid)):
							current_piece.rotation -= 1
			shape_pos = self.convert_shape_format(current_piece)
			for i in range(len(shape_pos)):
				x, y = shape_pos[i]
				if y > -1:
					grid[y][x] = current_piece.color
			if change_piece:
				for pos in shape_pos:
					p = (pos[0], pos[1])
					locked_positions[p] = current_piece.color
				current_piece = next_piece
				next_piece = self.get_shape()
				change_piece = False
				score += self.clear_rows(grid, locked_positions) * 10
			self.draw_window(self.win, grid, score, last_score)
			self.draw_next_shape(next_piece, self.win)
			pygame.display.update()
			if self.check_lost(locked_positions):
				self.draw_text_middle(self.win, "YOU LOST!", 80, (255, 255, 255))
				pygame.display.update()
				pygame.time.delay(1500)
				run = False
				self.update_score(score)
	def main_menu(self):  # *
		run = True
		while run:
			self.win.fill((0, 0, 0))
			self.draw_text_middle(self.win, 'Press Any Key To Play', 60, (255, 255, 255))
			pygame.display.update()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False
				if event.type == pygame.KEYDOWN:
					self.main()
		pygame.display.quit()
class Piece(object):  # *
	def __init__(self, x, y, shape, shapes, shape_colors):
		self.x = x
		self.y = y
		self.shape = shape
		self.color = shape_colors[shapes.index(shape)]
		self.rotation = 0
def LaunchTetris():
	te = tetris()
	te.main_menu()
# DuplicateFile {{{3
def chunk_reader(fobj, chunk_size=1024):
	while True:
		chunk = fobj.read(chunk_size)
		if not chunk:
			return
		yield chunk
def get_hash(filename, first_chunk_only=False, hash=hashlib.sha1):
	hashobj = hash()
	file_object = open(filename, 'rb')
	if first_chunk_only:
		hashobj.update(file_object.read(1024))
	else:
		for chunk in chunk_reader(file_object):
			hashobj.update(chunk)
	hashed = hashobj.digest()
	file_object.close()
	return hashed
def check_for_duplicates(paths, hash=hashlib.sha1, remove=False):
	hashes_by_size = defaultdict(list)
	hashes_on_1k = defaultdict(list)
	hashes_full = {}
	for path in paths:
		for dirpath, dirnames, filenames in os.walk(path):
			for filename in filenames:
				full_path = os.path.join(dirpath, filename)
				try:
					full_path = os.path.realpath(full_path)
					file_size = os.path.getsize(full_path)
					hashes_by_size[file_size].append(full_path)
				except (OSError,):
					continue
	for size_in_bytes, files in hashes_by_size.items():
		if len(files) < 2:
			continue
		for filename in files:
			try:
				small_hash = get_hash(filename, first_chunk_only=True)
				hashes_on_1k[(small_hash, size_in_bytes)].append(filename)
			except (OSError,):
				continue
	for __, files_list in hashes_on_1k.items():
		if len(files_list) < 2:
			continue
		for filename in files_list:
			try:
				full_hash = get_hash(filename, first_chunk_only=False)
				duplicate = hashes_full.get(full_hash)
				if duplicate:
					print("Duplication trouvé: {} and {}".format(filename, duplicate))
					if remove:
						os.remove(duplicate)
				else:
					hashes_full[full_hash] = filename
			except (OSError,):
				continue
def LaunchDuplicate():
	if sys.argv[1:]:
		check_for_duplicates(sys.argv[1:])
	else:
		check_for_duplicates(["./"])
# README Reader {{{3
def readfile(file):
	#	   Gras, Italique,			 Strike, code, Mcode, Hilight
	#	  0**	1*	 2__	3_	 4~~	5`	 6```   7==
	etat = [False, False, False, False, False, False, False, False]
	to_printfile = []
	with open(file, "r") as f:
		a = f.readlines()
	for i in a:
		current_ligne = i.rstrip()  # Fro keep \t
		if current_ligne == "---" or current_ligne == "___" or current_ligne == "***":
			current_ligne = os.get_terminal_size()[0] * "─"
		elif current_ligne[0:6] == "######":
			current_ligne = "\033[33mh6\u2588\u2588\u2588\u2588" + current_ligne[6:] + "\033[0m"
		elif current_ligne[0:5] == "#####":
			current_ligne = "\033[33mh5\u2588\u2588\u2588" + current_ligne[5:] + "\033[0m"
		elif current_ligne[0:4] == "####":
			current_ligne = "\033[33mH4\u2588\u2588" + current_ligne[4:] + "\033[0m"
		elif current_ligne[0:3] == "###":
			current_ligne = "\033[32m\033[1m" + (' ' + current_ligne[3:] + " ").center(os.get_terminal_size()[0], ".") + "\033[0m"
		elif current_ligne[0:2] == "##":
			current_ligne = "\033[34m\033[1m" + (' ' + current_ligne[2:] + " ").center(os.get_terminal_size()[0], "─") + "\033[0m"
		elif current_ligne[0:1] == "#":
			current_ligne = "\033[31m\033[1m\033[4m" + (' ' + current_ligne[1:] + " ").center(os.get_terminal_size()[0], "\u2588") + "\033[0m"
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
def printontermnal(to_printfile):
	for i in to_printfile:
		print(i)
def LauchPrintMd():
	if sys.argv[1:]:
		printontermnal(readfile(sys.argv[1]))
	else:
		printontermnal(readfile(input("Ficher Markdown: ")))
# Count Line {{{3
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
def LaunchCountLines():
	if len(sys.argv) > 1:
		match = sys.argv[1]
	else:
		match = "\.py$|\.md$|\.html$|\.css$|\.txt$|LICENCE$|\.cfg$|\.json$"
	print("nombre de lignes: " + str(count_number_of_lines_in_folder_verbose(".", match, otherinfo=True)))
	print("match: " + match)
	print("fichier courant: " + str(os.getcwd()))
# Shell {{{3
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
		if key == 