from argparse import ArgumentParser
from Config import Config
from smugmugv2py import Connection, User, Node, Album, SmugMugv2Utils
from sys import stdout, stdin
from os import linesep
from json import loads
from SmugMugLocalAlbum import SmugMugLocalAlbum
from pprint import pprint

api_key = "LXTk156AmDT0IhjLuDetBUwP9nWKCppg"
api_secret = "be735fbb3b44698d72506b29e21a434c"

def print_album(album):
	print str(album)
	for child in album.children:
		print_album(child)
		
def main():
	parser = ArgumentParser()
	parser.add_argument("site", help="the site to upload to")
	parser.add_argument("path", help="the path containing local photos")
	parser.add_argument("-r", "--reauth", help="force reauthorisation", action="store_true")
	args = parser.parse_args()
	print "Site: " + args.site
	print "Path: " + args.path

	config = Config(args.site)

	connection = Connection(api_key, api_secret)

	if args.reauth or not config.token or not config.secret:
		auth_url = connection.get_auth_url(access="Full", permissions="Modify")

		print "Visit the following URL and retrieve a verification code:%s%s" % (linesep, auth_url)

		stdout.write('Enter the six-digit code: ')
		stdout.flush()
		verifier = stdin.readline().strip()

		at, ats = connection.get_access_token(verifier)

		config.token = at
		config.secret = ats
		config.write(args.site)

	connection.authorise_connection(config.token, config.secret)
	user = User(SmugMugv2Utils.get_authorized_user(connection))
	print "User: " + user.nickname + " (" + user.name + ")"
	root_node = Node(SmugMugv2Utils.get_node(connection,user.node))
	
	root = SmugMugLocalAlbum(args.path)

	for child in root.children:
		if child.items:
			node=Node(root_node.create_child_album(connection, child.name, child.album_name, 'Public', child.name))
			pprint(node.album)
			album=Album(SmugMugv2Utils.get_album(connection, node.album))
		else:
			node=Node(root_node.create_child_folder(connection, child.name, child.album_name, 'Public'))
			
