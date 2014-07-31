import os
import pandas as pd
import numpy as np
import urllib2 as url
from StringIO import StringIO
import pickle
from datetime import date
from datetime import timedelta as td
import ast
from scipy.optimize import curve_fit
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt

temp_d = pickle.load( open( "basin_temps.p", "rb"))
r_latlon = pickle.load( open( "region_latlon.p", "rb"))
latlon_d = pd.concat([i for i in r_latlon.values()], ignore_index=True)
latlon_d = latlon_d.drop_duplicates()
stat_cds = pd.read_csv('stat_cd_nm_query.asc', sep='\t', skiprows=7)

####IMPORT EXTRA DATA####
lc = pd.read_csv('LCR.csv')
lc.columns = ['year', 'month', 'day', 'hour', 'temperature']
lcgb = lc.groupby(['year', 'month', 'day']).mean().reset_index()
lcgb['datetime'] = ['-'.join([str(lcgb['year'][i]), str(lcgb['month'][i]), str(lcgb['day'][i])]) for i in lcgb.index]
lcgb['01_00010_00003'] = lcgb['temperature']
lcgb['01_00010_00003_cd'] = ['A' for i in lcgb.index if lcgb['temperature'][i] != np.nan]
lcgb['site_no'] = '9999999'
lcimp = lcgb[['site_no', 'datetime', '01_00010_00003', '01_00010_00003_cd']]
temp_d['little_col'].update({'9999999' : lcimp})
##########################

class make_mohseni():
	def __init__(self):
#		self.basin = basin
		self.len_d = {}
		self.max_d = {}
		self.loc_d = {}
		self.diff_d = {}
		self.param_d = {}
		self.cat_d = {}
		self.src_data = {}
		self.isavg = {}
		
	def find_max_station(self):
		for k in temp_d.keys():
			self.len_d.update({k : {}})
			self.max_d.update({k : None})
			print k
			for i, v in temp_d[k].items():
				self.len_d[k].update({i : len(v)})
			if len(self.len_d[k]) > 0:
				maxix = max(self.len_d[k], key=self.len_d[k].get)
				maxlen = max(self.len_d[k].values())
				print maxix, maxlen
				self.max_d[k] = maxix	

	def make_loc_d(self):
		for fn in os.listdir('.'):
			if fn.endswith('txt'):
				f = pd.read_csv(fn, dtype={'SITE_NO' : str})
				sn = f['SITE_NO']
				f['latlon'] = zip(f['LAT_SITE'], f['LON_SITE'])
				sf = fn.split('.')[0]
				self.loc_d.update({sf : f[['SITE_NO', 'latlon', 'STATION_NM']]})

	def relate_met(self, basin, **kwargs):
		print basin
		if kwargs['automax'] == True:
			st_id = self.max_d[basin]
		else:
			st_id = kwargs['st_id']
		if len(temp_d[basin]) > 0:
			self.diff_d.update({basin : {}})
			fn_d = {}
			ll = self.loc_d[basin]['latlon'].ix[self.loc_d[basin]['SITE_NO'] == st_id]
			print ll
			ll = tuple(ll.values)[0]
			lat = ll[0]
			lon = ll[1]
			for v in latlon_d.values:
				diff = ((v[0] - lat)**2 + (v[1] - lon)**2)**0.5
				fn_d.update({v : diff})
			cell = min(fn_d, key=fn_d.get)
			print cell
			mi = fn_d[cell]
			print mi
			self.diff_d[basin].update({st_id : cell})
		else:
			print 'no stations'			

	def cat_vars(self, basin, **kwargs):
		if len(self.diff_d[basin]) > 0:
			if kwargs['automax'] == True:
				st_id = self.max_d[basin]
			else:
				st_id = kwargs['st_id']
			w = temp_d[basin][st_id]
			diff_coords = self.diff_d[basin][st_id]
	#		print diff_coords
	#		print [i for i in t['datetime']]
			w['date'] = [(date(int(i.split('-')[0]), int(i.split('-')[1]), int(i.split('-')[2]))) for i in w['datetime']]
			w = w.drop_duplicates(cols='date')
			col_li = [i for i in w.columns if '00010' in i]
			temp_cols = [i for i in col_li if not 'cd' in i]
			cd_cols = [i for i in col_li if 'cd' in i]
			col_d = {'temp' : {}, 'cd' : {}}
			for r in temp_cols:
				if r.split('_')[2] == '00001':
					col_d['temp'].update({'w_tmax' : r})
				if r.split('_')[2] == '00002':
					col_d['temp'].update({'w_tmin' : r})
				if r.split('_')[2] == '00003':
					col_d['temp'].update({'w_tavg' : r})
				if r.split('_')[2] == '00008':
					col_d['temp'].update({'w_tmed' : r})
			for r in cd_cols:
				if r.split('_')[2] == '00001':
					col_d['cd'].update({'w_tmax_cd' : r})
				if r.split('_')[2] == '00002':
					col_d['cd'].update({'w_tmin_cd' : r})
				if r.split('_')[2] == '00003':
					col_d['cd'].update({'w_tavg_cd' : r})
				if r.split('_')[2] == '00008':
					col_d['cd'].update({'w_tmed_cd' : r})
			cat_cols = ['date', 'site_no']
			for e, v in col_d['temp'].items():
				w[e] = w[v]
				cat_cols.append(e)
			for e, v in col_d['cd'].items():
				w[e] = w[v]
				cat_cols.append(e)
			cat_cols = list(set(cat_cols))
			w = w[[i for i in cat_cols]]
			w = w.set_index('date')
			w = w.replace(to_replace=['Ice'], value=[0.0])
			for j in col_d['temp'].keys():
				w[j] = w[j].convert_objects(convert_numeric=True)
			if 'w_tavg' in w.columns:
				self.isavg.update({st_id : True})
			elif 'w_tmed' in w.columns:
				w['w_tavg'] = w['w_tmed']
				self.isavg.update({st_id : True})
			elif ('w_tmax' in w.columns) and ('w_tmin' in w.columns):
				w['w_tavg'] = 0.5*(w['w_tmin'] + w['w_tmax'])
				self.isavg.update({st_id : True})
			else:
				self.isavg.update({st_id : False})
			if self.isavg[st_id] == True:
				a = pd.read_csv('./master/data_%s_%s' % (str(diff_coords[0]), str(diff_coords[1])), sep='\t', header=None, index_col=False, names=['year', 'month', 'day', 'prcp', 'tmax', 'tmin', 'wspd'])
				a['tavg'] = 0.5*(a['tmin'] + a['tmax'])
		#		d1 = date(1949, 1, 1)
		#		d2 = date(2010, 12, 31)
		#		ddelta = d2 - d1
		#		dr = [d1 + td(days=i) for i in range(ddelta.days + 1)]
		#		print len(dr)
		#		print a[['year', 'month', 'day']]
				a['date'] = [date(a['year'][i], a['month'][i], a['day'][i]) for i in a.index]
		#		print a['date']
				a = a.set_index('date')
				print 'w', w
				print 'a', a
				c = pd.concat([w,a], axis=1)
				print c
				self.cat_d.update({basin : {}})
				self.cat_d[basin].update({st_id : c})
			else:
				pass
			
		else:
			print 'No stations'

	def make_src_data(self, **src_kwargs):
		base_data = self.cat_d[src_kwargs['dbasin']][src_kwargs['dst_id']]
		self.src_data = base_data.dropna()#.ix[(base_data['w_tmax_cd'] == 'A') & (base_data['w_tmin_cd'] == 'A')]
		
	def mohseni(self, x, b, g):
		xdata = self.src_data['tavg']
		ydata = self.src_data['w_tavg']
		a = max(ydata)#.quantile(q=0.999)
		u = min(ydata)#.quantile(q=0.001)
		return u + (a-u)/(1 + np.exp(g*(b-x)))

	def NS(self, s,o):
		"""
		Nash Sutcliffe efficiency coefficient
		input:
			s: simulated
			o: observed
		output:
			ns: Nash Sutcliffe efficient coefficient
		"""
		return 1 - sum((s-o)**2)/sum((o-np.mean(o))**2)

	def fit_mohseni(self, basin, **kwargs):
		if kwargs['automax'] == True:
			st_id = self.max_d[basin]
		else:
			st_id = kwargs['st_id']
		if self.isavg[st_id] == True:
			self.make_src_data(dbasin=basin, dst_id=st_id)
			xdata = self.src_data['tavg']
			ydata = self.src_data['w_tavg']
			if len(ydata) < 1:
				pass
			else:
				b_init = 12.0
				g_init = 0.2
				popt, pcov = curve_fit(self.mohseni, xdata, ydata, p0=[b_init, g_init])
				NSC = self.NS(self.mohseni(xdata, popt[0], popt[1]), ydata)
				if basin not in self.param_d.keys():
					self.param_d.update({basin : {}})
				self.param_d[basin].update({st_id : {}})
				self.param_d[basin][st_id].update({'a': max(ydata), 'b': popt[0], 'g': popt[1], 'u': min(ydata), 'n': len(ydata), 'nsc': NSC})
				print popt, NSC
		else:
			pass

	def plot_curvefit(self, basin, **kwargs):
		if kwargs['automax'] == True:
			st_id = self.max_d[basin]
		else:
			st_id = kwargs['st_id']
		if self.isavg[st_id] == True:
			fig, ax = plt.subplots(1)
			xdata = self.src_data['tavg']
			ydata = self.src_data['w_tavg']
			if len(ydata) < 1:
				pass
			else:
				NSC = self.param_d[basin][st_id]['nsc']
				print 'NSC', NSC
				xy = np.vstack([xdata, ydata])
				z = gaussian_kde(xy)(xy)
				ax.scatter(xdata, ydata, c=z, s=100, edgecolor='')
				ax.plot(np.arange(-20, 61), self.mohseni(np.arange(-20, 61), self.param_d[basin][st_id]['b'], self.param_d[basin][st_id]['g']), c='black')
				statname = self.loc_d[basin]['STATION_NM'].ix[m.loc_d[basin]['SITE_NO'] == st_id]
				statname = statname.values[0]
				print statname
				plt.title('USGS STATION %s, %s' % (self.max_d[basin], statname))
				plt.xlabel('Air Temperature ($^\circ$C)')
				plt.ylabel('Stream Temperature ($^\circ$C)')
				plt.ylim([0, max(self.src_data['w_tavg']) + 5])
				plt.xlim([-20, 60])
#				textstr = r'$\beta=%.2f$\n$\gamma=%.2f$\n' % (self.param_d[basin][0][0], self.param_d[basin][0][1])
				textstr = '$\\alpha=%.2f$\n$\\beta=%.2f$\n$\\gamma=%.2f$\n$\\mu=%.2f$\n$n=%s$\n$N.S.C.=%.2f$' % (self.param_d[basin][st_id]['a'], self.param_d[basin][st_id]['b'], self.param_d[basin][st_id]['g'], self.param_d[basin][st_id]['u'], self.param_d[basin][st_id]['n'], self.param_d[basin][st_id]['nsc'])
				props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
				ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top', linespacing=1.25, bbox=props)
				if 'img' in os.listdir('.'):
					pass
				else:
					os.mkdir('./img')
				if basin in os.listdir('./img'):
					pass
				else:
					os.mkdir('./img/%s' % (basin))
				plt.savefig('./img/%s/%s.png' % (basin, st_id), bbox_inches='tight')
		else:
			pass
		
	def prep_data(self, basin, **kwargs):
		self.find_max_station()
		self.make_loc_d()
		if kwargs['automax'] == True:
			self.relate_met(basin, automax=True)
			self.cat_vars(basin, automax=True)
		else:
			st_id = kwargs['st_id']
			self.relate_met(basin, automax=False, st_id=st_id)
			self.cat_vars(basin, automax=False, st_id=st_id)
		
	def reg_exec(self, basin, **kwargs):
		if kwargs['automax'] == True:
			try:
				self.fit_mohseni(basin, automax=True)
			except RuntimeError:
				self.param_d[basin][st_id].update({'a': np.nan, 'b': np.nan, 'g': np.nan, 'u': np.nan, 'n': np.nan, 'nsc': np.nan})
			else:
				if kwargs['plot_results'] == True:
					self.plot_curvefit(basin, automax=True)
				else:
					pass
		else:
			st_id = kwargs['st_id']
			try:
				self.fit_mohseni(basin, automax=False, st_id=st_id)
			except RuntimeError:
				self.param_d[basin].update({st_id : {}})
				self.param_d[basin][st_id].update({'a': np.nan, 'b': np.nan, 'g': np.nan, 'u': np.nan, 'n': np.nan, 'nsc': np.nan})
			else:
				if kwargs['plot_results'] == True:
					self.plot_curvefit(basin, automax=False, st_id=st_id)
				else:
					pass		

m = make_mohseni()
for u in temp_d.keys():
	for q in temp_d[u].keys():
		m.prep_data(u, automax=False, st_id=q)
		m.reg_exec(u, automax=False, st_id=q, plot_results=False)
		
pickle.dump( m.param_d, open( "param_d.p", "wb" ) )

#######MAKE PARAM TABLE###########

param_d = m.param_d

df_li = []

for j in param_d:
	df = pd.DataFrame.from_dict(param_d[j], orient='index')
	df['basin'] = j
	df['lat'] = [m.loc_d[j]['latlon'].ix[m.loc_d[j]['SITE_NO'] == i].values[0][0] for i in df.index]
	df['lon'] = [m.loc_d[j]['latlon'].ix[m.loc_d[j]['SITE_NO'] == i].values[0][1] for i in df.index]
	df = df.dropna()
	print df
	df_li.append(df)


param_table = pd.concat(df_li)

param_table = param_table.drop(param_table['a'][param_table['a'] > param_table['a'].std() * 3].index)
param_table = param_table.drop(param_table['b'][param_table['b'] > param_table['b'].std() * 3].index)
param_table = param_table.drop(param_table['g'][param_table['g'] > param_table['g'].std() * 3].index)
param_table = param_table.drop(param_table['u'][param_table['u'] > param_table['u'].std() * 3].index)

param_table.to_csv('param_table.csv')

#######COKRIGING DATA#############
import os
import pandas as pd
import numpy as np
import ast

df_d = {}
ct = 0

for fn in os.listdir('.'):
	lat = ast.literal_eval(fn.split('_')[1])
	lon = ast.literal_eval(fn.split('_')[2])
	df = pd.read_csv(fn, sep='\t', header=None, index_col=None)
	df.columns = ['year', 'month', 'day', 'prcp', 'tmax', 'tmin', 'wspd']
	df = df.mean()
	df_d.update({ct : {}})
	df_d[ct].update({'lat': lat, 'lon': lon, 'prcp' : df['prcp'], 'tmax' : df['tmax'], 'tmin' : df['tmin'], 'wspd' : df['wspd']})
	ct = ct + 1
	
t = pd.DataFrame.from_dict(df_d, orient='index')

##################################

m.prep_data('lees_f', automax=True)
m.reg_exec('lees_f', automax=True)
m.prep_data('pitt', automax=True)
m.reg_exec('pitt', automax=True)
m.prep_data('pawnee', automax=True)
m.reg_exec('pawnee', automax=True)
m.prep_data('comanche', automax=True)
m.reg_exec('comanche', automax=True)
m.prep_data('glenn', automax=True)
m.reg_exec('glenn', automax=True)
m.prep_data('paper', automax=True)
m.reg_exec('paper', automax=True)
m.prep_data('corona', automax=True)
m.reg_exec('corona', automax=True)



m = make_mohseni()
m.prep_data('lees_f', automax=False, st_id='09095500')
m.reg_exec('lees_f', automax=False, st_id='09095500')


m = make_mohseni()
for q in temp_d['comanche'].keys():
	m.prep_data('comanche', automax=False, st_id=q)
	m.reg_exec('comanche', automax=False, st_id=q, plot_results=False)

m = make_mohseni()
for q in temp_d['paper'].keys():
	m.prep_data('paper', automax=False, st_id=q)
	m.reg_exec('paper', automax=False, st_id=q)
	
m = make_mohseni()
for q in temp_d['glenn'].keys():
	m.prep_data('glenn', automax=False, st_id=q)
	m.reg_exec('glenn', automax=False, st_id=q)

m = make_mohseni()
for q in temp_d['pawnee'].keys():
	m.prep_data('pawnee', automax=False, st_id=q)
	m.reg_exec('pawnee', automax=False, st_id=q)
	
m = make_mohseni()
for q in temp_d['pitt'].keys():
	m.prep_data('pitt', automax=False, st_id=q)
	m.reg_exec('pitt', automax=False, st_id=q, plot_results=False)

m = make_mohseni()
for q in temp_d['colstrip'].keys():
	m.prep_data('colstrip', automax=False, st_id=q)
	m.reg_exec('colstrip', automax=False, st_id=q)

m = make_mohseni()
for q in temp_d['intermtn'].keys():
	m.prep_data('intermtn', automax=False, st_id=q)
	m.reg_exec('intermtn', automax=False, st_id=q)

m = make_mohseni()
for q in temp_d['lees_f'].keys():
	m.prep_data('lees_f', automax=False, st_id=q)
	m.reg_exec('lees_f', automax=False, st_id=q)
	
m = make_mohseni()
for q in temp_d['brigham'].keys():
	m.prep_data('brigham', automax=False, st_id=q)
	m.reg_exec('brigham', automax=False, st_id=q, plot_results=False)
	
m = make_mohseni()
for q in temp_d['brigham'].keys():
	m.prep_data('brigham', automax=False, st_id=q)
	m.reg_exec('brigham', automax=False, st_id=q)

m = make_mohseni()
for q in temp_d['corona'].keys():
	m.prep_data('corona', automax=False, st_id=q)
	m.reg_exec('corona', automax=False, st_id=q)
	
m = make_mohseni()
for q in temp_d['lahontan'].keys():
	m.prep_data('lahontan', automax=False, st_id=q)
	m.reg_exec('lahontan', automax=False, st_id=q)

m = make_mohseni()
for q in temp_d['guer'].keys():
	m.prep_data('guer', automax=False, st_id=q)
	m.reg_exec('guer', automax=False, st_id=q)

m = make_mohseni()
for q in temp_d['salton'].keys():
	m.prep_data('salton', automax=False, st_id=q)
	m.reg_exec('salton', automax=False, st_id=q)
	
m = make_mohseni()
for q in temp_d['little_col'].keys():
	m.prep_data('little_col', automax=False, st_id=q)
	m.reg_exec('little_col', automax=False, st_id=q, plot_results=True)

m = make_mohseni()
for q in temp_d['wabuska'].keys():
	m.prep_data('wabuska', automax=False, st_id=q)
	m.reg_exec('wabuska', automax=False, st_id=q, plot_results=False)

m = make_mohseni()
m.find_max_station()
m.make_loc_d()
m.relate_met('lees_f', automax=True)
m.cat_vars('lees_f', automax=True)
m.fit_mohseni('lees_f', automax=True)
m.plot_curvefit('lees_f')

######################################

class make_mohseni_hyst():
	def __init__(self, basin):
		self.basin = basin
		self.src_data = cat_d[self.basin].dropna()
		self.param_d = {}
		
	def mohseni(self, x, b, g):
		xdata = self.src_data['tavg']
		ydata = self.src_data['w_tavg']
		a = max(ydata)#.quantile(q=0.999)
		u = min(ydata)#.quantile(q=0.001)
		return u + (a-u)/(1 + np.exp(g*(b-x)))

	def fit_mohseni(self):
		xdata = self.src_data['tavg']
		ydata = self.src_data['w_tavg']
		xdata1 = self.src_data['tavg'].ix[self.src_data['month'] < 7]
		ydata1 = self.src_data['w_tavg'].ix[self.src_data['month'] < 7]
		xdata2 = self.src_data['tavg'].ix[self.src_data['month'] >= 7]
		ydata2 = self.src_data['w_tavg'].ix[self.src_data['month'] >= 7]
		b_init = 12.0
		g_init = 0.2
		popt1, pcov1 = curve_fit(self.mohseni, xdata1, ydata1, p0=[b_init, g_init])
		popt2, pcov2 = curve_fit(self.mohseni, xdata2, ydata2, p0=[b_init, g_init])
		self.param_d.update({self.basin : [popt1, popt2, pcov1, pcov2]})
		print popt1, popt2, pcov1, pcov2
	
	def plot_curvefit(self):
		xdata = self.src_data['tavg']
		ydata = self.src_data['w_tavg']
		xy = np.vstack([xdata,ydata])
		z = gaussian_kde(xy)(xy)
		xdata1 = self.src_data['tavg'].ix[self.src_data['month'] < 7]
		ydata1 = self.src_data['w_tavg'].ix[self.src_data['month'] < 7]
		xdata2 = self.src_data['tavg'].ix[self.src_data['month'] >= 7]
		ydata2 = self.src_data['w_tavg'].ix[self.src_data['month'] >= 7]
		scatter(xdata, ydata, c=z, s=100, edgecolor='')
		plot(arange(-20, 60), self.mohseni(arange(-20, 60), self.param_d[self.basin][0][0], self.param_d[self.basin][0][1]))
		plot(arange(-20, 60), self.mohseni(arange(-20, 60), self.param_d[self.basin][1][0], self.param_d[self.basin][1][1]))
