import numpy as np
import pandas as pd
import os
import ast
import pickle
import datetime
import scipy
from scipy import optimize
from sklearn import linear_model, datasets
from pylab import *

#self.latlon_c = pickle.load( open('hydrostn.p', 'rb'))


	
######################################################

class rout_post():

	def __init__(self, picklepath, egrid_path):
		self.inflow_o = {}
		self.inflow_m = {}
		self.inflow_n = {}
		self.inflow_a = {}
		self.latlon_c = pickle.load(open(picklepath, 'rb'))
		self.egrid = pickle.load(open(egrid_path, 'rb'))
		self.p_dat = {}
		self.p_eqn = {}
		self.reg_basins = \
				{'cali' : ['pitt', 'cottonwood', 'tulare', 'rushcr', 'riohondo', 'redmtn', 'kern', 'coyotecr', 'corona', 'castaic', 'salton'],
				'color' : ['lees_f', 'little_col', 'gila_imp', 'billw', 'parker', 'imperial', 'hoover', 'gc', 'davis', 'virgin', 'paria'],
				'grb' : ['wabuska', 'lahontan', 'intermtn', 'brigham'],
				'ark' : ['comanche'],
				'mo' : ['pawnee', 'guer', 'colstrip', 'peck'],
				'pnw' : ['wauna', 'elwha', 'baker', 'hmjack', 'yelm', 'sodasprings', 'eaglept', 'irongate']
				}
	def init_datum(self):
		for scen in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:
			self.datum_d.update({scen : {'d' : None, 'm' : None}})
			if scen == 'hist':
				self.datum_d[scen]['d'] = hist_datum_day
				self.datum_d[scen]['m'] = hist_datum_month
			else:
				self.datum_d[scen]['d'] = fut_datum_day
				self.datum_d[scen]['m'] = fut_datum_month


	def rout_tables(self, basin, scen, typ, rpath):
		
		if not basin in self.inflow_o.keys():
			self.inflow_o.update({basin : {}})
		if not scen in self.inflow_o[basin].keys():
			self.inflow_o[basin].update({scen : {}})
		if not typ in self.inflow_o[basin][scen].keys():
			self.inflow_o[basin][scen].update({typ : None})

		inflow_d = {}

		slugtable = self.latlon_c[basin].set_index('slug')
		print slugtable
		fullpath = '%s/%s/%s' % (rpath, scen, basin) 
		for fn in os.listdir(fullpath):
			sp_typ = fn.split('.')
			sp_nm = sp_typ[0].split('_')
			pcode = slugtable['PCODE'].loc[sp_nm[-1].split()[0]]	
			if typ == 'd':
				if (sp_typ[1] == 'day') and (sp_nm[-1].split()[0] in slugtable.index):
					n = pd.read_fwf('%s/%s' % (fullpath, fn), header=None, widths=[12, 12, 12, 13])
					n.columns = ['year', 'month', 'day', '%s' % (pcode)]
					mkdate = lambda x: datetime.date(int(x['year']), int(x['month']), int(x['day']))
					n['date'] = n.apply(mkdate, axis=1)
					n = n.set_index('date')
					n = n['%s' % (pcode)]
					inflow_d.update({pcode: n})

			
			if typ == 'm':
				if (sp_typ[1] == 'month') and (sp_nm[-1].split()[0] in slugtable.index):
					n = pd.read_fwf('%s/%s' % (fullpath, fn), header=None, widths=[12, 12, 13])
					n.columns = ['year', 'month', '%s' % (pcode)]
					mkdate = lambda x: datetime.date(int(x['year']), int(x['month']), 1)
					n['date'] = n.apply(mkdate, axis=1)
					n = n.set_index('date')
					n = n['%s' % (pcode)]
					inflow_d.update({pcode: n})

		c = pd.concat([j for j in inflow_d.values()], axis=1)
		self.inflow_o[basin][scen][typ] = c

		
	##########################################	

	def adjust_colo(self, scen, typ):

		self.inflow_o['hoover'][scen][typ]['154.0'] =  self.inflow_o['hoover'][scen][typ]['154.0'] + self.inflow_o['lees_f'][scen][typ]['153.0'] + self.inflow_o['little_col'][scen][typ]['-9999'] + self.inflow_o['gc'][scen][typ]['-9999'] +  self.inflow_o['virgin'][scen][typ]['-9999']

		self.inflow_o['hoover'][scen][typ]['8902.0'] =  self.inflow_o['hoover'][scen][typ]['8902.0'] + self.inflow_o['lees_f'][scen][typ]['153.0'] + self.inflow_o['little_col'][scen][typ]['-9999'] + self.inflow_o['gc'][scen][typ]['-9999'] +  self.inflow_o['virgin'][scen][typ]['-9999']

		self.inflow_o['davis'][scen][typ]['152.0'] =  self.inflow_o['davis'][scen][typ]['152.0'] + self.inflow_o['hoover'][scen][typ]['154.0']

		self.inflow_o['parker'][scen][typ]['447.0'] =  self.inflow_o['parker'][scen][typ]['447.0'] + self.inflow_o['davis'][scen][typ]['152.0']

		self.inflow_o['imperial'][scen][typ]['-9999'] =  self.inflow_o['imperial'][scen][typ]['-9999'] + self.inflow_o['parker'][scen][typ]['447.0'] + self.inflow_o['gila_imp'][scen][typ]['100.0'] 
	
	##########################################
	

	def make_regression(self, basin):
		
		self.p_dat.update({basin : {}})
		
		pkeys = self.inflow_o[basin]['hist']['d'].keys()
		
		p_dat = {}
		p_eqn = {}

		for i in pkeys:
			
			p_dat.update({i : {'power' : [], 'rout' : [], 'nameplate' : None}})

			for j in self.egrid.keys():
			
				year = int(j.split('_')[1])
				if int(ast.literal_eval(i)) in self.egrid[j]['ORISPL'].values:
					hy_p = self.egrid[j].set_index('ORISPL').loc[int(ast.literal_eval(i))]
					nameplate = float(hy_p['NAMEPCAP'])
					capfac = float(hy_p['CAPFAC'])
					if np.isnan(nameplate) == False and np.isnan(capfac) == False:
						if datetime.date(year, 1, 1) in self.inflow_o[basin]['hist']['d'][i].index:
							rout = self.inflow_o[basin]['hist']['d'][i].loc[datetime.date(year, 1, 1):datetime.date(year, 12, 31)].mean()
							print year, i, nameplate, nameplate*capfac, rout
							p_dat[i]['power'].append(nameplate*capfac)
							p_dat[i]['rout'].append(rout)
							p_dat[i]['nameplate'] = nameplate
			
			n = len(p_dat[i]['power'])
			x = np.asarray(p_dat[i]['rout'])
			x = x[:, np.newaxis]
			y = np.asarray(p_dat[i]['power'])
				
			a, _, _, _ = np.linalg.lstsq(x, y)
			yhat = x*a
			ybar = np.sum(y)/len(y)
			ssreg = np.sum((yhat - ybar)**2)
			sstot = np.sum((y - ybar)**2)

			err = ssreg / sstot
#			err = np.sqrt(sum((xr - y)**2)/n)
			
			p_eqn.update({ i : [x, y, a, err]})

#			(m,b) = polyfit(p_dat[i]['rout'], p_dat[i]['power'], 1)
#			xr = polyval([m,b], p_dat[i]['rout'])
#			rout_nona = [k for k in p_dat[i]['rout'] if np.isnan(k) == False]
#			power_nona = [k for k in p_dat[i]['power'] if np.isnan(k) == False]
#			n = min(len(rout_nona), len(power_nona))
#			err = np.sqrt(sum((xr - p_dat[i]['power'])**2)/n)
			
#			mn = xr.mean()
#			yerror = [xr - p_dat[i]['power']]/mn
				
#			print yerror
			
#			n = len(p_dat[i]['rout'])
#			x = np.asarray(p_dat[i]['rout'])
#			x = np.reshape(x, (n,1))
#			y = np.asarray(p_dat[i]['power'])

#			linmodel = linear_model.LinearRegression()
#			linmodel.fit(x, y)

#			model_ransac = linear_model.RANSACRegressor(linmodel)
#			model_ransac.fit(x, y)
#			inlier_mask = model_ransac.inlier_mask_
#			outlier_mask = np.logical_not(inlier_mask)


#			self.p_eqn.update({i : [np.reshape(x, (n,)), y, linmodel.coef_, np.reshape(model_ransac.estimator_.coef_, (1,)), inlier_mask, outlier_mask]})	

		self.p_dat[basin] = p_dat
		self.p_eqn[basin] = p_eqn

	def apply_regression(self, basin, scen, wpath):
		
		pkeys = self.inflow_o[basin][scen]['d'].keys() 
		
		if not os.path.exists(wpath):
			os.mkdir(wpath)

		for i in pkeys:
			wipath = wpath + '/' + scen + '.' + i.split('.')[0]
			df = self.inflow_o[basin][scen]['d'][i]
			power_cap = pd.Series(df*self.p_eqn[basin][i][2], name='POWER_CAP_MW')
			power_cap.loc[power_cap > self.p_dat[basin][i]['nameplate']] = self.p_dat[basin][i]['nameplate']
			ndf = pd.concat([df, power_cap], axis=1)
			ndf = ndf.reset_index()
			mkyear = lambda x: x['date'].year
			mkmonth = lambda x: x['date'].month
			mkday = lambda x: x['date'].day
			ndf['year'] = ndf.apply(mkyear, axis=1)
			ndf['month'] = ndf.apply(mkmonth, axis=1)
			ndf['day'] = ndf.apply(mkday, axis=1)
			ndf.to_csv(wipath, sep='\t')

	def plot_regression(self, basin, i, wpath):
		
		fig, ax = plt.subplots(1)
		xdata = self.p_eqn[basin][i][0]
		ydata = self.p_eqn[basin][i][1]
		a = float(self.p_eqn[basin][i][2][0])
		err = self.p_eqn[basin][i][3]

		ax.scatter(xdata, ydata)
		ax.plot(xdata, a*xdata)

		statname = self.latlon_c[basin].set_index('PCODE').loc[ast.literal_eval(i), 'PNAME']
		plt.title('EIA Plant %s, %s' % (i.split('.')[0], statname))
		plt.xlabel('Annual Average Streamflow (cfs)')
		plt.ylabel('Annual Average Power Generation (MW)')
		textstr = 'P = %.4f*Q\nCoef. of Det.: %.4f' % (a, err)
		props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
		ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top', linespacing=1.25, bbox=props)

		wbpath = wpath + '/' + basin
		if not basin in os.listdir(wpath):
			os.mkdir(wbpath)
		plt.savefig('%s/%s.png' % (wbpath, i.split('.')[0]), bbox_inches='tight')


'''
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
				

	def adjust_normalized(self):
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
'''
'''
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
'''


b = rout_post('/home/chesterlab/Bartos/VIC/input/dict/hydrostn.p','/home/chesterlab/Bartos/VIC/input/dict/egrid_plant.p')


#for fn in b.latlon_c.keys():

#	b.rout_tables(fn, 'hist', 'd', '/home/chesterlab/Bartos/VIC/output/rout/d8')

#b.adjust_colo('hist', 'd')

#b.make_regression('lees_f')

li = [i for i in b.latlon_c.keys() if not i in ['little_col', 'imperial', 'gc', 'virgin', 'paria', 'billw', 'lees_f']]

for fn in li:
	for s in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:
		b.rout_tables(fn, s, 'd','/home/chesterlab/Bartos/VIC/output/rout/d8')

	b.make_regression(fn)

	for s in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:
		b.apply_regression(fn, s, '/home/chesterlab/Bartos/post/hy/%s' % (fn))




####



li = [i for i in b.latlon_c.keys() if not i in ['little_col', 'imperial', 'gc', 'virgin', 'paria', 'billw']]
for fn in li:
	print fn
	b.make_regression(fn)

	for k in b.p_eqn[fn].keys():
		b.plot_regression(fn, k, '/home/chesterlab/Bartos/post/img/hydrostn_reg')

#scatter(b.p_eqn['153.0'][0], b.p_eqn['153.0'][1], color='b')
#scatter(b.p_eqn['153.0'][0][b.p_eqn['153.0'][4]], b.p_eqn['153.0'][1][b.p_eqn['153.0'][4]], color='g')

#plot(b.p_eqn['153.0'][0], [b.p_eqn['153.0'][2]*i for i in b.p_eqn['153.0'][0]])

#plot(b.p_eqn['153.0'][0], [b.p_eqn['153.0'][3]*i for i in b.p_eqn['153.0'][0]])



scatter(b.p_dat['lees_f']['521.0']['rout'], b.p_dat['lees_f']['521.0']['power'])
plot(b.p_dat['lees_f']['521.0']['rout'], [b.p_eqn['521.0'][0]*i for i in b.p_dat['lees_f']['521.0']['rout']])

#b.rout_tables('pitt', 'hist', 'd', '/home/chesterlab/Bartos/VIC/output/rout/d8')


#b.adjust_colo('hist', 'd')
#b.make_egrid('pitt')

################################################################################

################################################################

import numpy as np
import pandas as pd
from pylab import *
import os
import datetime

def post_plot(rpath, wpath, basin):

	li_1 = list(set([i.split('.')[1] for i in os.listdir(rpath)]))
	
	for pcode in li_1:
		li_2 = [i for i in os.listdir(rpath) if i.endswith(pcode)]

		d = {}

		for j in li_2:
			f = pd.read_csv('%s' % (rpath + '/' + j), sep='\t')
			d.update({j : f})

		g = d['hist.%s' % (pcode)].groupby(['month', 'day']).mean().reset_index()  # FOR RC some basins, OP, PV needs to be 'DAY' instead of day
		hist, = plot(g.index, g['POWER_CAP_MW'], label='historical')
		g = d['ukmo_a1b.%s' % (pcode)].groupby(['month', 'day']).mean().reset_index()
		ukmo_a1b, = plot(g.index, g['POWER_CAP_MW'], label='ukmo-a1b')
		g = d['ukmo_a2.%s' % (pcode)].groupby(['month', 'day']).mean().reset_index()
		ukmo_a2, = plot(g.index, g['POWER_CAP_MW'], label='ukmo-a2')
		g = d['ukmo_b1.%s' % (pcode)].groupby(['month', 'day']).mean().reset_index()
		ukmo_b1, = plot(g.index, g['POWER_CAP_MW'], label='ukmo-b1')
		g = d['echam_a1b.%s' % (pcode)].groupby(['month', 'day']).mean().reset_index()
		echam_a1b, = plot(g.index, g['POWER_CAP_MW'], label='echam-a1b')
		g = d['echam_a2.%s' % (pcode)].groupby(['month', 'day']).mean().reset_index()
		echam_a2, = plot(g.index, g['POWER_CAP_MW'], label='echam-a2')
		g = d['echam_b1.%s' % (pcode)].groupby(['month', 'day']).mean().reset_index()
		echam_b1, = plot(g.index, g['POWER_CAP_MW'], label='echam-b1')
	
		legend(loc=1)
	
		xlim([1,366])
		title('Average daily useable capacity at Station %s' % (pcode))
		xlabel('Day of year')
		ylabel('Useable capacity (MW)')
		
		wbpath = wpath + '/' + basin

		if not os.path.exists(wbpath):
			os.mkdir(wbpath)

		plt.savefig('%s/%s.png' % (wbpath, pcode), bbox_inches='tight')
		clf()

post_plot('/home/chesterlab/Bartos/post/hy/pitt', '/home/chesterlab/Bartos/post/img/hy', 'pitt')

################################################################################

li = [i for i in os.listdir('.') if i.endswith('153')]

d = {}

for j in li:
	f = pd.read_csv(j, sep='\t')
	d.update({j : f})

g = d['hist.153'].groupby(['month', 'day']).mean().reset_index()
hist, = plot(g.index, g['POWER_CAP_MW'], label='historical')
g = d['ukmo_a1b.153'].groupby(['month', 'day']).mean().reset_index()
ukmo_a1b, = plot(g.index, g['POWER_CAP_MW'], label='ukmo-a1b')
g = d['ukmo_a2.153'].groupby(['month', 'day']).mean().reset_index()
ukmo_a2, = plot(g.index, g['POWER_CAP_MW'], label='ukmo-a2')
g = d['ukmo_b1.153'].groupby(['month', 'day']).mean().reset_index()
ukmo_b1, = plot(g.index, g['POWER_CAP_MW'], label='ukmo-b1')
g = d['echam_a1b.153'].groupby(['month', 'day']).mean().reset_index()
echam_a1b, = plot(g.index, g['POWER_CAP_MW'], label='echam-a1b')
g = d['echam_a2.153'].groupby(['month', 'day']).mean().reset_index()
echam_a2, = plot(g.index, g['POWER_CAP_MW'], label='echam-a2')
g = d['echam_b1.153'].groupby(['month', 'day']).mean().reset_index()
echam_b1, = plot(g.index, g['POWER_CAP_MW'], label='echam-b1')

legend(loc=1)

xlim([1,366])
title('Average daily useable capacity at Glen Canyon Dam')
xlabel('Day of year')
ylabel('Useable capacity (MW)')




'''
def apply_regression(basin, scen, wpath):
		
	pkeys = b.inflow_o[basin][scen]['d'].keys() 

	for i in pkeys:
		wipath = wpath + '/' + scen + '.' + i.split('.')[0]
		df = b.inflow_o[basin][scen]['d'][i]
		power_cap = pd.Series(df*b.p_eqn[basin][i][2], name='POWER_CAP_MW')
		power_cap.loc[power_cap > b.p_dat[basin][i]['nameplate']] = b.p_dat[basin][i]['nameplate']
		ndf = pd.concat([df, power_cap], axis=1)
		ndf = ndf.reset_index()
		print ndf
		mkyear = lambda x: x['date'].year
		mkmonth = lambda x: x['date'].month
		mkday = lambda x: x['date'].day
		ndf['year'] = ndf.apply(mkyear, axis=1)
		ndf['month'] = ndf.apply(mkmonth, axis=1)
		ndf['day'] = ndf.apply(mkday, axis=1)
		ndf.to_csv(wipath, sep='\t')

for s in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:
	apply_regression('lees_f', s, '/home/chesterlab/Bartos/post/hy')'''
