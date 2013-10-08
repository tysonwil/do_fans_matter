import sys
from pprint import pprint

#average sentiment following a loss!

def main():

	team_file = open(sys.argv[1])
	info = {}
	
	#LOAD IN INFO DICT THE SENTIMENTS AND LOSS INFO
	for line in team_file:
		columns = line.split(",")
		if columns[0] != '' :
			info[columns[0]] = dict(forum = float(columns[1]) , news = float(columns[2]), blog = float(columns[3]))
			if columns[4] == '0':
				info[columns[0]]['loss'] = 0
			else:
				info[columns[0]]['loss'] = 1

	#print " INFO : " , info
	pprint(info)
	# sentiments following loss
	forums_sentiment = []
	news_sentiment = []
	blogs_sentiment = []

	week = 1
	stop = None
	while stop is None:
		loss = info[str(week)]['loss']
		if loss == 1:
			forums_sentiment.append(info[str(week + 1)]['forum'])
			news_sentiment.append(info[str(week + 1)]['news'])
			blogs_sentiment.append(info[str(week + 1)]['blog'])

		week += 1
		if str(week) not in info:
			stop = True

	# average before loss
	forums_avg = sum(forums_sentiment)/len(forums_sentiment)
	news_avg = sum(news_sentiment)/len(news_sentiment)
	blogs_avg = sum(blogs_sentiment)/len(blogs_sentiment)

	# print results
	print "forums : ", forums_avg
	print "news : ", news_avg
	print "blogs : ", blogs_avg

if __name__ == '__main__':
	main()