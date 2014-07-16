import os
import numpy as np
import pandas as pd
import netCDF4
from datetime import date
import pysal as ps
import pickle

dirlist = {}

for fn in os.listdir('.'):
	if fn.endswith('.csv'):
		fs = fn.split('.')[0]
		dirlist.update({fs: fn})
	
latlon_c = {}

for key, val in dirlist.items():
	db = pd.read_csv(val)
	dbpass = {c: db[c] for c in ['PNAME', 'PCODE', 'LAT', 'LONG']}
	dbdf = pd.DataFrame(dbpass)
	dbdf = dbdf.drop_duplicates(cols='PCODE')
	dbdf['LAT_R'] = [round(j, 4) for j in dbdf.LAT]
	dbdf['LONG_R'] = [round(j, 4) for j in dbdf.LONG]
	dbdf['latlon'] = zip(dbdf.LAT_R, dbdf.LONG_R)
	latlon_c.update({key : pd.concat([dbdf['PNAME'], dbdf['PCODE'], dbdf['latlon']], axis=1)})
	
for i, v in latlon_c.items():
	v['slug'] = [str(j) for j in v['PNAME']]
	v['slug'] = [k.split(' ')[0] for k in v['slug']]
	v['slug'] = [k[:5] for k in v['slug']]
	vd = v.ix[v.duplicated(cols='slug')]
	da = []
	for o, x in vd['slug'].iteritems():
		da.append(x)
		n = da.count(x)
		if len(x) < 5:	
			latlon_c[i]['slug'][o] = x + str(n)
		elif (len(x) >= 5):
			latlon_c[i]['slug'][o] = x[:4] + str(n)
			


lees_f = {'PNAME' : ['Glen Canyon Dam'], 'PCODE' : [153], 'latlon' : ['(36.9161, -111.4599)'], 'slug' : ['lees_']} 
lees_f = pd.DataFrame(lees_f)
latlon_c.update({'lees_f' : lees_f})

hoover = {'PNAME' : ['Hoover Dam'], 'PCODE' : [154], 'latlon' : ['(35.9192, -114.8178)'], 'slug' : ['hoove']} 
hoover = pd.DataFrame(hoover)
latlon_c.update({'hoover' : hoover})

davis = {'PNAME' : ['Davis Dam'], 'PCODE' : [152], 'latlon' : ['(35.0075, -114.5991)'], 'slug' : ['davis']} 
davis = pd.DataFrame(davis)
latlon_c.update({'davis' : davis})

parker = {'PNAME' : ['Parker Dam'], 'PCODE' : [447], 'latlon' : ['(34.2622, -114.1661)'], 'slug' : ['parke']} 
parker = pd.DataFrame(parker)
latlon_c.update({'parker' : parker})

billw = {'PNAME' : ['Bill Williams'], 'PCODE' : [-9999], 'latlon' : ['(1.0, 1.0)'], 'slug' : ['billw']} 
billw = pd.DataFrame(billw)
latlon_c.update({'billw' : billw})

gc = {'PNAME' : ['Grand Canyon'], 'PCODE' : [-9999], 'latlon' : ['(1.0, 1.0)'], 'slug' : ['gc']} 
gc = pd.DataFrame(gc)
latlon_c.update({'gc' : gc})

little_col = {'PNAME' : ['Little Colorado'], 'PCODE' : [-9999], 'latlon' : ['(1.0, 1.0)'], 'slug' : ['littl']} 
little_col = pd.DataFrame(little_col)
latlon_c.update({'little_col' : little_col})

paria = {'PNAME' : ['Paria River'], 'PCODE' : [-9999], 'latlon' : ['(1.0, 1.0)'], 'slug' : ['paria']} 
paria = pd.DataFrame(paria)
latlon_c.update({'paria' : paria})

virgin = {'PNAME' : ['Virgin River'], 'PCODE' : [-9999], 'latlon' : ['(1.0, 1.0)'], 'slug' : ['virgi']} 
virgin = pd.DataFrame(virgin)
latlon_c.update({'virgin' : virgin})

imperial = {'PNAME' : ['Imperial Dam'], 'PCODE' : [-9999], 'latlon' : ['(1.0, 1.0)'], 'slug' : ['imper']} 
imperial = pd.DataFrame(imperial)
latlon_c.update({'imperial' : imperial})


pickle.dump( latlon_c, open('hydrostn.p', 'wb'))
