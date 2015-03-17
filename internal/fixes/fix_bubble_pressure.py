import os
import ast

for fn in os.listdir('.'):
	if not os.path.exists('fixed'):
		os.mkdir('fixed')
	f = open(fn, 'r')
	r = f.readlines()
	with open('./fixed/%s' % (fn), 'w') as outfile:
		for i in r:
			s = i.split()
			if s[27] == '-99.0':
				s[27] = str(0.32*ast.literal_eval(s[9]) + 4.3)
				s[28] = str(0.32*ast.literal_eval(s[10]) + 4.3)
				s[29] = str(0.32*ast.literal_eval(s[11]) + 4.3)
				j = ' '.join(s) + '\n'
				outfile.write(j)
			else:
				outfile.write(i)
