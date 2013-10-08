import sys
from pprint import pprint

# How often the sentiment increases/decreases after a win/loss

def main():
	win_count = 0
	loss_count = 0
	team_file = open(sys.argv[1])
	info = {}
	
	#LOAD IN INFO DICT THE SENTIMENTS AND LOSS INFO
	for line in team_file:
		columns = line.split(",")
		if columns[0] != '' :
			info[columns[0]] = dict(forum = float(columns[1]) , news = float(columns[2]), blog = float(columns[3]))
			if columns[4].strip() == '0':
				info[columns[0]]['loss'] = 0
				win_count += 1
			elif columns[4].strip() == '-1':
				info[columns[0]]['loss'] = -1
			else:
				info[columns[0]]['loss'] = 1
				loss_count += 1
				
	sorted_weeks = []
	neg_after_win = [0, 0, 0]
	pos_after_win = [0, 0, 0]
	neg_after_loss = [0, 0, 0]
	pos_after_loss = [0, 0, 0]

	for k in info:
		if k == 'END': k = len(info)
		sorted_weeks.append(int(k))
	sorted_weeks.sort()

	for week in range(1, len(sorted_weeks)):
		wk = str(week)
		next_wk = str(week+1)
		loss = info[wk]['loss']
		forum = (info[wk]['forum'], info[next_wk]['forum'])
		news = (info[wk]['news'], info[next_wk]['news'])
		blog = (info[wk]['blog'], info[next_wk]['blog'])
		if loss == 1:
			if forum[0] < forum[1]: pos_after_loss[0] += 1
			else: neg_after_loss[0] += 1
			if news[0] < news[1]: pos_after_loss[1] += 1
			else: neg_after_loss[1] += 1
			if blog[0] < blog[1]: pos_after_loss[2] += 1
			else: neg_after_loss[2] += 1
		else:
			if forum[0] < forum[1]: pos_after_win[0] += 1
			else: neg_after_win[0] += 1
			if news[0] < news[1]: pos_after_win[1] += 1
			else: neg_after_win[1] += 1
			if blog[0] < blog[1]: pos_after_win[2] += 1
			else: neg_after_win[2] += 1

	# print results
	"""
	print 'Positive after win\nForum:\t', float(pos_after_win[0])/game_count, '\nNews:\t', float(pos_after_win[1])/game_count, '\nBlog:\t', float(pos_after_win[2])/game_count
	print 'Negative after win\nForum:\t', float(neg_after_win[0])/game_count, '\nNews:\t', float(neg_after_win[1])/game_count, '\nBlog:\t', float(neg_after_win[2])/game_count
	print 'Positive after loss\nForum:\t', float(pos_after_loss[0])/game_count, '\nNews:\t', float(pos_after_loss[1])/game_count, '\nBlog:\t', float(pos_after_loss[2])/game_count
	print 'Negative after loss\nForum:\t', float(neg_after_loss[0])/game_count, '\nNews:\t', float(neg_after_loss[1])/game_count, '\nBlog:\t', float(neg_after_loss[2])/game_count
	"""
	print float(pos_after_win[0])/win_count, '\n', float(pos_after_win[1])/win_count, '\n', float(pos_after_win[2])/win_count, '\n\n'
	print float(neg_after_win[0])/win_count, '\n', float(neg_after_win[1])/win_count, '\n', float(neg_after_win[2])/win_count, '\n\n'
	print float(pos_after_loss[0])/loss_count, '\n', float(pos_after_loss[1])/loss_count, '\n', float(pos_after_loss[2])/loss_count, '\n\n'
	print float(neg_after_loss[0])/loss_count, '\n', float(neg_after_loss[1])/loss_count, '\n', float(neg_after_loss[2])/loss_count, '\n'

if __name__ == '__main__':
	main()


