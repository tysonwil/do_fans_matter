from urllib2 import urlopen
import sys
from bs4 import BeautifulSoup
import re
import simplejson as json
from pprint import pprint
from repustate import Repustate
import time
from datetime import datetime

client = Repustate(api_key='API KEY HERE', version='v2')

def updateDict(dictionary, key, new_val):
	current_val = dictionary[key]
	new_array = current_val + new_val
	dictionary[key] = new_array

def findWeek(weeks, date):
	i = 0
	bye_wk = 7
	if (date < weeks[0]) or (date > weeks[17]):
		return -1
	if date == weeks[17]:
		return 18
	while (date >= weeks[i]):
		i += 1
	if i >= bye_wk:
		return i+1
	else:
		return i

def scrapeForum():
	url_start = ''
	week_to_url = {}
	weeks = []
	# Range of each week during the Eagles 2012 season
	week_range = ['2012-08-01', '2012-09-09', '2012-09-16', '2012-09-23', '2012-09-30', '2012-10-07',
	'2012-10-14', '2012-10-28', '2012-11-05', '2012-11-11', '2012-11-18', '2012-11-26', '2012-12-02',
	'2012-12-09', '2012-12-13', '2012-12-23', '2012-12-30', '2013-01-06']
	for value in week_range:
		weeks.append(datetime.strptime(value,'%Y-%m-%d'))

	for p in range(1380, 1560, 30): #increments of 30 - start at 1350
		print 'PAGE: ' + str(p)
		forum_pg_start = 'http://boards.philadelphiaeagles.com/forum/30-the-411/page__prune_day__100__sort_by__Z-A__sort_key__last_post__topicfilter__all__st__'
		forum_pg = forum_pg_start + str(p)
		page = urlopen(forum_pg)
		soup = BeautifulSoup(page.read())
		search = soup.findAll('td', {'class':'col_f_content '})
		for base in search:
			curr_urls = []
			url = base.find('a', {'class':'topic_title'})['href']
			curr_urls.append(url)
			print url
			date = base.find('span', {'itemprop':'dateCreated'}).getText()
			date = datetime.strptime(date, '%d %b %Y')
			print date
			week = findWeek(weeks, date)
			print 'Week:   ' + str(week)
			if week != -1:
				if week_to_url.has_key(week):
					updateDict(week_to_url, week, curr_urls)
				else:
					week_to_url[week] = curr_urls
	with open('week_to_url_eagles.json', 'wb') as fp:
		json.dump(week_to_url, fp)

def getSentiment():
	with open('week_to_url_eagles.json', 'rb') as fp:
		week_to_url = json.load(fp)

	for wk in range(18, 19): #bye week 7
		wk_total = post_count = pg_count = 0
		for url in week_to_url[str(wk)]:
			pg_count += 1
			sent = client.sentiment(url=url)
			if 'text' in sent:
				score = sent['score']
				wk_total += score
				post_count += 1
				print 'Week: ' + str(wk) + ' Page #: ' + str(pg_count) + ' Post #: ' + str(post_count) + ' SCORE: ' + str(score) + ' TOTAL: ' + str(wk_total)
		final_wk_score = float(wk_total/post_count)
		print 'FINAL WEEK SCORE:    ' + str(wk) + '     ' + str(final_wk_score)

def main():
	scrapeForum()
	getSentiment()

if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding("utf-8")
	main()