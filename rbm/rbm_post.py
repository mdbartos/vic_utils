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

#			self.spec_d.update({k : {}})
#			self.spec_d[k].update({'ncol' : ncol, 'nrow' : nrow, 'xll' : xll, 'yll' : yll, 'cellsize' : cellsize, 'nodata' : nodata})



	def make_rc_outfiles(self, scen, basin, wpath):
		wtemp_path = self.rbm_path + '/' + basin
		atmo_path = self.atm_path + '/' + scen
		rc_rout_path = self.rc_rout_path + '/' + scen + '/' + basin
		for pcode in self.st_d['st_rc'][basin]['PCODE'].values:
			print pcode
#			with open('%s/%s.%s' % (wpath, scen, str(pcode).split('.')[0]), 'w') as outfile:
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
#			self.ext_atmo = atmo_df
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
#			Hout = (cat_df['OUT_AIR_TEMP']*(1.01 + 1.89*Oout) + 2500*Oout)/1000 ##TEMP ISN"T THE SAME AS Hin!!
			sigma = 0.8
			hfg = 2.45 #MJ/kg
			cpw = 0.004179 #MJ/kg-k
			gamma_func = lambda x: 0.7 if x['MONTH'] in [4,5,6,7,8,9] else 0.9 
			gamma = cat_df.apply(gamma_func, axis=1)
			ncc = 6
			tau = (1 - (ncc-1)/ncc) 
			Tc = Twb + 6
			
			if np.isnan(rc['ELEC_EFF_AVG']) == True:
				plprmfl = rc['PLPRMFL']
				rc['ELEC_EFF_AVG'] = self.eff_rc_d.loc[plprmfl]
			
	#		if np.isnan(rc['WCIRC_CALC']) == False:
	#			Wcirc = rc['WCIRC_CALC']
	#			Wmu = sigma*(Oout - Oin)*rc['WCIRC_CALC']
			if np.isnan(rc['WATER_FLOW']) == False:
				Wcirc = min(rc['WATER_FLOW'], rc['WCIRC_CALC'])
				Wmu = sigma*(Oout - Oin)*Wcirc
			else:
				Ksens_reg = lambda x: (-0.000279*x['OUT_AIR_TEMP']**3 + 0.00109*x['OUT_AIR_TEMP']**2 - 0.345*x['OUT_AIR_TEMP'] + 26.7)/100
				Ksens = cat_df.apply(Ksens_reg, axis=1)
				Wevap = (1/28.32)*(rc['NAMEPLATE']*rc['CAP_FRAC']*((1-rc['ELEC_EFF_AVG'] - rc['Kos'])/rc['ELEC_EFF_AVG'])*(1-Ksens))/hfg
				Wmu = ncc*Wevap/(ncc-1)
				Wcirc = Wmu/(sigma*(Oout - Oin))

#			if np.isnan(rc['TEMP_RISE']) == False:      #CAUSING PROBLEMS
#				Trange = rc['TEMP_RISE']/1.8
#			else:
			Trange = (rc['NAMEPLATE']*rc['CAP_FRAC']*(1-rc['ELEC_EFF_AVG'] - rc['Kos']))/(28.32*Wcirc*rc['ELEC_EFF_AVG']*cpw)

			Hout = Hin + (sigma*Trange*0.004186)
#			Tout = (1000*(sigma*cpw*Trange+Hin) - 2500*Oout)/(1.01+1.89*Oout)
#			Hout = (Tout*(1.01 + 1.89*Oout) + 2500*Oout)/1000  


	#		cat_df['Wevap'] = Wevap
			cat_df['Wmu'] = Wmu
			cat_df['Wcirc'] = Wcirc
			cat_df['Constr_Flow_CFS'] = gamma*cat_df['FLOW_CFS']
			Wmu_min = cat_df[['Wmu', 'Constr_Flow_CFS']].min(axis=1)
			cat_df['Wcirc_Constr'] = Wmu_min/(sigma*(Oout - Oin))
			cat_df['H_diff'] = Hout - Hin
	#		cat_df['H_in'] = Hin
			cat_df['O_diff'] = Oout - Oin
	#		cat_df['O_in'] = Oin

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

#			if np.isnan(op['Outlet Peak Summer Temperature']) == False:
#				Tlmax_summer = (5*op['Outlet Peak Summer Temperature']/9) - 32
#			else:
			Tlmax_summer = max(27, (op['Outlet Peak Summer Temperature'] - 32)/1.8)
#			if np.isnan(op['Outlet Peak Winter Temperature']) == False:
#				Tlmax_winter = (5*op['Outlet Peak Winter Temperature']/9) - 32

#			else:
			Tlmax_winter = max(27, (op['Outlet Peak Winter Temperature'] - 32)/1.8) 
			if np.isnan(op['TEMP_RISE']) == False:
				cat_df['TEMP_RISE'] = op['TEMP_RISE']/1.8
		#	elif (np.isnan(op['Outlet Peak Summer Temperature']) == False) and (np.isnan(op['Inlet Peak Summer Temperature']) == False):
		#		cat_df['TEMP_RISE'] =  op['Outlet Peak Summer Temperature'] -  op['Inlet Peak Summer Temperature']
		#	elif (np.isnan(op['Outlet Peak Winter Temperature']) == False) and (np.isnan(op['Inlet Peak Winter Temperature']) == False):
		#		cat_df['TEMP_RISE'] =  op['Outlet Peak Winter Temperature'] -  op['Inlet Peak Winter Temperature']
			elif np.isnan(op['INTAKE_RATE_AT_100_PCT']) == False:
				cat_df['TEMP_RISE'] = (op['NAMEPLATE']*op['CAP_FRAC']*(1-op['ELEC_EFF_AVG'] - op['Kos']))/(28.32*op['INTAKE_RATE_AT_100_PCT']*op['ELEC_EFF_AVG']*cpw)
#			elif np.isnan(op['WATER_FLOW']) == False:
#				cat_df['TEMP_RISE'] = (op['NAMEPLATE']*op['CAP_FRAC']*(1-op['ELEC_EFF_AVG'] - op['Kos']))/(28.32*op['WATER_FLOW']*op['ELEC_EFF_AVG']*cpw)

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

	def get_ct(self, scen, rpath, wpath):
		
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
	#		df['tavg'] = (df['tmax'] + df['tmin'])/2
			df['POWER_CAP_MW'] = float(pspec['NAMEPCAP'])*pspec['CAP_FRAC']*(-0.01*df['tmax'] + 1.15)
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
	#		df['tavg'] = (df['tmax'] + df['tmin'])/2
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
			
#			print wn_spec['NAMEPCAP'].dtype, wn_spec['CAP_FRAC'].dtype, wn_spec['CAPFAC'].dtype, df_scen['wspd'].dtype, hist_avg_wspd.dtype

			df_scen['POWER_CAP_MW'] = float(pspec['NAMEPCAP'])*pspec['CAP_FRAC']*pspec['CAPFAC']*(df_scen['wspd']**3)/(hist_avg_wspd**3)
			df_scen.to_csv('%s/%s.%s' % (wpath, scen, j), sep='\t')


#b = rbm_post('/home/chesterlab/Bartos/VIC/input/dict/opstn.p', '/home/chesterlab/Bartos/VIC/input/dict/rcstn.p', '/media/melchior/BALTHASAR/nsf_hydro/VIC/output/rbm/run', '/media/melchior/BALTHASAR/nsf_hydro/VIC/output/st_rc', '/media/melchior/BALTHASAR/nsf_hydro/VIC/output/rout/rc/d8', '/media/melchior/BALTHASAR/nsf_hydro/VIC/output/rout/op/d8', '/home/chesterlab/Bartos/VIC/input/dict/post_pp_d.p', '/home/chesterlab/Bartos/VIC/input/dict/tech_d.p')

####### WITH SYMLINK FIX

b = rbm_post('/home/chesterlab/Bartos/VIC/input/dict/opstn.p', '/home/chesterlab/Bartos/VIC/input/dict/rcstn.p', '/media/melchior/BALTHASAR/nsf_hydro/VIC/output/rbm/run', '/home/chesterlab/Bartos/VIC/output/st_rc', '/home/chesterlab/Bartos/VIC/output/rout/rc/d8', '/media/melchior/BALTHASAR/nsf_hydro/VIC/output/rout/op/d8', '/home/chesterlab/Bartos/VIC/input/dict/post_pp_d.p', '/home/chesterlab/Bartos/VIC/input/dict/tech_d.p')

b.make_spat_d()

b.fix_stnames(b.st_rc)

b.fix_stnames(b.st_op)

b.st_d['st_rc']['comanche'].loc[2] = ['Comanche', 470.0, (38.2664, -104.5747), 'Coman']

b.make_diff()

b.import_mohseni('/home/chesterlab/Bartos/pre/mohseni_bayes')

###

for s in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:
	for g in b.st_op.keys():
		b.make_op_outfiles(s, g, '/home/chesterlab/Bartos/post/op')

for s in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:

#	b.make_rc_outfiles(s, 'comanche', '/home/chesterlab/Bartos/post/rc/comanche')
#	b.make_rc_outfiles(s, 'parker', '/home/chesterlab/Bartos/post/rc/parker')
#	b.make_rc_outfiles(s, 'pitt', '/home/chesterlab/Bartos/post/rc/pitt')
#	b.make_rc_outfiles(s, 'paper', '/home/chesterlab/Bartos/post/rc/paper')
#	b.make_rc_outfiles(s, 'glenn', '/home/chesterlab/Bartos/post/rc/glenn')
#	b.make_rc_outfiles(s, 'hoover', '/home/chesterlab/Bartos/post/rc/hoover')
#	b.make_rc_outfiles(s, 'little_col', '/home/chesterlab/Bartos/post/rc/little_col')
#	b.make_rc_outfiles(s, 'pawnee', '/home/chesterlab/Bartos/post/rc/pawnee')
#	b.make_rc_outfiles(s, 'intermtn', '/home/chesterlab/Bartos/post/rc/intermtn')
	b.make_rc_outfiles(s, 'lees_f', '/home/chesterlab/Bartos/post/rc/lees_f')
#	b.make_rc_outfiles(s, 'colstrip', '/home/chesterlab/Bartos/post/rc/colstrip')
#	b.make_rc_outfiles(s, 'pitt', '/home/chesterlab/Bartos/post/rc/pitt')
#	b.make_rc_outfiles(s, 'wabuska', '/home/chesterlab/Bartos/post/rc/wabuska')
#	b.make_rc_outfiles(s, 'brigham', '/home/chesterlab/Bartos/post/rc/brigham')
#	b.make_rc_outfiles(s, 'guer', '/home/chesterlab/Bartos/post/rc/guer')
#	b.make_rc_outfiles(s, 'wauna', '/home/chesterlab/Bartos/post/rc/wauna')
#	b.make_rc_outfiles(s, 'salton', '/home/chesterlab/Bartos/post/rc/salton')
#	b.make_rc_outfiles(s, 'glenn', '/home/chesterlab/Bartos/post/rc/glenn')

#for s in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:	
#	for g in b.st_rc.keys():
#		print g
#		b.make_rc_outfiles(s, g, '/home/chesterlab/Bartos/post/rc')

#b.make_op_outfiles('hist', 'pitt', '/home/chesterlab/Bartos/post/op')

###

for s in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:
#	b.get_ct(s, '/home/chesterlab/Bartos/VIC/input/vic/forcing', '/home/chesterlab/Bartos/post/ct')
#	b.get_solar(s, '/home/chesterlab/Bartos/VIC/output/solar', '/home/chesterlab/Bartos/post/pv')
	b.get_wind(s, '/home/chesterlab/Bartos/VIC/input/vic/forcing', '/home/chesterlab/Bartos/post/wn')


################################################################

import numpy as np
import pandas as pd
from pylab import *
import os
import datetime

def post_plot(rpath, wpath):

	li_1 = list(set([i.split('.')[1] for i in os.listdir(rpath)]))
	
	for pcode in li_1:
		li_2 = [i for i in os.listdir(rpath) if i.endswith(pcode)]

		d = {}

		for j in li_2:
			f = pd.read_csv('%s' % (rpath + '/' + j), sep='\t')
			d.update({j : f})

		g = d['hist.%s' % (pcode)].groupby(['MONTH', 'DAY.1']).mean().reset_index()  # FOR RC some basins, OP, PV needs to be 'DAY' instead of DAY.1
		hist, = plot(g.index, g['POWER_CAP_MW'], label='historical')
		g = d['ukmo_a1b.%s' % (pcode)].groupby(['MONTH', 'DAY.1']).mean().reset_index()
		ukmo_a1b, = plot(g.index, g['POWER_CAP_MW'], label='ukmo-a1b')
		g = d['ukmo_a2.%s' % (pcode)].groupby(['MONTH', 'DAY.1']).mean().reset_index()
		ukmo_a2, = plot(g.index, g['POWER_CAP_MW'], label='ukmo-a2')
		g = d['ukmo_b1.%s' % (pcode)].groupby(['MONTH', 'DAY.1']).mean().reset_index()
		ukmo_b1, = plot(g.index, g['POWER_CAP_MW'], label='ukmo-b1')
		g = d['echam_a1b.%s' % (pcode)].groupby(['MONTH', 'DAY.1']).mean().reset_index()
		echam_a1b, = plot(g.index, g['POWER_CAP_MW'], label='echam-a1b')
		g = d['echam_a2.%s' % (pcode)].groupby(['MONTH', 'DAY.1']).mean().reset_index()
		echam_a2, = plot(g.index, g['POWER_CAP_MW'], label='echam-a2')
		g = d['echam_b1.%s' % (pcode)].groupby(['MONTH', 'DAY.1']).mean().reset_index()
		echam_b1, = plot(g.index, g['POWER_CAP_MW'], label='echam-b1')
	
		legend(loc=4)
	
		xlim([1,366])
		title('Average daily useable capacity at Station %s' % (pcode))
		xlabel('Day of year')
		ylabel('Useable capacity (MW)')
		
		if not os.path.exists(wpath):
			os.mkdir(wpath)

		plt.savefig('%s/%s.png' % (wpath, pcode), bbox_inches='tight')
		clf()

def post_plot_op(rpath, wpath):

	li_1 = list(set([i.split('.')[1] for i in os.listdir(rpath)]))
	
	for pcode in li_1:
		li_2 = [i for i in os.listdir(rpath) if i.endswith(pcode)]

		d = {}

		for j in li_2:
			f = pd.read_csv('%s' % (rpath + '/' + j), sep='\t')
			d.update({j : f})

		g = d['hist.%s' % (pcode)].groupby(['MONTH', 'DAY']).mean().reset_index()  
		hist, = plot(g.index, g['POWER_CAP_MW'], label='historical')
		g = d['ukmo_a1b.%s' % (pcode)].groupby(['MONTH', 'DAY']).mean().reset_index()
		ukmo_a1b, = plot(g.index, g['POWER_CAP_MW'], label='ukmo-a1b')
		g = d['ukmo_a2.%s' % (pcode)].groupby(['MONTH', 'DAY']).mean().reset_index()
		ukmo_a2, = plot(g.index, g['POWER_CAP_MW'], label='ukmo-a2')
		g = d['ukmo_b1.%s' % (pcode)].groupby(['MONTH', 'DAY']).mean().reset_index()
		ukmo_b1, = plot(g.index, g['POWER_CAP_MW'], label='ukmo-b1')
		g = d['echam_a1b.%s' % (pcode)].groupby(['MONTH', 'DAY']).mean().reset_index()
		echam_a1b, = plot(g.index, g['POWER_CAP_MW'], label='echam-a1b')
		g = d['echam_a2.%s' % (pcode)].groupby(['MONTH', 'DAY']).mean().reset_index()
		echam_a2, = plot(g.index, g['POWER_CAP_MW'], label='echam-a2')
		g = d['echam_b1.%s' % (pcode)].groupby(['MONTH', 'DAY']).mean().reset_index()
		echam_b1, = plot(g.index, g['POWER_CAP_MW'], label='echam-b1')
	
		legend(loc=4)
	
		xlim([1,366])
		title('Average daily useable capacity at Station %s' % (pcode))
		xlabel('Day of year')
		ylabel('Useable capacity (MW)')
		
		if not os.path.exists(wpath):
			os.mkdir(wpath)

		plt.savefig('%s/%s.png' % (wpath, pcode), bbox_inches='tight')
		clf()

def post_plot_wind_ct_monthly(rpath, wpath):

	li_1 = list(set([i.split('.')[1] for i in os.listdir(rpath)]))
	
	for pcode in li_1:
		li_2 = [i for i in os.listdir(rpath) if i.endswith(pcode)]

		d = {}

		for j in li_2:
			f = pd.read_csv('%s' % (rpath + '/' + j), sep='\t', parse_dates=True)
			d.update({j : f})
		
		for i in d.keys():
			d[i]['date'] = pd.to_datetime(d[i]['date'])
			mkmonth = lambda x: x['date'].month
			mkday = lambda x: x['date'].day
			d[i]['MONTH'] = d[i].apply(mkmonth, axis=1)
			d[i]['DAY'] = d[i].apply(mkday, axis=1)

		g = d['hist.%s' % (pcode)].groupby(['MONTH', 'DAY']).mean().reset_index() 
		hist, = plot(g.index, g['POWER_CAP_MW'], label='historical')
		g = d['ukmo_a1b.%s' % (pcode)].groupby(['MONTH', 'DAY']).mean().reset_index()
		ukmo_a1b, = plot(g.index, g['POWER_CAP_MW'], label='ukmo-a1b')
		g = d['ukmo_a2.%s' % (pcode)].groupby(['MONTH', 'DAY']).mean().reset_index()
		ukmo_a2, = plot(g.index, g['POWER_CAP_MW'], label='ukmo-a2')
		g = d['ukmo_b1.%s' % (pcode)].groupby(['MONTH', 'DAY']).mean().reset_index()
		ukmo_b1, = plot(g.index, g['POWER_CAP_MW'], label='ukmo-b1')
		g = d['echam_a1b.%s' % (pcode)].groupby(['MONTH', 'DAY']).mean().reset_index()
		echam_a1b, = plot(g.index, g['POWER_CAP_MW'], label='echam-a1b')
		g = d['echam_a2.%s' % (pcode)].groupby(['MONTH', 'DAY']).mean().reset_index()
		echam_a2, = plot(g.index, g['POWER_CAP_MW'], label='echam-a2')
		g = d['echam_b1.%s' % (pcode)].groupby(['MONTH', 'DAY']).mean().reset_index()
		echam_b1, = plot(g.index, g['POWER_CAP_MW'], label='echam-b1')
	
		legend(loc=4)
	
		xlim([1,366])
		title('Average daily useable capacity at Station %s' % (pcode))
		xlabel('Day of year')
		ylabel('Useable capacity (MW)')
		
		if not os.path.exists(wpath):
			os.mkdir(wpath)

		plt.savefig('%s/%s.png' % (wpath, pcode), bbox_inches='tight')
		clf()

def post_plot_wind_ct_sum(rpath, wpath, tech, typ):

	li_pcode = list(set([i.split('.')[1] for i in os.listdir(rpath)]))
	li_scen = ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']
	
	df_d = {}

	for scen in li_scen:
		li_2 = [i for i in os.listdir(rpath) if i.split('.')[0] == scen]

		d = {}

		for j in li_2:
			f = pd.read_csv('%s' % (rpath + '/' + j), sep='\t')
			if 'date' in f.columns:
				f = f.dropna(subset=['date'])
				f = f.set_index('date')
#				f = f['POWER_CAP_MW']
			else:
				mkdate =  lambda x: datetime.date(int(x['YEAR']), int(x['MONTH']), int(x['DAY']))
				f['date'] = f.apply(mkdate, axis=1) 
				f = f.set_index('date')
#				f = f['POWER_CAP_MW']

			d.update({j : f})
		
		scen_df = pd.concat([d[i]['POWER_CAP_MW'] for i in d.keys()], axis=1)
		print scen_df
#		print scen_df.columns
#		tc = scen_df.columns
#		stc = (set(tc))
#		dupr = sorted([list(tc).index(i) for i in stc])
#		print dupr
#		scen_df = scen_df.iloc[:, dupr]
		df_d.update({scen : scen_df})

#		hist_li = [d[i] for i in d.keys() if 'hist' in i]
#		ukmo_a1b_li = [d[i] for i in d.keys() if 'ukmo_a1b' in i]
#		ukmo_a2_li = [d[i] for i in d.keys() if 'ukmo_a2' in i]
#		ukmo_b1_li = [d[i] for i in d.keys() if 'ukmo_b1' in i]
#		echam_a1b_li = [d[i] for i in d.keys() if 'echam_a1b' in i]
#		echam_a2_li = [d[i] for i in d.keys() if 'echam_a2' in i]
#		echam_b1_li = [d[i] for i in d.keys() if 'echam_b1' in i]

#		hist_df = pd.concat([d[i] for i in d.keys() if 'hist' in i], axis=1)
#		ukmo_a1b = pd.concat([d[i] for i in d.keys() if 'ukmo_a1b' in i], axis=1) 
#		ukmo_a2 = pd.concat([d[i] for i in d.keys() if 'ukmo_a2' in i], axis=1)  
#		ukmo_b1 = pd.concat([d[i] for i in d.keys() if 'ukmo_b1' in i], axis=1)  
#		echam_a1b = pd.concat([d[i] for i in d.keys() if 'echam_a1b' in i], axis=1)  
#		echam_a2 = pd.concat([d[i] for i in d.keys() if 'echam_a2' in i], axis=1)   
#		echam_b1 = pd.concat([d[i] for i in d.keys() if 'echam_b1' in i], axis=1)  


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

#		print scen_df.columns
#		tc = scen_df.columns
#		stc = (set(tc))
#		dupr = sorted([list(tc).index(i) for i in stc])
#		print dupr
#		scen_df = scen_df.iloc[:, dupr]


#		hist_li = [d[i] for i in d.keys() if 'hist' in i]
#		ukmo_a1b_li = [d[i] for i in d.keys() if 'ukmo_a1b' in i]
#		ukmo_a2_li = [d[i] for i in d.keys() if 'ukmo_a2' in i]
#		ukmo_b1_li = [d[i] for i in d.keys() if 'ukmo_b1' in i]
#		echam_a1b_li = [d[i] for i in d.keys() if 'echam_a1b' in i]
#		echam_a2_li = [d[i] for i in d.keys() if 'echam_a2' in i]
#		echam_b1_li = [d[i] for i in d.keys() if 'echam_b1' in i]

#		hist_df = pd.concat([d[i] for i in d.keys() if 'hist' in i], axis=1)
#		ukmo_a1b = pd.concat([d[i] for i in d.keys() if 'ukmo_a1b' in i], axis=1) 
#		ukmo_a2 = pd.concat([d[i] for i in d.keys() if 'ukmo_a2' in i], axis=1)  
#		ukmo_b1 = pd.concat([d[i] for i in d.keys() if 'ukmo_b1' in i], axis=1)  
#		echam_a1b = pd.concat([d[i] for i in d.keys() if 'echam_a1b' in i], axis=1)  
#		echam_a2 = pd.concat([d[i] for i in d.keys() if 'echam_a2' in i], axis=1)   
#		echam_b1 = pd.concat([d[i] for i in d.keys() if 'echam_b1' in i], axis=1)  


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
	
	if not os.path.exists(wpath):
		os.mkdir(wpath)

	plt.savefig('%s/%s.png' % (wpath, tech), bbox_inches='tight')
	clf()


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

#		print scen_df.columns
#		tc = scen_df.columns
#		stc = (set(tc))
#		dupr = sorted([list(tc).index(i) for i in stc])
#		print dupr
#		scen_df = scen_df.iloc[:, dupr]


#		hist_li = [d[i] for i in d.keys() if 'hist' in i]
#		ukmo_a1b_li = [d[i] for i in d.keys() if 'ukmo_a1b' in i]
#		ukmo_a2_li = [d[i] for i in d.keys() if 'ukmo_a2' in i]
#		ukmo_b1_li = [d[i] for i in d.keys() if 'ukmo_b1' in i]
#		echam_a1b_li = [d[i] for i in d.keys() if 'echam_a1b' in i]
#		echam_a2_li = [d[i] for i in d.keys() if 'echam_a2' in i]
#		echam_b1_li = [d[i] for i in d.keys() if 'echam_b1' in i]

#		hist_df = pd.concat([d[i] for i in d.keys() if 'hist' in i], axis=1)
#		ukmo_a1b = pd.concat([d[i] for i in d.keys() if 'ukmo_a1b' in i], axis=1) 
#		ukmo_a2 = pd.concat([d[i] for i in d.keys() if 'ukmo_a2' in i], axis=1)  
#		ukmo_b1 = pd.concat([d[i] for i in d.keys() if 'ukmo_b1' in i], axis=1)  
#		echam_a1b = pd.concat([d[i] for i in d.keys() if 'echam_a1b' in i], axis=1)  
#		echam_a2 = pd.concat([d[i] for i in d.keys() if 'echam_a2' in i], axis=1)   
#		echam_b1 = pd.concat([d[i] for i in d.keys() if 'echam_b1' in i], axis=1)  


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
	
	if not os.path.exists(wpath):
		os.mkdir(wpath)

	plt.savefig('%s/%s.png' % (wpath, tech), bbox_inches='tight')
	clf()



post_plot_op('/home/chesterlab/Bartos/post/op', '/home/chesterlab/Bartos/post/img/op')

post_plot_wind_ct_sum('/home/chesterlab/Bartos/post/ct', '/home/chesterlab/Bartos/post/img/sum', 'CT_yearly', 'century')
post_plot_wind_ct_sum('/home/chesterlab/Bartos/post/ct', '/home/chesterlab/Bartos/post/img/sum', 'CT_annual', 'annual')
post_plot_wind_ct_sum('/home/chesterlab/Bartos/post/wn', '/home/chesterlab/Bartos/post/img/sum', 'WT_yearly', 'century')
post_plot_wind_ct_sum('/home/chesterlab/Bartos/post/wn', '/home/chesterlab/Bartos/post/img/sum', 'WT_annual', 'annual')
post_plot_wind_ct_sum('/home/chesterlab/Bartos/post/pv', '/home/chesterlab/Bartos/post/img/sum', 'PV_yearly', 'century')
post_plot_wind_ct_sum('/home/chesterlab/Bartos/post/pv', '/home/chesterlab/Bartos/post/img/sum', 'PV_annual', 'annual')
post_plot_hy_sum('/home/chesterlab/Bartos/post/hy', '/home/chesterlab/Bartos/post/img/sum', 'HY_annual', 'annual')
post_plot_hy_sum('/home/chesterlab/Bartos/post/hy', '/home/chesterlab/Bartos/post/img/sum', 'HY_yearly', 'century')
post_plot_hy_sum('/home/chesterlab/Bartos/post/rc', '/home/chesterlab/Bartos/post/img/sum', 'RC_annual', 'annual')
post_plot_hy_sum('/home/chesterlab/Bartos/post/rc', '/home/chesterlab/Bartos/post/img/sum', 'RC_yearly', 'century')


#post_plot('/home/chesterlab/Bartos/post/rc/lees_f', '/home/chesterlab/Bartos/post/img/rc/lees_f')
#post_plot('/home/chesterlab/Bartos/post/rc/colstrip', '/home/chesterlab/Bartos/post/img/rc/colstrip')
post_plot('/home/chesterlab/Bartos/post/rc/wauna', '/home/chesterlab/Bartos/post/img/rc/wauna')
post_plot('/home/chesterlab/Bartos/post/rc/salton', '/home/chesterlab/Bartos/post/img/rc/salton')
post_plot('/home/chesterlab/Bartos/post/rc/pitt', '/home/chesterlab/Bartos/post/img/rc/pitt')

post_plot('/home/chesterlab/Bartos/post/rc/pitt', '/home/chesterlab/Bartos/post/img/rc/pitt')

#b = rbm_post('/media/chesterlab/My Passport/Files/VIC/input/dict/opstn.p', '/media/chesterlab/My Passport/Files/VIC/input/dict/rcstn.p', '/media/chesterlab/storage/post/rbm', '/media/chesterlab/storage/post/st_rc')

#b.make_spat_d()

#b.make_diff()

#b.make_rc_outfiles('hist', 'little_col', '/media/chesterlab/storage/post/wpath') 
