import numpy as np
import pandas as pd
import os
import ast

d = {-9999: 0.00}

def frac_convert(filename):
	line_li = []
	new_li = []
	
	df = pd.DataFrame()
	
	popfile = filename.split('.')[0]
	
	if 'frac' in os.listdir('.'):
		pass
	else:
		os.mkdir('./frac')
	
	f = open(filename, 'r')
	tempfile = open('./frac/%s.asc' % popfile, 'w')
	
	fwf = pd.read_table(filename, sep=' ', skiprows=6, header=None)
	
#	print fwf
	
	for i in range(len(fwf)):
		line_li.append(list(fwf.ix[i]))
	
	for j in line_li:
		templi = []
		for k in j:
			if k in d.keys():
				templi.append(d[k])
			else:
				templi.append(np.round(k, 2))
		new_li.append(templi)

#	print line_li
#	print new_li
	
	new_s = []
	
	for i in new_li:
		new_s.append(pd.Series(i))

#	print new_s
	
	df = df.append(new_s, ignore_index=True)

#	print df
	
	dfwrite = df.to_csv('dfwrite', sep=' ', header=False, index=False)
	dfread = open('dfwrite', 'r')
	
	head = f.readlines()[:5]
	
	xll = head[2].split()
	yll = head[3].split()
	xll[1] = str(np.round(ast.literal_eval(xll[1]), 3))
	yll[1] = str(np.round(ast.literal_eval(yll[1]), 3))
	
	head[2] = '     '.join(xll) + '\n'
	head[3] = '     '.join(yll)	+ '\n'
	
	for i in head:
		tempfile.write(i)
	
	tempfile.write('NODATA_value  0\n')
	
	for i in dfread.readlines():
		tempfile.write(i)
	
	f.close()
	tempfile.close()
	dfread.close()
	os.remove('./dfwrite')
	
###########################
#EXAMPLE
###########################

for fn in os.listdir('.'):
    frac_convert(fn)
