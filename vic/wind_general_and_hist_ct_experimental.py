#cd Southwest Team Share

import os
import numpy as np
import pandas as pd
import netCDF4
from datetime import date
import pickle
import shutil

'''
Prime Mover Types:
	BT = Binary cycle turbine
	CA = Combined cycle steam turbine
	CC = Combined cycle - total unit
	CE = Compressed air energy storage
c	CS = Combined cycle - single shaft
c	CT = Combined cycle combustion turbine
	FC = Fuel cell
c	GT = Combustion (gas) turbine
	HY = Hydraulic turbine
c	IC = Internal combustion (diesel)
c	IG = Integrated gasification combustion turbine
	OT = Other turbine
	PS = Hydraulic turbine - reversible (pumped storage)
s	PV = Photovoltaic
	ST = Steam turbine (boiler, nuclear, geothermal, and solar steam)
w	WT = Wind turbine 
'''

class get_cells():

		
	def __init__(self, tech_d, latlon_path):
			
		self.reg_conv = {'Arkansas-White-Red': 'arkred',
		'California' : 'cali',
		'Great Basin' : 'gbas',
		'Missouri' : 'mo',
		'Pacific Northwest' : 'pnw',
		'Rio Grande' : 'riog',
		'Upper Colorado' : 'colo',
		'Lower Colorado' : 'colo'}

		self.oldnew_conv = {'ark': 'arkred',
		'cali': 'cali',
		'grb': 'gbas',
		'mo' : 'mo',
		'crb' : 'pnw',
		'rio': 'riog',
		'color' : 'colo'}
	
		self.newold_conv = {'arkred': 'ark',
		'cali': 'cali',
		'gbas': 'grb',
		'mo' : 'mo',
		'pnw' : 'crb',
		'riog': 'rio',
		'colo' : 'color'}
		
		self.pp = {}
		self.diff_d = {}
		
		self.tech_d = tech_d
	
		
		for o, t in tech_d.items():
			self.pp.update({o : {}})
			for i in set(t['WR_REG'].dropna()):
				s_tech = t.ix[t['WR_REG'] == i]
				self.pp[o].update({i : {}})
				for j, k in s_tech.iterrows():
					print j, k
					self.pp[o][i].update({int(j) : (k['LAT'], k['LON'])})
		
		self.r_latlon = pickle.load( open( latlon_path, "rb"))
		self.reg_latlon = {}
		self.reg_latlon['arkred'] = self.r_latlon['ark']
		self.reg_latlon['cali'] = self.r_latlon['cali']
		self.reg_latlon['colo'] = self.r_latlon['color']
		self.reg_latlon['gbas'] = self.r_latlon['grb']
		self.reg_latlon['mo'] = self.r_latlon['mo']
		self.reg_latlon['pnw'] = self.r_latlon['crb']
		self.reg_latlon['riog'] = self.r_latlon['rio']
	
		for z in tech_d.keys():	
			self.diff_d.update({z : {}})

		self.region_df = {'arkred' : {}, 'cali' : {}, 'colo' : {}, 'gbas' : {}, 'mo' : {}, 'pnw' : {}, 'riog' : {}}
		self.region_dict = {'arkred' : [], 'cali' : [], 'colo' : [], 'gbas' : [], 'mo' : [], 'pnw' : [], 'riog' : []}
	
		self.modelpath = ''
		
	def make_diff(self, tech):
		temp_diff_d = {}
		for i in self.pp[tech].keys():
			j_d = {}
	#		print os.getcwd()
			for j, k in self.pp[tech][i].items():
				fn_d = {}
				j_d.update({j : None})
	#			print j_d
				lo = tuple([k[0], k[1]])
				for fn in self.reg_latlon[self.oldnew_conv[i]]:
	#				fn_d = {}
					diff = ((fn[0] - lo[0])**2 + (fn[1] - lo[1])**2)**0.5
					fn_d.update({fn : diff})
				cell = min(fn_d, key=fn_d.get)
				mi = fn_d[cell]
				j_d[j] = cell		
			print j_d.items()
			temp_diff_d.update({i : j_d})
		self.diff_d[tech] = temp_diff_d
	
	
	def get_hist(self, tech, **kwargs):
		if 'searchpath' in kwargs:
			h = kwargs['searchpath']
		else:
			h = os.getcwd()
		print h
		if 'copypath' in kwargs:
			c = kwargs['copypath']
		else:
			c = os.getcwd()
		print c
		for i in self.diff_d.keys():
			if not os.path.exists('%s/%s' % (c, i)):
				os.mkdir('%s/%s' % (c, i))
			for b in self.diff_d[i].keys():
#				cv = self.newold_conv[b]
				if not os.path.exists('%s/%s/%s' % (c, i, b)):
					os.mkdir('%s/%s/%s' % (c, i, b))
				bdir = c + ('/%s/%s' % (i, b))
#				os.chdir('%s' % (self.newold_conv[b]))
				for j in self.diff_d[i][b].keys():
					print self.diff_d[i][b][j]
					shutil.copy('%s/%s/data_%s_%s' % (h, b, self.diff_d[i][b][j][0], self.diff_d[i][b][j][1]), bdir)
#				os.chdir(h)
				
					
	
	
#	def cat_hist(old, hist):
#		for i in diff_d.keys():
#			if i == 'wind':
#				print os.getcwd()
#				os.chdir('./%s' % (i))
#			for b in diff_d[i].keys():
#				if old == False:
#					os.chdir('./%s' % (b))
#				elif old == True:
#					os.chdir('./%s' % (self.newold_conv[b]))
#				pp_d = {}
#				for j in diff_d[i][b].keys():
#					print diff_d[i][b][j]
#					f = open('data_%s_%s' % (diff_d[i][b][j][0], diff_d[i][b][j][1]), 'r')
#					r = f.readlines()
#					f.close()
#					print os.getcwd()
#					w_li = []			
#					for x in r:
#						if hist == False:
#							s = float(x.split()[3])
#							w_li.append(s)
#						elif hist == True:
#							s = float(x.split()[6])
#							w_li.append(s)
#					w_s = pd.Series(w_li)
#					pp_d.update({j : w_s})
#	#			print pp_d
#				pp_df = pd.DataFrame(pp_d)
#				print pp_df
#				pp_df.to_csv('%s_%s.csv' % (b, i))
#				os.chdir('..')

#######FUTURE ONLY####################

	def init_regdict(self, modelpath):
		self.modelpath = modelpath
		print self.modelpath
		for fn in os.listdir(self.modelpath):
			if fn.endswith('nc'):
				for region in self.region_dict.keys():
					if region in fn[:6]:
						self.region_dict[region].append(fn)
	
		
	def make_reg_single(self, reg, tech):
			
		nc = {}
		
		for fn in self.region_dict[reg]:
			pfn = self.modelpath + '/' + fn
			if self.newold_conv[reg] in self.diff_d[tech].keys():
				f = netCDF4.Dataset(pfn, 'r')								
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
				
				pan = pd.Panel(f.variables[v][:], items=f.variables['time'][:], major_axis=f.variables['lat'][:], minor_axis=f.variables['lon'][:])
				
				for i in self.diff_d[tech][self.newold_conv[reg]].values():
#					nc.update({i : {'prcp': {}, 'tmax': {}, 'tmin': {}, 'wind': {}}})
#					nc[i][v].update({yr:{}})
#					ilat = np.where(f.variables['lat'] == i[0])[0]
#					ilon = np.where(f.variables['lon'] == i[1])[0]
#					s = f.variables[v][:, ilat, ilon]
#					nc[i][v][yr] = s				
					if i[0] in pan.major_axis:
						if i[1] in pan.minor_axis:
							if i not in nc:
								nc.update({i : {'prcp': {}, 'tmax': {}, 'tmin': {}, 'wind': {}}})
							nc[i][v].update({yr:{}})
							s = pan.ix[:, i[0], i[1]]
							nc[i][v][yr] = s					
	
#			f.close()
			
		self.region_df[reg] = nc
		print self.region_df[reg]
				
	
	
	def write_files(self, reg, tech, **kwargs):

		if 'wpath' in kwargs:
			wpath = kwargs['wpath']
		else:
			wpath = self.modelpath
			
		for i, v in self.region_df[reg].items():
			if not v == None:
				c_prcp = pd.concat(self.region_df[reg][i]['prcp'].values())
				c_tmax = pd.concat(self.region_df[reg][i]['tmax'].values())
				c_tmin = pd.concat(self.region_df[reg][i]['tmin'].values())
				c_wind = pd.concat(self.region_df[reg][i]['wind'].values())
			
				latlon_df = pd.concat([c_prcp, c_tmax, c_tmin, c_wind], axis=1)
				latlon_df.columns = ['prcp', 'tmax', 'tmin', 'wind']
#				latlon_df['date'] = [date.fromordinal(int(711858 + j)) for j in latlon_df.index]
#				latlon_df['mo'] = [j.month for j in latlon_df.date]
#				latlon_df['day'] = [j.day for j in latlon_df.date]
#				latlon_df['year'] = [j.year for j in latlon_df.date]
		
#				latlon_df['prcp_r'] = np.round(latlon_df['prcp'], 2)
#				latlon_df['tmax'] = np.round(latlon_df['tmax'], 2)
#				latlon_df['tmin'] = np.round(latlon_df['tmin'], 2)
#				latlon_df['wind'] = np.round(latlon_df['wind'], 2)
				
				latlon_df = latlon_df[['prcp', 'tmax', 'tmin', 'wind']]				
				
				if not os.path.exists('%s/%s' % (wpath, tech)):
					os.mkdir('%s/%s' % (wpath, tech))
				if not os.path.exists('%s/%s/%s' % (wpath, tech, reg)):
					os.mkdir('%s/%s/%s' % (wpath, tech, reg))
				else:
					pass
				latlon_df.to_csv('%s/%s/%s/data_%s_%s' % (wpath, tech, reg, i[0], i[1]), sep="	", header=False, index=False)
			
	def basin_all(self, tech, mpath):
		
		self.init_regdict(mpath)
		for i in self.region_df.keys():
			self.region_df = {'arkred' : {}, 'cali' : {}, 'colo' : {}, 'gbas' : {}, 'mo' : {}, 'pnw' : {}, 'riog' : {}}
			print i
			self.make_reg_single(i, tech)
			self.write_files(i, tech)

			
ct = pd.read_csv('CT_WECC.csv', index_col=0).dropna(subset=['WR_REG'])
st_op = pd.read_csv('ST_WECC_OP.csv', index_col=0).dropna(subset=['WR_REG'])
st_rc = pd.read_csv('ST_WECC_RC.csv', index_col=0).dropna(subset=['WR_REG'])
solar = pd.read_csv('PV_WECC.csv', index_col=0).dropna(subset=['WR_REG'])
wind = pd.read_csv('WN_WECC.csv', index_col=0).dropna(subset=['WR_REG'])

techs = {'ct' : ct, 'st_op' : st_op, 'st_rc' : st_rc, 'solar' : solar, 'wind' : wind}

b = get_cells(techs, 'c:/Users/Matt Bartos/Desktop/cmip3_hydro_inputs/dict/region_latlon.p')

for a in techs.keys():
	b.make_diff(a)

b.basin_all('solar', 'c:/Users/Matt Bartos/Desktop/cmip3_hydro_inputs/sresa1b.ukmo_hadcm3.1')

for a in techs.keys():
	b.basin_all(a, 'c:/Users/Matt Bartos/Desktop/cmip3_hydro_inputs/sresa1b.ukmo_hadcm3.1')	



ct = pd.read_csv('CT_WECC.csv', index_col=0).dropna(subset=['WR_REG'])
st_op = pd.read_csv('ST_WECC_OP.csv', index_col=0).dropna(subset=['WR_REG'])
st_rc = pd.read_csv('ST_WECC_RC.csv', index_col=0).dropna(subset=['WR_REG'])

techs = {'ct' : ct, 'st_op' : st_op, 'st_rc' : st_rc}

b = get_cells(techs, '/home/melchior/Desktop/ct_st_forcings/region_latlon.p')

for a in techs.keys():
	b.make_diff(a)

for a in techs.keys():
	b.get_renhist(a, searchpath='/media/melchior/BALTHASAR/nsf_hydro/pre/source_data/source_hist_forcings', copypath='/home/melchior/Desktop/ct_st_forcings')


#########Make latlon_d for solar to apply clips



pickle.dump(latlon_d, open('solar.p', 'wb'))

latlon_d = {}

for i in diff_d.keys():
	if i == 'solar':
		for b in diff_d[i].keys():
			ili = []
			ili.extend(diff_d[i][b].values())
			ili = list(set(ili))
			print ili
			latlon_d.update({self.newold_conv[b] : ili})
####################

make_wind()
make_solar()

####################

class makebasin():
	def __init__(self):


#		self.model = model
		



###########################
mb = makebasin()
mb.basin_all('wind')
mb.basin_all('solar')
###########################

import shutil

#cd 'C:\Users\Matt Bartos\Desktop\a1b'


#		os.chdir('..')
		
write_ren()


