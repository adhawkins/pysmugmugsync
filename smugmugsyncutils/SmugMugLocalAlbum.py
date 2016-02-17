import os.path

class SmugMugLocalAlbum:
	directory = ""
	name = ""
	parent = None
	children = []
	items = []
	
	def __init__(self, directory, parent = None):
		self.directory = directory
		self.name = os.path.basename(os.path.normpath(directory))
		self.album_name = self.name.replace(" ", "-")
		self.album_name = self.album_name.translate(None, '()')
		self.parent = parent
		self.children = []
		self.items = []

		entries=os.listdir(self.directory)

		for entry in entries:
			if os.path.isdir(os.path.join(self.directory,entry)):
				self.children.append(SmugMugLocalAlbum(directory=os.path.join(self.directory,entry), parent=self))
			else:
				if os.path.isfile(os.path.join(self.directory,entry)):
					self.items.append(entry)

	def __repr__(self):
		return "<SmugMugLocalAlbum directory:%s name:%s (%s) parent: %s children: %s items: %s" % \
			(self.directory, self.name, self.album_name, self.parent, len(self.children), len(self.items))

