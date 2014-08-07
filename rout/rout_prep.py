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
			ndf = table_d[d].loc[self.i_li].loc[:, self.c_li]
			#print ndf
			ndf = ndf.sort(axis=0, ascending=False).sort(axis=1, ascending=True)
			for i in ndf.columns:
				coltype = type(ndf[i].iloc[0])
				fillzero = self.nd
				fillzero = coltype(fillzero)		
#				print fillzero
				ndf[i].fillna(value=fillzero, inplace=True)
			#print d
			#print ndf
			self.ndf_d.update({d : ndf})
			self.nspec_d.update({d : {}})
			self.nspec_d[d].update({'cellsize' : ncellsize, 'ncol' : len(ndf.columns), 'nrow' : len(ndf.index), 'yll' : (min(ndf.index) - ncellsize/2), 'xll' : (min(ndf.columns) - ncellsize/2), 'nodata' : nnodata})
			
#			ndf_cols = sorted(list(ndf.columns))
#			ndf[ndf_cols]
		
		##############################
		#FIND STATION LOCATIONS	
		##############################	
	def get_stations(self, srpath, swpath):
		stnlocs = pickle.load( open(srpath, 'rb'))
		if self.newname in stnlocs.keys():
			stnloc = stnlocs[self.newname]
			if not os.path.exists(swpath):
				os.mkdir(swpath)
#			lldf = pd.DataFrame(index=self.i_li, columns=self.c_li).sort(axis=0, ascending=False).sort(axis=1, ascending=True)
#			for g in lldf.columns:
#				q = [g for t in lldf[g]] 
#				lldf[g] = zip(lldf.index, q)

			diff_d = {}

			with open('%s/%s.stnloc' % (swpath, self.newname), 'w') as stn_tempfile:
				for p in stnloc.iterrows():
					for x in self.c_li:
						for i in self.i_li:
							lo = tuple([i,x])
	#						print lo
							diff = ((lo[0] - p[1][2][0])**2 + (lo[1] - p[1][2][1])**2)**0.5
							diff_d.update({(i, x) : diff})
				
					cell = min(diff_d, key=diff_d.get)
					rowno = self.i_li.index(cell[0]) + 1
					colno = self.c_li.index(cell[1]) + 1
					stn_tempfile.write("1 %s            %s %s -9999\nNONE\n" % (p[1][3], colno, rowno))
	#				print 'row:', cellno[0]+1, 'col:', cellno[1]+1
		else:
			pass

	def set_bounds(self):
		dfbound = self.ndf_d['frac'] == self.nd
		self.ndf_d['dir'][dfbound] = self.nd

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
				st_df = st_df[1:].replace('\n ', '\n').replace('  ', ' ')
				outfile.write(st_df)



#1/16 degree

li = list(set(['_'.join(i.split('_')[:-1]) for i in os.listdir('/home/chesterlab/Bartos/pre/ascii_16d')]))

for a in li:
	b = rout_prep({'frac' : '/home/chesterlab/Bartos/pre/ascii_16d/%s_f.asc' % (a)}, {'dir' : '/home/chesterlab/Bartos/VIC/input/rout/src_data/flowdir_16d.asc', 'alpha' : '/home/chesterlab/Bartos/VIC/input/rbm/mohseni/d16/bayeskrig_a.txt', 'beta' : '/home/chesterlab/Bartos/VIC/input/rbm/mohseni/d16/bayeskrig_b.txt', 'gamma' : '/home/chesterlab/Bartos/VIC/input/rbm/mohseni/d16/bayeskrig_g.txt', 'mu' : '/home/chesterlab/Bartos/VIC/input/rbm/mohseni/d16/bayeskrig_u.txt'}, a)
	b.prep_tables()
	b.get_stations('/home/chesterlab/Bartos/VIC/input/dict/hydrostn.p', '/home/chesterlab/Bartos/VIC/input/rout/d16/%s' % (a))
	b.write_files('/home/chesterlab/Bartos/VIC/input/rout/d16/%s' % (a))
	del b


#1/8 degree

li = list(set(['_'.join(i.split('_')[:-1]) for i in os.listdir('/home/chesterlab/Bartos/pre/ascii_8d')]))

for a in li:
	b = rout_prep({'frac' : '/home/chesterlab/Bartos/pre/ascii_8d/%s_f.asc' % (a)}, {'dir' : '/home/chesterlab/Bartos/VIC/input/rout/src_data/flowdir_8d.asc', 'alpha' : '/home/chesterlab/Bartos/VIC/input/rbm/mohseni/d8/bayeskrig_a.txt', 'beta' : '/home/chesterlab/Bartos/VIC/input/rbm/mohseni/d8/bayeskrig_b.txt', 'gamma' : '/home/chesterlab/Bartos/VIC/input/rbm/mohseni/d8/bayeskrig_g.txt', 'mu' : '/home/chesterlab/Bartos/VIC/input/rbm/mohseni/d8/bayeskrig_u.txt'}, a)
	b.prep_tables()
	b.get_stations('/home/chesterlab/Bartos/VIC/input/dict/hydrostn.p', '/home/chesterlab/Bartos/VIC/input/rout/d8/%s' % (a))
	b.write_files('/home/chesterlab/Bartos/VIC/input/rout/d8/%s' % (a))
	del b


#RBM

li = os.listdir('/media/melchior/BALTHASAR/nsf_hydro/VIC/output/full-energy/hist')  

outlet_d = \
{'baker': [48.522917, -121.951158],
 'billw': [34.209146, -113.608841],
 'brigham': [41.405775, -112.827558],
 'castaic': [34.399037, -118.784297],
 'colstrip': [46.254606, -106.715845],
 'comanche': [38.264583, -104.535417],
 'corona': [33.882482, -117.663351],
 'cottonwood': [36.465939, -117.94375],
 'coyotecr': [33.788092, -118.089583],
 'davis': [35.198558, -114.565003],
 'eaglept': [42.510417, -122.840234],
 'elwha': [48.098935, -123.555232],
 'gc': [36.11875, -112.084781],
 'gila_imp': [32.735053, -114.465405],
 'glenn': [42.947917, -115.297917],
 'guer': [42.202083, -104.502083],
 'hmjack': [48.019592, -122.189583],
 'hoover': [36.031796, -114.721969],
 'imperial': [32.892721, -114.466957],
 'intermtn': [38.989061, -113.122394],
 'irongate': [41.922742, -122.43533],
 'kern': [35.389583, -119.037057],
 'lahontan': [39.522221, -118.739583],
 'lees_f': [36.86185, -111.588661],
 'little_col': [35.916685, -111.580886],
 'paper': [46.438448, -116.98125],
 'paria': [36.873747, -111.595799],
 'parker': [34.305715, -114.139496],
 'pawnee': [40.297917, -103.639071],
 'peck': [48.027083, -105.989583],
 'pitt': [38.046113, -121.895622],
 'redmtn': [33.327083, -117.33125],
 'riohondo': [33.941766, -118.170734],
 'rushcr': [38.025318, -118.999682],
 'salton': [33.331882, -115.83125],
 'sodasprings': [43.294926, -122.496699],
 'tulare': [36.041109, -119.635417],
 'virgin': [36.893115, -113.924861],
 'wabuska': [39.140158, -119.155675],
 'wauna': [46.19375, -123.38125],
 'yelm': [47.042985, -122.677083]}


for a in li:
	b = rout_prep({'frac' : '/home/chesterlab/Bartos/pre/ascii_8d/%s_f.asc' % (a)}, {'dir' : '/home/chesterlab/Bartos/VIC/input/rout/src_data/flowdir_8d.asc', 'alpha' : '/home/chesterlab/Bartos/VIC/input/rbm/mohseni/d8/bayeskrig_a.txt', 'beta' : '/home/chesterlab/Bartos/VIC/input/rbm/mohseni/d8/bayeskrig_b.txt', 'gamma' : '/home/chesterlab/Bartos/VIC/input/rbm/mohseni/d8/bayeskrig_g.txt', 'mu' : '/home/chesterlab/Bartos/VIC/input/rbm/mohseni/d8/bayeskrig_u.txt'}, a, rbm=True, outlet=outlet_d[a])
	b.prep_tables()
	b.write_files('/home/chesterlab/Bartos/VIC/input/rbm/run/d8/%s' % (a))
	del b


