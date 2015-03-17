import os
import numpy as np
import pandas as pd
import netCDF4
from datetime import date
import pysal as ps
import pickle

class prep_stn_d():

	def __init__(self):

		self.dirlist = {}
		self.latlon_c = {}

	def init_dirlist(self, rpath):
		for fn in os.listdir(rpath):
			if fn.endswith('csv') or fn.endswith('txt'):
				fs = fn.split('.')[0]
				fs = '_'.join(fs.split('_')[:-1])
				self.dirlist.update({fs: fn})

	def mk_stn_d(self, **kwargs):
		for key, val in self.dirlist.items():
			db = pd.read_csv(val, **kwargs)
			dbpass = {c: db[c] for c in ['PNAME', 'PCODE', 'LAT', 'LONG']}
			dbdf = pd.DataFrame(dbpass)
			dbdf = dbdf.drop_duplicates(subset=['PCODE'])
			#dbdf['LAT_R'] = [round(j, 4) for j in dbdf.LAT]
			#dbdf['LONG_R'] = [round(j, 4) for j in dbdf.LONG]
			dbdf['latlon'] = zip(dbdf.LAT, dbdf.LONG)
			self.latlon_c.update({key : pd.concat([dbdf['PNAME'], dbdf['PCODE'], dbdf['latlon']], axis=1)})
	
	def fix_stnames(self):		
		for i, v in self.latlon_c.items():
			v['slug'] = [str(j).split(' ')[0][:5] for j in v['PNAME']]
			da = []
			for o, x in v.ix[v.duplicated(subset=['slug'])]['slug'].iteritems():
				#print x
				da.append(x)
				n = da.count(x)
				if len(x) < 5:
					print x
					self.latlon_c[i].ix[o, 'slug'] = x + str(n)
				elif (len(x) >= 5):
					print x
					self.latlon_c[i].ix[o, 'slug'] = x[:4] + str(n)
				#print self.latlon_c[i]['slug'][o] 
			

b = prep_stn_d()
b.init_dirlist('/home/melchior/Desktop/sb_export/hy')
b.mk_stn_d(header=None, names=['FID', 'PCODE', 'PNAME', 'LAT', 'LONG'], sep='\t')
b.fix_stnames()
b.fix_stnames()
#wtf??^^

#lees_f = {'PNAME' : ['Glen Canyon Dam'], 'PCODE' : [153], 'latlon' : ['(36.9161, -111.4599)'], 'slug' : ['lees_']} 
#lees_f = pd.DataFrame(lees_f)
#latlon_c.update({'lees_f' : lees_f})

#hoover = {'PNAME' : ['Hoover Dam'], 'PCODE' : [154], 'latlon' : ['(35.9192, -114.8178)'], 'slug' : ['hoove']} 
#hoover = pd.DataFrame(hoover)
#latlon_c.update({'hoover' : hoover})
#
#davis = {'PNAME' : ['Davis Dam'], 'PCODE' : [152], 'latlon' : ['(35.0075, -114.5991)'], 'slug' : ['davis']} 
#davis = pd.DataFrame(davis)
#latlon_c.update({'davis' : davis})

#parker = {'PNAME' : ['Parker Dam'], 'PCODE' : [447], 'latlon' : ['(34.2622, -114.1661)'], 'slug' : ['parke']} 
#parker = pd.DataFrame(parker)
#latlon_c.update({'parker' : parker})

billw = {'PNAME' : ['Bill Williams'], 'PCODE' : [-9999], 'latlon' : [(34.209146, -113.608841)], 'slug' : ['billw']} 
billw = pd.DataFrame(billw)
b.latlon_c.update({'billw' : billw})

gc = {'PNAME' : ['Grand Canyon'], 'PCODE' : [-9999], 'latlon' : [(36.118750, -112.084781)], 'slug' : ['gc']} 
gc = pd.DataFrame(gc)
b.latlon_c.update({'gc' : gc})

little_col = {'PNAME' : ['Little Colorado'], 'PCODE' : [-9999], 'latlon' : [(35.916685, -111.580886)], 'slug' : ['littl']} 
little_col = pd.DataFrame(little_col)
b.latlon_c.update({'little_col' : little_col})

paria = {'PNAME' : ['Paria River'], 'PCODE' : [-9999], 'latlon' : [(36.873747, -111.595799)], 'slug' : ['paria']} 
paria = pd.DataFrame(paria)
b.latlon_c.update({'paria' : paria})

virgin = {'PNAME' : ['Virgin River'], 'PCODE' : [-9999], 'latlon' : [(36.893115, -113.924861)], 'slug' : ['virgi']} 
virgin = pd.DataFrame(virgin)
b.latlon_c.update({'virgin' : virgin})

imperial = {'PNAME' : ['Imperial Dam'], 'PCODE' : [-9999], 'latlon' : [(32.892721, -114.466957)], 'slug' : ['imper']} 
imperial = pd.DataFrame(imperial)
b.latlon_c.update({'imperial' : imperial})


pickle.dump( b.latlon_c, open('hydrostn.p', 'wb'))
