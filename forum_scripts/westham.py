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
	forum_start = 'http://www.kumb.com/forum/viewforum.php?f=2&st=0&sk=t&sd=d&start='
	post_start = 'http://www.kumb.com/forum'
	post_end = '&start='

	# RETRIEVE ALL FORUM LINKS
	for p in range(125, 2125, 25):
		print 'PAGE: ' + str(p)
		url = forum_start + str(p)
		page = urlopen(url)
		soup = BeautifulSoup(page.read())
		search1 = soup.findAll('li', {'class':'row bg1'})
		search2 = soup.findAll('li', {'class':'row bg2'})
		search = search1 + search2
		for base in search:
			#print base
			url = base.find('a', {'class':'topictitle'})['href'].split('&sid')[0][1:]
			if '30546' in url:  #Sticky post
				continue
			url = post_start + url
			print url
			pagination = base.find('strong', {'class':'pagination'})
			if pagination:
				pages = pagination.getText()
				pages = int(pages.split(',')[-1][1:])
				print pages
				for pg in range(0, (pages+1) * 20, 20):
					urls.append(url + post_end + str(pg))
			else:
				urls.append(url)
	pprint(urls)
	pickle.dump(urls, open('urls.p', 'wb'))

def getSentiment():
	urls = pickle.load(open('urls.p', 'rb'))
	daily_sentiment_score = {}
	post_count = {}
	current_url = 0
	num_pages = len(urls)
	print 'Amount of pages to be scraped: ' + str(num_pages)
	for url in urls:
		current_url += 1
		print str(current_url) + '/' + str(len(urls))
		page = urlopen(url)
		soup = BeautifulSoup(page.read())
		search = soup.findAll('div', {'class':'postbody'})
		for base in search:
			#print base
			date = base.find('p')
			if not date: continue
			date = re.search('by (.*) on (.*) [ap]m', date.getText())
			date = date.group(2)[4:16]
			date = str(datetime.strptime(date, '%b %d, %Y'))
			print date
			text = base.find('div', {'class':'content'})
			if not text: continue
			text = text.getText()
			sent = client.sentiment(text)
			if 'text' not in sent: continue
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
	with open('daily_sentiment_westham.json', 'wb') as fp:
		json.dump(daily_sentiment_score, fp)
	with open('post_count_westham.json', 'wb') as fp:
		json.dump(post_count, fp)

def dailySentiment():
	normalized_sent = {}
	f = open('westham_daily_sent.txt', 'w')
	total_posts = 0
	with open('daily_sentiment_westham.json', 'rb') as fp:
		daily_sentiment = json.load(fp)
	with open('post_count_westham.json', 'rb') as fp:
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
			#out.write(str(date)[:-9] + ',' + str(normalized_sent[k]) + '\n')
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