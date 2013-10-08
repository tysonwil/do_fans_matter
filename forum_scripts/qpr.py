from urllib2 import urlopen
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
	forum_start = 'http://www.qprdot.org/viewforum.php?f=12&topicdays=0&start='
	post_start = 'http://www.qprdot.org/'
	post_end = '&start='

	# RETRIEVE ALL FORUM LINKS
	for p in range(150, 4600, 25):
		print 'PAGE: ' + str(p)
		url = forum_start + str(p)
		page = urlopen(url)
		try:
			soup = BeautifulSoup(page.read())
		except httplib.IncompleteRead:
			continue
		search = soup.findAll('td', {'class':'row1'})
		for base in search:
			url = base.find('a')
			if not url: continue
			url = post_start + url['href'].split('&')[0]
			if '47093' in url or '42076' in url: continue  # Stickies
			if 'Goto page' in base.getText():
				pages = base.getText().split(',')
				pages = int(re.sub('[ \]]', '', pages[len(pages)-1]))
				for pg in range(0, (pages)*15, 15):
					urls.append(url + post_end + str(pg))
			else:
				urls.append(url)
		print 'Total pages: ' + str(len(urls))
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
		page = page.read()
		soup = BeautifulSoup(page)
		search = soup.findAll('td', {'class':'row2'})
		for base in search:
			if 'Posted:' in base.getText():
				base = base.getText().strip().replace('\n', '')
				date = re.search('Posted: .{4}(\w{3} \d{2}, \d{4}).*', base)
				if date:
					date = str(datetime.strptime(date.group(1), '%b %d, %Y'))
					#print date
				text = re.search('Post subject:(.*)', base)
				if text:
					text = text.group(1).strip()
					#print text

			# Call Repustate for sentiment of each post
				try:
					sent = client.sentiment(text)
				except urllib2.HTTPError:
					continue
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

	with open('daily_sentiment_qpr.json', 'wb') as fp:
		json.dump(daily_sentiment_score, fp)
	with open('post_count_qpr.json', 'wb') as fp:
		json.dump(post_count, fp)

def dailySentiment():
	normalized_sent = {}
	f = open('qpr_daily_sent.txt', 'w')
	total_posts = 0
	with open('daily_sentiment_qpr.json', 'rb') as fp:
		daily_sentiment = json.load(fp)
	with open('post_count_qpr.json', 'rb') as fp:
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