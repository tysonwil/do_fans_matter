import sys

# How often the sentiment increases/decreases after a win/loss

def main():
	win_count = 0
	loss_count = 0
	tie_count = 0
	team_file = open(sys.argv[1])
	info = {}
	
	#LOAD IN INFO DICT THE SENTIMENTS AND WIN INFO
	for line in team_file:
		columns = line.split(",")
		if columns[0] != '' :
			info[columns[0]] = dict(forum = float(columns[1]) , news = float(columns[2]), blog = float(columns[3]), tabloid = float(columns[4]))
			if columns[5].strip() == '1':
				info[columns[0]]['win'] = 1
				win_count += 1
			elif columns[5].strip() == '-1':
				info[columns[0]]['win'] = -1
				loss_count += 1
			elif columns[5].strip() == '0':
				info[columns[0]]['win'] = 0
				tie_count += 1

	neg_after_win = [0, 0, 0, 0]
	pos_after_win = [0, 0, 0, 0]
	neg_after_loss = [0, 0, 0, 0]
	pos_after_loss = [0, 0, 0, 0]
	neg_after_tie = [0, 0, 0, 0]
	pos_after_tie = [0, 0, 0, 0]
	sorted_weeks = []

	for k in info:
		if k == 'END': k = len(info)
		sorted_weeks.append(int(k))
	sorted_weeks.sort()

	for week in range(1, len(sorted_weeks)):
		wk = str(week)
		next_wk = str(week+1)
		win = info[wk]['win']
		forum = (info[wk]['forum'], info[next_wk]['forum'])
		news = (info[wk]['news'], info[next_wk]['news'])
		blog = (info[wk]['blog'], info[next_wk]['blog'])
		tabloid = (info[wk]['tabloid'], info[next_wk]['tabloid'])

		if win == 1:
			if forum[0] < forum[1]: pos_after_win[0] += 1
			else: neg_after_win[0] += 1
			if news[0] < news[1]: pos_after_win[1] += 1
			else: neg_after_win[1] += 1
			if blog[0] < blog[1]: pos_after_win[2] += 1
			else: neg_after_win[2] += 1
			if tabloid[0] < tabloid[1]: pos_after_win[3] += 1
			else: neg_after_win[3] += 1
		elif win == -1:
			if forum[0] < forum[1]: pos_after_loss[0] += 1
			else: neg_after_loss[0] += 1
			if news[0] < news[1]: pos_after_loss[1] += 1
			else: neg_after_loss[1] += 1
			if blog[0] < blog[1]: pos_after_loss[2] += 1
			else: neg_after_loss[2] += 1
			if tabloid[0] < tabloid[1]: pos_after_loss[3] += 1
			else: neg_after_loss[3] += 1
		elif win == 0:
			if forum[0] < forum[1]: pos_after_tie[0] += 1
			else: neg_after_tie[0] += 1
			if news[0] < news[1]: pos_after_tie[1] += 1
			else: neg_after_tie[1] += 1
			if blog[0] < blog[1]: pos_after_tie[2] += 1
			else: neg_after_tie[2] += 1
			if tabloid[0] < tabloid[1]: pos_after_tie[3] += 1
			else: neg_after_tie[3] += 1

	# print results
	print 'Positive after win\nForum:\t', float(pos_after_win[0])/win_count, '\nNews:\t', float(pos_after_win[1])/win_count, '\nBlog:\t', float(pos_after_win[2])/win_count, '\nTabloid:\t', float(pos_after_win[3])/win_count
	print 'Negative after win\nForum:\t', float(neg_after_win[0])/win_count, '\nNews:\t', float(neg_after_win[1])/win_count, '\nBlog:\t', float(neg_after_win[2])/win_count, '\nTabloid:\t', float(neg_after_win[3])/win_count
	print 'Positive after loss\nForum:\t', float(pos_after_loss[0])/loss_count, '\nNews:\t', float(pos_after_loss[1])/loss_count, '\nBlog:\t', float(pos_after_loss[2])/loss_count, '\nTabloid:\t', float(pos_after_loss[3])/loss_count
	print 'Negative after loss\nForum:\t', float(neg_after_loss[0])/loss_count, '\nNews:\t', float(neg_after_loss[1])/loss_count, '\nBlog:\t', float(neg_after_loss[2])/loss_count,  '\nTabloid:\t', float(neg_after_loss[3])/loss_count
	print 'Postive after tie\nForum:\t', float(pos_after_tie[0])/tie_count, '\nNews:\t', float(pos_after_tie[1])/tie_count, '\nBlog:\t', float(pos_after_tie[2])/tie_count,  '\nTabloid:\t', float(pos_after_tie[3])/tie_count
	print 'Negative after tie\nForum:\t', float(neg_after_tie[0])/tie_count, '\nNews:\t', float(neg_after_tie[1])/tie_count, '\nBlog:\t', float(neg_after_tie[2])/tie_count,  '\nTabloid:\t', float(neg_after_tie[3])/tie_count
	"""
	print float(pos_after_win[0])/win_count, '\n', float(pos_after_win[1])/win_count, '\n', float(pos_after_win[2])/win_count, '\n\n'
	print float(neg_after_win[0])/win_count, '\n', float(neg_after_win[1])/win_count, '\n', float(neg_after_win[2])/win_count, '\n\n'
	print float(pos_after_loss[0])/loss_count, '\n', float(pos_after_loss[1])/loss_count, '\n', float(pos_after_loss[2])/loss_count, '\n\n'
	print float(neg_after_loss[0])/loss_count, '\n', float(neg_after_loss[1])/loss_count, '\n', float(neg_after_loss[2])/loss_count, '\n'
	"""

if __name__ == '__main__':
	main()
