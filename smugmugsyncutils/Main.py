from argparse import ArgumentParser
from Config import Config
from smugmugv2py import Connection, User, Node, Album, AlbumImage
from sys import stdout, stdin, exit
from os import linesep
from json import loads
from SmugMugLocalAlbum import SmugMugLocalAlbum
from requests import exceptions
from pkg_resources import get_distribution

def update_image(connection, remote_image, image_json):
	image_patch={}

	if image_json["keywords"] != remote_image.keywords:
		image_patch["Keywords"]=image_json["keywords"]

	if image_json["caption"] != remote_image.caption:
		image_patch["Caption"]=image_json["caption"]

	if image_json["title"] != remote_image.title:
		image_patch["Title"]=image_json["title"]

	if image_patch:
		print "Updating image " + remote_image.filename
		remote_image.change_album_image(connection, image_patch)

def find_remote_child_node(remote_children, uri, url_name):
	for remote_child in remote_children:
		if (uri and remote_child.uri == uri) or \
				(url_name and remote_child.url_name == url_name):
			return remote_child

def find_local_child_node(local_children, uri, url_name):
	for local_child in local_children:
		if (uri and local_child.json["uri"] == uri) or \
				(url_name and local_child.json["url_name"] == url_name):
			return local_child

def find_remote_image(remote_images, local_image_filename):
	for remote_image in remote_images:
		if remote_image.filename == local_image_filename:
			return remote_image

def find_local_image(local_images, remote_image):
	for local_image in local_images:
		if local_image["name"] == remote_image.filename:
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
		remote_image = find_remote_image(remoteimages, localimage["name"])
		do_upload = False
		if remote_image:
			#print "Image: " + localimage["name"] + \
			#		", localtime: " + str(localimage["mtime"]) + \
			#		", remotetime: " + str(remote_image.last_updated) + \
			#		", localsize: " + str(localimage["size"]) + \
			#		", remotesize: " + str(remote_image.archived_size)

			if localimage["mtime"] > remote_image.last_updated:
				print "Local is newer - updating"
				do_upload = True

			#if localimage["size"] != remote_image.archived_size:
			#	print "Sizes don't match - (" + str(localimage["size"]) + " != " + str(remote_image.archived_size) + ") - updating"
			#	do_upload = True

			if do_upload:
				remote_image.delete_album_image(connection)

		else:
			print("Not found")
			do_upload = True

		if do_upload:
			print "Uploading " + localimage["name"]
			try:
				response = connection.upload_image(local.directory + "/" + localimage["name"], remote.uri)
				if "Image" in response:
					remote_image = AlbumImage.get_album_image(connection, response["Image"]["ImageUri"])
				else:
					print "Error uploading: " + response["message"]
			except exceptions.ConnectionError as e:
				print "ConnectionError: " + str(e)

		if remote_image:
			update_image(connection, remote_image, local.json["files"][localimage["name"]])

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
			node = find_remote_child_node(remote_children, child.json["uri"], child.json["url_name"])
			if not node:
				print "Creating album " + child.json["url_name"]
				node=remote.create_child_album(connection, child.json["name"], child.json["url_name"], 'Public', child.json["description"])

			child.json["uri"]=node.uri

			album=Album.get_album(connection, node.album)
			sync_album(connection, child, album)
		else:
			node = find_remote_child_node(remote_children, child.json["uri"], child.json["url_name"])
			if not node:
				print "Creating node " + child.json["url_name"]
				node=remote.create_child_folder(connection, child.json["title"], child.json["url_name"], 'Public')

			child.json["uri"]=node.uri

			sync_node(connection, child, node)

	print "Checking to delete remote children in " + local.directory
	for child in remote_children:
		if not find_local_child_node(local.children, child.uri, child.url_name):
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
	parser.add_argument("-k", "--api-key", help="smugmug API key")
	parser.add_argument("-s", "--api-secret", help="smugmug API secret")
	args = parser.parse_args()

	root_dir=args.path

	config = Config()
	site_config = {}

	if ("api-key" not in config.json and not args.api_key) or \
		("api-secret" not in config.json and not args.api_secret):
		print "API key and secret must be in either config or on command line"

		parser.print_help()
		exit(-1)

	if args.site in config.json:
		site_config = config.json[args.site]

	save_config = False

	if args.api_key:
		config.json["api-key"] = args.api_key
		save_config = True

	if args.api_secret:
		config.json["api-secret"] = args.api_secret
		save_config = True

	if "exclusions" not in site_config:
		save_config = True
		site_config["exclusions"]=[]

	connection = Connection(config.json["api-key"],
													config.json["api-secret"],
													user_agent = "pysmugmugsync/" + get_distribution('pysmugmugsync').version
												)

	if args.reauth or "token" not in site_config or "secret" not in site_config:
		auth_url = connection.get_auth_url(access="Full", permissions="Modify")

		print "Visit the following URL and retrieve a verification code:%s%s" % (linesep, auth_url)

		stdout.write('Enter the six-digit code: ')
		stdout.flush()
		verifier = stdin.readline().strip()

		at, ats = connection.get_access_token(verifier)

		site_config["token"] = at
		site_config["secret"] = ats
		save_config = True

	if save_config:
		config.json[args.site] = site_config
		config.write()

	connection.authorise_connection(site_config["token"], site_config["secret"])
	user = User.get_authorized_user(connection)
	print "User: " + user.nickname + " (" + user.name + ")"
	root_node = Node.get_node(connection,user.node)

	root = SmugMugLocalAlbum(exclusions=site_config["exclusions"], directory=args.path)

	sync_node(connection, root, root_node)

