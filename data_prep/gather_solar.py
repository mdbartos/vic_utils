import os
import numpy as np
import pandas as pd
import datetime

class gather_solar():
	def __init__(self, eiapath='~/EIA_form_data/eia_form_860/eia8602012'):
		gen = pd.read_excel('%s/GeneratorY2012.xlsx' % (eiapath), skiprows=1)
		plant = pd.read_excel('%s/PlantY2012.xlsx' % (eiapath), skiprows=1)

		pcodes = gen.loc[gen['Prime Mover'].isin(['PV', 'CP'])]['Plant Code'].unique()

		solar_plants = plant.set_index('Plant Code').loc[pcodes]
		wecc_solar_plants = solar_plants.loc[solar_plants['NERC Region'] == 'WECC']

		wecc_solar_ll = zip(wecc_solar_plants['Latitude'], wecc_solar_plants['Longitude'])

		wecc_solar_pcodes = wecc_solar_plants.index

		solar_gen = gen.loc[gen['Prime Mover'].isin(['PV', 'CP'])].groupby('Plant Code').sum()['Nameplate Capacity (MW)'].loc[wecc_solar_pcodes]

		self.solar = pd.concat([solar_gen, solar_plants['Latitude'], solar_plants['Longitude']], axis=1, join='inner')

		westbound = int(self.solar['Longitude'].min()) - 1
		eastbound = int(self.solar['Longitude'].max()) + 1
		northbound = int(self.solar['Latitude'].max()) + 1
		southbound = int(self.solar['Latitude'].min()) - 1

		lats = pd.Series(np.arange(southbound, northbound, 0.0625)[1:][::2])
		longs = pd.Series(np.arange(westbound, eastbound, 0.0625)[1:][::2])

		self.solar['lat_grid'] = 0.0
		self.solar['lon_grid'] = 0.0

		for i in self.solar.index:
			sitelat = self.solar.loc[i, 'Latitude']
			sitelon = self.solar.loc[i, 'Longitude']
			lat_grid = lats.loc[abs((lats - sitelat)).idxmin()]
			lon_grid = longs.loc[abs((longs - sitelon)).idxmin()]
			self.solar.loc[i, 'lat_grid'] = lat_grid
			self.solar.loc[i, 'lon_grid'] = lon_grid

		##########SUNY GRID FOR SOLAR RADIATION

		lats_suny = pd.Series(np.arange(southbound, northbound, 0.05)[1:][::2])
		longs_suny = pd.Series(np.arange(westbound, eastbound, 0.05)[1:][::2])

		self.solar['lat_suny'] = 0.0
		self.solar['lon_suny'] = 0.0

		for i in self.solar.index:
			sitelat = self.solar.loc[i, 'Latitude']
			sitelon = self.solar.loc[i, 'Longitude']
			lat_grid = lats_suny.loc[abs((lats_suny - sitelat)).idxmin()]
			lon_grid = longs_suny.loc[abs((longs_suny - sitelon)).idxmin()]
			self.solar.loc[i, 'lat_suny'] = lat_grid
			self.solar.loc[i, 'lon_suny'] = lon_grid

		#########################################

		self.basin_masks = pd.read_pickle('~/pre/source_proj_forcings/basin_masks.p') 

		###GET SOLAR COORDS IN EACH BASIN

		coord_li = list(set(['%s_%s' % (self.solar.loc[i, 'lat_grid'], self.solar.loc[i, 'lon_grid']) for i in self.solar.index]))

		self.reg_d = {}

		for j in self.basin_masks.keys():
			self.reg_d.update({j : []})

		for i in coord_li:
			for j in self.basin_masks.keys():
				if i in self.basin_masks[j]['coords']:
					self.reg_d[j].append(i)

	def key_solar(self):
		
		self.reg_pcodes = {}

		solkey = self.solar
		solkey['ll_str'] = solkey['lat_grid'].astype(str) + '_' + solkey['lon_grid'].astype(str)
		solkey['basin'] = ''

		for k in self.reg_d.keys():

			solkey['basin'].loc[solkey['ll_str'].isin(self.reg_d[k])] = k
		
		for k in self.reg_d.keys():
			ll_li = list(solkey.loc[solkey['basin'] == k].index)
			self.reg_pcodes.update({k : ll_li})

	def cat_solar_files(self, inpath='/home/chesterlab/Bartos/post/pv'):

		self.df_d = {}
		
		for i in self.reg_pcodes.keys():
			basin_d = {}

			for scen in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:
				
				if scen == 'hist':
					scen_df = pd.DataFrame(index=pd.date_range(start=datetime.date(1949,1,1), end=datetime.date(2010,12,31)))
				else:
					scen_df = pd.DataFrame(index=pd.date_range(start=datetime.date(2010,1,1), end=datetime.date(2099,12,31)))
				
				scen_df['CAP_MW'] = 0.0

				for j in self.reg_pcodes[i]:

					df = pd.read_csv('%s/%s.%s' % (inpath, scen, j), sep='\t')
					mkdate =  lambda x: datetime.date(int(x['year']), int(x['month']), int(x['day']))
					df['date'] = df.apply(mkdate, axis=1) 
					df = df.set_index('date')
					
					scen_df['CAP_MW'] = scen_df['CAP_MW'] + df['CAP_MW']

				basin_d.update({scen : scen_df})

			self.df_d.update({i : basin_d})
