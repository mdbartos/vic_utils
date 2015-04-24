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
	

	def make_regression(self, basin, intercept=False):
		
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

			if intercept == False:

				a, _, _, _ = np.linalg.lstsq(x, y)
				
				regarray = pd.Series(y)
				xser = pd.Series(x.flatten())
				print regarray, xser
				r = regarray.corr(xser)
				p_eqn.update({ i : [x, y, [a], r]})

			if intercept == True:

				a, b  = np.polyfit(np.asarray(p_dat[i]['rout']), y, 1)
				
				regarray = pd.Series(np.asarray(p_dat[i]['power']))
				xser = pd.Series(p_dat[i]['rout'])
				print regarray, xser
				r = regarray.corr(xser)
				p_eqn.update({ i : [x, y, [a, b], r]})

		self.p_dat[basin] = p_dat
		self.p_eqn[basin] = p_eqn

	def apply_regression(self, basin, scen, wpath):
		
		pkeys = self.inflow_o[basin][scen]['d'].keys() 
		
		if not os.path.exists(wpath):
			os.mkdir(wpath)

		for i in pkeys:
			wipath = wpath + '/' + scen + '.' + i.split('.')[0]
			df = self.inflow_o[basin][scen]['d'][i]
			if len(self.p_eqn[basin][i][2]) == 1:
				power_cap = pd.Series(df*self.p_eqn[basin][i][2][0], name='POWER_CAP_MW')
			elif len(self.p_eqn[basin][i][2]) == 2:
				power_cap = pd.Series(df*self.p_eqn[basin][i][2][0] + self.p_eqn[basin][i][2][1], name='POWER_CAP_MW')			
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
		print self.p_eqn[basin][i][2]
		a = float(self.p_eqn[basin][i][2][0])
		if len(self.p_eqn[basin][i][2]) > 1: 
			b = float(self.p_eqn[basin][i][2][1])
		r = self.p_eqn[basin][i][3]

		ax.scatter(xdata, ydata)

		if len(self.p_eqn[basin][i][2]) > 1: 
			ax.plot(xdata, a*xdata + b)
		else:
			ax.plot(xdata, a*xdata)


		statname = self.latlon_c[basin].set_index('PCODE').loc[ast.literal_eval(i), 'PNAME']
		plt.title('EIA Plant %s, %s' % (i.split('.')[0], statname))
		plt.xlabel('Annual Average Streamflow (cfs)')
		plt.ylabel('Annual Average Power Generation (MW)')	
		if len (self.p_eqn[basin][i][2]) > 1: 
			textstr = 'P = %.4f*Q+%.4f\nr = %.4f' % (a, b, r)
		else:
			textstr = 'P = %.4f*Q\nr = %.4f' % (a, r)
		props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
		ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top', linespacing=1.25, bbox=props)

		wbpath = wpath + '/' + basin
		if not basin in os.listdir(wpath):
			os.mkdir(wbpath)
		plt.savefig('%s/%s.png' % (wbpath, i.split('.')[0]), bbox_inches='tight')


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
