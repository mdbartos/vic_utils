import os
import numpy as np
import pandas as pd
import ast

def rout_scale(spath, wpath)
		
	for fn in os.listdir(spath):
		if "fluxes" in fn:
			o_lat = ast.literal_eval(fn.split('_')[1])
			o_lon = ast.literal_eval(fn.split('_')[2])
			q1 = [(o_lat + 0.03125), (o_lon - 0.03125)]
			q2 = [(o_lat + 0.03125), (o_lon + 0.03125)]
			q3 = [(o_lat - 0.03125), (o_lon - 0.03125)]
			q4 = [(o_lat - 0.03125), (o_lon + 0.03125)]
			q1str = "fluxes_" + str(q1[0]) + "_" + str(q1[1])
			q2str = "fluxes_" + str(q2[0]) + "_" + str(q2[1])
			q3str = "fluxes_" + str(q3[0]) + "_" + str(q3[1])
			q4str = "fluxes_" + str(q4[0]) + "_" + str(q4[1])
			os.symlink((spath + fn), '%s/%s' % (wpath, q1str))
			os.symlink((spath + fn), '%s/%s' % (wpath, q2str))
			os.symlink((spath + fn), '%s/%s' % (wpath, q3str))
			os.symlink((spath + fn), '%s/%s' % (wpath, q4str))


def call_rscale(scen, srcpath, wrpath):
	srcpath = srcpath + '/' + scen + '/'
	for fn in os.listdir(wrpath):
		#print fn
		if fn in os.listdir(srcpath):
			linkpath = srcpath + fn + '/'
			print linkpath
			xpath = wrpath + '/' + fn + '/sym/' + scen
			print xpath

			rout_scale(linkpath, xpath)

call_rscale('hist','/media/melchior/BALTHASAR/nsf_hydro/VIC/output/sub-basin', '/home/chesterlab/Bartos/VIC/input/rout/d16')

