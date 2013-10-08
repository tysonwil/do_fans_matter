from urllib2 import urlopen
import sys
from datetime import datetime
import time
from bs4 import BeautifulSoup
import re
import simplejson as json
from pprint import pprint
from repustate import Repustate
import requests

client = Repustate(api_key='API KEY HERE', version='v2')

def findPages(url, curr_urls):
	i = 2
	try_url = url + 'page-'
	curr_urls.append(url)
	while(1):
		try_url = try_url + str(i)
		page1 = urlopen(url).geturl()
		page2 = urlopen(try_url).geturl()
		if page1 == page2:
			return i-1
		curr_urls.append(try_url)
		i += 1
		url = try_url

def updateDict(dictionary, key, new_val):
	current_val = dictionary[key]
	new_array = current_val + new_val
	dictionary[key] = new_array

def findWeek(weeks, date):
	i = 0
	if (date < weeks[0]) or (date > weeks[19]):
		return -1
	if date == weeks[19]:
		return 20
	while (date >= weeks[i]):
		i += 1
	if i >= 10:
		return i+1
	else:
		return i

def scrapeForum():
	weeks = []
	week_to_url = {}
	url_start = 'http://www.packerforum.com/'
	# Range of each week during the Packers 2012 season
	week_range = ['2012-08-01', '2012-09-09', '2012-09-13', '2012-09-24', '2012-09-30', '2012-10-07',
	'2012-10-14', '2012-10-21', '2012-10-28', '2012-11-04', '2012-11-18', '2012-11-25', '2012-12-02',
	'2012-12-09', '2012-12-16', '2012-12-23', '2012-12-30', '2013-01-05', '2013-01-12', '2013-01-19']
	for value in week_range:
		weeks.append(datetime.strptime(value,'%Y-%m-%d'))

	for p in range(15, 20):
		url = 'http://www.packerforum.com/forums/packer-fan-forum.20/page-' + str(p)
		page = urlopen(url)
		soup = BeautifulSoup(page.read())
		base = soup.findAll('div', {'class':'titleText'})

		for text in base:
			curr_urls = []
			url = url_start + text.find('a')['href']
			num_pages = findPages(url, curr_urls)
			print 'NUM pages  ' + str(num_pages)

			date_base = str(text.find('span',{'class':'DateTime'}))
			date = date_base[-19:-7].replace('>', '')
			date = client.date_extraction(date)['dates'][0]
			date = datetime.strptime(date,'%Y-%m-%d')
			print date

			week = findWeek(weeks, date)
			print 'WEEK:   ' + str(week)
			if week != -1:
				if week_to_url.has_key(week):
					updateDict(week_to_url, week, curr_urls)
				else:
					week_to_url[week] = curr_urls

	with open('week_to_url_packers_2.json', 'wb') as fp:
		json.dump(week_to_url, fp)


def getSentiment():
	with open('week_to_url_packers_2.json', 'rb') as fp:
		week_to_url = json.load(fp)

	for wk in range (20, 21):
		pg_count = 0 
		post_count = 0
		total = 0
		score = 0
		values = week_to_url[str(wk)]
		print 'week: ' + str(wk)
		for url in values:
			pg_count += 1
			page = urlopen(url)
			soup = BeautifulSoup(page.read())
			search = soup.findAll('blockquote')
			print search
			for text in search:
				posts = ''.join(text.findAll(text=True))
				sent = client.sentiment(posts)
				if 'text' in sent:
					post_count += 1
					total += sent['score']
					print 'Week: ' + str(wk) + ' Page #: ' + str(pg_count) + ' Post #: ' + str(post_count) + ' SCORE: ' + str(sent['score']) + ' TOTAL: ' + str(total)
		final_week_score = float(total/post_count)
		print 'FINAL WEEK SCORE:    ' + str(wk) + '     ' + str(final_week_score)

def main():
	scrapeForum()
	getSentiment()

if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding("utf-8")
	main()