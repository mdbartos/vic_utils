import os
import numpy as np
import pandas as pd
import netCDF4
from datetime import date
import pysal as ps
import pickle


class makebasin():
	def __init__(self, basinpath, regionpath):

		self.region_df = {'arkred' : {}, 'cali' : {}, 'colo' : {}, 'gbas' : {}, 'mo' : {}, 'pnw' : {}, 'riog' : {}}
		self.region_dict = {'arkred' : [], 'cali' : [], 'colo' : [], 'gbas' : [], 'mo' : [], 'pnw' : [], 'riog' : []}
		self.latlon_d = pickle.load( open( basinpath, "rb"))
		self.r_latlon = pickle.load( open( regionpath, "rb"))
		self.latlon_b = {}
		self.r_latlon['arkred'] = self.r_latlon.pop('ark')
		self.r_latlon['colo'] = self.r_latlon.pop('color')
		self.r_latlon['pnw'] = self.r_latlon.pop('crb')
		self.r_latlon['riog'] = self.r_latlon.pop('rio')
		self.r_latlon['gbas'] = self.r_latlon.pop('grb')
		for i,v in self.latlon_d.items():
			s = pd.Series(v)
			self.latlon_b.update({i: s})
		
	def init_regdict(self):
		for fn in os.listdir('.'):
			for region in self.region_dict.keys():
				if region in fn[:6]:
					self.region_dict[region].append(fn)
					
					
	def check_basin(self, basin):
		chkb = {}
		for j, k in self.r_latlon.items():
			for i in self.latlon_b[basin]:
				if i in list(k):
					if j not in chkb:
						chkb.update({j : []})
					chkb[j].append(i)
	
		print '\n'
		print basin
		print len(chkb), 'entries'
		print set(chkb)
		print list(set(chkb))
		return list(set(chkb))
	
	def return_basin(self, basin, region):
		rt_b = []
		for i in self.latlon_b[basin]:
				if i in list(self.r_latlon[region]):
					rt_b.append(i)
		return rt_b
		
	def make_reg_single(self, basin, reg):
			
			nc = {}
				
			for fn in self.region_dict[reg]:
				f = netCDF4.Dataset(fn, 'r')
				v = ''
				
				if fn[-12:-8] == 'prcp':
					v = 'prcp'
				
				if fn[-12:-8] == 'tmax':
					v = 'tmax'
					
				if fn[-12:-8] == 'tmin':
					v = 'tmin'
					
				if fn[-12:-8] == 'wind':
					v = 'wind'
				
				yr = fn[-7:-3]
			
				pan = pd.Panel(f.variables[v][:], items=f.variables['time'][:], major_axis=f.variables['lat'], minor_axis=f.variables['lon'][:])
								
				for i in self.return_basin(basin, reg):
					if i[0] in pan.major_axis:
						if i[1] in pan.minor_axis:
							if i not in nc:
								nc.update({i : {'prcp': {}, 'tmax': {}, 'tmin': {}, 'wind': {}}})
							nc[i][v].update({yr:{}})
							s = pan.ix[:, i[0], i[1]]
							nc[i][v][yr] = s			
			
			self.region_df[reg] = nc
	
	
	def write_files(self, basin, reg):

		for i, v in self.region_df[reg].items():
			c_prcp = pd.concat(self.region_df[reg][i]['prcp'].values()).sort_index()
			c_tmax = pd.concat(self.region_df[reg][i]['tmax'].values()).sort_index()
			c_tmin = pd.concat(self.region_df[reg][i]['tmin'].values()).sort_index()
			c_wind = pd.concat(self.region_df[reg][i]['wind'].values()).sort_index()
		
			self.latlon_df = pd.concat([c_prcp, c_tmax, c_tmin, c_wind], axis=1)
			self.latlon_df.columns = ['prcp', 'tmax', 'tmin', 'wind']
			self.latlon_df['date'] = [date.fromordinal(int(711858 + j)) for j in self.latlon_df.index]
			self.latlon_df['mo'] = [j.month for j in self.latlon_df.date]
			self.latlon_df['day'] = [j.day for j in self.latlon_df.date]
			self.latlon_df['year'] = [j.year for j in self.latlon_df.date]
	
			self.latlon_df['prcp_r'] = np.round(self.latlon_df['prcp'], 2)
			self.latlon_df['tmax'] = np.round(self.latlon_df['tmax'], 2)
			self.latlon_df['tmin'] = np.round(self.latlon_df['tmin'], 2)
			self.latlon_df['wind'] = np.round(self.latlon_df['wind'], 2)
			
			self.latlon_df = self.latlon_df[['prcp_r', 'tmax', 'tmin', 'wind']]				
			
			if not os.path.exists(basin):
				os.mkdir(basin)
			else:
				pass
			self.latlon_df.to_csv('./%s/data_%s_%s' % (basin, i[0], i[1]), sep=" ", header=False, index=False)
			
	def basin_all(self, li):
		
		self.init_regdict()
		for i in li:
			r = self.check_basin(i)
			for j in r:
				self.region_df = {'arkred' : [], 'cali' : [], 'colo' : [], 'gbas' : [], 'mo' : [], 'pnw' : [], 'riog' : []}
				self.make_reg_single(i, j)
				self.write_files(i, j)
