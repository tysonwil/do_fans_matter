import sys

# How often a team wins/looses after an increase/decrease of sentiment

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
	win_after_pos = [0, 0, 0]
	loss_after_pos = [0, 0, 0]
	win_after_neg = [0, 0, 0]
	loss_after_neg = [0, 0, 0]

	for k in info:
		if k == 'END': k = len(info)
		sorted_weeks.append(int(k))
	sorted_weeks.sort()
	if info['1']['loss'] == 1: loss_count -= 1
	else: win_count -= 1

	for week in range(2, len(sorted_weeks)):
		wk = str(week)
		prev_wk = str(week-1)
		loss = info[wk]['loss']
		forum = (info[prev_wk]['forum'], info[wk]['forum'])
		news = (info[prev_wk]['news'], info[wk]['news'])
		blog = (info[prev_wk]['blog'], info[wk]['blog'])
		if loss == 1:
			if forum[0] < forum[1]: loss_after_pos[0] += 1
			else: loss_after_neg[0] += 1
			if news[0] < news[1]: loss_after_pos[1] += 1
			else: loss_after_neg[1] += 1
			if blog[0] < blog[1]: loss_after_pos[2] += 1
			else: loss_after_neg[2] += 1
		else:
			if forum[0] < forum[1]: win_after_pos[0] += 1
			else: win_after_neg[0] += 1
			if news[0] < news[1]: win_after_pos[1] += 1
			else: win_after_neg[1] += 1
			if blog[0] < blog[1]: win_after_pos[2] += 1
			else: win_after_neg[2] += 1

	# print results
	print 'Win after positive\nForum:\t', float(win_after_pos[0])/win_count, '\nNews:\t', float(win_after_pos[1])/win_count, '\nBlog:\t', float(win_after_pos[2])/win_count, '\n'
	print 'Win after negative\nForum:\t', float(win_after_neg[0])/win_count, '\nNews:\t', float(win_after_neg[1])/win_count, '\nBlog:\t', float(win_after_neg[2])/win_count, '\n'
	print 'Loss after positive\nForum:\t', float(loss_after_pos[0])/loss_count, '\nNews:\t', float(loss_after_pos[1])/loss_count, '\nBlog:\t', float(loss_after_pos[2])/loss_count, '\n'
	print 'Loss after negative\nForum:\t', float(loss_after_neg[0])/loss_count, '\nNews:\t', float(loss_after_neg[1])/loss_count, '\nBlog:\t', float(loss_after_neg[2])/loss_count, '\n'

if __name__ == '__main__':
	main()

