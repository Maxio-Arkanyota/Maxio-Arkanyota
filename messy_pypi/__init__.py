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
	pygame = glo