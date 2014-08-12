import pandas as pd
import numpy as np
import pickle
import os
import ast 

#from colo_r_basins import latlon_x as self.latlon_d
#latlon_d = pickle.load( open( "utpp_basins.p", "rb"))
#master_param = pd.HDFStore('master_param.h5')

##########################################
#CLIP REGIONAL SOIL PARAMS TO TARGET BASIN
##########################################

class clip_params():

	def __init__(self, master_param, master_veg, latlon_d):
		self.latlon_d = latlon_d
		self.master_param = pd.HDFStore(master_param)
		self.master_veg = master_veg
		self.veg_d = {}
		
		self.soilclip = None
		self.vegclip = None
		self.snowclip = None

	def clip_soil(self, basin, wpath):
	
		self.master_param.open()
		soil = self.master_param.soil
		soil = soil.reset_index()
		del soil['index']
		soil[0].replace(to_replace=0, value=1, inplace=True)
		soil[4].replace(to_replace=0.0, value=0.1, inplace=True)
		for j, k in soil.iterrows():
			if k[27] <= 0.0:
				soil[27][j] = 0.32*k[9] + 4.3
				soil[28][j] = 0.32*k[10] + 4.3
				soil[29][j] = 0.32*k[11] + 4.3
		for j, k in soil[4].iteritems():
			if k <= 0.0:
				print "warning b infilt", j, k
		for j, k in soil[27].iteritems():
			if k <= 0.0:
				print "warning bubble pressure", j, k
	#	print soil
		self.master_param.close()
		soil['latlon'] = zip(soil[2], soil[3])
		soil['st_latlon'] = [str(i) for i in soil['latlon']]
		soil = soil.set_index(soil['st_latlon'])
		del soil['latlon']
		del soil['st_latlon']
		latlon_s = [str(i) for i in self.latlon_d[basin]]
		soilclip = soil.ix[latlon_s]
	#	print soilclip
		soilclip = soilclip.dropna(axis=0, subset=[0])
		soilclip = soilclip.dropna(axis=1)
		soilclip = soilclip.drop_duplicates(cols=1)
		soilclip[0] = soilclip[0].astype(int)
		self.soilclip = soilclip
		print soilclip
	#	print set(soilclip[0])
		if not os.path.exists('%s/soil' % (wpath)):
			os.mkdir('%s/soil' % (wpath))
		else:
			pass
		soilclip.to_csv('%s/soil/soil_%s' % (wpath, basin), sep = ' ', header=False, index=False)
	
	############################################
	#CLIP VEG PARAMS TO TARGET BASIN
	############################################
	
	def make_veg_d(self):
	
		f = open(self.master_veg, 'r')
		rf = f.readlines()[:]
		f.close()
		
		f = open(self.master_veg, 'r')
		
		for i, line in enumerate(f):
			if line[0] in ['1','2','3','4','5','6','7','8','9']:
				par_l = line.split()
				gridcel = par_l[0]
				nveg = ast.literal_eval(par_l[1])
	#			print gridcel, type(gridcel)
	#			print nveg, type(nveg)
	#			print i
				nlines = [j for j in rf[i+1: i + nveg*2 + 1]]
				self.veg_d.update({gridcel : (nveg, nlines)})
	
				
	def clip_veg(self, basin, wpath):
		self.master_param.open()
		gridcel = self.master_param.gridcel
		self.master_param.close()
		latlon_s = [str(i) for i in self.latlon_d[basin]]
		gridcel_s = gridcel[latlon_s]
		if not os.path.exists('%s/veg' % (wpath)):
			os.mkdir('%s/veg' % (wpath))
		else:
			pass
		with open('%s/veg/veg_%s' % (wpath, basin), 'w') as newveg:
	#	print gridcel_s
			for i in list(set(gridcel_s.values)):
				i = i.astype(str)
				newveg.write("%s %s\n" % (i, self.veg_d[i][0]))
				for j in self.veg_d[i][1]:
					newveg.write("%s" % (j))
				
	
	
	##############################################			
	#CLIP SNOWBANDS TO TARGET BASIN
	##############################################
	
	
	def clip_snow(self, basin, wpath):
	
		self.master_param.open()
		snow = self.master_param.snow
		gridcel = self.master_param.gridcel
		self.master_param.close()
		snow = snow.set_index(snow[0])
		latlon_s = [str(i) for i in self.latlon_d[basin]]
	#	print latlon_s
		gridcel_s = gridcel[latlon_s]
	#	print gridcel_s
		snowclip = snow.ix[gridcel_s]
	#	print snowclip.tail()
		snowclip = snowclip.drop_duplicates(cols=0)
		snowclip = snowclip.dropna(axis=0, subset=[0])
		snowclip = snowclip.dropna(axis=1)
		self.snowclip = snowclip
	#	for i in snowclip.columns:
	#		snowclip[i] = np.round(snowclip[i], 4)
	#	print snowclip
	#	print len(snowclip.index)
	#	print len(set(list(snowclip.index)))
		if not os.path.exists('%s/snowbands' % (wpath)):
			os.mkdir('%s/snowbands' % (wpath))
		else:
			pass
		snowclip.to_csv('%s/snowbands/snowbands_%s' % (wpath, basin), sep = ' ', header=False, index=False)


##################################################
#APPLY CLIP
##################################################

latlon_miss = {}

latlon_miss['lees_f_missing'] = [(42.9375, -110.6875), (42.8125, -110.6875), (42.6875, -110.6875), (42.8125, -110.5625), (42.6875, -110.5625), (42.5625, -110.5625), (43.0625, -110.4375), (42.9375, -110.4375), (43.3125, -110.3125), (43.0625, -110.3125), (42.9375, -110.3125), (43.3125, -110.1875), (43.1875, -110.1875), (43.0625, -110.1875), (37.5625, -106.8125), (36.8125, -106.6875), (37.0625, -106.5625)]

b = [i for i in latlon_miss.keys()]

c = clip_params('/home/chesterlab/Bartos/VIC/input/vic/params/master/master_param.h5', '/home/chesterlab/Bartos/VIC/input/vic/params/master/master_veg', latlon_miss)

outdir = '/home/chesterlab/Desktop/test_param'

for basin in b:
	c.clip_soil(basin, outdir)

c.make_veg_d()

for basin in b:
	c.clip_veg(basin, outdir)

for basin in b:
	c.clip_snow(basin, outdir)
