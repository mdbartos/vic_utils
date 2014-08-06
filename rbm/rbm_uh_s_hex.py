import os
import ast
import shutil

def make_rbm_stn(dpath, wpath)

	basin = open(dpath, 'r')
	r = basin.readlines()
	h = r[:6]
	ncol = ast.literal_eval(h[0].split()[1])
	nrow = ast.literal_eval(h[1].split()[1])
	xll = ast.literal_eval(h[2].split()[1])
	yll = ast.literal_eval(h[3].split()[1])
	cellsize = ast.literal_eval(h[4].split()[1])
	nodata = ast.literal_eval(h[5].split()[1])
	
	xd = {}
	yd = {}
	
	ncol_array = range(ncol)
	nrow_array = range(nrow)
	
	for i in ncol_array:
		xd.update({(i+1) : (xll + cellsize/2 + i*cellsize)})
	
	for i in nrow_array:
		yd.update({(i+1) : (yll + cellsize/2 + i*cellsize)})
	
	lines = r[6:]
	
	li = []
	
	for i in range(len(lines)):
		sp = lines[i].split()
		for s in range(len(sp)):
			print len(sp)
			if sp[s] != '0':
				print str(nrow - i) + '_' + str(sp[s])
				li.append(tuple([s+1, nrow - i]))
	
	li = list(set(li))
	
	with open('all_stn', 'w') as outfile:
		for k in li:
			outfile.write('1 %s_%s             %s %s -9999\nNONE\n' % (hex(k[1]).split('x')[1], hex(k[0]).split('x')[1], k[0], k[1]))


##RENAME##

def rename_rbm_stn(uhpath, wrpath)
	for fn in os.listdir(uhpath):
		ff = fn.split('.')[0]
		fs = ff.split('_')
		shutil.copy('%s/%s' % (uhpath, fn), '%s/%s_%s.uh_s' % (wrpath, yd[int(fs[0], 16)], xd[int(fs[1], 16)]))
		os.remove('%s/%s' % (uhpath, fn))
