import numpy as np
import pandas as pd
import os
import ast
import pickle
import datetime

#self.latlon_c = pickle.load( open('hydrostn.p', 'rb'))


	
######################################################

class rout_post():

	def __init__(self, picklepath):
		self.inflow_o = {}
		self.inflow_m = {}
		self.inflow_n = {}
		self.inflow_a = {}
		self.latlon_c = pickle.load(open(picklepath, 'rb'))
	
	def init_datum(self):
		for scen in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:
			self.datum_d.update({scen : {'d' : None, 'm' : None}})
			if scen = 'hist':
				self.datum_d[scen]['d'] = hist_datum_day
				self.datum_d[scen]['m'] = hist_datum_month
			else:
				self.datum_d[scen]['d'] = fut_datum_day
				self.datum_d[scen]['m'] = fut_datum_month


	def rout_tables(self, basin, scen, typ, rpath):
		
		if not basin in inflow_o.keys():
			self.inflow_o.update({basin : {}})
		if not scen in inflow_o[basin].keys():
			self.inflow_o[basin].update({scen : {})
		if not typ in inflow_o[basin][scen].keys():
			self.inflow_o[basin][scen].update({typ : None})

		inflow_d = {}

		slugtable = self.latlon_c[basin].set_index('slug')
		print slugtable
		fullpath = '%s/%s/%s' % (rpath, basin, scen) 
		for fn in os.listdir(fullpath):
			sp_typ = fn.split('.')
			sp_nm = sp_typ[0].split('_')
			pcode = slugtable['PCODE'].loc[sp_nm[-1].split()[0]]	
			if typ == 'd':
				if (sp_typ[1] == 'day') and (sp_nm[-1] in slugtable.index):
					n = pd.read_fwf('%s/%s' % (fullpath, fn), header=None, widths=[12, 12, 12, 13])
					n.columns = ['year', 'month', 'day', '%s' % (pcode)]
					mkdate = lambda x: datetime.date(x['year'], x['month'], x['day'])
					n['date'] = n.apply(mkdate, axis=1)
					n = n.set_index('date')
					n = n['%s' % (pcode)]
					inflow_d.update({slugtable['PCODE'].loc[pcode: n})

			
			if typ == 'm':
				if (sp_typ[1] == 'month') and (sp_nm[-1] == in slugtable.index):
					n = pd.read_fwf('%s/%s' % (fullpath, fn), header=None, widths=[12, 12, 13])
					n.columns = ['year', 'month', '%s' % (pcode)]
					mkdate = lambda x: datetime.date(x['year'], x['month'], 1)
					n['date'] = n.apply(mkdate, axis=1)
					n = n.set_index('date')
					n = n['%s' % (pcode)]
					inflow_d.update({pcode: n})

		c = pd.concat([j for j in inflow_d.values()], axis=1)
		self.inflow_o[basin][scen][typ] = c

		
	##########################################	

	def adjust_colo(self, basin, scen, typ):

		self.inflow_o['hoover'][scen][typ][154] =  self.inflow_o['hoover'][scen][typ][154] + self.inflow_o['lees_f'][scen][typ][-9999] + self.inflow_o['little_col'][scen][typ][-9999] + self.inflow_o['gc'][scen][typ][-9999] +  self.inflow_o['virgin'][scen][typ][-9999]

		self.inflow_o['hoover'][scen][typ][8902] =  self.inflow_o['hoover'][scen][typ][8902] + self.inflow_o['lees_f'][scen][typ][-9999] + self.inflow_o['little_col'][scen][typ][-9999] + self.inflow_o['gc'][scen][typ][-9999] +  self.inflow_o['virgin'][scen][typ][-9999]

		self.inflow_o['davis'][scen][typ][152] =  self.inflow_o['davis'][scen][typ][152] + self.inflow_o['hoover'][scen][typ][154]

		self.inflow_o['parker'][scen][typ][447] =  self.inflow_o['parker'][scen][typ][447] + self.inflow_o['davis'][scen][typ][152]

		self.inflow_o['imperial'][scen][typ][-9999] =  self.inflow_o['imperial'][scen][typ][-9999] + self.inflow_o['parker'][scen][typ][447] + self.inflow_o['gila_imp'][scen][typ][100] 
	
	##########################################
	
	def make_mean(self):
		for i, k in self.inflow_o.items():
			if 'hist' in i:
	#		print i
	#		print k.mean()
	#		print k
	#		print k/k.mean()
				self.inflow_m.update({'%s-mean' % (i) : k.mean()})



	def make_normalized(self):
		for i, k in self.inflow_o.items():
			for j, v in self.inflow_m.items():
				o = i.split('-')
				m = j.split('-')
				if o[0] == m[0] and o[-1] == m[-2]:
					norm = k/v
					norm['year'] = k['year']
					norm['month'] = k['month']
					if 'day' in norm.columns:
						norm['day'] = k['day']
					self.inflow_n.update({'%s-normalized' % (i) : norm})
				


	for i, k in self.inflow_n.items():
		if ('castaic' in i) or ('corona' in i) or ('riohondo' in i) or ('coyotecr' in i) or ('redmtn' in i):
			newmel = self.inflow_n['pitt-%s-%s-normalized' % (i.split('-')[1], i.split('-')[2])][6158]
			bishp = self.inflow_n['cottonwood-%s-%s-normalized' % (i.split('-')[1], i.split('-')[2])][326]
			gila = self.inflow_n['imperial-%s-%s-normalized' % (i.split('-')[1], i.split('-')[2])][-9999]
			transf = pd.concat([newmel, bishp, gila], axis=1)
			n = k
			print n
			ncol = [p for p in n.columns if type(p) == float]
			for x in ncol:
				n[x] = n[x]*0.396 + newmel*0.255 + bishp*0.089 + gila*0.264
			self.inflow_a.update({i : n})
		elif ('tulare' in i):
			newmel = self.inflow_n['pitt-%s-%s-normalized' % (i.split('-')[1], i.split('-')[2])][6158]
			friant = self.inflow_n['pitt-%s-%s-normalized' % (i.split('-')[1], i.split('-')[2])][50393]
			transf = pd.concat([newmel, friant], axis=1)
			n = k
			ncol = [p for p in n.columns if type(p) == float]
			for x in ncol:
				n[x] = n[x]*0.678 + newmel*0.22 + friant*0.102
			self.inflow_a.update({i : n})
		else:
			self.inflow_a.update({i : k})			
			
	for i, k in self.inflow_a.items():
		k.to_csv('./tables_normalized/%s/%s.csv' % (i.split('-')[1], i))

	##########################

	cali_basins = ['castaic', 'corona', 'cottonwood', 'coyotecr', 'kern', 'pitt', 'redmtn', 'riohondo', 'rushcr', 'tulare']
	colo_basins = ['billw', 'davis', 'gc', 'hoover', 'imperial', 'lees_f', 'little_col', 'paria', 'parker', 'virgin', 'gila_imp']

	calicct = {'hist': [], 'a1b': [], 'a2': [], 'b1': []}
	colocct = {'hist': [], 'a1b': [], 'a2': [], 'b1': []}

	for q in self.inflow_o.keys():
		psp = q.split('.')[0]
		ssp = q.split('-')
		if (ssp[0] in cali_basins) and (ssp[2] == 'd'):
			calicct[ssp[1]].append(self.inflow_o[q])
		if (ssp[0] in cali_basins) and (ssp[2] == 'd'):
			colocct[ssp[1]].append(self.inflow_o[q])

	for a in calicct.keys():
		t = pd.concat(calicct[a], axis=1)
		tc = t.columns
		stc = (set(tc))
		dupr = sorted([list(tc).index(i) for i in stc])
		print dupr
		t = t.iloc[:, dupr]
		t.to_csv('./combined_tables_raw/%s/%s_cali.csv' % (a, a))

	for a in colocct.keys():
		t = pd.concat(colocct[a], axis=1)
		tc = t.columns
		stc = (set(tc))
		dupr = sorted([list(tc).index(i) for i in stc])
		print dupr
		t = t.iloc[:, dupr]
		t.to_csv('./combined_tables_raw/%s/%s_colo.csv' % (a, a))

	###########################

	for q in self.inflow_a.keys():
		psp = q.split('.')[0]
		ssp = q.split('-')
		if (ssp[0] in cali_basins) and (ssp[2] == 'd'):
			calicct[ssp[1]].append(self.inflow_a[q])
		if (ssp[0] in cali_basins) and (ssp[2] == 'd'):
			colocct[ssp[1]].append(self.inflow_a[q])

	for a in calicct.keys():
		t = pd.concat(calicct[a], axis=1)
		tc = t.columns
		stc = (set(tc))
		dupr = sorted([list(tc).index(i) for i in stc])
		print dupr
		t = t.iloc[:, dupr]
		t.to_csv('./combined_tables_norm/%s/%s_cali.csv' % (a, a))

	for a in colocct.keys():
		t = pd.concat(colocct[a], axis=1)
		tc = t.columns
		stc = (set(tc))
		dupr = sorted([list(tc).index(i) for i in stc])
		print dupr
		t = t.iloc[:, dupr]
		t.to_csv('./combined_tables_norm/%s/%s_colo.csv' % (a, a))


b = rout_post('/home/chesterlab/Bartos/VIC/input/dict/hydrostn.p')

b.rout_tables('lees_f', 'hist', 'd', '/home/chesterlab/Bartos/VIC/output/rout/d8')

for i in self.latlon_c.keys():
	rout_tables(i, 'hist', 'm')
	rout_tables(i, 'a1b', 'm')
	rout_tables(i, 'hist', 'd')
	rout_tables(i, 'a1b', 'd')
	rout_tables(i, 'a2', 'm')
	rout_tables(i, 'a2', 'd')
	rout_tables(i, 'b1', 'm')
	rout_tables(i, 'b1', 'd')

for i, k in self.inflow_o.items():
	k.to_csv('./tables_raw/%s/%s.csv' % (i.split('-')[1], i))
