import os

def convert_cols():
	for fn in os.listdir('.'):
		f = open(fn, 'r')
		r = f.readlines()
		f = open(fn, 'w')
		for i in r:
			s = i.split()[3:7]
			j = ' '.join(s)
			n = j + '\n'
			f.write(n)
		f.close()
