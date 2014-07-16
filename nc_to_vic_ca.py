import os
import numpy as np
import pandas as pd
import netCDF4
from datetime import date
import pysal as ps
import pickle

###########################################
#
#dirlist = {
#'castaic': '/GIS/CA_contrib_area/intersect/castaic_int.dbf',
#'corona': '/GIS/CA_contrib_area/intersect/corona_int.dbf',
#'cottonwood': '/GIS/CA_contrib_area/intersect/cottonwood_int.dbf',
#'coyotecr': '/GIS/CA_contrib_area/intersect/coyotecr_int.dbf',
#'kern': '/GIS/CA_contrib_area/intersect/kern_int.dbf',
#'pitt': '/GIS/CA_contrib_area/intersect/pitt_int.dbf',
#'redmtn': '/GIS/CA_contrib_area/intersect/redmtn_int.dbf',
#'riohondo': '/GIS/CA_contrib_area/intersect/riohondo_int.dbf',
#'rushcr': '/GIS/CA_contrib_area/intersect/rushcr_int.dbf',
#'tulare': '/GIS/CA_contrib_area/intersect/tulare_int.dbf',
#'gila_imp': '/GIS/gila_imp/intersect/gila_imp_int.dbf',
#}
#
#latlon_d = {}
#
#for key, val in dirlist.items():
#	db = ps.open(val)
#	dbpass = {col: db.by_col(col) for col in ['calc_lat', 'calc_lon']}
#	dbdf = pd.DataFrame(dbpass)
#	dbdf['calc_lat_r'] = [round(j, 4) for j in dbdf.calc_lat]
#	dbdf['calc_lon_r'] = [round(j, 4) for j in dbdf.calc_lon]
#	dbdf['latlon'] = zip(dbdf.calc_lat_r, dbdf.calc_lon_r)
#	latlon_d.update({key : list(dbdf['latlon'])})
#
#pickle.dump( latlon_d, open( "ca_sr_basins.p", "wb" ) )

###############################

#from colo_r_basins import latlon_x as latlon_d

###############################

latlon_d = pickle.load( open( "./dict/ca_sr_basins.p", "rb"))

latlon_b = {}

r_latlon = pickle.load( open( "./dict/region_latlon.p", "rb"))

r_latlon['arkred'] = r_latlon.pop('ark')
r_latlon['colo'] = r_latlon.pop('color')
r_latlon['pnw'] = r_latlon.pop('crb')
r_latlon['riog'] = r_latlon.pop('rio')
r_latlon['gbas'] = r_latlon.pop('grb')

for i,v in latlon_d.items():
	s = pd.Series(v)
	latlon_b.update({i: s})

###############################################################

class makebasin():
	def __init__(self):

		self.region_df = {'arkred' : {}, 'cali' : {}, 'colo' : {}, 'gbas' : {}, 'mo' : {}, 'pnw' : {}, 'riog' : {}}
		self.region_dict = {'arkred' : [], 'cali' : [], 'colo' : [], 'gbas' : [], 'mo' : [], 'pnw' : [], 'riog' : []}
		
	def init_regdict(self):
		for fn in os.listdir('.'):
			for region in self.region_dict.keys():
				if region in fn[:6]:
					self.region_dict[region].append(fn)
					
					
	def check_basin(self, basin):
		chkb = {}
		for j, k in r_latlon.items():
			for i in latlon_b[basin]:
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
		for i in latlon_b[basin]:
				if i in list(r_latlon[region]):
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
		
			latlon_df = pd.concat([c_prcp, c_tmax, c_tmin, c_wind], axis=1)
			latlon_df.columns = ['prcp', 'tmax', 'tmin', 'wind']
			latlon_df['date'] = [date.fromordinal(int(711858 + j)) for j in latlon_df.index]
			latlon_df['mo'] = [j.month for j in latlon_df.date]
			latlon_df['day'] = [j.day for j in latlon_df.date]
			latlon_df['year'] = [j.year for j in latlon_df.date]
	
			latlon_df['prcp_r'] = np.round(latlon_df['prcp'], 2)
			latlon_df['tmax'] = np.round(latlon_df['tmax'], 2)
			latlon_df['tmin'] = np.round(latlon_df['tmin'], 2)
			latlon_df['wind'] = np.round(latlon_df['wind'], 2)
			
			latlon_df = latlon_df[['prcp_r', 'tmax', 'tmin', 'wind']]				
			
			if not os.path.exists(basin):
				os.mkdir(basin)
			else:
				pass
			latlon_df.to_csv('./%s/data_%s_%s' % (basin, i[0], i[1]), sep=" ", header=False, index=False)
			
	def basin_all(self, li):
		
		self.init_regdict()
		for i in li:
			r = self.check_basin(i)
			for j in r:
				self.region_df = {'arkred' : [], 'cali' : [], 'colo' : [], 'gbas' : [], 'mo' : [], 'pnw' : [], 'riog' : []}
				self.make_reg_single(i, j)
				self.write_files(i, j)
