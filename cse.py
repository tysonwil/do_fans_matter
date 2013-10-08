"""
Finds the weekly sentiment score for a particular team.

Requirements:
- A Google CSE for the domain in which you are searching (EPL/NFL, city, source, etc)
- Repustate API key

Input parameters:
<source> <team> <dates> <cx> <"+"_seperated_keywords> <number_of_results> <NFL_team_file>(NFL only)
"""
import sys
import datetime
from urllib2 import urlopen
import urllib2
import httplib
import simplejson as json
from repustate import Repustate

client = Repustate(api_key='API KEY HERE', version='v2')

def sentiment(source, team):
	"""
	Find sentiment of each CSE result and return a weekly normalized score.
	"""
	with open(source + '/' + team + '/urls.json', 'rb') as fp:
		relevant_urls = json.load(fp)
	weekly_score = {}
	url_cnt = 0

	for date in relevant_urls:
		length = len(relevant_urls[date])
		url_cnt += length
		for url in relevant_urls[date]:
			print url
			try:
				score = client.sentiment(url=url)['score']
			except (urllib2.HTTPError, httplib.BadStatusLine, KeyError):
				print 'Error'
				continue
			print score
			if weekly_score.has_key(date):
				weekly_score[date] += score
			else:
				weekly_score[date] = score
		total = weekly_score[date]
		weekly_score[date] = float(total/length)

	print 'Total pgs: ' + str(url_cnt)

	with open(source + '/' + team + '/score.json', 'wb') as fp:
		json.dump(weekly_score, fp)

def getResults(source, team, date_file, cx, keywords, num_results, NFL):
	"""
	Retrieve relevant results using a Google CSE.
	"""
	cse_start = 'https://www.googleapis.com/customsearch/v1?'
	key = 'key=CSE API KEY HERE'
	cx = '&cx=' + cx
	q = '&q=' + keywords
	date_range = '&sort=date:r:'
	format = '&alt=json'
	start = '&start='
	relevant_urls = {}
	dates = []
	teams = []
	for date in date_file:
		dates.append(date.rstrip())
	if NFL:
		team_list = open(sys.argv[8])
		for t in team_list:
			if t != team:
				teams.append(t.rstrip())

	for date in dates:
		urls = []
		print date
		# Retrieve results
		for s in range(1, num_results, 10):
			# Build URL to search
			search = cse_start + key + cx + q + date_range + date + format + start + str(s)
			result = json.load(urlopen(search))
			if 'items' not in result:
				print 'No results'
				continue
			for u in result['items']:
				if 'vs' in u['link']:
					continue
				if NFL:
					# Make sure post is only talking about this team.
					# This filters out match previews, analysis etc.
					if any(substring in u['link'].lower() for substring in teams):
						continue
				urls.append(u['link'])
		urls = list(set(urls))

		if relevant_urls.has_key(date):
			old = relevant_urls[date]
			new = old + urls
			relevant_urls[date] = new
		else:
			relevant_urls[date] = urls

	with open(source + '/' + team + '/urls.json', 'wb') as fp:
		json.dump(relevant_urls, fp)

def main():
	if len(sys.argv) != (7 or 8):
		print 'Usage: python cse.py <source> <team> <dates> <cx> <"+"_seperated_keywords> <number_of_results> <NFL_team_file>(NFL only)'
	source = sys.argv[1]
	team = sys.argv[2]
	date_file = open(sys.argv[3])
	cx = sys.argv[4]
	keywords = sys.argv[5]
	num_results = int(sys.argv[6]) + 1
	if len(sys.argv) == 8:
		NFL = True
	else: NFL = False
	getResults(source, team, date_file, cx, keywords, num_results, NFL)
	sentiment(source, team)

if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding("utf-8")
	main()