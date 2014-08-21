import numpy as np
import pandas as pd
import os
import pickle
import ast
from StringIO import StringIO
import datetime
import math


class rbm_post():

	def __init__(self, op_path, rc_path, rbm_path, atm_path, rc_rout_path, op_rout_path):
		self.st_rc = pickle.load(open(rc_path, 'rb'))
		self.st_op = pickle.load(open(op_path, 'rb'))
		self.atm_path = atm_path
#		self.flowpath = flowpath
		self.st_d = {}
		self.st_d.update({'st_rc' : self.st_rc, 'st_op' : self.st_op})
		self.rbm_path = rbm_path
		self.spat_d = {}
		self.cell_d = {}
		self.ll_d = {}
		self.ext_wt = pd.DataFrame()
		self.ext_atmo = pd.DataFrame()
		self.rc_rout_path = rc_rout_path
		self.op_rout_path = op_rout_path

	def make_spat_d(self):
		for fn in os.listdir(self.rbm_path):
			spat = pd.read_fwf('%s/%s/hist.Spat' % (self.rbm_path, fn), names=['reach', 'cell', 'row', 'column', 'lat', 'lon', 'ndelta'])
			spat['latlon'] = zip(spat['lat'], spat['lon'])
			spat = spat.drop_duplicates(subset=['latlon'])
			self.spat_d.update({fn : spat})

	def fix_stnames(self, fix_d):		
		for i, v in fix_d.items():
			v['slug'] = [str(j).split(' ')[0][:5] for j in v['PNAME']]
			da = []
			for o, x in v.ix[v.duplicated(subset=['slug'])]['slug'].iteritems():
				#print x
				da.append(x)
				n = da.count(x)
				if len(x) < 5:
					print x
					fix_d[i].ix[o, 'slug'] = x + str(n)
				elif (len(x) >= 5):
					print x
					fix_d[i].ix[o, 'slug'] = x[:4] + str(n)

	def make_diff(self):
		temp_cell_d = {}
		temp_ll_d = {}
		for p in self.st_d.keys():
			temp_cell_d.update({p : {}})
			temp_ll_d.update({p : {}})
		for tech in self.st_d.keys():
			for i in self.st_d[tech].keys():
				if i in self.spat_d.keys():
					jcell_d = {}
					jll_d = {}
			#		print os.getcwd()
					for k in self.st_d[tech][i].values:
						cell_d = {}
						ll_d = {}
						jcell_d.update({k[1] : None})
						jll_d.update({k[1] : None})
			#			print j_d
						stn_ll = k[2]
						for spat_ll in self.spat_d[i].values:
			#				fn_d = {}
							diff = ((spat_ll[4] - stn_ll[0])**2 + (spat_ll[5] - stn_ll[1])**2)**0.5
							cell_d.update({spat_ll[1] : diff})	
							ll_d.update({str(tuple([spat_ll[4], spat_ll[5]])) : diff})
		#				print k, ll_d
						cell = min(cell_d, key=cell_d.get)
						ll = min(ll_d, key=ll_d.get)
						#print tech, i, k[1], cell
						mi = cell_d[cell]
						jcell_d[k[1]] = cell
						jll_d[k[1]] = ll
			#		print j_d.items()
					temp_cell_d[tech].update({i : jcell_d})
					temp_ll_d[tech].update({i : jll_d})
				self.cell_d[tech] = temp_cell_d[tech]
				self.ll_d[tech] = temp_ll_d[tech]

	def make_rc_outfiles(self, scen, basin, wpath):
		wtemp_path = self.rbm_path + '/' + basin
		atmo_path = self.atm_path + '/' + scen
		rc_rout_path = self.rc_rout_path + '/' + scen + '/' + basin
		for pcode, cell in self.cell_d['st_rc'][basin].items():
#			with open('%s/%s.%s' % (wpath, scen, str(pcode).split('.')[0]), 'w') as outfile:
			line_d = {}
			set_li = []

			if os.path.exists(wtemp_path):
				with open('%s/%s.Temp' % (wtemp_path, scen), 'rb') as wtempfile:
					line_d.update({'wtemp' : []})
					for line in wtempfile:
						sp = line.split()
						if sp[3] == str(cell).split('.')[0]: 
							line_d['wtemp'].append(line)
				
				wtemp_str = ''.join(line_d['wtemp'])
				wtemp_str = StringIO(wtemp_str)
				wtemp_df = pd.read_fwf(wtemp_str, header=None, names=['YEAR', 'DAY', 'REACH', 'CELL', 'SEGMENT', 'WTEMP', 'HEADTEMP', 'AIRTEMP'])
				wtemp_df = wtemp_df.groupby('YEAR').mean()
				wtemp_df = wtemp_df.reset_index()
				wtemp_df['ord'] = wtemp_df.index
				wd =  lambda x: datetime.date.fromordinal((datetime.date(1949, 1, 1)).toordinal() + int(x['ord']))
				wtemp_df['DATE'] = wtemp_df.apply(wd, axis=1)
				del wtemp_df['ord']
				wtemp_df = wtemp_df.set_index('DATE')
				set_li.append(wtemp_df)


			with open('%s/full_data_%s_%s' % (atmo_path, ast.literal_eval(self.ll_d['st_rc'][basin][pcode])[0], ast.literal_eval(self.ll_d['st_rc'][basin][pcode])[1])) as atmofile:
				line_d.update({'atmo' : ''.join(atmofile.readlines())})


			atmo_str = StringIO(line_d['atmo'])
			atmo_df = pd.read_table(atmo_str, skiprows=5)
			atmo_df = atmo_df.rename(columns = {'# YEAR': 'YEAR'})
			self.ext_atmo = atmo_df
			ad =  lambda x: datetime.date(int(x['YEAR']), int(x['MONTH']), int(x['DAY']))
			atmo_df['DATE'] = atmo_df.apply(ad, axis=1)
			atmo_df = atmo_df.set_index('DATE')
			set_li.append(atmo_df)




			rout_fn = basin + '_' + self.st_rc[basin].set_index('PCODE').loc[pcode]['slug']
			if len(rout_fn) < 5:
				rout_fn = rout_fn + ' '*(5-len(rout_fn))
			rout_df = pd.read_fwf('%s/%s.day' % (rc_rout_path, rout_fn), header=None, widths=[12, 12, 12, 13])
			rout_df.columns = ['routyear', 'routmonth', 'routday', 'FLOW_CFS']
			mkdate = lambda x: datetime.date(int(x['routyear']), int(x['routmonth']), int(x['routday']))
			rout_df['date'] = rout_df.apply(mkdate, axis=1)
			rout_df = rout_df.set_index('date')
			set_li.append(rout_df)

			print [i for i in set_li]
			print [type(i) for i in set_li]

			cat_df = pd.concat([i for i in set_li], join='inner', axis=1)
			del cat_df['routyear']
			del cat_df['routmonth']
			del cat_df['routday']
			print cat_df

			cat_df.to_csv('%s/%s.%s' % (wpath, scen, str(pcode).split('.')[0]), sep='\t')
				





b = rbm_post('/home/chesterlab/Bartos/VIC/input/dict/opstn.p', '/home/chesterlab/Bartos/VIC/input/dict/rcstn.p', '/media/melchior/BALTHASAR/nsf_hydro/VIC/output/rbm/run', '/media/melchior/BALTHASAR/nsf_hydro/VIC/output/st_rc', '/media/melchior/BALTHASAR/nsf_hydro/VIC/output/rout/rc/d8', '/media/melchior/BALTHASAR/nsf_hydro/VIC/output/rout/op/d8')

b.make_spat_d()

b.fix_stnames(b.st_rc)

b.make_diff()

b.make_rc_outfiles('hist', 'little_col', '/home/chesterlab/Bartos/post/rc') 






b = rbm_post('/media/chesterlab/My Passport/Files/VIC/input/dict/opstn.p', '/media/chesterlab/My Passport/Files/VIC/input/dict/rcstn.p', '/media/chesterlab/storage/post/rbm', '/media/chesterlab/storage/post/st_rc')

b.make_spat_d()

b.make_diff()

b.make_rc_outfiles('hist', 'little_col', '/media/chesterlab/storage/post/wpath') 
