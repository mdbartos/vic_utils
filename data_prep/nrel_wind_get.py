import subprocess as sub
import os
import pandas as pd
import numpy as np

df = pd.read_csv('~/Dropbox/Southwest Heat Vulnerability Team Share/ppdb_data/USGS_wind.csv')

idx = df['nrel_idx'].unique()

urlbase = 'http://wind.nrel.gov/Web_nrel/data/'
years = ['2004', '2005', '2006']

for y in years:
	for i in idx:
		cmd = "wget --random-wait -P ~/Downloads/nrel_wind/%s/ %s/%s/%s.csv" % (y, urlbase, y, i)
		sub.call(cmd, shell=True)
