from argparse import ArgumentParser
from Config import Config
from smugmugv2py import SmugMugConnection
from sys import stdout, stdin
from os import linesep
from json import loads

api_key = "Bwlfnuv1WMNUkcPynYuElBDBy2e8k7Am"
api_secret = "e808da94417c928654353b1199afdebf"

def main():
	parser = ArgumentParser()
	parser.add_argument("site", help="the site to upload to")
	parser.add_argument("path", help="the path containing local photos")
	parser.add_argument("-r", "--reauth", help="force reauthorisation", action="store_true")
	args = parser.parse_args()
	print "Site: " + args.site
	print "Path: " + args.path

	config = Config(args.site)

	connection = SmugMugConnection(api_key, api_secret)

	if args.reauth or not config.token or not config.secret:
		auth_url = connection.get_auth_url()

		print "Visit the following URL and retrieve a verification code:%s%s" % (linesep, auth_url)

		stdout.write('Enter the six-digit code: ')
		stdout.flush()
		verifier = stdin.readline().strip()

		at, ats = connection.get_access_token(verifier)

		config.token = at
		config.secret = ats
		config.write(args.site)

	connection.authorise_connection(config.token, config.secret)

	json = connection.test_connection()
	result = loads(json)
	print result["Response"]["User"]["Name"]
