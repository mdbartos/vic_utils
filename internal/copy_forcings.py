import os
import shutil
import pickle

#########cd github folder

#from colo_r_basins import latlon_x as latlon_d

latlon_d = pickle.load( open( "ca_sr_basins.p", "rb"))

#########cd forcing folder

def basin_forcings(basin):
	if basin in os.listdir('.'):
		pass
	else:
		os.mkdir('/home/chesterlab/Bartos/VIC/input/vic/forcing/hist/region/master/%s' % (basin))
	for i in latlon_d[basin]:
		for fn in os.listdir('.'):
#			if fn == 'fluxes_%s_%s' % (i[0], i[1]):
#			if fn == 'snow_%s_%s' % (i[0], i[1]):
			if fn == 'data_%s_%s' % (i[0], i[1]):
				print fn
				shutil.copyfile(fn, '/home/chesterlab/Bartos/VIC/input/vic/forcing/hist/region/master/%s/%s' % (basin, fn))
