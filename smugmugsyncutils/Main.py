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

def find_child_node(children, child_name):
	for child in children:
		if child.url_name == child_name:
			return child

def find_image(images, image_filename):
	for image in images:
		if image.filename == image_filename:
			return image

def sync_album(connection, local, remote):
	print "Syncing local album " + local.url_name + " with remote " + remote.url_name

	remoteimages = remote.get_images(connection)

	for localimage in local.items:
		print "Checking " + localimage

		if not find_image(remoteimages, localimage):
			print "Not found, uploading"
			connection.upload_image(local.directory + "/" + localimage, remote.uri)

def sync_node(connection, local, remote):
	global root_node

	print "Syncing node " + local.name + " with " + remote.name
	remote_children = remote.get_children(connection)

	for child in local.children:
		if child.items:
			node = find_child_node(remote_children, child.url_name)
			if not node:
				print "Creating album " + child.url_name
				node=Node(remote.create_child_album(connection, child.name, child.url_name, 'Public', child.name))

			album=Album(SmugMugv2Utils.get_album(connection, node.album))
			sync_album(connection, child, album)
		else:
			node = find_child_node(remote_children, child.url_name)
			if not node:
				print "Creating node " + child.url_name
				node=Node(remote.create_child_folder(connection, child.name, child.url_name, 'Public'))

			sync_node(connection, child, node)

	for child in remote_children:
		if not find_child_node(local.children, child.url_name):
			if child.uri == root_node.uri:
				import sys
				print "*** About to delete root node"
				sys.exit(1)

			child.delete_node(connection)

def main():
	global root_node

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

	sync_node(connection, root, root_node)

