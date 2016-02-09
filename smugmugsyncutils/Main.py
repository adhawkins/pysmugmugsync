from SmugMugLocalAlbum import SmugMugLocalAlbum
import argparse

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--site", help="specify which site to upload to")
	parser.add_argument("path")
	args = parser.parse_args()
	print "Site: " + args.site
	print "Path: " + args.path

	root = SmugMugLocalAlbum(directory=args.path)
	print root

