import os
import pandas as pd
import numpy as np

def round_multiple(self, rnum, rprec, rbase):
    return round(rbase * round(float(rnum)/rbase), rprec)

li = []

def import_tables(c):
				
    	    df = pd.read_table(c, sep=' ', skiprows=6, header=None)
    	    df = df.dropna(axis=1)
			
    	    df_o = open(c, 'r')	
    	    dfhead = df_o.readlines()[:6]
	    df_o.close()
				
	    ncol = int(dfhead[0].split()[1])
	    nrow = int(dfhead[1].split()[1])
	    xll = float(dfhead[2].split()[1])
	    yll = float(dfhead[3].split()[1])
	    cellsize = float(dfhead[4].split()[1])
	    cellprec = len(dfhead[4].split()[1].split('.')[1])
	    nodata = dfhead[5].split()[1]
            if xll % cellsize != 0.0:
	    	xll = round_multiple(xll, cellprec, cellsize)
	    if yll % cellsize != 0.0:
	    	yll = round_multiple(yll, cellprec, cellsize)	
	
	    df_col = [(xll + cellsize/2 + cellsize*i) for i in range(len(df.columns))]
	    df['idx'] = [(yll + cellsize/2 + cellsize*i) for i in range(len(df.index))][::-1]
	    df = df.set_index('idx')
	    df.columns = df_col

            df.replace(-9999, np.nan, inplace=True)
            df.dropna(axis=1, how='all', inplace=True)
            df.dropna(axis=0, how='all', inplace=True)

            print df
            li.append(df)

import_tables('canada_asc.txt')

df = li[0]
ll = []

for col in df.columns:
    for idx in df.index:
        if df.loc[idx, col] == 5129:
            ll.append('data_%s_%s' % (idx, col))

pd.DataFrame(ll).to_csv('canada_ll.csv')

#################################

c = pd.read_csv('canada_ll.csv', index_col=0)
c = c['0'].values

dirli = ['/media/melchior/BALTHASAR/nsf_hydro/VIC/input/vic/forcing/hist/sub-basin/wauna1','/media/melchior/BALTHASAR/nsf_hydro/VIC/input/vic/forcing/hist/sub-basin/wauna2','/media/melchior/BALTHASAR/nsf_hydro/VIC/input/vic/forcing/hist/sub-basin/wauna3','/media/melchior/BALTHASAR/nsf_hydro/VIC/input/vic/forcing/hist/sub-basin/wauna4']

fileli = []

for i in dirli:
	fileli.extend(os.listdir(i))

canada_new = [i for i in c if not i in fileli]

lats = sorted(set([float(i.split('_')[1]) for i in canada_new]))
lons = sorted(set([float(i.split('_')[2]) for i in canada_new])) 

df = pd.DataFrame(index = lats, columns=lons)

for i in canada_new:
	clat = float(i.split('_')[1])
	clon = float(i.split('_')[2])
	df.loc[clat, clon] = 1

li_05 = []

for fn in os.listdir('/home/melchior/Documents/maurer_0.5d/maurer_0.5d_hist_ascii/canada'):
	dlat0 = float(fn.split('_')[1])-0.25
	dlat1 = float(fn.split('_')[1])+0.25
	dlon0 = float(fn.split('_')[2])-0.25
	dlon1 = float(fn.split('_')[2])+0.25

	mat = df.loc[(df.index >= dlat0) & (df.index <= dlat1), (df.columns >= dlon0) & (df.columns <= dlon1)].values
	if 1 in mat:
		li_05.append(fn)

os.chdir('/home/melchior/Documents/maurer_0.5d/maurer_0.5d_hist_ascii/canada')

os.mkdir('canada')

import shutil

for i in li_05:
	shutil.copy(i, './canada')
