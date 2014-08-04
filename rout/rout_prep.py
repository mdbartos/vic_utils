#TRY RECODING SUCH THAT INDEX IS SPECIFIED BY LAT/LON

import numpy as np
import pandas as pd
import os
import ast
import pickle

#latlon_c = pickle.load( open('hydrostn.p', 'rb'))

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
			
		self.dirconv = {1:3, 2:4, 4:5, 8:6, 16:7, 32:8, 64:1, 128:2, -9999: self.nd, 0: self.nd}
		self.fracconv = {-9999: self.nd}

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
			print k
			print df

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
			print k
			print df			
		

	def convert_dir_internal(self, dirtable):
		for i in self.dirconv.keys():
			dirtable.replace(to_replace=i, value=self.dirconv[i], inplace=True)
		self.spec_d['dir']['nodata'] = int(self.nd)
		
	
	def convert_frac_internal(self, fractable):
		for i in self.fracconv.keys():
			fractable.replace(to_replace=i, value=self.fracconv[i], inplace=True)
		self.spec_d['frac']['nodata'] = float(self.nd)
			
#	def convert_rbm_internal(self, ctables):
#		for n, j in ctables.items():
#			for i in self.fracconv.keys():
#				j.replace(to_replace=i, value=self.fracconv[i], inplace=True)
#			self.spec_d[n]['nodata'] = -1

		######################
		#COMBINE INDICES	
		######################
	def combine_idx(self):

		for d in self.df_d.keys():
			self.i_li.extend([i for i in self.df_d[d].index])
			self.c_li.extend([i for i in self.df_d[d].columns])
			self.i_li = sorted(list(set(self.i_li)))
			self.c_li = sorted(list(set(self.c_li)))
			print self.i_li
			print self.c_li
			
		######################
		#INDEX NEW TABLES	
		######################

	def idx_tables(self, table_d):
		
		for d in table_d.keys():
			ncellsize = self.spec_d[d]['cellsize']
			nnodata = self.spec_d[d]['nodata']
			ndf = table_d[d].loc[self.i_li, self.c_li]
			print ndf
			ndf = ndf.sort(axis=0, ascending=False).sort(axis=1, ascending=True)
			for i in ndf.columns:
				coltype = type(ndf[i].iloc[0])
				fillzero = 0
				fillzero = coltype(fillzero)
#				print fillzero
				ndf[i].fillna(value=fillzero, inplace=True)
			print d
			print ndf
			self.ndf_d.update({d : ndf})
			self.nspec_d.update({d : {}})
			self.nspec_d[d].update({'cellsize' : ncellsize, 'ncol' : len(ndf.columns), 'nrow' : len(ndf.index), 'xll' : (min(ndf.index) - ncellsize/2), 'yll' : (min(ndf.columns) - ncellsize/2), 'nodata' : nnodata})
			
#			ndf_cols = sorted(list(ndf.columns))
#			ndf[ndf_cols]
		
		##############################
		#FIND STATION LOCATIONS	
		##############################	
	def get_stations(self, srpath, swpath):
		stnlocs = pickle.load( open(srpath, 'rb'))
		stnloc = stnlocs[self.newname]
		
#		lldf = pd.DataFrame(index=self.i_li, columns=self.c_li).sort(axis=0, ascending=False).sort(axis=1, ascending=True)
#		for g in lldf.columns:
#			q = [g for t in lldf[g]] 
#			lldf[g] = zip(lldf.index, q)

		diff_d = {}

		with open('%s/%s.stnloc' % (swpath, self.newname), 'w') as stn_tempfile:
			for p in stnloc.iterrows():
				for x in self.c_li:
					for i in self.i_li:
						lo = tuple([i,x])
	#					print lo
						diff = ((lo[0] - p[1][2][0])**2 + (lo[1] - p[1][2][1])**2)**0.5
						diff_d.update({(i, x) : diff})
			
				cell = min(diff_d, key=diff_d.get)
				rowno = self.i_li.index(cell[0]) + 1
				colno = self.c_li.index(cell[1]) + 1
				stn_tempfile.write("1 %s            %s %s -9999\nNONE\n" % (p[1][3], colno, rowno))
	#			print 'row:', cellno[0]+1, 'col:', cellno[1]+1

	def set_bounds(self):
		dfbound = self.ndf_d['frac'] == self.nd
		b.ndf_d['dir'][dfbound] = self.nd
		
		#################################
		#PREP OUTPUT TABLES
		#################################
		
	def prep_tables(self):
		self.import_tables()
		self.convert_dir_internal(self.df_d['dir'])
		self.convert_frac_internal(self.df_d['frac'])
		self.combine_idx()
		self.idx_tables(self.df_d)
		self.idx_tables(self.cl_d)
		self.set_bounds()
		
		#####################
		#WRITE FILES	
		#####################
	def write_files(self, ascpath):
		if self.newname in os.listdir('.'):
			pass
		else:
			os.mkdir('./%s' % self.newname)
		
		for i in self.ndf_d.keys():
			with open('%s/%s_%s' % (ascpath, self.newname, i), 'w') as outfile:
				outfile.write('ncols         %s\n' % (self.nspec_d[i]['ncol']))
				outfile.write('nrows         %s\n' % (self.nspec_d[i]['nrow']))
				outfile.write('xllcorner     %s\n' % (self.nspec_d[i]['xll']))
				outfile.write('yllcorner     %s\n' % (self.nspec_d[i]['yll']))
				outfile.write('cellsize      %s\n' % (self.nspec_d[i]['cellsize']))
				outfile.write('NODATA_value  %s\n' % (self.nspec_d[i]['nodata']))
				st_df = str(self.ndf_d[i].to_string(header=False, index=False, index_names=False, justify='left'))
				st_df = st_df[1:].replace('\n ', '\n').replace('  ', ' ')
				outfile.write(st_df)

b = rout_prep({'dir' : '/home/melchior/Desktop/ascii_16d/pitt_d.asc', 'frac' : '/home/melchior/Desktop/ascii_16d/pitt_f.asc'}, {'alpha' : '/home/melchior/Desktop/ascii_16d/bayeskrig_a.txt', 'beta' : '/home/melchior/Desktop/ascii_16d/bayeskrig_b.txt', 'gamma' : '/home/melchior/Desktop/ascii_16d/bayeskrig_g.txt', 'mu' : '/home/melchior/Desktop/ascii_16d/bayeskrig_u.txt'}, 'pitt')
b.prep_tables()
b.get_stations('/home/melchior/Desktop/hydrostn.p', '/home/melchior/Desktop/wpath')
b.write_files('/home/melchior/Desktop/wpath')
