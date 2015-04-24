import os
import errno
import numpy as np
import pandas as pd
import ast


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
