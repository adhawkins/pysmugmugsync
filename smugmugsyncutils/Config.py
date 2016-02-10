import ConfigParser
import os.path

class Config:
	filename = os.path.expanduser("~/.pysmugmugsync.cfg")
	token = ""
	secret = ""

	def __init__(self, site):
		config = ConfigParser.RawConfigParser()
		config.read(self.filename)

		if config.has_section(site):
			self.token = config.get(site, 'token')
			self.secret = config.get(site, 'secret')

	def write(self, site):
		config = ConfigParser.RawConfigParser()
		config.read(self.filename)

		if not config.has_section(site):
			config.add_section(site)

		config.set(site, 'token', self.token)
		config.set(site, 'secret', self.secret)
		with open(self.filename, 'wb') as configfile:
			config.write(configfile)
