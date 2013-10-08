import sys
from pprint import pprint

# Compute the probability of a win

def main():
	win_count = 0
	loss_count = 0
	tie_count = 0
	high_win = 0
	above_baseline_game = 0
	best_baseline = 0
	high_prob = 0
	data_source = sys.argv[1]
	#baseline = float(sys.argv[2])
	nfl_input = ['chiefs.txt', 'cowboys.txt', 'eagles.txt', 'giants.txt', 'packers.txt', 'ravens.txt']
	epl_input = ['chelsea.txt', 'manutd.txt', 'qpr.txt', 'sunderland.txt', 'tottenham.txt', 'westham.txt']

	for baseline in range (-100, 200, 5):
		baseline = baseline/1000.0

		team = 'ravens.txt'
		info = {}
		team_file = open('input/' + team)
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

		week = 1
		stop = None
		while stop is None:
			loss = info[str(week)]['loss']
			forum_score = info[str(week)][data_source]
			if forum_score > baseline:
				above_baseline_game += 1
				if loss == 0:
					high_win += 1
			week += 1
			if str(week) not in info:
				stop = True

		for team in epl_input:
			info = {}
			team_file = open('input/' + team)
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
			week = 1
			stop = None
			while stop is None:
				won_game = info[str(week)]['win']
				forum_score = info[str(week)][data_source]
				if forum_score > baseline:
					# if score beats our baseline
					above_baseline_game += 1
					if won_game == 1:
						# win above baseline score
						high_win += 1
				week += 1
				if week not in info:
					stop = True

		# print results
		print baseline, ',', float(high_win)/above_baseline_game


	"""
	print "Win count:", win_count
	print "Above baseline games:" , above_baseline_game
	print "High win:", high_win
	print "Probability of a win with sentiment above", baseline, '--->', float(high_win)/above_baseline_game
"""

if __name__ == '__main__':
	main()