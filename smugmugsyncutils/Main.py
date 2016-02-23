from argparse import ArgumentParser
from Config import Config
from smugmugv2py import Connection, User, Node, Album, SmugMugv2Utils
from sys import stdout, stdin
from os import linesep
from json import loads
from SmugMugLocalAlbum import SmugMugLocalAlbum

api_key = "LXTk156AmDT0IhjLuDetBUwP9nWKCppg"
api_secret = "be735fbb3b44698d72506b29e21a434c"

def find_remote_child_node(remote_children, uri):
	for remote_child in remote_children:
		if remote_child.uri == uri:
			return remote_child

def find_local_child_node(local_children, uri):
	for local_child in local_children:
		if local_child.json["uri"] == uri:
			return local_child

def find_remote_image(remote_images, local_image_filename):
	for remote_image in remote_images:
		if remote_image.filename == local_image_filename:
			return remote_image

def find_local_image(local_images, remote_image):
	for local_image in local_images:
		if local_image == remote_image.filename:
			return local_image

def sync_album(connection, local, remote):
	print "Syncing local album " + local.json["url_name"] + " with remote " + remote.url_name

	remoteimages = remote.get_images(connection)

	if local.directory != root_dir:
		album_patch={}

		if local.json["description"] != remote.description:
			album_patch["Description"]=local.json["description"]

		if local.json["url_name"] != remote.url_name:
			album_patch["UrlName"]=local.json["url_name"]

		if local.json["keywords"] != remote.keywords:
			album_patch["Keywords"]=local.json["keywords"]

		if local.json["name"] != remote.name:
			album_patch["Name"]=local.json["name"]

		if local.json["album_sort_method"] != remote.sort_method:
			album_patch["SortMethod"]=local.json["album_sort_method"]

		if album_patch:
			remote.change_album(connection, album_patch)

	for localimage in local.items:
		if not find_remote_image(remoteimages, localimage):
			print "Not found, uploading " + localimage
			connection.upload_image(local.directory + "/" + localimage, remote.uri)

	for remoteimage in remoteimages:
		if not find_local_image(local.items, remoteimage):
			print "Not found, deleting " + remoteimage.filename
			remoteimage.delete_album_image(connection)

	local.save_json()

def sync_node(connection, local, remote):
	global root_node
	global root_dir

	print "Syncing node " + local.json["url_name"] + " with " + remote.url_name
	remote_children = remote.get_children(connection)

	if local.directory != root_dir:
		node_patch={}

		if local.json["description"] != remote.description:
			node_patch["Description"]=local.json["description"]

		if local.json["url_name"] != remote.url_name:
			node_patch["UrlName"]=local.json["url_name"]

		if local.json["node_sort_method"] != remote.sort_method:
			node_patch["SortMethod"]=local.json["node_sort_method"]

		if node_patch:
			remote.change_node(connection, node_patch)

	for child in local.children:
		if child.items:
			node = find_remote_child_node(remote_children, child.json["uri"])
			if not node:
				print "Creating album " + child.json["url_name"]
				node=Node(remote.create_child_album(connection, child.json["name"], child.json["url_name"], 'Public', child.json["description"]))
				child.json["uri"]=node.uri

			album=Album(SmugMugv2Utils.get_album(connection, node.album))
			sync_album(connection, child, album)
		else:
			node = find_remote_child_node(remote_children, child.json["uri"])
			if not node:
				print "Creating node " + child.json["url_name"]
				node=Node(remote.create_child_folder(connection, child.json["title"], child.json["url_name"], 'Public'))
				child.json["uri"]=node.uri

			sync_node(connection, child, node)

	for child in remote_children:
		if not find_local_child_node(local.children, child.uri):
			if child.uri == root_node.uri:
				import sys
				print "*** About to delete root node"
				sys.exit(1)

			child.delete_node(connection)

	local.save_json()

def main():
	global root_node
	global root_dir

	parser = ArgumentParser()
	parser.add_argument("site", help="the site to upload to")
	parser.add_argument("path", help="the path containing local photos")
	parser.add_argument("-r", "--reauth", help="force reauthorisation", action="store_true")
	args = parser.parse_args()
	print "Site: " + args.site
	print "Path: " + args.path
	root_dir=args.path

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

