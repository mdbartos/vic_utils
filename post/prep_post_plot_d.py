import numpy as np
import pandas as pd
from pylab import *
import os
import datetime
import pickle

class post_plot_rc_region():
	
	def __init__(self, rpath, tech, post_pp_d_path):
		self.rpath = rpath
#		self.wpath = wpath
		self.tech = tech
#		self.typ = typ
		self.li_basin = os.listdir(rpath)
		self.li_scen = ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']
		self.post_pp_d = pd.read_pickle(post_pp_d_path)		
	
		self.reg_d = {}
	
		if tech == 'op':
			stech = 'st_op'
		elif tech == 'rc':
			stech = 'st_rc'
		else:
			stech = tech

		self.tech_pp = self.post_pp_d[stech]
	
		self.regs = list(set(self.tech_pp['WR_REG']))
		
		if tech in ['rc', 'op']:
			for i in self.regs:
				wr = self.tech_pp.loc[self.tech_pp['WR_REG'] == i].loc[self.tech_pp['W_SRC'].isin(['Surface Water', 'Unknown Freshwater', 'GW/Surface Water'])]
				self.reg_d.update({i : list(wr.index)})
		else:
			for i in self.regs:
				wr = self.tech_pp.loc[self.tech_pp['WR_REG'] == i]
				self.reg_d.update({i : list(wr.index)})
		
		self.reg_basin_d = {}
		self.reg_df_d = {}

	def prep_reg_basins(self):

		for region in self.reg_d.keys():
			
			reg_df = {}
			pcodes = [str(i).split('.')[0] for i in self.reg_d[region]]
			print 'pcodes', pcodes
			self.reg_basin_d.update({region : {}})

			for basin in self.li_basin:

				self.reg_basin_d[region].update({basin : []})
				rbpath = self.rpath + '/' + basin
				rb_li = list(set([i.split('.')[1] for i in os.listdir(rbpath)]))
				print 'basin list', rb_li
				b_pcodes = [j for j in pcodes if j in rb_li]
				self.reg_basin_d[region][basin].extend(b_pcodes)

	def plot_region(self, wreg):
		
		self.reg_df_d.update({wreg : {}})

		for scen in self.li_scen:
			self.reg_df_d[wreg].update({scen : {}})

		for basin in self.reg_basin_d[wreg].keys():
			if len(self.reg_basin_d[wreg][basin]) > 0:
				rbpath = self.rpath + '/' + basin
				b_d = {}

				for scen in self.li_scen:
					li_2 = ['.'.join([scen, i]) for i in self.reg_basin_d[wreg][basin]]

					
					d = {}
		
					for j in li_2:
						
						jb = basin + '-' + j 
		
						f = pd.read_csv('%s' % (self.rpath + '/' + basin + '/' + j), sep='\t')
						if 'date' in f.columns:
							f = f.dropna(subset=['date'])
							f = f.set_index('date')
			#				f = f['POWER_CAP_MW']
						elif 'YEAR.1' in f.columns:
							mkdate =  lambda x: datetime.date(int(x['YEAR.1']), int(x['MONTH']), int(x['DAY.1']))
							f['date'] = f.apply(mkdate, axis=1) 
							f = f.set_index('date')
			#				f = f['POWER_CAP_MW']
						else:
							mkdate =  lambda x: datetime.date(int(x['YEAR']), int(x['MONTH']), int(x['DAY']))
							f['date'] = f.apply(mkdate, axis=1) 
							f = f.set_index('date')	
						d.update({jb : f})
				
					scen_df = pd.concat([d[i]['POWER_CAP_MW'] for i in d.keys()], axis=1)
					print scen_df
					b_d.update({scen : scen_df})
				
				for j in b_d.keys():
					b_d[j]['BASIN_CAP'] = b_d[j].sum(axis=1)
					self.reg_df_d[wreg][j].update({basin : b_d[j]['BASIN_CAP']})
		
		for k in self.reg_df_d[wreg].keys():
			print k
			print '\n'
			print self.reg_df_d[wreg][k]
			self.reg_df_d[wreg][k] = pd.concat(self.reg_df_d[wreg][k].values(), axis=1)
	
		for i in self.reg_df_d[wreg].keys():
	
			self.reg_df_d[wreg][i]['SUM_CAP'] = self.reg_df_d[wreg][i].sum(axis=1)
			self.reg_df_d[wreg][i]['date'] = self.reg_df_d[wreg][i].index
			self.reg_df_d[wreg][i]['date'] = pd.to_datetime(self.reg_df_d[wreg][i]['date'])
			mkyear = lambda x: x['date'].year
			mkmonth = lambda x: x['date'].month
			mkday = lambda x: x['date'].day
			self.reg_df_d[wreg][i]['YEAR'] = self.reg_df_d[wreg][i].apply(mkyear, axis=1)
			self.reg_df_d[wreg][i]['MONTH'] = self.reg_df_d[wreg][i].apply(mkmonth, axis=1)
			self.reg_df_d[wreg][i]['DAY'] = self.reg_df_d[wreg][i].apply(mkday, axis=1)
			self.reg_df_d[wreg][i] = self.reg_df_d[wreg][i][['YEAR', 'MONTH', 'DAY', 'SUM_CAP']]
			print self.reg_df_d[wreg][i]
	

	def plot_op_region(self, wreg):

		self.reg_df_d.update({wreg : {}})
		r_d = {}
		for scen in self.li_scen:
			self.reg_df_d[wreg].update({scen : {}})

		for scen in self.li_scen:
			li_2 = ['.'.join([scen, str(i).split('.')[0]]) for i in self.reg_d[wreg]]

			d = {}
	
			for j in li_2:
				
	
				f = pd.read_csv('%s' % (self.rpath + '/' + j), sep='\t')
				print f
				print f.columns
				if 'date' in f.columns:
					print 'FOUND DATE'
					f = f.dropna(subset=['date'])
					f = f.set_index('date')
	#				f = f['POWER_CAP_MW']
				elif 'DATE' in f.columns:
					f = f.dropna(subset=['DATE'])
					f = f.set_index('DATE')
	#				f = f['POWER_CAP_MW']
				elif set(['YEAR', 'MONTH', 'DAY']).issubset(f.columns):
					mkdate =  lambda x: datetime.date(int(x['YEAR']), int(x['MONTH']), int(x['DAY']))
					f['date'] = f.apply(mkdate, axis=1) 
					f = f.set_index('date')	
				elif 'YEAR.1' in f.columns:
					mkdate =  lambda x: datetime.date(int(x['YEAR.1']), int(x['MONTH']), int(x['DAY.1']))
					f['date'] = f.apply(mkdate, axis=1) 
					f = f.set_index('date')
	#				f = f['POWER_CAP_MW']
				elif 'Unnamed: 0' in f.columns:
					f['date'] = f['Unnamed: 0']
					del f['Unnamed: 0']
					f = f.set_index('date')
				else:
					mkdate =  lambda x: datetime.date(int(x['YEAR']), int(x['MONTH']), int(x['DAY']))
					f['date'] = f.apply(mkdate, axis=1) 
					f = f.set_index('date')	
				d.update({j : f})
		
			scen_df = pd.concat([d[i]['POWER_CAP_MW'] for i in d.keys()], axis=1)
			print scen_df
			self.reg_df_d[wreg].update({scen : scen_df})
		
		for j in self.reg_df_d[wreg].keys():
			self.reg_df_d[wreg][j]['SUM_CAP'] = self.reg_df_d[wreg][j].sum(axis=1)
	
		for i in self.reg_df_d[wreg].keys():
	
			self.reg_df_d[wreg][i]['date'] = self.reg_df_d[wreg][i].index
			self.reg_df_d[wreg][i]['date'] = pd.to_datetime(self.reg_df_d[wreg][i]['date'])
			mkyear = lambda x: x['date'].year
			mkmonth = lambda x: x['date'].month
			mkday = lambda x: x['date'].day
			self.reg_df_d[wreg][i]['YEAR'] = self.reg_df_d[wreg][i].apply(mkyear, axis=1)
			self.reg_df_d[wreg][i]['MONTH'] = self.reg_df_d[wreg][i].apply(mkmonth, axis=1)
			self.reg_df_d[wreg][i]['DAY'] = self.reg_df_d[wreg][i].apply(mkday, axis=1)
			self.reg_df_d[wreg][i] = self.reg_df_d[wreg][i][['YEAR', 'MONTH', 'DAY', 'SUM_CAP']]
			print self.reg_df_d[wreg][i]




class post_plot_hy_region():
	
	def __init__(self, rpath, tech):
		self.rpath = rpath
#		self.wpath = wpath
		self.tech = tech
#		self.typ = typ
		self.li_basin = os.listdir(rpath)
		self.li_scen = ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']	
		self.reg_basins = \
				{'cali' : ['pitt', 'cottonwood', 'tulare', 'rushcr', 'riohondo', 'redmtn', 'kern', 'coyotecr', 'corona', 'castaic', 'salton'],
				'color' : ['lees_f', 'little_col', 'gila_imp', 'billw', 'parker', 'imperial', 'hoover', 'gc', 'davis', 'virgin', 'paria'],
				'grb' : ['wabuska', 'lahontan', 'intermtn', 'brigham'],
				'ark' : ['comanche'],
				'mo' : ['pawnee', 'guer', 'colstrip', 'peck'],
				'pnw' : ['wauna', 'elwha', 'baker', 'hmjack', 'yelm', 'sodasprings', 'eaglept', 'irongate']
				}

		self.reg_d = {}
			
		self.reg_basin_d = {}
		self.reg_df_d = {}



	def plot_region(self, wreg):
		
		self.reg_df_d.update({wreg : {}})

		for scen in self.li_scen:
			self.reg_df_d[wreg].update({scen : {}})

		for basin in self.reg_basins[wreg]:
			if basin in os.listdir(self.rpath):
				rbpath = self.rpath + '/' + basin
				b_d = {}
	
				for scen in self.li_scen:
					li_2 = [i for i in os.listdir(rbpath) if i.split('.')[0] == scen]  
	
					
					d = {}
		
					for j in li_2:
						
						jb = basin + '-' + j 
		
						f = pd.read_csv('%s' % (self.rpath + '/' + basin + '/' + j), sep='\t')
						if 'date' in f.columns:
							f = f.dropna(subset=['date'])
							f = f.set_index('date')
			#				f = f['POWER_CAP_MW']
						elif 'YEAR.1' in f.columns:
							mkdate =  lambda x: datetime.date(int(x['YEAR.1']), int(x['MONTH']), int(x['DAY.1']))
							f['date'] = f.apply(mkdate, axis=1) 
							f = f.set_index('date')
			#				f = f['POWER_CAP_MW']
						else:
							mkdate =  lambda x: datetime.date(int(x['YEAR']), int(x['MONTH']), int(x['DAY']))
							f['date'] = f.apply(mkdate, axis=1) 
							f = f.set_index('date')	
						d.update({jb : f})
				
					scen_df = pd.concat([d[i]['POWER_CAP_MW'] for i in d.keys()], axis=1)
					print scen_df
					b_d.update({scen : scen_df})
				
				for j in b_d.keys():
					b_d[j]['BASIN_CAP'] = b_d[j].sum(axis=1)
					self.reg_df_d[wreg][j].update({basin : b_d[j]['BASIN_CAP']})
		
		for k in self.reg_df_d[wreg].keys():
			print k
			print '\n'
			print self.reg_df_d[wreg][k]
			self.reg_df_d[wreg][k] = pd.concat(self.reg_df_d[wreg][k].values(), axis=1)
	
		for i in self.reg_df_d[wreg].keys():
	
			self.reg_df_d[wreg][i]['SUM_CAP'] = self.reg_df_d[wreg][i].sum(axis=1)
			self.reg_df_d[wreg][i]['date'] = self.reg_df_d[wreg][i].index
			self.reg_df_d[wreg][i]['date'] = pd.to_datetime(self.reg_df_d[wreg][i]['date'])
			mkyear = lambda x: x['date'].year
			mkmonth = lambda x: x['date'].month
			mkday = lambda x: x['date'].day
			self.reg_df_d[wreg][i]['YEAR'] = self.reg_df_d[wreg][i].apply(mkyear, axis=1)
			self.reg_df_d[wreg][i]['MONTH'] = self.reg_df_d[wreg][i].apply(mkmonth, axis=1)
			self.reg_df_d[wreg][i]['DAY'] = self.reg_df_d[wreg][i].apply(mkday, axis=1)
			self.reg_df_d[wreg][i] = self.reg_df_d[wreg][i][['YEAR', 'MONTH', 'DAY', 'SUM_CAP']]
			print self.reg_df_d[wreg][i]


b = post_plot_rc_region('/home/chesterlab/Bartos/post/rc_ub', 'rc', '/home/chesterlab/Bartos/VIC/input/dict/post_pp_d.p')

b.prep_reg_basins()

b_li = [i for i in b.reg_d.keys() if i != 'rio']

for v in b_li:
    b.plot_region(v)

b = post_plot_rc_region('/home/chesterlab/Bartos/post/op', 'op', '/home/chesterlab/Bartos/VIC/input/dict/post_pp_d.p')

for v in b.reg_d.keys():
	b.plot_op_region(v)

b = post_plot_rc_region('/home/chesterlab/Bartos/post/ct', 'ct', '/home/chesterlab/Bartos/VIC/input/dict/post_pp_d.p')

for v in b.reg_d.keys():
	b.plot_op_region(v)

