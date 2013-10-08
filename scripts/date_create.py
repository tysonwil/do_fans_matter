import sys
import time
from datetime import datetime, timedelta
import re

def main():
	date_file = open(sys.argv[1], 'r')
	dates = []
	dates2 = []
	ranges = []
	clean = []

	for line in date_file:
		date = re.match('\d* (\d+ .* \d{4})', line)
		if date:
			print date.group(1)
			clean.append(date.group(1))

	for line in clean:
		line = line.strip()
		date = datetime.strptime(line, '%d %B %Y')
		date2 = date - timedelta(days=1)
		dates.append(date.strftime('%Y%m%d'))
		dates2.append(date2.strftime('%Y%m%d'))
	dates.sort()
	dates2.sort()

	for i in range(0, len(dates)-1):
		d1 = dates[i]
		d2 = dates2[i+1]
		ranges.append(d1 + ':' + d2)
	print ranges

if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding("utf-8")
	main()