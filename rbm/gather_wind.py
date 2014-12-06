import numpy as np
import pandas as pd
import os
import datetime
import pickle

#windpath = '/home/tabris/Dropbox/Southwest Heat Vulnerability Team Share/ppdb_data/USGS_wind.csv'

#nrel_path = '/home/tabris/Downloads/nrel_wind'

class gather_wind():
	def __init__(self, windpath='/home/tabris/Dropbox/Southwest Heat Vulnerability Team Share/ppdb_data/USGS_wind.csv', nrel_path = '/home/tabris/Downloads/nrel_wind'):
		self.windpath = windpath
		self.nrel_path = nrel_path
		self.df = pd.read_csv(self.windpath)
		self.gmw = self.df.groupby(['nrel_idx', 'mpower_coeff', 'rated_wspd', 'tower_h', 'rotor_s_a']).sum()['MW_turbine']
		self.gll = self.df.groupby(['nrel_idx', 'mpower_coeff', 'rated_wspd', 'tower_h', 'rotor_s_a']).last()[['lat_grid', 'lon_grid']]

		self.g = pd.concat([self.gmw, self.gll], axis=1)

		s = pd.Series()

		self.g['nrel_str'] = ''

		for i in range(len(self.g.index)):
			
			idx = self.g.index[i][0]
			if idx in s.values:
				num = len(s.loc[s == idx])
				self.g.iloc[i, 3] = str(idx) + '.' + str(num)
				s.loc[i] = idx

			else:
				self.g.iloc[i, 3] = str(idx)
				s.loc[i] = idx

		self.key_coords = self.g.set_index('nrel_str')[['lat_grid', 'lon_grid']]	
		
		self.basin_masks = pd.read_pickle('/home/chesterlab/Bartos/pre/source_proj_forcings/basin_masks.p') 

			###GET SOLAR COORDS IN EACH BASIN

		coord_li = list(set(['%s_%s' % (self.key_coords.loc[i, 'lat_grid'], self.key_coords.loc[i, 'lon_grid']) for i in self.key_coords.index]))

		self.reg_d = {}

		for j in self.basin_masks.keys():
			self.reg_d.update({j : []})

		for i in coord_li:
			for j in self.basin_masks.keys():
				if i in self.basin_masks[j]['coords']:
					self.reg_d[j].append(i)

	def key_wind(self):
		
		self.reg_pcodes = {}

		wnkey = self.key_coords
		wnkey['ll_str'] = wnkey['lat_grid'].astype(str) + '_' + wnkey['lon_grid'].astype(str)
		wnkey['basin'] = ''

		for k in self.reg_d.keys():

			wnkey['basin'].loc[wnkey['ll_str'].isin(self.reg_d[k])] = k
		
		for k in self.reg_d.keys():
			ll_li = list(wnkey.loc[wnkey['basin'] == k].index)
			self.reg_pcodes.update({k : ll_li})

	def cat_wind_files(self, inpath='/home/chesterlab/Bartos/post/wn', cap='cap_mw'):

		self.df_d = {}
		
		for i in self.reg_pcodes.keys():
			basin_d = {}

			for scen in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:
				
				if scen == 'hist':
					scen_df = pd.DataFrame(index=pd.date_range(start=datetime.date(1949,1,1), end=datetime.date(2010,12,31), freq='H'))
				else:
					scen_df = pd.DataFrame(index=pd.date_range(start=datetime.date(2040,1,1), end=datetime.date(2060,1,1), freq='H'))
				
				scen_df['CAP_MW'] = 0.0

				for j in self.reg_pcodes[i]:
					try:
						df = pd.read_csv('%s/%s_%s' % (inpath, scen, j), sep='\t')
						mkdatetime =  lambda x: datetime.datetime(int(x['year']), int(x['month']), int(x['day']), int(x['hour']))
						df['date'] = df.apply(mkdatetime, axis=1) 
						df = df.set_index('date')
					
						scen_df['CAP_MW'] = scen_df['CAP_MW'] + df[cap]
					except:
						print 'missing %s' % (j)
					
				basin_d.update({scen : scen_df})

			self.df_d.update({i : basin_d})

		pickle.dump(self.df_d, open('wn_region.p', 'wb'))
