import numpy as np
import pandas as pd
import os
import ast
import pickle

class rout_prep():

	def __init__(self, fns_idx, fns_clip, newname, **kwargs):
		
		self.newname = newname
		self.fns_idx = fns_idx
		self.fns_clip = fns_clip
		self.df_d = {}
		self.cl_d = {}
		self.spec_d = {}
		self.i_li = []
		self.c_li = []
		self.ndf_d = {}
		self.nspec_d = {}
		if 'outlet' in kwargs:
			self.outlet = kwargs['outlet']
		if 'nd' in kwargs:
			self.nd = kwargs['nd']
		else:
			self.nd = 0
		if 'rbm' in kwargs:
			self.rbm = kwargs['rbm']
		else:
			self.rbm = False
		if self.rbm == True:
			self.nd = -1
		if 'stnloc' in kwargs:
			self.stnloc = pickle.load(open(kwargs['stnloc'], 'rb'))
			
		self.dirconv = {1:3, 2:4, 4:5, 8:6, 16:7, 32:8, 64:1, 128:2, -9999: self.nd, 0: self.nd}
		self.fracconv = {-9999: self.nd}
		print self.newname

	def round_multiple(self, rnum, rprec, rbase):
		return round(rbase * round(float(rnum)/rbase), rprec)
		
	def import_tables(self):
				
		######################
		#CREATE DATAFRAME AND SPEC DICTIONARIES	
		######################	

		for k, c in self.fns_idx.items():
			df = pd.read_table(c, sep=' ', skiprows=6, header=None)
			df = df.dropna(axis=1)
			
			df_o = open(c, 'r')	
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
			self.df_d.update({k : df})
			self.spec_d.update({k : {}})
			self.spec_d[k].update({'ncol' : ncol, 'nrow' : nrow, 'xll' : xll, 'yll' : yll, 'cellsize' : cellsize, 'nodata' : nodata})
			#print k
			#print df

		for k, c in self.fns_clip.items():
			df = pd.read_table(c, sep=' ', skiprows=6, header=None)
			df = df.dropna(axis=1)
			
			df_o = open(c, 'r')	
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
			self.cl_d.update({k : df})
			self.spec_d.update({k : {}})
			self.spec_d[k].update({'ncol' : ncol, 'nrow' : nrow, 'xll' : xll, 'yll' : yll, 'cellsize' : cellsize, 'nodata' : nodata})
			#print k
			#print df			
		

	def convert_dir_internal(self, dirtable):
		for i in dirtable.columns:
			dirtable[i] = dirtable[i].map(self.dirconv)
		self.spec_d['dir']['nodata'] = int(self.nd)
		
	
	def convert_frac_internal(self, fractable):
		for i in self.fracconv.keys():
			fractable.replace(to_replace=i, value=self.fracconv[i], inplace=True)
		self.spec_d['frac']['nodata'] = float(self.nd)
			
		######################
		#COMBINE INDICES	
		######################
	def combine_idx(self):

		for d in self.df_d.keys():
			self.i_li.extend([i for i in self.df_d[d].index])
			self.c_li.extend([i for i in self.df_d[d].columns])
			self.i_li = sorted(list(set(self.i_li)))
			self.c_li = sorted(list(set(self.c_li)))
			#print self.i_li
			#print self.c_li
			
		######################
		#INDEX NEW TABLES	
		######################

	def idx_tables(self, table_d):
		
		for d in table_d.keys():
			ncellsize = self.spec_d[d]['cellsize']
			nnodata = self.spec_d[d]['nodata']
			ndf = table_d[d].loc[self.i_li].loc[:, self.c_li]
			ndf = ndf.sort(axis=0, ascending=False).sort(axis=1, ascending=True)
			for i in ndf.columns:
				coltype = type(ndf[i].iloc[0])
				fillzero = self.nd
				fillzero = coltype(fillzero)		
				ndf[i].fillna(value=fillzero, inplace=True)

			self.ndf_d.update({d : ndf})
			self.nspec_d.update({d : {}})
			self.nspec_d[d].update({'cellsize' : ncellsize, 'ncol' : len(ndf.columns), 'nrow' : len(ndf.index), 'yll' : (min(ndf.index) - ncellsize/2), 'xll' : (min(ndf.columns) - ncellsize/2), 'nodata' : nnodata})
			

	def fix_stnames(self):		
		for i, v in self.stnloc.items():
			v['slug'] = [str(j).split(' ')[0][:5] for j in v['PNAME']]
			da = []
			for o, x in v.ix[v.duplicated(subset=['slug'])]['slug'].iteritems():
				#print x
				da.append(x)
				n = da.count(x)
				if len(x) < 5:
					print x
					self.stnloc[i].ix[o, 'slug'] = x + str(n)
				elif (len(x) >= 5):
					print x
					self.stnloc[i].ix[o, 'slug'] = x[:4] + str(n)

		##############################
		#FIND STATION LOCATIONS	
		##############################	
	def get_stations(self, swpath, **stnkwargs):
		if 'typemarker' in stnkwargs:
			typemarker = stnkwargs['typemarker']
			stnfile_name = self.newname + '_' + typemarker
		else:
			stnfile_name = self.newname
		if self.newname in self.stnloc.keys():
			stnloc = self.stnloc[self.newname]
			if not os.path.exists(swpath):
				os.mkdir(swpath)

			diff_d = {}

			with open('%s/%s.stnloc' % (swpath, stnfile_name), 'w') as stn_tempfile:
				for p in stnloc.iterrows():
					for x in self.c_li:
						for i in self.i_li:
							lo = tuple([i,x])
							diff = ((lo[0] - p[1][2][0])**2 + (lo[1] - p[1][2][1])**2)**0.5
							diff_d.update({(i, x) : diff})
				
					cell = min(diff_d, key=diff_d.get)
					rowno = self.i_li.index(cell[0]) + 1
					colno = self.c_li.index(cell[1]) + 1
					stn_tempfile.write("1 %s            %s %s -9999\nNONE\n" % (p[1][3], colno, rowno))
		else:
			pass

	def set_bounds(self):
		dfbound = self.ndf_d['frac'] == self.nd
		self.ndf_d['dir'][dfbound] = self.nd

	def check_forcings(self, chkdir):
		internal_latlon = []
		df_internal = self.ndf_d['frac'][self.ndf_d['frac'] != self.nd]
		for i in df_internal.columns:
			int_row = df_internal[i].dropna().index
			for j in int_row:
				internal_latlon.append(str(tuple([j, i])))
		f_li = [str(tuple([ast.literal_eval(fn.split('_')[-2]), ast.literal_eval(fn.split('_')[-1])])) for fn in os.listdir(chkdir)]
		print [x for x in internal_latlon if not x in f_li]

	def set_outlet(self):
		olat = self.outlet[0]
		olon = self.outlet[1]
		diff_d = {}
		for x in self.c_li:
			for y in self.i_li:
				diff = ((y - olat)**2 + (x - olon)**2)**0.5
				diff_d.update({(y, x) : diff})
		cell = min(diff_d, key=diff_d.get)
		self.ndf_d['dir'].loc[cell[0], cell[1]] = 9

		#################################
		#PREP OUTPUT TABLES
		#################################
		
	def prep_tables(self):
		self.import_tables()
		self.convert_dir_internal(self.cl_d['dir'])
		self.convert_frac_internal(self.df_d['frac'])
		self.combine_idx()
		self.idx_tables(self.df_d)
		self.idx_tables(self.cl_d)
		self.set_bounds()
		if self.rbm == True:
			self.set_outlet()
		
		#####################
		#WRITE FILES	
		#####################
	def write_files(self, ascpath):
		if not os.path.exists(ascpath):
			os.mkdir(ascpath)
		for i in self.ndf_d.keys():
			with open('%s/%s.%s' % (ascpath, self.newname, i), 'w') as outfile:
				outfile.write('ncols         %s\n' % (self.nspec_d[i]['ncol']))
				outfile.write('nrows         %s\n' % (self.nspec_d[i]['nrow']))
				outfile.write('xllcorner     %s\n' % (self.nspec_d[i]['xll']))
				outfile.write('yllcorner     %s\n' % (self.nspec_d[i]['yll']))
				outfile.write('cellsize      %s\n' % (self.nspec_d[i]['cellsize']))
				outfile.write('NODATA_value  %s\n' % (self.nspec_d[i]['nodata']))
				st_df = str(self.ndf_d[i].to_string(header=False, index=False, index_names=False, justify='left'))
				st_df = st_df.replace('\n ', '\n').replace('  ', ' ')
				if st_df[0] == ' ' or '\t':
					st_df = st_df[1:]
				outfile.write(st_df)
