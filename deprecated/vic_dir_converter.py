import numpy as np
import pandas as pd
import os

d = {1:3, 2:4, 4:5, 8:6, 16:7, 32:8, 64:1, 128:2, -9999:0, 0:0}

def dir_convert(filename):
	line_li = []
	new_li = []
	
	df = pd.DataFrame()
	
	popfile = filename.split('.')[0]
	
	if 'dir' in os.listdir('.'):
		pass
	else:
		os.mkdir('./dir')
	
	f = open(filename, 'r')
	tempfile = open('./dir/%s.asc' % popfile, 'w')
	
	fwf = pd.read_table(filename, sep=' ', skiprows=6, header=None)
	#del fwf[len(fwf.columns)-1]
	
	for i in range(len(fwf)):
		line_li.append(list(fwf.ix[i]))
	
	for j in line_li:
		templi = []
		for k in j:
			if k in d.keys():
				templi.append(d[k])
			else:
				continue
#				templi.append(k)
#				print 'warning', j, k
		new_li.append(templi)
	
	new_s = []
	
	for i in new_li:
		new_s.append(pd.Series(i))
		
	df = df.append(new_s, ignore_index=True)

	dfwrite = df.to_csv('dfwrite', sep=' ', header=False, index=False)
	dfread = open('dfwrite', 'r')
	
	head = f.readlines()[:5]
	
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
    dir_convert(fn)
