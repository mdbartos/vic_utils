import numpy as np
import pandas as pd
import os
import ast
import pickle

latlon_c = pickle.load( open('hydrostn.p', 'rb'))

def dir_frac_clip(fracname, dirname, rename, stn):
	
	df = pd.DataFrame()
	
	if rename in os.listdir('.'):
		pass
	else:
		os.mkdir('./%s' % rename)
	
	fracfile_o = open(fracname, 'r')

	######################
	#CREATE FRAC DATAFRAME	
	######################	
	
	fractable = pd.read_table(fracname, sep=' ', skiprows=6, header=None)
	fractable = fractable.dropna(axis=1)
	
	fracfile_o = open(fracname, 'r')
	
	frachead = fracfile_o.readlines()[:6]
	
	f_ncol = int(frachead[0].split()[1])
	f_nrow = int(frachead[1].split()[1])
	f_xll = round(float(frachead[2].split()[1]), 3)
	f_yll = round(float(frachead[3].split()[1]), 3)
	cellsize = round(float(frachead[4].split()[1]), 3)
	f_nodata = frachead[5].split()[1]

	fractable['id'] = range(f_nrow)[::-1]
	fractable = fractable.set_index('id')
	print fractable

	
	fracfile_o.close()

	fracli = []
		
	for i in range(f_ncol):
		tupli = []
		for j in range(f_nrow):
			yi = f_yll + cellsize*j
			xi = f_xll + cellsize*i
			z = str(tuple([yi, xi]))
			tupli.append(z)
		fracli.append(tupli[::-1])

	frac_s = []
	for i in fracli:
		j = pd.Series(i)
		frac_s.append(j)
		
#	print frac_s
		
	frac_ll_table = pd.concat(frac_s, axis=1)
	frac_ll_table['id'] = range(f_nrow)[::-1]
	frac_ll_table = frac_ll_table.set_index('id')
#	print frac_ll_table


	######################
	#CREATE DIR DATAFRAME	
	######################	
	

	dirfile_o = open(dirname, 'r')
#	f_tempfile = open('./frac/%s.asc' % popfile, 'w')
	
	dirtable = pd.read_table(dirname, sep=' ', skiprows=6, header=None)
	dirtable = dirtable.dropna(axis=1)
	

	
	dirfile_o = open(dirname, 'r')
	
	dirhead = dirfile_o.readlines()[:6]
	
	d_ncol = int(dirhead[0].split()[1])
	d_nrow = int(dirhead[1].split()[1])
	d_xll = round(float(dirhead[2].split()[1]), 3)
	d_yll = round(float(dirhead[3].split()[1]), 3)
	d_nodata = dirhead[5].split()[1]

	dirtable['id'] = range(d_nrow)[::-1]
	dirtable = dirtable.set_index('id')
#	print dirtable
	
#	print d_xll, type(d_xll) 
#	print d_yll, type(d_yll)

	
	dirfile_o.close()

	dirli = []
		
	for i in range(d_ncol):
		tupli = []
		for j in range(d_nrow):
			yi = d_yll + cellsize*j
			xi = d_xll + cellsize*i
			z = str(tuple([yi, xi]))
			tupli.append(z)
		dirli.append(tupli[::-1])

	dir_s = []
	
	for i in dirli:
		j = pd.Series(i)
		dir_s.append(j)
		

		
	dir_ll_table = pd.concat(dir_s, axis=1)
	dir_ll_table['id'] = range(d_nrow)[::-1]
	dir_ll_table = dir_ll_table.set_index('id')


	#####################
	#CLIP DIR TO FRAC	
	#####################
	
	
	fracvals = []
	
	for i in list(frac_ll_table.values):
		fracvals.extend(i)
		

	
	dir_in_frac = dir_ll_table.isin(fracvals)

	
	newdir_s_container = []
	
	for x in dirtable.columns:
		t = dirtable[x].ix[dir_in_frac[x]]
		newdir_s_container.append(t)
	

	
	newdir_table = pd.concat(newdir_s_container, axis=1).dropna(axis=1)
#	print newdir_table

	#####################
	#CLIP FRAC TO DIR	
	#####################
	
	dirvals = []
	
	for i in list(dir_ll_table.values):
		dirvals.extend(i)
		
	
	frac_in_dir = frac_ll_table.isin(dirvals)

	
	newfrac_s_container = []
	
	for x in fractable.columns:
		t = fractable[x].ix[frac_in_dir[x]]
		newfrac_s_container.append(t)
	
	
	newfrac_table = pd.concat(newfrac_s_container, axis=1).dropna(axis=1)
	
#	print newfrac_table
	
	

	newdir_ll_container = []
	
#	print dir_in_frac
	
	for x in dir_ll_table.columns:
		t = dir_ll_table[x].ix[dir_in_frac[x]]
		newdir_ll_container.append(t)
	
	newdir_ll_table = pd.concat(newdir_ll_container, axis=1).dropna(axis=1)
#	print newdir_ll_table	
#	newdir_ll_table.columns = ['c' + str(s) for s in list(newdir_ll_table.columns)]
	
	d_ll_new = ast.literal_eval(newdir_ll_table.loc[min(list(newdir_ll_table.index)), min(list(newdir_ll_table.columns))])
	
#	print d_ll_new
	
	d_xll_new = d_ll_new[1]
	d_yll_new = d_ll_new[0]
	d_ncol_new = len(newdir_ll_table.columns)
	d_nrow_new = len(newdir_ll_table.index)
#	print d_xll_new 
#	print d_yll_new 	
#	print d_ncol_new	
#	print d_nrow_new	

	newfrac_ll_container = []
	
	for x in frac_ll_table.columns:
		t = frac_ll_table[x].ix[frac_in_dir[x]]
		newfrac_ll_container.append(t)
	
	newfrac_ll_table = pd.concat(newfrac_ll_container, axis=1).dropna(axis=1)
#	print newfrac_ll_table	
#	print newfrac_ll_table
	
	f_ll_new = ast.literal_eval(newfrac_ll_table.loc[min(list(newfrac_ll_table.columns)), min(list(newfrac_ll_table.index))])
#	print f_ll_new
	
	f_xll_new = f_ll_new[1]
	f_yll_new = f_ll_new[0]
	f_ncol_new = len(newfrac_ll_table.columns)
	f_nrow_new = len(newfrac_ll_table.index)
#	print f_xll_new 
#	print f_yll_new 
#	print f_ncol_new
#	print f_nrow_new
	
	##############################
	#SET DIR OUT OF BOUNDS TO ZERO	
	##############################	
	
	newdir_table.columns = newfrac_table.columns
	newdir_table['id'] = newfrac_table.index
	newdir_table = newdir_table.set_index('id')
#	del newdir_table['id']
	
	newdir_ll_table.columns = newfrac_ll_table.columns
	newdir_ll_table['id'] = newfrac_ll_table.index
	newdir_ll_table = newdir_ll_table.set_index('id')
#	del newdir_ll_table['id']
	
#	print newdir_table
#	print newfrac_table

	
	for x in newdir_table.columns:
		for i in newdir_table.index:
#			print i, x
			if newfrac_table.loc[i, x] <= 0:
				newdir_table.loc[i, x] = d_nodata
			else:
				continue
				
#	print newdir_table
	
	
	##############################
	#FIND STATION LOCATION	
	##############################	
	
#	stn_name = latlon_c[stn]['PNAME']
	stnloc = latlon_c[stn]
	
	diff_d = {}
	
	stn_tempfile = open('./%s/%s.stnloc' % (rename, rename), 'w')
	
	with open('./%s/%s.stnloc' % (rename, rename), 'w') as stn_tempfile:
		for p in stnloc.iterrows():
			for x in newdir_ll_table.columns:
				for i in newdir_ll_table.index:
					lo = ast.literal_eval(newdir_ll_table.loc[i, x])
#					print lo
					diff = ((lo[0] - p[1][2][0])**2 + (lo[1] - p[1][2][1])**2)**0.5
					diff_d.update({(i, x) : diff})
		
			cellno = min(diff_d, key=diff_d.get)
			stn_tempfile.write("1 %s            %s %s -9999\nNONE\n" % (p[1][3], cellno[1]+1, cellno[0]+1))
#			print 'row:', cellno[0]+1, 'col:', cellno[1]+1
	
	#####################
	#WRITE FILES	
	#####################
	
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
