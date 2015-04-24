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
			
