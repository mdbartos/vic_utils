import numpy as np
import pandas as pd
import os
import pickle
import ast
from StringIO import StringIO
import datetime
import math
from db_mash import mash_db as mash
from datetime import date
from datetime import timedelta as td

class rbm_post():

	def __init__(self, op_path, rc_path, rbm_path, atm_path, rc_rout_path, op_rout_path, post_pp_d_path, tech_d_path):
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
#		self.ext_wt = pd.DataFrame()
		self.ext_cat_df = pd.DataFrame()
		self.rc_rout_path = rc_rout_path
		self.op_rout_path = op_rout_path
		self.post_pp_d = pickle.load(open(post_pp_d_path, 'rb'))
		self.tech_d = pickle.load(open(tech_d_path, 'rb'))
		self.mohseni_d = {}
		self.eff_rc_d = self.post_pp_d['st_rc'].groupby('PLPRMFL').mean()['ELEC_EFF_AVG'].fillna(0.40)

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
					for k in self.st_d[tech][i].values:
						cell_d = {}
						ll_d = {}
						jcell_d.update({k[1] : None})
						jll_d.update({k[1] : None})
						stn_ll = k[2]
						for spat_ll in self.spat_d[i].values:
							diff = ((spat_ll[4] - stn_ll[0])**2 + (spat_ll[5] - stn_ll[1])**2)**0.5
							cell_d.update({spat_ll[1] : diff})	
							ll_d.update({str(tuple([spat_ll[4], spat_ll[5]])) : diff})
						cell = min(cell_d, key=cell_d.get)
						ll = min(ll_d, key=ll_d.get)
						mi = cell_d[cell]
						jcell_d[k[1]] = cell
						jll_d[k[1]] = ll
					temp_cell_d[tech].update({i : jcell_d})
					temp_ll_d[tech].update({i : jll_d})
				self.cell_d[tech] = temp_cell_d[tech]
				self.ll_d[tech] = temp_ll_d[tech]
	

	def import_mohseni(self, mohseni_path):
		for c in os.listdir(mohseni_path):

			cpath = mohseni_path + '/' + c
			df = pd.read_table(cpath, sep=' ', skiprows=6, header=None)
			df = df.dropna(axis=1)
			
			df_o = open(cpath, 'r')	
			dfhead = df_o.readlines()[:6]
			df_o.close()
				
			ncol = int(dfhead[0].split()[1])
			nrow = int(dfhead[1].split()[1])
			xll = float(dfhead[2].split()[1])
			yll = float(dfhead[3].split()[1])
			cellsize = float(dfhead[4].split()[1])
			cellprec = len(dfhead[4].split()[1].split('.')[1])
			nodata = dfhead[5].split()[1]
			if xll % cellsize != 0.0:
				xll = self.round_multiple(xll, cellprec, cellsize)
			if yll % cellsize != 0.0:
				yll = self.round_multiple(yll, cellprec, cellsize)	
	
			df_col = [(xll + cellsize/2 + cellsize*i) for i in range(len(df.columns))]
			df['idx'] = [(yll + cellsize/2 + cellsize*i) for i in range(len(df.index))][::-1]
			df = df.set_index('idx')
			df.columns = df_col

			self.mohseni_d.update({c.split('.')[0] : df})


	def make_rc_outfiles(self, scen, basin, wpath, sigma = 0.8, gsum = 0.7, gwint = 0.9, ncc = 6, Tapp = 6):
		wtemp_path = self.rbm_path + '/' + basin
		atmo_path = self.atm_path + '/' + scen
		rc_rout_path = self.rc_rout_path + '/' + scen + '/' + basin
		for pcode in self.st_d['st_rc'][basin]['PCODE'].values:
			print pcode
			line_d = {}
			set_li = []

			if basin in self.cell_d['st_rc']:
				cell = self.cell_d['st_rc'][basin][pcode]

				if os.path.exists(wtemp_path):
					with open('%s/%s.Temp' % (wtemp_path, scen), 'r') as wtempfile:
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
					if scen == 'hist':
						wd =  lambda x: datetime.date.fromordinal((datetime.date(1949, 1, 1)).toordinal() + int(x['ord']))
					else:

						wd =  lambda x: datetime.date.fromordinal((datetime.date(2010, 1, 1)).toordinal() + int(x['ord']))
					wtemp_df['DATE'] = wtemp_df.apply(wd, axis=1)
					del wtemp_df['ord']
					wtemp_df = wtemp_df.set_index('DATE')
					set_li.append(wtemp_df)
					atmo_lat = ast.literal_eval(self.ll_d['st_rc'][basin][pcode])[0]
					atmo_lon = ast.literal_eval(self.ll_d['st_rc'][basin][pcode])[1]

			else:
				rc = {}
		
				for i in self.tech_d['st_rc'].keys():
					for j in self.tech_d['st_rc'][i].keys():
						rc.update({j : self.tech_d['st_rc'][i][j]})
				
				p_lat = rc[pcode][0]
				p_lon = rc[pcode][1]

				alpha = self.mohseni_d['bayeskrig_a'].loc[p_lat, p_lon]
				beta = self.mohseni_d['bayeskrig_b'].loc[p_lat, p_lon]
				gamma = self.mohseni_d['bayeskrig_g'].loc[p_lat, p_lon]
				mu = self.mohseni_d['bayeskrig_u'].loc[p_lat, p_lon]
			
				atmo_lat = p_lat
				atmo_lon = p_lon



			with open('%s/full_data_%s_%s' % (atmo_path, atmo_lat, atmo_lon), 'r') as atmofile:
				line_d.update({'atmo' : ''.join(atmofile.readlines())})


			atmo_str = StringIO(line_d['atmo'])
			atmo_df = pd.read_table(atmo_str, skiprows=5)
			atmo_df.columns = ['YEAR', 'MONTH', 'DAY', 'OUT_AIR_TEMP', 'OUT_PRESSURE', 'OUT_DENSITY', 'OUT_VP', 'OUT_VPD', 'OUT_QAIR', 'OUT_REL_HUMID']
			ad =  lambda x: datetime.date(int(x['YEAR']), int(x['MONTH']), int(x['DAY']))
			atmo_df['DATE'] = atmo_df.apply(ad, axis=1)
			atmo_df = atmo_df.set_index('DATE')
			set_li.append(atmo_df)




			rout_fn = basin + '_' + self.st_rc[basin].set_index('PCODE').loc[pcode]['slug']
			if len(rout_fn.split('_')[-1]) < 5:
				rout_fn = rout_fn + ' '*(5-len(rout_fn.split('_')[-1]))
			rout_df = pd.read_fwf('%s/%s.day' % (rc_rout_path, rout_fn), header=None, widths=[12, 12, 12, 13])
			rout_df.columns = ['routyear', 'routmonth', 'routday', 'FLOW_CFS']
			rout_df['FLOW_M3S'] = rout_df['FLOW_CFS']*0.0283168466
			mkdate = lambda x: datetime.date(int(x['routyear']), int(x['routmonth']), int(x['routday']))
			rout_df['date'] = rout_df.apply(mkdate, axis=1)
			rout_df = rout_df.set_index('date')
			set_li.append(rout_df)

			print [i for i in set_li]
			print [type(i) for i in set_li]

			cat_df = pd.concat([i for i in set_li], join='inner', axis=1)
			
			if not 'WTEMP' in cat_df.columns:
				mohseni_eqn = lambda x: mu + ((alpha - mu)/(1+math.e**(gamma*(beta - x['OUT_AIR_TEMP']))))
				cat_df['WTEMP'] = cat_df.apply(mohseni_eqn, axis=1)

			del cat_df['routyear']
			del cat_df['routmonth']
			del cat_df['routday']

#INDEX POST_PP_D TO PCODE HERE; CAN SAVE TO VARIABLES/DICTS

			#ATMO ARRAYS
			rc = self.post_pp_d['st_rc'].loc[pcode]


			Pws = 100*cat_df['OUT_VP']/cat_df['OUT_REL_HUMID']
			Twb = (cat_df['OUT_VP'] + 0.000662*(cat_df['OUT_PRESSURE']*cat_df['OUT_AIR_TEMP']))/(Pws + 0.000662*cat_df['OUT_PRESSURE'])
			Bf = 0.6219907
			Oin = Bf*cat_df['OUT_VP']/(cat_df['OUT_PRESSURE'] - cat_df['OUT_VP'])
			Oout = Bf*Pws/(cat_df['OUT_PRESSURE'] - Pws)
			Hin = (cat_df['OUT_AIR_TEMP']*(1.01 + 1.89*Oin) + 2500*Oin)/1000
			hfg = 2.45 #MJ/kg
			cpw = 0.004179 #MJ/kg-k
			gamma_func = lambda x: gsum if x['MONTH'] in [4,5,6,7,8,9] else gwint 
			gamma = cat_df.apply(gamma_func, axis=1)
			tau = (1 - (ncc-1)/ncc) 
			Tc = Twb + Tapp
			
			if np.isnan(rc['ELEC_EFF_AVG']) == True:
				plprmfl = rc['PLPRMFL']
				rc['ELEC_EFF_AVG'] = self.eff_rc_d.loc[plprmfl]
			
			if np.isnan(rc['WATER_FLOW']) == False:
				Wcirc = min(rc['WATER_FLOW'], rc['WCIRC_CALC'])
				Wmu = sigma*(Oout - Oin)*Wcirc
			else:
				Ksens_reg = lambda x: (-0.000279*x['OUT_AIR_TEMP']**3 + 0.00109*x['OUT_AIR_TEMP']**2 - 0.345*x['OUT_AIR_TEMP'] + 26.7)/100
				Ksens = cat_df.apply(Ksens_reg, axis=1)
				Wevap = (1/28.32)*(rc['NAMEPLATE']*rc['CAP_FRAC']*((1-rc['ELEC_EFF_AVG'] - rc['Kos'])/rc['ELEC_EFF_AVG'])*(1-Ksens))/hfg
				Wmu = ncc*Wevap/(ncc-1)
				Wcirc = Wmu/(sigma*(Oout - Oin))

			Trange = (rc['NAMEPLATE']*rc['CAP_FRAC']*(1-rc['ELEC_EFF_AVG'] - rc['Kos']))/(28.32*Wcirc*rc['ELEC_EFF_AVG']*cpw)

			Hout = Hin + (sigma*Trange*0.004186)
			cat_df['Wmu'] = Wmu
			cat_df['Wcirc'] = Wcirc
			cat_df['Constr_Flow_CFS'] = gamma*cat_df['FLOW_CFS']
			Wmu_min = cat_df[['Wmu', 'Constr_Flow_CFS']].min(axis=1)
			cat_df['Wcirc_Constr'] = Wmu_min/(sigma*(Oout - Oin))
			cat_df['H_diff'] = Hout - Hin
			cat_df['O_diff'] = Oout - Oin

			cat_df['POWER_CAP_MW'] = (1000*0.028317*cat_df['Wcirc_Constr'])*(Hout + Tc*cpw*tau*(Oout - Oin) - cat_df['WTEMP']*cpw*(Oout - Oin) - Hin)/(sigma*(1-rc['ELEC_EFF_AVG'] - rc['Kos'])/rc['ELEC_EFF_AVG'])
			cat_df.loc[cat_df['POWER_CAP_MW'] > rc['NAMEPLATE']*rc['CAP_FRAC'], 'POWER_CAP_MW'] = rc['NAMEPLATE']*rc['CAP_FRAC']
			
			self.ext_cat_df = cat_df

			print cat_df
			cat_df.to_csv('%s/%s.%s' % (wpath, scen, str(pcode).split('.')[0]), sep='\t')
				

	def make_op_outfiles(self, scen, basin, wpath):
		wtemp_path = self.rbm_path + '/' + basin
		atmo_path = self.atm_path + '/' + scen
		op_rout_path = self.op_rout_path + '/' + scen + '/' + basin
		for pcode, cell in self.cell_d['st_op'][basin].items():
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
				if scen == 'hist':
					wd =  lambda x: datetime.date.fromordinal((datetime.date(1949, 1, 1)).toordinal() + int(x['ord']))
				else:
					wd =  lambda x: datetime.date.fromordinal((datetime.date(2010, 1, 1)).toordinal() + int(x['ord']))

				wtemp_df['DATE'] = wtemp_df.apply(wd, axis=1)
				del wtemp_df['ord']
				wtemp_df = wtemp_df.set_index('DATE')
				set_li.append(wtemp_df)


			rout_fn = basin + '_' + self.st_op[basin].set_index('PCODE').loc[pcode]['slug']
			if len(rout_fn.split('_')[-1]) < 5:
				rout_fn = rout_fn + ' '*(5-len(rout_fn.split('_')[-1]))

			rout_df = pd.read_fwf('%s/%s.day' % (op_rout_path, rout_fn), header=None, widths=[12, 12, 12, 13])
			rout_df.columns = ['routyear', 'routmonth', 'routday', 'FLOW_CFS']
			rout_df['FLOW_M3S'] = rout_df['FLOW_CFS']*0.0283168466
			mkdate = lambda x: datetime.date(int(x['routyear']), int(x['routmonth']), int(x['routday']))
			rout_df['date'] = rout_df.apply(mkdate, axis=1)
			rout_df = rout_df.set_index('date')
			set_li.append(rout_df)

			print [i for i in set_li]
			print [type(i) for i in set_li]

			cat_df = pd.concat([i for i in set_li], join='inner', axis=1)
			cat_df['YEAR'] = cat_df['routyear']
			cat_df['MONTH'] = cat_df['routmonth']
			cat_df['DAY'] = cat_df['routday']

			del cat_df['routyear']
			del cat_df['routmonth']
			del cat_df['routday']

#INDEX POST_PP_D TO PCODE HERE; CAN SAVE TO VARIABLES/DICTS

			op = self.post_pp_d['st_op'].loc[pcode]

			cpw = 0.004179 #MJ/kg-k

			Tlmax_summer = max(32, (op['Outlet Peak Summer Temperature'] - 32)/1.8)
			Tlmax_winter = max(32, (op['Outlet Peak Winter Temperature'] - 32)/1.8) 
			if np.isnan(op['TEMP_RISE']) == False:
				cat_df['TEMP_RISE'] = op['TEMP_RISE']/1.8
			elif np.isnan(op['INTAKE_RATE_AT_100_PCT']) == False:
				cat_df['TEMP_RISE'] = (op['NAMEPLATE']*op['CAP_FRAC']*(1-op['ELEC_EFF_AVG'] - op['Kos']))/(28.32*op['INTAKE_RATE_AT_100_PCT']*op['ELEC_EFF_AVG']*cpw)

			else:
				cat_df['TEMP_RISE'] = 11


			gamma_func = lambda x: 0.7 if x['MONTH'] in [4,5,6,7,8,9] else 0.9 
			gamma = cat_df.apply(gamma_func, axis=1)
			cat_df['Constr_Flow_CFS'] = gamma*cat_df['FLOW_CFS']
			templimit_func = lambda x: Tlmax_summer if x['MONTH'] in [4,5,6,7,8,9] else Tlmax_winter
			cat_df['Tlmax'] = cat_df.apply(templimit_func, axis=1)
			cat_df['T_diff'] = cat_df['Tlmax'] - cat_df['WTEMP']
			cat_df['min_T_diff'] = cat_df[['TEMP_RISE', 'T_diff']].min(axis=1)
			cat_df[cat_df['min_T_diff'] < 0] = 0

			cat_df['Wop_calc'] = (op['NAMEPLATE']*op['CAP_FRAC']*(1-op['ELEC_EFF_AVG'] - op['Kos'])/op['ELEC_EFF_AVG'])/(cpw*cat_df['min_T_diff'])/28.32
			cat_df['Wop_constr'] = cat_df[['Wop_calc', 'Constr_Flow_CFS']].min(axis=1)

			cat_df['POWER_CAP_MW'] = (cat_df['Wop_constr']*cat_df['min_T_diff']*cpw*28.32)/((1-op['ELEC_EFF_AVG'] - op['Kos'])/op['ELEC_EFF_AVG'])
			print cat_df
			self.ext_cat_df = cat_df

			cat_df.to_csv('%s/%s.%s' % (wpath, scen, str(pcode).split('.')[0]), sep='\t')

	def get_ct(self, scen, rpath, wpath, rpercent=0.01):
		
		ct_rpath = rpath + '/' + scen + '/' + 'ct'
		ct_spec = self.post_pp_d['ct']
		ct_spec['NAMEPCAP'] = ct_spec['NAMEPCAP'].str.replace(',', '')

		d1 = date(1949, 1, 1)
		d2 = date(2009, 12, 31)
		d3 = date(2010, 1, 1)
		d4 = date(2099, 12, 31)
		
		ddelta_hist = d2 - d1
		ddelta_fut = d4 - d3

		drange_hist = [d1 + td(days=i) for i in range(ddelta_hist.days + 1)]
		drange_hist = pd.Series(drange_hist, name='date')
		drange_fut = [d3 + td(days=i) for i in range(ddelta_fut.days + 1)]
		drange_fut = pd.Series(drange_fut, name='date')

		ct = {}
		
		for i in self.tech_d['ct'].keys():
			for j in self.tech_d['ct'][i].keys():
				ct.update({j : self.tech_d['ct'][i][j]})

		for j, k in ct.items():
			pspec = ct_spec.loc[j]	
			fn = ct_rpath + '/' + 'data_%s_%s' % (k[0], k[1])
			if scen == 'hist':
				df = pd.read_table(fn, sep=' ', names=['prcp', 'tmax', 'tmin', 'wspd'])
				df = pd.concat([drange_hist, df['tmax']], axis=1)
			else:
				df = pd.read_table(fn, sep='\t', names=['prcp', 'tmax', 'tmin', 'wspd'])
				df = pd.concat([drange_fut, df['tmax']], axis=1)
			df['POWER_CAP_MW'] = float(pspec['NAMEPCAP'])*pspec['CAP_FRAC']*(-rpercent*df['tmax'] + 1.15)
			df.to_csv('%s/%s.%s' % (wpath, scen, j), sep='\t')

	def get_solar(self, scen, rpath, wpath):

		pv_rpath = rpath + '/' + scen
		pv_spec = self.post_pp_d['pv']
		pv_spec['NAMEPCAP'] = pv_spec['NAMEPCAP'].str.replace(',', '')

		pv = {}
		
		for i in self.tech_d['solar'].keys():
			for j in self.tech_d['solar'][i].keys():
				pv.update({j : self.tech_d['solar'][i][j]})

		for j, k in pv.items():
			pspec = pv_spec.loc[j]
			print j, float(pspec['NAMEPCAP'])*pspec['CAP_FRAC']
			fn = pv_rpath + '/' + 'full_data_%s_%s' % (k[0], k[1])
			df = pd.read_table(fn, sep='\t', skiprows=6, names=['YEAR', 'MONTH', 'DAY', 'OUT_AIR_TEMP', 'OUT_R_NET', 'OUT_SHORTWAVE', 'OUT_LONGWAVE', 'OUT_RAD_TEMP', 'OUT_ALBEDO', 'OUT_TSKC'])
			df['POWER_CAP_MW'] = float(pspec['NAMEPCAP'])*pspec['CAP_FRAC']*(df['OUT_SHORTWAVE']/1000)*(1 - 0.0041*(df['OUT_AIR_TEMP'] - 25))
			df.to_csv('%s/%s.%s' % (wpath, scen, j), sep='\t')

	def get_wind(self, scen, rpath, wpath):

		wn_rpath = rpath + '/' + scen + '/' + 'wind'
		wn_histpath = rpath + '/hist/' + 'wind'
		wn_spec = self.post_pp_d['wn']
		
		d1 = date(1949, 1, 1)
		d2 = date(2009, 12, 31)
		d3 = date(2010, 1, 1)
		d4 = date(2099, 12, 31)
		
		ddelta_hist = d2 - d1
		ddelta_fut = d4 - d3

		drange_hist = [d1 + td(days=i) for i in range(ddelta_hist.days + 1)]
		drange_hist = pd.Series(drange_hist, name='date')
		drange_fut = [d3 + td(days=i) for i in range(ddelta_fut.days + 1)]
		drange_fut = pd.Series(drange_fut, name='date')

		wn = {}


		for i in self.tech_d['wind'].keys():
			for j in self.tech_d['wind'][i].keys():
				wn.update({j : self.tech_d['wind'][i][j]})

		print wn.keys()
		print wn.items()

		for j, k in wn.items():
			print type(j)
			pspec = wn_spec.loc[j]
			fn_scen = wn_rpath + '/' + 'data_%s_%s' % (k[0], k[1])
			fn_hist = wn_histpath + '/' + 'data_%s_%s' % (k[0], k[1])
			df_hist = pd.read_table(fn_hist, sep=' ', names=['prcp_hist', 'tmax_hist', 'tmin_hist', 'wspd_hist'])
			if scen == 'hist':
				df_scen = pd.read_table(fn_scen, sep=' ', names=['prcp', 'tmax', 'tmin', 'wspd'])
				df_scen = pd.concat([drange_hist, df_scen['wspd']], axis=1)
			else:
				df_scen = pd.read_table(fn_scen, sep='\t', names=['prcp', 'tmax', 'tmin', 'wspd'])
				df_scen = pd.concat([drange_fut, df_scen['wspd']], axis=1)

			df_hist = pd.concat([drange_hist, df_hist], axis=1)
			hist_avg_wspd = df_hist.loc[21915:].mean()['wspd_hist']
			
			df_scen['POWER_CAP_MW'] = float(pspec['NAMEPCAP'])*pspec['CAP_FRAC']*pspec['CAPFAC']*(df_scen['wspd']**3)/(hist_avg_wspd**3)
			df_scen.to_csv('%s/%s.%s' % (wpath, scen, j), sep='\t')
