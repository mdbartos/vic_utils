import numpy as np
import pandas as pd
from pylab import *
import os
import datetime
import pickle

def post_plot_rc_sum(rpath, wpath, tech, typ):
	
	li_basin = os.listdir(rpath)
#	li_pcode = list(set([i.split('.')[1] for i in os.listdir(rpath)]))
	li_scen = ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']
	
	df_d = {}

	for scen in li_scen:
		df_d.update({scen : {}})

	for basin in li_basin:

		rbpath = rpath + '/' + basin
		b_d = {}
#		df_d.update({basin : {}})

		for scen in li_scen:
			li_2 = [i for i in os.listdir(rbpath) if i.split('.')[0] == scen]
	
			d = {}
	
			for j in li_2:
				
				jb = basin + '-' + j 

				f = pd.read_csv('%s' % (rpath + '/' + basin + '/' + j), sep='\t')
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
			df_d[j].update({basin : b_d[j]['BASIN_CAP']})

	for k in df_d.keys():
		print k
		print '\n'
		print df_d[k]
		df_d[k] = pd.concat(df_d[k].values(), axis=1)

	for i in df_d.keys():

		df_d[i]['SUM_CAP'] = df_d[i].sum(axis=1)
		df_d[i]['date'] = df_d[i].index
		df_d[i]['date'] = pd.to_datetime(df_d[i]['date'])
		mkyear = lambda x: x['date'].year
		mkmonth = lambda x: x['date'].month
		mkday = lambda x: x['date'].day
		df_d[i]['YEAR'] = df_d[i].apply(mkyear, axis=1)
		df_d[i]['MONTH'] = df_d[i].apply(mkmonth, axis=1)
		df_d[i]['DAY'] = df_d[i].apply(mkday, axis=1)
		df_d[i] = df_d[i][['YEAR', 'MONTH', 'DAY', 'SUM_CAP']]
		print df_d[i]

	if typ == 'annual':

		g = df_d['hist'].groupby(['MONTH', 'DAY']).mean().reset_index() 
		hist, = plot(g.index, g['SUM_CAP'], label='historical')
		g = df_d['ukmo_a1b'].groupby(['MONTH', 'DAY']).mean().reset_index()
		ukmo_a1b, = plot(g.index, g['SUM_CAP'], label='ukmo-a1b')
		g = df_d['ukmo_a2'].groupby(['MONTH', 'DAY']).mean().reset_index()
		ukmo_a2, = plot(g.index, g['SUM_CAP'], label='ukmo-a2')
		g = df_d['ukmo_b1'].groupby(['MONTH', 'DAY']).mean().reset_index()
		ukmo_b1, = plot(g.index, g['SUM_CAP'], label='ukmo-b1')
		g = df_d['echam_a1b'].groupby(['MONTH', 'DAY']).mean().reset_index()
		echam_a1b, = plot(g.index, g['SUM_CAP'], label='echam-a1b')
		g = df_d['echam_a2'].groupby(['MONTH', 'DAY']).mean().reset_index()
		echam_a2, = plot(g.index, g['SUM_CAP'], label='echam-a2')
		g = df_d['echam_b1'].groupby(['MONTH', 'DAY']).mean().reset_index()
		echam_b1, = plot(g.index, g['SUM_CAP'], label='echam-b1')

#		legend(loc=3)

		xlim([1,366])
		title('Average daily useable %s capacity' % (tech))
		xlabel('Day of year')
		ylabel('Useable capacity (MW)')

	if typ == 'century':

		g = df_d['hist'].groupby('YEAR').mean().reset_index() 
		hist, = plot(g['YEAR'], g['SUM_CAP'], label='historical')
		g = df_d['ukmo_a1b'].groupby('YEAR').mean().reset_index()
		ukmo_a1b, = plot(g['YEAR'], g['SUM_CAP'], label='ukmo-a1b')
		g = df_d['ukmo_a2'].groupby('YEAR').mean().reset_index()
		ukmo_a2, = plot(g['YEAR'], g['SUM_CAP'], label='ukmo-a2')
		g = df_d['ukmo_b1'].groupby('YEAR').mean().reset_index()
		ukmo_b1, = plot(g['YEAR'], g['SUM_CAP'], label='ukmo-b1')
		g = df_d['echam_a1b'].groupby('YEAR').mean().reset_index()
		echam_a1b, = plot(g['YEAR'], g['SUM_CAP'], label='echam-a1b')
		g = df_d['echam_a2'].groupby('YEAR').mean().reset_index()
		echam_a2, = plot(g['YEAR'], g['SUM_CAP'], label='echam-a2')
		g = df_d['echam_b1'].groupby('YEAR').mean().reset_index()
		echam_b1, = plot(g['YEAR'], g['SUM_CAP'], label='echam-b1')

#		legend(loc=3)

		xlim([1950, 2090])
		axvline(x=2010, linestyle='--', color='black')
		title('Average daily useable %s capacity' % (tech))
		xlabel('Year')
		ylabel('Useable capacity (MW)')

	if typ == 'period':
		for scen in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:
		
			a = df_d[scen]['SUM_CAP']
			max_val = a.max()
			len_a = len(a)
			b = (max_val - a)/max_val
			c = b.order(ascending=False) #.reset_index()
			ep = c.rank(method='min', ascending=False)/(1+len(a))
			t = (1/ep)/365
			plot(t, c*100, label=scen)
		legend(loc=4)
		
		xlim([0,50])
		title('Reductions in Useable %s Capacity' % (tech))
		xlabel('Return Period (years)')
		ylabel('Percent Reduction in Useable Capacity (%)')

	if not os.path.exists(wpath):
		os.mkdir(wpath)

	plt.savefig('%s/%s.png' % (wpath, tech), bbox_inches='tight')
	clf()

def post_plot_hy_sum(rpath, wpath, tech, typ):
	
	li_basin = os.listdir(rpath)
#	li_pcode = list(set([i.split('.')[1] for i in os.listdir(rpath)]))
	li_scen = ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']
	
	df_d = {}

	for scen in li_scen:
		df_d.update({scen : {}})

	for basin in li_basin:

		rbpath = rpath + '/' + basin
		b_d = {}
#		df_d.update({basin : {}})

		for scen in li_scen:
			li_2 = [i for i in os.listdir(rbpath) if i.split('.')[0] == scen]
	
			d = {}
	
			for j in li_2:
				
				jb = basin + '-' + j 

				f = pd.read_csv('%s' % (rpath + '/' + basin + '/' + j), sep='\t')
				if 'date' in f.columns:
					f = f.dropna(subset=['date'])
					f = f.set_index('date')
	#				f = f['POWER_CAP_MW']
				else:
					mkdate =  lambda x: datetime.date(int(x['YEAR']), int(x['MONTH']), int(x['DAY']))
					f['date'] = f.apply(mkdate, axis=1) 
					f = f.set_index('date')
	#				f = f['POWER_CAP_MW']
	
				d.update({jb : f})
		
			scen_df = pd.concat([d[i]['POWER_CAP_MW'] for i in d.keys()], axis=1)
			print scen_df
			b_d.update({scen : scen_df})
		
		for j in b_d.keys():
			b_d[j]['BASIN_CAP'] = b_d[j].sum(axis=1)
			df_d[j].update({basin : b_d[j]['BASIN_CAP']})

	for k in df_d.keys():
		print k
		print '\n'
		print df_d[k]
		df_d[k] = pd.concat(df_d[k].values(), axis=1)

	for i in df_d.keys():

		df_d[i]['SUM_CAP'] = df_d[i].sum(axis=1)
		df_d[i]['date'] = df_d[i].index
		df_d[i]['date'] = pd.to_datetime(df_d[i]['date'])
		mkyear = lambda x: x['date'].year
		mkmonth = lambda x: x['date'].month
		mkday = lambda x: x['date'].day
		df_d[i]['YEAR'] = df_d[i].apply(mkyear, axis=1)
		df_d[i]['MONTH'] = df_d[i].apply(mkmonth, axis=1)
		df_d[i]['DAY'] = df_d[i].apply(mkday, axis=1)
		df_d[i] = df_d[i][['YEAR', 'MONTH', 'DAY', 'SUM_CAP']]
		print df_d[i]

	if typ == 'annual':

		g = df_d['hist'].groupby(['MONTH', 'DAY']).mean().reset_index() 
		hist, = plot(g.index, g['SUM_CAP'], label='historical')
		g = df_d['ukmo_a1b'].groupby(['MONTH', 'DAY']).mean().reset_index()
		ukmo_a1b, = plot(g.index, g['SUM_CAP'], label='ukmo-a1b')
		g = df_d['ukmo_a2'].groupby(['MONTH', 'DAY']).mean().reset_index()
		ukmo_a2, = plot(g.index, g['SUM_CAP'], label='ukmo-a2')
		g = df_d['ukmo_b1'].groupby(['MONTH', 'DAY']).mean().reset_index()
		ukmo_b1, = plot(g.index, g['SUM_CAP'], label='ukmo-b1')
		g = df_d['echam_a1b'].groupby(['MONTH', 'DAY']).mean().reset_index()
		echam_a1b, = plot(g.index, g['SUM_CAP'], label='echam-a1b')
		g = df_d['echam_a2'].groupby(['MONTH', 'DAY']).mean().reset_index()
		echam_a2, = plot(g.index, g['SUM_CAP'], label='echam-a2')
		g = df_d['echam_b1'].groupby(['MONTH', 'DAY']).mean().reset_index()
		echam_b1, = plot(g.index, g['SUM_CAP'], label='echam-b1')

#		legend(loc=3)

		xlim([1,366])
		title('Average daily useable %s capacity' % (tech))
		xlabel('Day of year')
		ylabel('Useable capacity (MW)')

	if typ == 'century':

		g = df_d['hist'].groupby('YEAR').mean().reset_index() 
		hist, = plot(g['YEAR'], g['SUM_CAP'], label='historical')
		g = df_d['ukmo_a1b'].groupby('YEAR').mean().reset_index()
		ukmo_a1b, = plot(g['YEAR'], g['SUM_CAP'], label='ukmo-a1b')
		g = df_d['ukmo_a2'].groupby('YEAR').mean().reset_index()
		ukmo_a2, = plot(g['YEAR'], g['SUM_CAP'], label='ukmo-a2')
		g = df_d['ukmo_b1'].groupby('YEAR').mean().reset_index()
		ukmo_b1, = plot(g['YEAR'], g['SUM_CAP'], label='ukmo-b1')
		g = df_d['echam_a1b'].groupby('YEAR').mean().reset_index()
		echam_a1b, = plot(g['YEAR'], g['SUM_CAP'], label='echam-a1b')
		g = df_d['echam_a2'].groupby('YEAR').mean().reset_index()
		echam_a2, = plot(g['YEAR'], g['SUM_CAP'], label='echam-a2')
		g = df_d['echam_b1'].groupby('YEAR').mean().reset_index()
		echam_b1, = plot(g['YEAR'], g['SUM_CAP'], label='echam-b1')

#		legend(loc=3)

		xlim([1950, 2090])
		axvline(x=2010, linestyle='--', color='black')
		title('Average daily useable %s capacity' % (tech))
		xlabel('Year')
		ylabel('Useable capacity (MW)')

	if typ == 'period':
		for scen in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:
			
			a = df_d[scen].groupby('YEAR').mean()

			a = a['SUM_CAP']
			max_val = a.max()
			len_a = len(a)

			b = (max_val - a)/max_val
			c = b.order(ascending=False) #.reset_index()
			ep = c.rank(method='min', ascending=False)/(1+len(a))
			t = (1/ep)
			plot(t, c*100, label=scen)
		legend(loc=4)
		
		xlim([0,50])
		title('Reductions in Useable %s Capacity' % (tech))
		xlabel('Return Period (years)')
		ylabel('Percent Reduction in Useable Capacity (%)')

	if not os.path.exists(wpath):
		os.mkdir(wpath)

	plt.savefig('%s/%s.png' % (wpath, tech), bbox_inches='tight')
	clf()

def indiv_ep_plot(pcode):
	for scen in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:
		df = pd.read_csv('%s.%s' % (scen, pcode), sep='\t')
	
		a = df['POWER_CAP_MW']
		max_val = a.max()
		len_a = len(a)
	
		b = (max_val - df['POWER_CAP_MW'])/max_val
		c = b.order(ascending=False) #.reset_index()
		ep = c.rank(method='min', ascending=False)/(1+len(a))
		t = (1/ep)/365
		plot(t, c*100, label=scen)
	
	legend(loc=4)
		
	xlim([0,50])
	title('Reductions in Useable Capacity at Station %s' % (pcode))
	xlabel('Return Period (years)')
	ylabel('Percent Reduction in Useable Capacity (%)')


def indiv_ep_plot_hy(pcode):
	for scen in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:
		df = pd.read_csv('%s.%s' % (scen, pcode), sep='\t').groupby('year').mean()

		a = df['POWER_CAP_MW']
		max_val = a.max()
		len_a = len(a)
	
		b = (max_val - df['POWER_CAP_MW'])/max_val
		c = b.order(ascending=False) #.reset_index()
		ep = c.rank(method='min', ascending=False)/(1+len(a))
		t = (1/ep)
		plot(t, c*100, label=scen)
	
	legend(loc=4)
		
	xlim([0,50])
	title('Reductions in Useable Capacity at Station %s' % (pcode))
	xlabel('Return Period (years)')
	ylabel('Percent Reduction in Useable Capacity (%)')


class post_plot_rc_region():
	
	def __init__(self, rpath, wpath, tech, typ, post_pp_d_path):
		self.rpath = rpath
		self.wpath = wpath
		self.tech = tech
		self.typ = typ
		self.li_basin = os.listdir(rpath)
		self.li_scen = ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']
		self.post_pp_d = pickle.load(open(post_pp_d_path, 'rb'))		
	
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
	
		df_d = self.reg_df_d[wreg]

		if self.typ == 'pickle':
			pickle.dump( df_d, open( '%s/region_rc_%s' % (self.wpath, wreg), 'wb')) 

		if self.typ == 'annual':
	
			g = df_d['hist'].groupby(['MONTH', 'DAY']).mean().reset_index() 
			hist, = plot(g.index, g['SUM_CAP'], label='historical')
			g = df_d['ukmo_a1b'].groupby(['MONTH', 'DAY']).mean().reset_index()
			ukmo_a1b, = plot(g.index, g['SUM_CAP'], label='ukmo-a1b')
			g = df_d['ukmo_a2'].groupby(['MONTH', 'DAY']).mean().reset_index()
			ukmo_a2, = plot(g.index, g['SUM_CAP'], label='ukmo-a2')
			g = df_d['ukmo_b1'].groupby(['MONTH', 'DAY']).mean().reset_index()
			ukmo_b1, = plot(g.index, g['SUM_CAP'], label='ukmo-b1')
			g = df_d['echam_a1b'].groupby(['MONTH', 'DAY']).mean().reset_index()
			echam_a1b, = plot(g.index, g['SUM_CAP'], label='echam-a1b')
			g = df_d['echam_a2'].groupby(['MONTH', 'DAY']).mean().reset_index()
			echam_a2, = plot(g.index, g['SUM_CAP'], label='echam-a2')
			g = df_d['echam_b1'].groupby(['MONTH', 'DAY']).mean().reset_index()
			echam_b1, = plot(g.index, g['SUM_CAP'], label='echam-b1')
	
	#		legend(loc=3)
	
			xlim([1,366])
			title('Average daily useable %s capacity' % (self.tech))
			xlabel('Day of year')
			ylabel('Useable capacity (MW)')

		if self.typ == 'annual_fill':
	
			comb = pd.concat([self.reg_df_d[wreg][i] for i in self.reg_df_d[wreg].keys() if not 'hist' in i], axis=1)['SUM_CAP']
			hist = self.reg_df_d[wreg]['hist'].groupby(['MONTH', 'DAY']).mean().reset_index()

			a1b = pd.DataFrame(pd.concat([self.reg_df_d[wreg][i] for i in self.reg_df_d[wreg].keys() if 'a1b' in i], axis=1)['SUM_CAP'].mean(axis=1))

			a2 = pd.DataFrame(pd.concat([self.reg_df_d[wreg][i] for i in self.reg_df_d[wreg].keys() if 'a2' in i], axis=1)['SUM_CAP'].mean(axis=1))	
			
			b1 = pd.DataFrame(pd.concat([self.reg_df_d[wreg][i] for i in self.reg_df_d[wreg].keys() if 'b1' in i], axis=1)['SUM_CAP'].mean(axis=1))


			comb['MONTH'] = [i.month for i in comb.index]
			comb['DAY'] = [i.day for i in comb.index]
			comb = comb.groupby(['MONTH', 'DAY']).mean()

			a1b['MONTH'] = [i.month for i in a1b.index]
			a1b['DAY'] = [i.day for i in a1b.index]
			a1b = a1b.groupby(['MONTH', 'DAY']).mean().reset_index()[0]

			a2['MONTH'] = [i.month for i in a2.index]
			a2['DAY'] = [i.day for i in a2.index]
			a2 = a2.groupby(['MONTH', 'DAY']).mean().reset_index()[0]

			b1['MONTH'] = [i.month for i in b1.index]
			b1['DAY'] = [i.day for i in b1.index]
			b1 = b1.groupby(['MONTH', 'DAY']).mean().reset_index()[0]

			print comb

			comb['max'] = comb.max(axis=1)
			comb['min'] = comb.min(axis=1)
			comb = comb.reset_index()

			print comb

			x = comb.index
			y_upper = pd.rolling_mean(comb['max'], 14).fillna(comb['max']).values
			y_lower = pd.rolling_mean(comb['min'], 14).fillna(comb['min']).values

			plt.fill_between(x, y_upper, y_lower, facecolor="0.85", linewidth=0)
			plt.plot(hist.index, pd.rolling_mean(hist['SUM_CAP'], 14).fillna(hist), color='black', label='hist')
			plt.plot(a1b.index, pd.rolling_mean(a1b, 14).fillna(a1b), color='royalblue', label='a1b')
			plt.plot(a2.index, pd.rolling_mean(a2, 14).fillna(a2), color='midnightblue', label='a2')
			plt.plot(b1.index, pd.rolling_mean(b1, 14).fillna(b1), color='lightskyblue', label='b1')

			xlim([1,366])
			title('%s' % (wreg))
			xlabel('Day of year')
			ylabel('Useable capacity (MW)')
			plt.legend(loc=4)

		if self.typ == 'century':
	
			g = df_d['hist'].groupby('YEAR').mean().reset_index() 
			hist, = plot(g['YEAR'], g['SUM_CAP'], label='historical')
			g = df_d['ukmo_a1b'].groupby('YEAR').mean().reset_index()
			ukmo_a1b, = plot(g['YEAR'], g['SUM_CAP'], label='ukmo-a1b')
			g = df_d['ukmo_a2'].groupby('YEAR').mean().reset_index()
			ukmo_a2, = plot(g['YEAR'], g['SUM_CAP'], label='ukmo-a2')
			g = df_d['ukmo_b1'].groupby('YEAR').mean().reset_index()
			ukmo_b1, = plot(g['YEAR'], g['SUM_CAP'], label='ukmo-b1')
			g = df_d['echam_a1b'].groupby('YEAR').mean().reset_index()
			echam_a1b, = plot(g['YEAR'], g['SUM_CAP'], label='echam-a1b')
			g = df_d['echam_a2'].groupby('YEAR').mean().reset_index()
			echam_a2, = plot(g['YEAR'], g['SUM_CAP'], label='echam-a2')
			g = df_d['echam_b1'].groupby('YEAR').mean().reset_index()
			echam_b1, = plot(g['YEAR'], g['SUM_CAP'], label='echam-b1')
	
	#		legend(loc=3)
	
			xlim([1950, 2090])
			axvline(x=2010, linestyle='--', color='black')
			title('Average daily useable %s capacity' % (self.tech))
			xlabel('Year')
			ylabel('Useable capacity (MW)')
	
		if self.typ == 'period':
			for scen in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:
			
				a = df_d[scen]['SUM_CAP']
				max_val = a.max()
				len_a = len(a)
				b = (max_val - a) #/max_val
				c = b.order(ascending=False) #.reset_index()
				ep = c.rank(method='min', ascending=False)/(1+len(a))
				t = (1/ep)/365
				plot(t, c, label=scen)
			legend(loc=4)
			
			xlim([0,50])
			title('Reductions in Useable %s Capacity' % (self.tech))
			xlabel('Return Period (years)')
			ylabel('Reduction in Useable Capacity')
	
		if not os.path.exists(self.wpath):
			os.mkdir(self.wpath)
	
#UNCOMMENT THIS		plt.savefig('%s/%s.png' % (self.wpath, wreg), bbox_inches='tight')
#		clf()

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

		df_d = self.reg_df_d[wreg]

		if self.typ == 'annual':
	
			g = df_d['hist'].groupby(['MONTH', 'DAY']).mean().reset_index() 
			hist, = plot(g.index, g['SUM_CAP'], label='historical')
			g = df_d['ukmo_a1b'].groupby(['MONTH', 'DAY']).mean().reset_index()
			ukmo_a1b, = plot(g.index, g['SUM_CAP'], label='ukmo-a1b')
			g = df_d['ukmo_a2'].groupby(['MONTH', 'DAY']).mean().reset_index()
			ukmo_a2, = plot(g.index, g['SUM_CAP'], label='ukmo-a2')
			g = df_d['ukmo_b1'].groupby(['MONTH', 'DAY']).mean().reset_index()
			ukmo_b1, = plot(g.index, g['SUM_CAP'], label='ukmo-b1')
			g = df_d['echam_a1b'].groupby(['MONTH', 'DAY']).mean().reset_index()
			echam_a1b, = plot(g.index, g['SUM_CAP'], label='echam-a1b')
			g = df_d['echam_a2'].groupby(['MONTH', 'DAY']).mean().reset_index()
			echam_a2, = plot(g.index, g['SUM_CAP'], label='echam-a2')
			g = df_d['echam_b1'].groupby(['MONTH', 'DAY']).mean().reset_index()
			echam_b1, = plot(g.index, g['SUM_CAP'], label='echam-b1')
	
	#		legend(loc=3)
	
			xlim([1,366])
			title('Average daily useable %s capacity' % (self.tech))
			xlabel('Day of year')
			ylabel('Useable capacity (MW)')
	
		if self.typ == 'century':
	
			g = df_d['hist'].groupby('YEAR').mean().reset_index() 
			hist, = plot(g['YEAR'], g['SUM_CAP'], label='historical')
			g = df_d['ukmo_a1b'].groupby('YEAR').mean().reset_index()
			ukmo_a1b, = plot(g['YEAR'], g['SUM_CAP'], label='ukmo-a1b')
			g = df_d['ukmo_a2'].groupby('YEAR').mean().reset_index()
			ukmo_a2, = plot(g['YEAR'], g['SUM_CAP'], label='ukmo-a2')
			g = df_d['ukmo_b1'].groupby('YEAR').mean().reset_index()
			ukmo_b1, = plot(g['YEAR'], g['SUM_CAP'], label='ukmo-b1')
			g = df_d['echam_a1b'].groupby('YEAR').mean().reset_index()
			echam_a1b, = plot(g['YEAR'], g['SUM_CAP'], label='echam-a1b')
			g = df_d['echam_a2'].groupby('YEAR').mean().reset_index()
			echam_a2, = plot(g['YEAR'], g['SUM_CAP'], label='echam-a2')
			g = df_d['echam_b1'].groupby('YEAR').mean().reset_index()
			echam_b1, = plot(g['YEAR'], g['SUM_CAP'], label='echam-b1')
	
	#		legend(loc=3)
	
			xlim([1950, 2090])
			axvline(x=2010, linestyle='--', color='black')
			title('Average daily useable %s capacity' % (self.tech))
			xlabel('Year')
			ylabel('Useable capacity (MW)')
	
		if self.typ == 'period':
			for scen in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:
			
				a = df_d[scen]['SUM_CAP']
				max_val = a.max()
				len_a = len(a)
				b = (max_val - a) #/max_val
				c = b.order(ascending=False) #.reset_index()
				ep = c.rank(method='min', ascending=False)/(1+len(a))
				t = (1/ep)/365
				plot(t, c, label=scen)
			legend(loc=4)
			
			xlim([0,50])
			title('Reductions in Useable %s Capacity' % (self.tech))
			xlabel('Return Period (years)')
			ylabel('Reduction in Useable Capacity')
	
		if not os.path.exists(self.wpath):
			os.mkdir(self.wpath)
	
		plt.savefig('%s/%s.png' % (self.wpath, wreg), bbox_inches='tight')
		clf()



class post_plot_hy_region():
	
	def __init__(self, rpath, wpath, tech, typ):
		self.rpath = rpath
		self.wpath = wpath
		self.tech = tech
		self.typ = typ
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
	
		df_d = self.reg_df_d[wreg]

		if self.typ == 'annual':
	
			g = df_d['hist'].groupby(['MONTH', 'DAY']).mean().reset_index() 
			hist, = plot(g.index, g['SUM_CAP'], label='historical')
			g = df_d['ukmo_a1b'].groupby(['MONTH', 'DAY']).mean().reset_index()
			ukmo_a1b, = plot(g.index, g['SUM_CAP'], label='ukmo-a1b')
			g = df_d['ukmo_a2'].groupby(['MONTH', 'DAY']).mean().reset_index()
			ukmo_a2, = plot(g.index, g['SUM_CAP'], label='ukmo-a2')
			g = df_d['ukmo_b1'].groupby(['MONTH', 'DAY']).mean().reset_index()
			ukmo_b1, = plot(g.index, g['SUM_CAP'], label='ukmo-b1')
			g = df_d['echam_a1b'].groupby(['MONTH', 'DAY']).mean().reset_index()
			echam_a1b, = plot(g.index, g['SUM_CAP'], label='echam-a1b')
			g = df_d['echam_a2'].groupby(['MONTH', 'DAY']).mean().reset_index()
			echam_a2, = plot(g.index, g['SUM_CAP'], label='echam-a2')
			g = df_d['echam_b1'].groupby(['MONTH', 'DAY']).mean().reset_index()
			echam_b1, = plot(g.index, g['SUM_CAP'], label='echam-b1')
	
	#		legend(loc=3)
	
			xlim([1,366])
			title('Average daily useable %s capacity' % (self.tech))
			xlabel('Day of year')
			ylabel('Useable capacity (MW)')
	
		if self.typ == 'century':
	
			g = df_d['hist'].groupby('YEAR').mean().reset_index() 
			hist, = plot(g['YEAR'], g['SUM_CAP'], label='historical')
			g = df_d['ukmo_a1b'].groupby('YEAR').mean().reset_index()
			ukmo_a1b, = plot(g['YEAR'], g['SUM_CAP'], label='ukmo-a1b')
			g = df_d['ukmo_a2'].groupby('YEAR').mean().reset_index()
			ukmo_a2, = plot(g['YEAR'], g['SUM_CAP'], label='ukmo-a2')
			g = df_d['ukmo_b1'].groupby('YEAR').mean().reset_index()
			ukmo_b1, = plot(g['YEAR'], g['SUM_CAP'], label='ukmo-b1')
			g = df_d['echam_a1b'].groupby('YEAR').mean().reset_index()
			echam_a1b, = plot(g['YEAR'], g['SUM_CAP'], label='echam-a1b')
			g = df_d['echam_a2'].groupby('YEAR').mean().reset_index()
			echam_a2, = plot(g['YEAR'], g['SUM_CAP'], label='echam-a2')
			g = df_d['echam_b1'].groupby('YEAR').mean().reset_index()
			echam_b1, = plot(g['YEAR'], g['SUM_CAP'], label='echam-b1')
	
	#		legend(loc=3)
	
			xlim([1950, 2090])
			axvline(x=2010, linestyle='--', color='black')
			title('Average daily useable %s capacity' % (self.tech))
			xlabel('Year')
			ylabel('Useable capacity (MW)')
	
		if self.typ == 'period':
			for scen in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:
				df = df_d[scen].groupby('YEAR').mean()	
				a = df['SUM_CAP']
				max_val = df_d[scen]['SUM_CAP'].max()
				len_a = len(a)
				b = (max_val - a)/max_val
				c = b.order(ascending=False) #.reset_index()
				ep = c.rank(method='min', ascending=False)/(1+len(a))
				t = (1/ep)
				plot(t, c, label=scen)
			legend(loc=4)
			
			xlim([0,50])
			title('Reductions in Useable %s Capacity' % (self.tech))
			xlabel('Return Period (years)')
			ylabel('Reduction in Useable Capacity')
	
		if not os.path.exists(self.wpath):
			os.mkdir(self.wpath)
	
		plt.savefig('%s/%s.png' % (self.wpath, wreg), bbox_inches='tight')
		clf()

#b = post_plot_hy_region('/home/chesterlab/Bartos/post/hy', '/home/chesterlab/Bartos/post/img/reg', 'hy', 'period')
#b = post_plot_hy_region('/home/chesterlab/Bartos/post/hy', '/home/chesterlab/Bartos/post/img/reg', 'hy', 'century')
b = post_plot_hy_region('/home/chesterlab/Bartos/post/hy', '/home/chesterlab/Bartos/post/img/reg', 'hy', 'annual')

for v in b.reg_basins.keys():
	b.plot_region(v)


b = post_plot_rc_region('/home/chesterlab/Bartos/post/rc', '/home/chesterlab/Bartos/post/img/reg', 'rc', 'annual_fill', '/home/chesterlab/Bartos/VIC/input/dict/post_pp_d.p')

b = post_plot_rc_region('/home/chesterlab/Bartos/post/op', '/home/chesterlab/Bartos/post/img/reg', 'op', 'period', '/home/chesterlab/Bartos/VIC/input/dict/post_pp_d.p')

for v in b.reg_d.keys():
	b.plot_op_region(v)

b = post_plot_rc_region('/home/chesterlab/Bartos/post/ct', '/home/chesterlab/Bartos/post/img/reg', 'ct', 'period', '/home/chesterlab/Bartos/VIC/input/dict/post_pp_d.p')

b = post_plot_rc_region('/home/chesterlab/Bartos/post/wn', '/home/chesterlab/Bartos/post/img/reg', 'wn', 'annual', '/home/chesterlab/Bartos/VIC/input/dict/post_pp_d.p')

b = post_plot_rc_region('/home/chesterlab/Bartos/post/rc', '/home/chesterlab/Bartos/post/img/reg', 'rc', 'annual', '/home/chesterlab/Bartos/VIC/input/dict/post_pp_d.p')
b.prep_reg_basins()

reg_list = [i for i in b.reg_basin_d.keys() if i != 'rio']

for v in reg_list:
	b.plot_region(v)


# SUM ALL REGIONS

import numpy as np
import pandas as pd
from pylab import *
import os
import datetime
import pickle

class sum_regions():
	def __init__(self):
		self.ct = pickle.load(open('/home/chesterlab/Bartos/post/d/ct_region.p', 'rb')) 
		self.rc = pickle.load(open('/home/chesterlab/Bartos/post/d/rc_region.p', 'rb'))
		self.op = pickle.load(open('/home/chesterlab/Bartos/post/d/op_region.p', 'rb'))
		self.hy = pickle.load(open('/home/chesterlab/Bartos/post/d/hy_region.p', 'rb'))
		self.pv = pickle.load(open('/home/chesterlab/Bartos/post/d/pv_region.p', 'rb')) 
		self.wn = pickle.load(open('/home/chesterlab/Bartos/post/d/wn_region.p', 'rb'))  	
		self.hy['crb'] = self.hy['pnw']
		del self.hy['pnw']
		
		self.regs = ['color', 'mo', 'crb', 'cali', 'grb', 'ark']
		self.tech_d = {'ct' : self.ct, 'rc' : self.rc, 'op' : self.op, 'hy' : self.hy, 'pv' : self.pv, 'wn' : self.wn}
		
		self.df_d = {}
		self.reg_techs = {}
	
	def fix_hydro(self):
		for i in self.tech_d['hy'].keys():
			for j in self.tech_d['hy'][i].keys():
				g = self.tech_d['hy'][i][j].groupby('YEAR').mean()
				for h in g.index:
					self.tech_d['hy'][i][j].loc[self.tech_d['hy'][i][j]['YEAR'] == h, 'SUM_CAP'] = g.loc[h, 'SUM_CAP']
	def fix_indices(self):
		for i in self.tech_d.keys():
			for j in self.tech_d[i].keys():
				for k in self.tech_d[i][j].keys():
					self.tech_d[i][j][k].index = pd.to_datetime(self.tech_d[i][j][k].index)

	def prep_tables(self):
		for i in self.regs:
			self.df_d.update({i : {}})
			self.reg_techs.update({i : []})
			for j in self.tech_d.keys():
				if i in self.tech_d[j].keys():
					self.reg_techs[i].append(j)

		for i in self.reg_techs.keys():
			for scen in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:
				scen_li = [self.tech_d[k][i][scen]['SUM_CAP'] for k in self.reg_techs[i]]
				scen_df = pd.concat(scen_li, axis=1)
				scen_df['REG_CAP'] = scen_df.sum(axis=1)
				if scen == 'hist':
					scen_df = scen_df.loc[:datetime.date(2009, 12, 31)]
				else:
					scen_df = scen_df.loc[:datetime.date(2090, 12, 31)]	
				self.df_d[i].update({scen : scen_df['REG_CAP']})

	def plot_sum(self, wreg, typ, wpath):
		
		df_d = self.df_d[wreg]

		for i in df_d.keys():
			df_d[i] = pd.DataFrame(df_d[i])	
			df_d[i]['date'] = df_d[i].index
			df_d[i]['date'] = pd.to_datetime(df_d[i]['date'])
			mkyear = lambda x: x['date'].year
			mkmonth = lambda x: x['date'].month
			mkday = lambda x: x['date'].day
			df_d[i]['YEAR'] = df_d[i].apply(mkyear, axis=1)
			df_d[i]['MONTH'] = df_d[i].apply(mkmonth, axis=1)
			df_d[i]['DAY'] = df_d[i].apply(mkday, axis=1)
			df_d[i] = df_d[i][['YEAR', 'MONTH', 'DAY', 'REG_CAP']]
			print df_d[i]

		if typ == 'annual':
	
			g = df_d['hist'].groupby(['MONTH', 'DAY']).mean().reset_index() 
			hist, = plot(g.index, g['REG_CAP'], label='historical')
			g = df_d['ukmo_a1b'].groupby(['MONTH', 'DAY']).mean().reset_index()
			ukmo_a1b, = plot(g.index, g['REG_CAP'], label='ukmo-a1b')
			g = df_d['ukmo_a2'].groupby(['MONTH', 'DAY']).mean().reset_index()
			ukmo_a2, = plot(g.index, g['REG_CAP'], label='ukmo-a2')
			g = df_d['ukmo_b1'].groupby(['MONTH', 'DAY']).mean().reset_index()
			ukmo_b1, = plot(g.index, g['REG_CAP'], label='ukmo-b1')
			g = df_d['echam_a1b'].groupby(['MONTH', 'DAY']).mean().reset_index()
			echam_a1b, = plot(g.index, g['REG_CAP'], label='echam-a1b')
			g = df_d['echam_a2'].groupby(['MONTH', 'DAY']).mean().reset_index()
			echam_a2, = plot(g.index, g['REG_CAP'], label='echam-a2')
			g = df_d['echam_b1'].groupby(['MONTH', 'DAY']).mean().reset_index()
			echam_b1, = plot(g.index, g['REG_CAP'], label='echam-b1')
	
			legend(loc=3)
	
			xlim([1,366])
			title('%s' % (wreg))
			xlabel('Day of year')
			ylabel('Useable capacity (MW)')
	
		if typ == 'century':
	
			g = df_d['hist'].groupby('YEAR').mean().reset_index() 
			hist, = plot(g['YEAR'], g['REG_CAP'], label='historical')
			g = df_d['ukmo_a1b'].groupby('YEAR').mean().reset_index()
			ukmo_a1b, = plot(g['YEAR'], g['REG_CAP'], label='ukmo-a1b')
			g = df_d['ukmo_a2'].groupby('YEAR').mean().reset_index()
			ukmo_a2, = plot(g['YEAR'], g['REG_CAP'], label='ukmo-a2')
			g = df_d['ukmo_b1'].groupby('YEAR').mean().reset_index()
			ukmo_b1, = plot(g['YEAR'], g['REG_CAP'], label='ukmo-b1')
			g = df_d['echam_a1b'].groupby('YEAR').mean().reset_index()
			echam_a1b, = plot(g['YEAR'], g['REG_CAP'], label='echam-a1b')
			g = df_d['echam_a2'].groupby('YEAR').mean().reset_index()
			echam_a2, = plot(g['YEAR'], g['REG_CAP'], label='echam-a2')
			g = df_d['echam_b1'].groupby('YEAR').mean().reset_index()
			echam_b1, = plot(g['YEAR'], g['REG_CAP'], label='echam-b1')
	
	#		legend(loc=3)
	
			xlim([1950, 2090])
			axvline(x=2010, linestyle='--', color='black')
			title('%s' % (wreg))
			xlabel('Year')
			ylabel('Useable capacity (MW)')
	
		if typ == 'period':
			for scen in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:

				a = df_d[scen]['REG_CAP']
				max_val = a.max()
				len_a = len(a)
				b = (max_val - a) #/max_val
				c = b.order(ascending=False) #.reset_index()
				ep = c.rank(method='min', ascending=False)/(1+len(a))
				t = (1/ep)/365
				plot(t, c, label=scen)

			legend(loc=4)
			
			xlim([0,50])
			title('%s' % (wreg))
			xlabel('Return Period (years)')
			ylabel('Reduction in Useable Capacity')
	
		if not os.path.exists(wpath):
			os.mkdir(wpath)
	
		plt.savefig('%s/%s.png' % (wpath, wreg), bbox_inches='tight')
		clf()

b = sum_regions()
b.fix_indices()
b.fix_hydro()
b.prep_tables()
for y in b.df_d.keys():
	b.plot_sum(y, 'annual', '/home/chesterlab/Bartos/post/img/reg')

for y in b.df_d.keys():
	b.plot_sum(y, 'period', '/home/chesterlab/Bartos/post/img/reg')

for y in b.df_d.keys():
	b.plot_sum(y, 'century', '/home/chesterlab/Bartos/post/img/reg')
