from urllib2 import urlopen
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
	post_start = 'http://www.redcafe.net/'
	post_end = 'page-'
	forum_start = 'http://www.redcafe.net/forums/manchester-united-forum.6/page-'

	# GET ALL FORUM LINKS
	for p in range(3, 38):
		print 'PAGE: ' + str(p)
		url = forum_start + str(p)
		page = urlopen(url)
		soup = BeautifulSoup(page.read())
		search = soup.findAll('div', {'class':'titleText'})
		for base in search:
			link = post_start + base.find('a')['href'] + post_end
			print link
			pages = base.find('span', {'class': 'itemPageNav'})
			if pages:
				pages = int(pages.getText().split('\n')[-2])
				for pg in range(1, pages+1):
					urls.append(link + str(pg))
			else:
				urls.append(link + '1')
	pickle.dump(urls, open('urls.p', 'wb'))

def getSentiment():
	urls = pickle.load(open('urls.p', 'rb'))
	daily_sentiment = {}
	post_count = {}
	num_pages = len(urls)
	print 'Amount of pages to be scraped: ' + str(num_pages)
	url_count = 0
	for url in urls:
		url_count += 1
		print str(url_count) + '/' + str(num_pages)
		page = urlopen(url)
		soup = BeautifulSoup(page.read())
		search = soup.findAll('li')
		for base in search:
			msg = base.find('div', {'class':'messageContent'})
			if not msg:
				continue
			sent = client.sentiment(msg)
			if 'text' not in sent:
				continue
			score = sent['score']
			print 'score: ' + str(score)
			date = base.find('span', {'class':'DateTime'})
			if not date:
				continue
			date = str(datetime.strptime(date.getText(),'%b %d, %Y'))[:-9]
			if daily_sentiment.has_key(date):
				daily_sentiment[date] += score
				post_count[date] += 1
				print date
				print daily_sentiment[date]
				print post_count[date]
			else:
				daily_sentiment[date] = score
				post_count[date] = 1
				print date
				print daily_sentiment[date]
				print post_count[date]
	with open('daily_sentiment_manutd.json', 'wb') as fp:
		json.dump(daily_sentiment, fp)
	with open('post_count_manutd.json', 'wb') as fp:
		json.dump(post_count, fp)

def dailySentiment():
	normalized_sent = {}
	f = open('manutd_daily_sent.txt', 'w')
	total_posts = 0
	with open('daily_sentiment_manutd.json', 'rb') as fp:
		daily_sentiment = json.load(fp)
	with open('post_count_manutd.json', 'rb') as fp:
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
		date = datetime.strptime(k, '%Y-%m-%d')
		#print date
		if date > min_date:
			dates.append(str(date))
	dates.sort()
	for k in dates:
		out.write(k[:-9] + ',' + str(normalized_sent[k[:-9]]) + '\n')

def main():
	scrapeForum()
	getSentiment()
	dailySentiment()
	clean()

if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding("utf-8")
	main()