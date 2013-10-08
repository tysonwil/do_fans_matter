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

def findWeek(weeks, date):
	i = 0
	if (date < weeks[0]) or (date > weeks[17]):
		return -1
	if date == weeks[17]:
		return 18
	while (date >= weeks[i]):
		i += 1
	if i >= 5:
		return i+1
	else:
		return i

def scrapeForum():
	url_start = ''
	week_to_url = {}
	weeks = []
	# Range of each week during the Cowboys 2012 season
	week_range = ['2012-08-01', '2012-09-05', '2012-09-16', '2012-09-23', '2012-10-01', '2012-10-14',
	'2012-10-21', '2012-10-28', '2012-11-04', '2012-11-11', '2012-11-18', '2012-11-22', '2012-12-02',
	'2012-12-09', '2012-12-16', '2012-12-23', '2012-12-30', '2013-01-06']
	for value in week_range:
		weeks.append(datetime.strptime(value,'%Y-%m-%d'))

	for p in range(74,91):
		forum_pg = 'http://boards.dallascowboys.com/forum/10-dallas-cowboys-forum/page-' + str(p)
		page = urlopen(forum_pg)
		soup = BeautifulSoup(page.read())
		search = soup.findAll('td', {'class':'col_f_content '})

		for base in search:
			curr_urls = []
			url = base.find('a', {'class':'topic_title'})['href']

			pagination = base.find('ul', {'class':'mini_pagination'})
			if pagination:
				num_pages = findPages(url, curr_urls)
				print 'NUM pages  ' + str(num_pages)
			else:
				curr_urls.append(url)
			print curr_urls

			d = str(base.find('a', {'class':'topic_title'})['title'])
			d = re.search('- started  (.*) \-', d)
			date = datetime.strptime(d.group(1),'%d %B %Y')
			print date
			week = findWeek(weeks, date)
			print week
			if week != -1:
				if week_to_url.has_key(week):
					updateDict(week_to_url, week, curr_urls)
				else:
					week_to_url[week] = curr_urls
	with open('week_to_url_cowboys.json', 'wb') as fp:
		json.dump(week_to_url, fp)

def getSentiment():
	with open('week_to_url_cowboys.json', 'rb') as fp:
		week_to_url = json.load(fp)

	for wk in range (18, 19):
		wk_total = post_count = pg_count = 0
		for url in week_to_url[str(wk)]:
			pg_count += 1
			page = urlopen(url)
			soup = BeautifulSoup(page.read())
			search = soup.findAll('div', {'itemprop':'commentText'})
			for text in search:
				text = text.getText()
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