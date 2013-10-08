from urllib2 import urlopen
import sys
from bs4 import BeautifulSoup
import re
import simplejson as json
from pprint import pprint
from repustate import Repustate

client = Repustate(api_key='API KEY HERE', version='v2')

def findWeek(date):
	print date
	# Range of each week that will be analyzed for the 2012 Ravens season. Formatted as mm/dd
	week_ranges = [
		(801, 910), (910, 916), (916, 923), (923, 927), (927, 1007), (1007, 1014), (1014, 1021),
		(1021, 1104), (1104, 1111), (1111, 1118), (1118, 1125), (1125, 1202), (1202, 1209), (1209, 1216),
		(1216, 1223), (1223, 1230), (1, 106), (106, 112), (112, 120), (120, 203), (203, 210)
		]
	if date == 1231:
		return 18
	for i in range(len(week_ranges)):
		if date in range(week_ranges[i][0], week_ranges[i][1]):
			if i >= 7:
				print 'week: ' + str(i+2)
				return i + 2
			else:
				print 'week: ' + str(i+1)
				return i + 1
	return 0

def updateDict(dictionary, key, new_val):
	current_val = dictionary[key]
	new_array = current_val + new_val
	dictionary[key] = new_array

def scrapeForum(week_to_url):
	url_start = 'http://russellstreetreport.com/forum/'

	for p in range(40, 54):
		url = 'http://russellstreetreport.com/forum/forumdisplay.php?3-Ravens-24x7/page' + str(p)

		page = urlopen(url)

		soup = BeautifulSoup(page.read())
		search = soup.findAll('div', {'class':'inner'})

		for base in search:
			num_pages = 1
			curr_urls = []
			titles = base.findAll('a', {'class':'title'})
			dates = base.findAll('a', {'class':'username understate'})
			pages = base.findAll('dt', {'class':'label'})

			if pages:
				num_pages = int(str(pages[0])[18])

			for t in titles:
				for i in range(1, num_pages+1):
					curr_urls.append(url_start + t['href'].split('&')[0] + '/page' + str(i))
				print (curr_urls)

			for d in dates:
				date = int(d['title'][-19:-13].replace('-', '').lstrip('0'))
				week = findWeek(date)
				if week != 0:
					if week_to_url.has_key(week):
						updateDict(week_to_url, week, curr_urls)
					else:
						week_to_url[week] = curr_urls

	with open('week_to_url.json', 'wb') as fp:
		json.dump(week_to_url, fp)

def getPosts(url):
	clean_posts = []
	extraneous_text = ('Re:', 'You may not', 'Posting Permissions', 'Forum Rules', '.', 'Everywhere sidebar')
	posts = client.clean_html(url)
	if 'text' in posts:
		posts = posts['text'].split('\n')
	else:
		return None
	for text in posts:
		text = text.strip()
		if text.startswith(extraneous_text):
			continue
		clean_posts.append(text)
	return clean_posts

def getSentiment():
	print "SENTIMENT"
	with open('week_to_url.json', 'rb') as fp:
		week_to_url = json.load(fp)

	#for wk in range(16,22):
	wk = '22'
	week_total = 0
	post_count = 0
	pg_count = 0
	for url in week_to_url[wk]:
		posts = getPosts(url)
		if posts is None:
			continue
		pg_count += 1
		for p in posts:
			sent = client.sentiment(p)
			if 'text' in sent:
				week_total += sent['score']
				post_count += 1
				print 'Week: ' + str(wk) + ' Page #: ' + str(pg_count) + ' Post #: ' + str(post_count) + ' SCORE: ' + str(sent['score']) + ' TOTAL: ' + str(week_total)

	final_week_score = float(week_total/post_count)
	print 'FINAL WEEK SCORE:    ' + str(wk) + '     ' + str(final_week_score)


def main():
	week_to_url = {}
	scrapeForum(week_to_url)
	getText()
	getSentiment()


if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding("utf-8")
	main()