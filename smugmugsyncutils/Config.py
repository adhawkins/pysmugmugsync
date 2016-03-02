import os.path
from json import load, dump
from copy import deepcopy

class Config:
	__filename = os.path.expanduser("~/.pysmugmugsync.cfg")
	orig_json = {}
	json = {}

	def __init__(self):
		if os.path.isfile(self.__filename):
			with open(self.__filename, "r") as f:
				try:
					self.orig_json = load(f)
					self.json = deepcopy(self.orig_json)
				except Exception:
					pass

	def write(self):
		with open(self.__filename, "w") as f:
			dump(self.json, f, indent=2)

