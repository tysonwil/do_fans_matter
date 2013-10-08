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

def findPages(url, curr_urls):
	i = 15
	end = '&start='
	curr_urls.append(url)
	while(1):
		p = url + end + str(i)
		page = urlopen(p)
		soup = BeautifulSoup(page.read())
		search = soup.find('td', {'class':'row1'}).getText()
		if 'Could not obtain post/user information' in search:
			return curr_urls
		else:
			curr_urls.append(p)
			i += 15

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
	url_start = 'http://www.footballsfuture.com/phpBB2/'
	week_to_url = {}
	weeks = []
	# Range of each week during the Chiefs 2012 season
	week_range = ['2012-08-01', '2012-09-09', '2012-09-16', '2012-09-23', '2012-09-30', '2012-10-07',
	'2012-10-14', '2012-10-28', '2012-11-01', '2012-11-12', '2012-11-18', '2012-11-25', '2012-12-02',
	'2012-12-09', '2012-12-16', '2012-12-23', '2012-12-30', '2013-01-06']
	for value in week_range:
		weeks.append(datetime.strptime(value,'%Y-%m-%d'))

	for p in range(400, 480, 40): #increments of 40 - end at 720
		print 'PAGE: ' + str(p)
		forum_pg_start = 'http://www.footballsfuture.com/phpBB2/viewforum.php?f=22&topicdays=0&start='
		url_start = 'http://www.footballsfuture.com/phpBB2/'
		forum_pg = forum_pg_start + str(p)
		page = urlopen(forum_pg)
		soup = BeautifulSoup(page.read())

		dates = []
		page_urls = []
		url_search = soup.findAll('td', {'class':'row1'})
		date_search = soup.findAll('td', {'class':'row3Right'})

		for text in url_search:
			url = text.find('a', {'class':'topictitle'})
			if url:
					page_urls.append(url_start + url['href'])
		print page_urls

		for text in date_search:
			date =  text.find('span', {'class':'postdetails'}).getText()[4:16]
			date = datetime.strptime(date, '%b %d, %Y')
			dates.append(date)
		print dates

		# Skip first page which is a sticky
		for i in range(2,41):
			curr_urls = []
			week = findWeek(weeks, dates[i])
			print 'Week: ' + str(week)
			findPages(page_urls[i], curr_urls)
			print curr_urls
			if week != -1:
				if week_to_url.has_key(week):
					updateDict(week_to_url, week, curr_urls)
				else:
					week_to_url[week] = curr_urls
	with open('week_to_url_chiefs.json', 'wb') as fp:
		json.dump(week_to_url, fp)

def getSentiment():
	with open('week_to_url_chiefs.json', 'rb') as fp:
		week_to_url = json.load(fp)

	for wk in range(18, 19): #bye week 7
		wk_total = post_count = pg_count = 0
		for url in week_to_url[str(wk)]:
			pg_count += 1
			page = urlopen(url)
			soup = BeautifulSoup(page.read())
			first = soup.findAll('td', {'colspan':'2'})
			search = soup.findAll('td', {'class':'row2'})
			# Get sentiment for the original post
			sent = client.sentiment(first[4].getText())
			if 'text' in sent:
				score = sent['score']
				wk_total += score
				post_count += 1
				print 'Week: ' + str(wk) + ' Page #: ' + str(pg_count) + ' Post #: ' + str(post_count) + ' SCORE: ' + str(score) + ' TOTAL: ' + str(wk_total)
			# Sentiment for all replies
			for text in search:
				txt = text.find('span', {'class':'postbody'})
				text = text.getText().replace('\n', '')
				if text.startswith('Posted'):
					sent = client.sentiment(text)
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