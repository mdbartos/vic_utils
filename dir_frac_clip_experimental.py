#TRY RECODING SUCH THAT INDEX IS SPECIFIED BY LAT/LON

import numpy as np
import pandas as pd
import os
import ast
import pickle

#latlon_c = pickle.load( open('hydrostn.p', 'rb'))

class rout_clip():

	def __init__(self, fns, newname, stn):
		
		self.newname = newname
		self.fns = fns
		self.stn = stn
		self.df_d = {}
		self.spec_d = {}
		self.i_li = []
		self.c_li = []
		self.ndf_d = {}
		self.dirconv = {1:3, 2:4, 4:5, 8:6, 16:7, 32:8, 64:1, 128:2, -9999:0, 0:9}
		self.fracconv = {-9999: 0.00}

	def dir_convert(self, filename):
#		line_li = []
#		new_li = []
		
		popfile = filename.split('.')[0]
		
		if 'dir' in os.listdir('.'):
			pass
		else:
			os.mkdir('./dir')
		
		f = open(filename, 'r')
		head = f.readlines()[:5]
		
		tempfile = open('./dir/%s.asc' % popfile, 'w')
		
		df = pd.read_table(filename, sep=' ', skiprows=6, header=None)
		for i in self.dirconv.keys():
			df.replace(to_replace=i, value=dirconv[i], inplace=True)
		
		st_df = df.to_string(header=False, index=False, index_names=False)
	
		with open('./dir/%s.asc' % popfile, 'w') as tempfile:
			tempfile.write(''.join(head))
			tempfile.write('NODATA_value  0\n')
			tempfile.write(st_df)
		
	def frac_convert(filename):
#		line_li = []
#		new_li = []		
#		df = pd.DataFrame()
		
		popfile = filename.split('.')[0]
		
		if 'frac' in os.listdir('.'):
			pass
		else:
			os.mkdir('./frac')
		
		f = open(filename, 'r')
		tempfile = open('./frac/%s.asc' % popfile, 'w')
		
		df = pd.read_table(filename, sep=' ', skiprows=6, header=None, index=False)
		
		for i in self.fracconv.keys():
			df.replace(to_replace=i, value=fracconv[i], inplace=True)
		
		st_df = df.to_string(header=False, index=False, index_names=False)
	#	print fwf
		
#		for i in range(len(fwf)):
#			line_li.append(list(fwf.ix[i]))
#		
#		for j in line_li:
#			templi = []
#			for k in j:
#				if k in fracconv.keys():
#					templi.append(fracconv[k])
#				else:
#					templi.append(k)
#			new_li.append(templi)
	
	#	print line_li
	#	print new_li
		
		new_s = []
		
		for i in new_li:
			new_s.append(pd.Series(i))
	
	#	print new_s
		
		df = df.append(new_s, ignore_index=True)
	
	#	print df
		
		dfwrite = df.to_csv('dfwrite', sep=' ', header=False, index=False)
		dfread = open('dfwrite', 'r')
		
		head = f.readlines()[:5]
		
		xll = head[2].split()
		yll = head[3].split()
		xll[1] = str(np.round(ast.literal_eval(xll[1]), 3))
		yll[1] = str(np.round(ast.literal_eval(yll[1]), 3))
		
		head[2] = '     '.join(xll) + '\n'
		head[3] = '     '.join(yll)	+ '\n'
		
		for i in head:
			tempfile.write(i)
		
		tempfile.write('NODATA_value  0\n')
		
		for i in dfread.readlines():
			tempfile.write(i)
		
		f.close()
		tempfile.close()
		dfread.close()
		os.remove('./dfwrite')
	
	
	def import_tables(self):
				
		######################
		#CREATE DATAFRAME AND SPEC DICTIONARIES	
		######################	

		for c in self.fns:
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
			nodata = dfhead[5].split()[1]
	
			df_col = [(xll + cellsize/2 + cellsize*i) for i in range(len(df.columns))]
			df['idx'] = [(yll + cellsize/2 + cellsize*i) for i in range(len(df.index))][::-1]
			df = df.set_index('idx')
			df.columns = df_col
			self.df_d.update({c : df})
			self.spec_d.update({c : {}})
			self.spec_d[c].update({'ncol' : ncol, 'nrow' : nrow, 'xll' : xll, 'yll' : yll, 'cellsize' : cellsize, 'nodata' : nodata})
			print c
			print df
	
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

	def idx_tables(self):
		
		for d in self.df_d.keys():
			ndf = self.df_d[d].loc[self.i_li, self.c_li]
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
#			ndf_cols = sorted(list(ndf.columns))
#			ndf[ndf_cols]
		
		##############################
		#FIND STATION LOCATIONS	
		##############################	
	def get_stations(self):
		stnloc = latlon_c[stn]
		
#		lldf = pd.DataFrame(index=self.i_li, columns=self.c_li).sort(axis=0, ascending=False).sort(axis=1, ascending=True)
#		for g in lldf.columns:
#			q = [g for t in lldf[g]] 
#			lldf[g] = zip(lldf.index, q)

		diff_d = {}

		stn_tempfile = open('./%s/%s.stnloc' % (rename, rename), 'w')
		with open('./%s/%s.stnloc' % (rename, rename), 'w') as stn_tempfile:
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
		
		#####################
		#WRITE FILES	
		#####################
	def write_files():
		if rename in os.listdir('.'):
			pass
		else:
			os.mkdir('./%s' % rename)
			
		fracwrite = newfrac_table.to_csv('fracwrite', sep=' ', header=False, index=False)
		
		f_tempfile = open('./%s/%s_frac.asc' % (rename, rename), 'w')
	
		f_tempfile.write('')
		
		f_tempfile.write('ncols         %s\n' % (f_ncol_new))
		f_tempfile.write('nrows         %s\n' % (f_nrow_new))
		f_tempfile.write('xllcorner     %s\n' % (f_xll_new))
		f_tempfile.write('yllcorner     %s\n' % (f_yll_new))
		f_tempfile.write('cellsize      %s\n' % (cellsize))
		f_tempfile.write('NODATA_value  %s\n' % (f_nodata))
	
		fracread = open('fracwrite', 'r')	
		
		for i in fracread.readlines():
			f_tempfile.write(i)
		
		fracread.close()
		f_tempfile.close()
	
		
		dirwrite = newdir_table.to_csv('dirwrite', sep=' ', header=False, index=False)
	
		
		d_tempfile = open('./%s/%s_dir.asc' % (rename, rename), 'w')
	
		d_tempfile.write('')
		
		d_tempfile.write('ncols         %s\n' % (d_ncol_new))
		d_tempfile.write('nrows         %s\n' % (d_nrow_new))
		d_tempfile.write('xllcorner     %s\n' % (d_xll_new))
		d_tempfile.write('yllcorner     %s\n' % (d_yll_new))
		d_tempfile.write('cellsize      %s\n' % (cellsize))
		d_tempfile.write('NODATA_value  %s\n' % (d_nodata))
		
		dirread = open('dirwrite', 'r')
		
		for i in dirread.readlines():
			d_tempfile.write(i)
		
		dirread.close()
		d_tempfile.close()
		
		del fracread
		del dirread
	
#	os.remove('./fracwrite')
#	os.remove('./dirwrite')
	
	
#####################################################

dir_frac_clip('castaic_frac.asc', 'castaic_dir.asc', 'castaic', 'castaic')
dir_frac_clip('corona_frac.asc', 'corona_dir.asc', 'corona', 'corona')
dir_frac_clip('cottonwood_frac.asc', 'cottonwood_dir.asc', 'cottonwood', 'cottonwood')
dir_frac_clip('coyotecr_frac.asc', 'coyotecr_dir.asc', 'coyotecr', 'coyotecr')
dir_frac_clip('kern_frac.asc', 'kern_dir.asc', 'kern', 'kern')
dir_frac_clip('pitt_frac.asc', 'pitt_dir.asc', 'pitt', 'pitt')
dir_frac_clip('redmtn_frac.asc', 'redmtn_dir.asc', 'redmtn', 'redmtn')
dir_frac_clip('riohondo_frac.asc', 'riohondo_dir.asc', 'riohondo', 'riohondo')
dir_frac_clip('rushcr_frac.asc', 'rushcr_dir.asc', 'rushcr', 'rushcr')
dir_frac_clip('tulare_frac.asc', 'tulare_dir.asc', 'tulare', 'tulare')
dir_frac_clip('gila_imp_frac.asc', 'gila_imp_dir.asc', 'gila_imp', 'gila_imp')
