import os
import errno
import numpy as np
import pandas as pd
import ast

#def rout_scale(spath, wpath):
#		
#	for fn in os.listdir(spath):
#		if "fluxes" in fn:
#			o_lat = ast.literal_eval(fn.split('_')[1])
#			o_lon = ast.literal_eval(fn.split('_')[2])
#			q1 = [(o_lat + 0.03125), (o_lon - 0.03125)]
#			q2 = [(o_lat + 0.03125), (o_lon + 0.03125)]
#			q3 = [(o_lat - 0.03125), (o_lon - 0.03125)]
#			q4 = [(o_lat - 0.03125), (o_lon + 0.03125)]
#			q1str = "fluxes_" + str(q1[0]) + "_" + str(q1[1])
#			q2str = "fluxes_" + str(q2[0]) + "_" + str(q2[1])
#			q3str = "fluxes_" + str(q3[0]) + "_" + str(q3[1])
#			q4str = "fluxes_" + str(q4[0]) + "_" + str(q4[1])
#			os.symlink((spath + fn), '%s/%s' % (wpath, q1str))
#			os.symlink((spath + fn), '%s/%s' % (wpath, q2str))
#			os.symlink((spath + fn), '%s/%s' % (wpath, q3str))
#			os.symlink((spath + fn), '%s/%s' % (wpath, q4str))

def force_symlink(file1, file2):
    try:
        os.symlink(file1, file2)
    except OSError, e:
        if e.errno == errno.EEXIST:
            os.remove(file2)
            os.symlink(file1, file2)


def rout_scale(spath, wpath, o_res, dsf):
	d = []
	for fn in os.listdir(spath):
		if "fluxes" in fn:
			o_lat = ast.literal_eval(fn.split('_')[1])
			o_lon = ast.literal_eval(fn.split('_')[2])
			if dsf == 1:
				force_symlink((spath + fn), '%s/%s' % (wpath, fn))
			r = [x for x in range(dsf) if x%2 != 0]
			#d = []
			for i in r:
				q1 = [(o_lat + 0.5*i*(o_res/dsf)), (o_lon - 0.5*i*(o_res/dsf))]
				q2 = [(o_lat + 0.5*i*(o_res/dsf)), (o_lon + 0.5*i*(o_res/dsf))]
				q3 = [(o_lat - 0.5*i*(o_res/dsf)), (o_lon - 0.5*i*(o_res/dsf))]
				q4 = [(o_lat - 0.5*i*(o_res/dsf)), (o_lon + 0.5*i*(o_res/dsf))]
				d.append("fluxes_" + str(q1[0]) + "_" + str(q1[1]))
				d.append("fluxes_" + str(q2[0]) + "_" + str(q2[1]))
				d.append("fluxes_" + str(q3[0]) + "_" + str(q3[1]))
				d.append("fluxes_" + str(q4[0]) + "_" + str(q4[1]))
			for j in d:

				force_symlink((spath + fn), '%s/%s' % (wpath, j))


def call_rscale(scen, srcpath, wrpath, res, factor):
	srcpath = srcpath + '/' + scen + '/'
	for fn2 in os.listdir(wrpath):
		#print fn2
		if fn2 in os.listdir(srcpath):
			linkpath = srcpath + fn2 + '/'
			print linkpath
			xpath = wrpath + '/' + fn2 + '/sym/' + scen
			print xpath
			rout_scale(linkpath, xpath, res, factor)


#1/16 degree
for i in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:
	call_rscale(i,'/media/melchior/BALTHASAR/nsf_hydro/VIC/output/sub-basin', '/home/chesterlab/Bartos/VIC/input/rout/d16', 0.125, 2)

#1/8 degree
for i in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:
	call_rscale(i,'/media/melchior/BALTHASAR/nsf_hydro/VIC/output/sub-basin', '/home/chesterlab/Bartos/VIC/input/rout/d8', 0.125, 1)



'''
mkdir wauna
mv wauna1/* wauna
mv wauna2/* wauna
mv wauna3/* wauna
mv wauna4/* wauna
rmdir wauna1
rmdir wauna2
rmdir wauna3
rmdir wauna4
'''

'''
for fn in os.listdir('.'):
	for sc in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:  
		if not os.path.exists('%s/sym' % (fn)):
			os.mkdir('%s/sym' % (fn))
		if not os.path.exists('%s/sym/%s' % (fn, sc)):
			os.mkdir('%s/sym/%s' % (fn, sc)) 
'''


