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
	forum_start = 'http://www.tottenhamhotspurs.tv/players-lounge/index'
	forum_end = '.html'
	post_end = 'page-'
	# replace 'forum/' with '' , add -pg , then .html

	# RETRIEVE ALL FORUM LINKS
	for p in range(5, 71):
		print 'PAGE: ' + str(p)
		url = forum_start + str(p) + forum_end
		page = urlopen(url)
		soup = BeautifulSoup(page.read())
		search = soup.findAll('div', {'class':'inner'})
		for base in search:
			if 'Sticky' in base.getText():
				continue
			url = base.find('a', {'class':'title'})['href']
			urls.append(url)
			print url
			pagination = base.find('dl', {'class':'pagination'})
			if not pagination:
				continue
			pages = re.search('(.*) Pages', pagination.getText())
			pages = int(pages.group(1))
			for pg in range(2, pages+1):
				curr_url = url.replace('forum/', '') + '-' + str(pg) + '.html'
				urls.append(curr_url)
				print curr_url
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
		search = soup.findAll('li', {'class':'postbitlegacy postbitim postcontainer old'})
		for base in search:
			date = base.find('span', {'class':'date'})
			if not date:
				continue
			date = date.getText()[:-10]
			date = str(datetime.strptime(date, '%d-%m-%Y'))[:-9]
			print date
			text = base.find('blockquote', {'class':'postcontent restore '})
			if not text:
				continue
			text = text.getText()
			sent = client.sentiment(text)
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
	with open('daily_sentiment_tottenham.json', 'wb') as fp:
		json.dump(daily_sentiment_score, fp)
	with open('post_count_tottenham.json', 'wb') as fp:
		json.dump(post_count, fp)

def dailySentiment():
	normalized_sent = {}
	f = open('tottenham_daily_sent.txt', 'w')
	total_posts = 0
	with open('daily_sentiment_tottenham.json', 'rb') as fp:
		daily_sentiment = json.load(fp)
	with open('post_count_tottenham.json', 'rb') as fp:
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
			#out.write(str(date)[:-9] + ',' + str(normalized_sent[k]) + '\n')
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