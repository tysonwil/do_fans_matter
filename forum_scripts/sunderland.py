from urllib2 import urlopen
import urllib2
import httplib
import sys
from bs4 import BeautifulSoup
import re
import simplejson as json
from pprint import pprint
from repustate import Repustate
import time
from datetime import datetime
import pickle

client = Repustate(api_key='API KEY HERE', version='v2')

def scrapeForum():
	urls = []
	forum_start = 'http://www.readytogo.net/smb/forumdisplay.php?f=86&order=desc&page='
	forum_end = '&pp=35&sort=lastpost&order=desc&daysprune=365'
	post_start = 'http://www.readytogo.net/smb/'
	post_end = '&page='

	# RETRIEVE ALL FORUM LINKS
	for p in range(45, 950):
		print 'PAGE: ' + str(p)
		url = forum_start + str(p) + forum_end
		page = urlopen(url)
		try:
			soup = BeautifulSoup(page.read())
		except httplib.IncompleteRead:
			continue
		search = soup.findAll('td', {'class':'alt1'})
		for base in search:
			base = base.find('div')
			if not base: continue
			url = base.find('a')
			if url:
				url = url['href']
				if 'showthread' in url:
					urls.append(post_start  + url)
			pagination = base.find('span', {'class':'smallfont'})
			if pagination:
				pages = pagination.findAll('a')
				pages = int(pages[len(pages)-1]['href'].split('=')[3])
				for pg in range(2, pages+1):
					urls.append(post_start + url + post_end + str(pg))
		print 'Total pages: ' + str(len(urls))
	pprint(urls)
	pickle.dump(urls, open('urls.p', 'wb'))

def getSentiment():
	urls = pickle.load(open('urls.p', 'rb'))
	daily_sentiment_score = {}
	post_count = {}
	#with open('daily_sentiment_sunderland.json', 'rb') as fp:
	#	daily_sentiment_score = json.load(fp)
	#with open('post_count_sunderland.json', 'rb') as fp:
	#	post_count = json.load(fp)
	current_url = 0
	num_pages = len(urls)
	print 'Amount of pages to be scraped: ' + str(num_pages)
	for url in urls: #go to page 124560
		dates = []
		posts = []
		current_url += 1
		print '\n' + str(current_url) + '/' + str(len(urls))
		page = urlopen(url)
		soup = BeautifulSoup(page.read())
		search = soup.findAll('div', {'align':'center'})
		for base in search:
			date = base.find('td', {'class':'thead'})
			if date:
				date = date.getText().strip()
				if 'Sponsored' not in date and 'Bookmarks' not in date:
					date = date[:-10]
					date = re.sub('(th|nd|rd|st)', '', date, 1)
					date = str(datetime.strptime(date, '%d %B %Y'))
					dates.append(date)
					text = base.find('div', {'id':re.compile('post_message_\d{8}')})
					if text:
						posts.append(text.getText())

		# Get sentiment of each post on page
		for i in range(0, len(dates), 2):
			date = dates[i]
			text = posts[i]
			try:
				sent = client.sentiment(text)
			except urllib2.HTTPError:
				continue
			if 'text' not in sent:
				continue
			score = sent['score']
			print 'score: ' + str(score)
			if daily_sentiment_score.has_key(date):
				daily_sentiment_score[date] += score
				post_count[date] += 1
				print date
				print 'Daily score: '+ str(daily_sentiment_score[date])
				print 'Number of posts: ' + str(post_count[date])
			else:
				daily_sentiment_score[date] = score
				post_count[date] = 1
				print date
				print 'Daily score: '+ str(daily_sentiment_score[date])
				print 'Number of posts: ' + str(post_count[date])

	with open('daily_sentiment_sunderland.json', 'wb') as fp:
		json.dump(daily_sentiment_score, fp)
	with open('post_count_sunderland.json', 'wb') as fp:
		json.dump(post_count, fp)

def dailySentiment():
	normalized_sent = {}
	f = open('sunderland_daily_sent.txt', 'w')
	total_posts = 0
	with open('daily_sentiment_sunderland.json', 'rb') as fp:
		daily_sentiment = json.load(fp)
	with open('post_count_sunderland.json', 'rb') as fp:
		post_count = json.load(fp)

	for k in daily_sentiment:
		total_posts += post_count[k]
		total_score = daily_sentiment[k]
		num_posts = post_count[k]
		normalized_sent[k] = float(total_score / num_posts)
		print str(k) + ',' + str(normalized_sent[k])
		f.write(str(k) + ',' + str(normalized_sent[k]) + '\n')
	print 'Total posts: ' + str(total_posts)
	with open('normalized_sent.json', 'wb') as fp:
		json.dump(normalized_sent, fp)

def clean():
	dates = []
	with open('normalized_sent.json', 'rb') as fp:
		normalized_sent = json.load(fp)
	out = open('clean_daily.csv', 'wb')
	min_date = datetime.strptime('2012-08-01', '%Y-%m-%d')
	for k in normalized_sent:
		date = datetime.strptime(k[:-9], '%Y-%m-%d')
		#print date
		if date > min_date:
			dates.append(str(date))
	dates.sort()
	for k in dates:
		out.write(k[:-9] + ',' + str(normalized_sent[k]) + '\n')

def main():
	scrapeForum()
	getSentiment()
	dailySentiment()
	clean()

if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding("utf-8")
	main()