import os.path

class SmugMugRemoteAlbum:
	directory = ""
	name = ""
	parent = None
	children = []
	items = []
	
	def __init__(self, directory, parent = None):
		self.directory = directory
		self.name = os.path.basename(os.path.normpath(directory))
		self.parent = parent
		self.children = []
		self.items = []

		print "Directory: %s, children: %d, items: %d" % (self.directory, len(self.children), len(self.items))

	def __repr__(self):
		return "<SmugMugRemoteAlbum directory:%s name:%s parent: %s children: %s items: %s" % \
			(self.directory, self.name, self.parent, len(self.children), len(self.items))
