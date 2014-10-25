import pandas as pd
import numpy as np
import os
import pickle
import datetime

class heat_map_extract():
	def __init__(self, post_pp_path, rc_d_path, op_d_path, hy_d_path):
		self.post_pp_d = pickle.load( open(post_pp_path, 'rb')) 

		self.rc = pickle.load( open(rc_d_path, 'rb'))
		self.op = pickle.load( open(op_d_path, 'rb'))
		self.ct = self.post_pp_d['ct']
		self.wn = self.post_pp_d['wn']
		self.pv = self.post_pp_d['pv']
		self.hy = pickle.load( open(hy_d_path, 'rb'))

		self.rc_d = {}
		self.op_d = {}
		self.ct_d = {}
		self.wn_d = {}
		self.pv_d = {}
		self.hy_d = {}
		self.ll_d = {}

		self.comb_df = {}

	def get_rc(self, rcpath, startdate, enddate):
		
		timeslice = pd.date_range(start=startdate, end=enddate)
	
		for basin in self.rc.keys():
			self.rc[basin] = self.rc[basin].set_index('PCODE')
			for pcode in self.rc[basin].index:
				self.rc_d.update( {pcode : {}} )
				for scen in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:
					handle_str = '%s.%s' % (scen, int(pcode))
					if handle_str in os.listdir('%s/%s' % (rcpath, basin)):
						df = pd.read_csv('%s/%s/%s.%s' % (rcpath, basin, scen, int(pcode)), sep='\t', index_col=0)
						df['DATE'] = pd.to_datetime(df.index)
						print df
						if scen == 'hist':
							df = df.set_index('DATE')
						else:
							df = df.set_index('DATE').loc[timeslice]
						summer_mean = df.groupby('MONTH').mean()['POWER_CAP_MW'].loc[[6,7,8]].mean()
						self.rc_d[pcode].update({ scen : summer_mean })
						self.ll_d.update( {pcode : {'lat' : self.rc[basin].loc[pcode, 'latlon'][0], 'lon' : self.rc[basin].loc[pcode, 'latlon'][1]}} )


	def get_op(self, oppath, startdate, enddate):
		
		timeslice = pd.date_range(start=startdate, end=enddate)
	
		for basin in self.op.keys():
			self.op[basin] = self.op[basin].set_index('PCODE')
			for pcode in self.op[basin].index:
				self.op_d.update( {pcode : {}} )
				for scen in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:
					handle_str = '%s.%s' % (scen, int(pcode))
					if handle_str in os.listdir(oppath):
						df = pd.read_csv('%s/%s.%s' % (oppath, scen, int(pcode)), sep='\t', index_col=0)
						df['DATE'] = pd.to_datetime(df.index)
						if scen == 'hist':
							df = df.set_index('DATE')
						else:
							df = df.set_index('DATE').loc[timeslice]
						summer_mean = df.groupby('MONTH').mean()['POWER_CAP_MW'].loc[[6,7,8]].mean()
						self.op_d[pcode].update({ scen : summer_mean })
						self.ll_d.update( {pcode : {'lat' : self.op[basin].loc[pcode, 'latlon'][0], 'lon' : self.op[basin].loc[pcode, 'latlon'][1]}} )


	def get_hy(self, hypath, startdate, enddate):
		
		timeslice = pd.date_range(start=startdate, end=enddate)
	
		for basin in self.hy.keys():
			hy_reindex = self.hy[basin].set_index('PCODE')
			if os.path.exists('%s/%s' % (hypath, basin)):
				for pcode in hy_reindex.index:
					self.hy_d.update( {pcode : {}} )
					for scen in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:
						handle_str = '%s.%s' % (scen, int(pcode))
						if handle_str in os.listdir('%s/%s' % (hypath, basin)):
							df = pd.read_csv('%s/%s/%s.%s' % (hypath, basin, scen, int(pcode)), sep='\t')
							df['date'] = pd.to_datetime(df['date'])
							if scen == 'hist':
								df = df.set_index('date')
							else:
								df = df.set_index('date').loc[timeslice]
							summer_mean = df.groupby('month').mean()['POWER_CAP_MW'].mean()
							self.hy_d[pcode].update({ scen : summer_mean })
							self.ll_d.update( {pcode : {'lat' : hy_reindex.loc[int(pcode), 'latlon'][0], 'lon' : hy_reindex.loc[int(pcode), 'latlon'][1]}} )

	def get_ct(self, ctpath, startdate, enddate):
	
		timeslice = pd.date_range(start=startdate, end=enddate)
	
		for pcode in self.ct.index:
			self.ct_d.update( {pcode : {}} )
			for scen in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:
				handle_str = '%s.%s' % (scen, int(pcode))
				if handle_str in os.listdir(ctpath):
					df = pd.read_csv('%s/%s.%s' % (ctpath, scen, int(pcode)), sep='\t')
					df['date'] = pd.to_datetime(df['date'])
					if scen == 'hist':
						df = df.set_index('date')
					else:
						df = df.set_index('date').loc[timeslice]
					df['month'] = [i.month for i in df.index]
					summer_mean = df.groupby('month').mean()['POWER_CAP_MW'].loc[[6,7,8]].mean()
					self.ct_d[pcode].update({ scen : summer_mean })
					self.ll_d.update( {pcode : {'lat' : self.ct.loc[pcode]['LAT'], 'lon' : self.ct.loc[pcode]['LON']}} )

	def get_wn(self, wnpath, startdate, enddate):
	
		timeslice = pd.date_range(start=startdate, end=enddate)
	
		for pcode in self.wn.index:
			self.wn_d.update( {pcode : {}} )
			for scen in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:
				handle_str = '%s.%s' % (scen, int(pcode))
				if handle_str in os.listdir(wnpath):
					df = pd.read_csv('%s/%s.%s' % (wnpath, scen, int(pcode)), sep='\t')
					df['date'] = pd.to_datetime(df['date'])
					if scen == 'hist':
						df = df.set_index('date')
					else:
						df = df.set_index('date').loc[timeslice]
					df['month'] = [i.month for i in df.index]
					summer_mean = df.groupby('month').mean()['POWER_CAP_MW'].loc[[6,7,8]].mean()
					self.wn_d[pcode].update({ scen : summer_mean })
					self.ll_d.update( {pcode : {'lat' : self.wn.loc[pcode]['LAT'], 'lon' : self.wn.loc[pcode]['LON']}} )

	def get_pv(self, pvpath, startdate, enddate):
	
		timeslice = pd.date_range(start=startdate, end=enddate)

		mkdate = lambda x: datetime.date(int(x['YEAR']), int(x['MONTH']), int(x['DAY']))	
		
		for pcode in self.pv.index:
			self.pv_d.update( {pcode : {}} )
			for scen in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:
				handle_str = '%s.%s' % (scen, int(pcode))
				if handle_str in os.listdir(pvpath):
					df = pd.read_csv('%s/%s.%s' % (pvpath, scen, int(pcode)), sep='\t')
					df['date'] = df.apply(mkdate, axis=1)
					if scen == 'hist':
						df = df.set_index('date')
					else:
						df = df.set_index('date').loc[timeslice]
					df['month'] = [i.month for i in df.index]
					summer_mean = df.groupby('month').mean()['POWER_CAP_MW'].loc[[6,7,8]].mean()
					self.pv_d[pcode].update({ scen : summer_mean })
					self.ll_d.update( {pcode : {'lat' : self.pv.loc[pcode]['LAT'], 'lon' : self.pv.loc[pcode]['LON']}} )	
	
	def make_output_table(self):

		rc_df = pd.DataFrame.from_dict(self.rc_d, orient='index').reset_index()			
		op_df = pd.DataFrame.from_dict(self.op_d, orient='index').reset_index()		
		hy_df = pd.DataFrame.from_dict(self.hy_d, orient='index').reset_index()		
		ct_df = pd.DataFrame.from_dict(self.ct_d, orient='index').reset_index()		
		wn_df = pd.DataFrame.from_dict(self.wn_d, orient='index').reset_index()		
		pv_df = pd.DataFrame.from_dict(self.pv_d, orient='index').reset_index()			
	
		ll_df = pd.DataFrame.from_dict(self.ll_d, orient='index')   

		comb_df = pd.concat([rc_df, op_df, hy_df, ct_df, wn_df, pv_df]).groupby('index').sum()
		comb_df = pd.concat([comb_df, ll_df], axis=1)
		self.comb_df = comb_df

b = heat_map_extract('/home/chesterlab/Bartos/VIC/input/dict/post_pp_d.p', '/home/chesterlab/Bartos/VIC/input/dict/rcstn.p', '/home/chesterlab/Bartos/VIC/input/dict/opstn.p', '/home/chesterlab/Bartos/VIC/input/dict/hydrostn.p')

sd = datetime.date(2040, 1, 1)
ed = datetime.date(2060, 1, 1)

b.get_rc('/home/chesterlab/Bartos/post/rc' , sd, ed)
b.get_op('/home/chesterlab/Bartos/post/op' , sd, ed)
b.get_hy('/home/chesterlab/Bartos/post/hy' , sd, ed)
b.get_ct('/home/chesterlab/Bartos/post/ct' , sd, ed)
b.get_wn('/home/chesterlab/Bartos/post/wn' , sd, ed)
b.get_pv('/home/chesterlab/Bartos/post/pv' , sd, ed)
b.make_output_table()

