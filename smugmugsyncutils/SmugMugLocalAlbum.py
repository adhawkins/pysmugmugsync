import os.path
from copy import deepcopy
from json import load, dump
from collections import OrderedDict

class SmugMugLocalAlbum:
	def __init__(self, directory, parent = None):
		self.directory = directory

		self.__name = os.path.basename(os.path.normpath(directory))
		self.__url_name = self.__name.replace(" ", "-").capitalize()
		self.__url_name = self.__url_name.translate(None, '()\'",;:&')[:30]
		self.parent = parent
		self.children = []
		self.items = []
		self.orig_json=OrderedDict()
		self.json_file=self.directory + "/smugmug.json"

		if os.path.isfile(self.json_file):
			with open(self.json_file, "r") as f:
				self.orig_json = load(f)

		self.json = deepcopy(self.orig_json)

		self.default_json()

		self.json["url_name"] = self.json["url_name"].replace(" ", "-").capitalize()[:30]

		entries=os.listdir(self.directory)

		for entry in entries:
			if os.path.isdir(os.path.join(self.directory,entry)):
				self.children.append(SmugMugLocalAlbum(directory=os.path.join(self.directory,entry), parent=self))
			else:
				if os.path.isfile(os.path.join(self.directory,entry)) and \
						entry != "smugmug.json":
					self.default_album()
					self.default_album_image(entry)

					self.items.append(entry)

		if self.items:
			self.json.pop("node_sort_method", None)
		else:
			self.json.pop("album_sort_method", None)

	def default_album(self):
		if not "description" in self.json:
			self.json["description"]=""

		if not "keywords" in self.json:
			self.json["keywords"]=""

		if not "name" in self.json:
			self.json["name"]=self.__name

		if not "album_sort_method" in self.json:
			self.json["album_sort_method"]="Filename"

		if not "files" in self.json:
			self.json["files"]={}

	def default_album_image(self, entry):
		if not entry in self.json["files"]:
			self.json["files"][entry]={}

		if not "caption" in self.json["files"][entry]:
			self.json["files"][entry]["caption"]=""

		if not "keywords" in self.json["files"][entry]:
			self.json["files"][entry]["keywords"]=""

		if not "title" in self.json["files"][entry]:
			self.json["files"][entry]["title"]=""

	def default_json(self):
		if not "uri" in self.json:
			self.json["uri"]=""

		if not "title" in self.json:
			self.json["title"]=self.__name

		if not "description" in self.json:
			self.json["description"]=""

		if not "url_name" in self.json:
			self.json["url_name"]=self.__url_name

		if not "node_sort_method" in self.json:
			self.json["node_sort_method"]="Name"

	def save_json(self):
		from pprint import pprint

		if self.json != self.orig_json:
			with open(self.json_file, "w") as f:
				dump(self.json, f, indent=2)

	def __repr__(self):
		return "<SmugMugLocalAlbum directory:%s name:%s (%s) parent: %s children: %s items: %s" % \
			(self.directory, self.name, self.album_name, self.parent, len(self.children), len(self.items))

