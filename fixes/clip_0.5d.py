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

