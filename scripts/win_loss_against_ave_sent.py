import sys

# How often a team wins/looses againt their average seasonal sentiment

def main():
	win_count = 0
	loss_count = 0
	team_file = open(sys.argv[1])
	info = {}
	

	sum_forum = 0
	sum_news = 0
	sum_blog = 0
	nb_games = 0
	#LOAD IN INFO DICT THE SENTIMENTS AND LOSS INFO
	for line in team_file:
		columns = line.split(",")
		nb_games += 1
		if columns[0] != '' :
			info[columns[0]] = dict(forum = float(columns[1]) , news = float(columns[2]), blog = float(columns[3]))
			sum_forum += float(columns[1])
			sum_blog += float(columns[3])
			sum_news += float(columns[2])

			if columns[4].strip() == '0':
				info[columns[0]]['loss'] = 0
				win_count += 1
			elif columns[4].strip() == '-1':
				info[columns[0]]['loss'] = -1
			else:
				info[columns[0]]['loss'] = 1
				loss_count += 1

	#AVERAGES
	av_forum = sum_forum / nb_games
	av_news = sum_news / nb_games
	av_blog = sum_blog / nb_games

	print 'Averages\nForum:\t', av_forum, '\nNews:\t', av_news, '\nBlog:\t', av_blog, '\n'

	sorted_weeks = []
	win_after_pos = [0, 0, 0]
	loss_after_pos = [0, 0, 0]
	win_after_neg = [0, 0, 0]
	loss_after_neg = [0, 0, 0]

	for k in info:
		if k == 'END': k = len(info)
		sorted_weeks.append(int(k))
	sorted_weeks.sort()

	for week in range(1, len(sorted_weeks)):
		wk = str(week)
		loss = info[wk]['loss']
		forum = info[wk]['forum']
		news = info[wk]['news']
		blog = info[wk]['blog']
		if loss == 1:
			if av_forum < forum: loss_after_pos[0] += 1
			else: loss_after_neg[0] += 1
			if av_news < news: loss_after_pos[1] += 1
			else: loss_after_neg[1] += 1
			if av_blog < blog: loss_after_pos[2] += 1
			else: loss_after_neg[2] += 1
		else:
			if av_forum < forum: win_after_pos[0] += 1
			else: win_after_neg[0] += 1
			if av_news < news: win_after_pos[1] += 1
			else: win_after_neg[1] += 1
			if av_blog < blog: win_after_pos[2] += 1
			else: win_after_neg[2] += 1

	# print results
	print 'Win after above average sentiment\nForum:\t', float(win_after_pos[0])/win_count, '\nNews:\t', float(win_after_pos[1])/win_count, '\nBlog:\t', float(win_after_pos[2])/win_count, '\n'
	print 'Win after below average sentiment\nForum:\t', float(win_after_neg[0])/win_count, '\nNews:\t', float(win_after_neg[1])/win_count, '\nBlog:\t', float(win_after_neg[2])/win_count, '\n'
	print 'Loss after above average sentiment\nForum:\t', float(loss_after_pos[0])/loss_count, '\nNews:\t', float(loss_after_pos[1])/loss_count, '\nBlog:\t', float(loss_after_pos[2])/loss_count, '\n'
	print 'Loss after below average sentiment\nForum:\t', float(loss_after_neg[0])/loss_count, '\nNews:\t', float(loss_after_neg[1])/loss_count, '\nBlog:\t', float(loss_after_neg[2])/loss_count, '\n'

if __name__ == '__main__':
	main()

