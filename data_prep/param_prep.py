import pandas as pd
import numpy as np
import pickle
import os
import ast 

##################################
#STORE REGIONAL SOIL PARAMS
##################################

#cd soil params directory

d = {}

for fn in os.listdir('.'):
	print fn
	f = pd.read_table(fn, sep=' ')
	f.columns = [range(len(f.columns))]
	d.update({fn : f})


r_latlon_d = {}

for i, v in d.items():
	v['latlon'] = zip(v[2], v[3])
	r_latlon_d.update({i[10:] : v['latlon']})

out = open("region_latlon.p", "wb")
pickle.dump(r_latlon_d, out)
out.close()

#LOAD LATLON PICKLE

r_latlon = pickle.load( open( "./region_latlon.p", "rb"))
		
#######################################
#STORE SOIL, VEG, SNOWBANDS as HDF5
#######################################

master_param = pd.HDFStore('master_param.h5')



#SOIL


#cd soil region dir

soil_d = {}

for fn in os.listdir('.'):
	print fn
	f = pd.read_table(fn, sep=' ')
	f.columns = [range(len(f.columns))]
	soil_d.update({fn : f})

soil = pd.concat([x for x in soil_d.values()])



#VEG

#cd veg region dir

fn_li = [i for i in os.listdir('.')]

with open('master_veg', 'w') as outfile:
    for fname in fn_li:
        with open(fname) as infile:
            for line in infile:
                outfile.write(line)
				

			
#SNOWBANDS

#cd snowband region dir

snow_d = {}

for fn in os.listdir('.'):
	print fn
	f = pd.read_table(fn, sep=' ')
	f.columns = [range(len(f.columns))]
	snow_d.update({fn : f})

snow = pd.concat([x for x in snow_d.values()])


#HDFSTORE


master_param['soil'] = soil
master_param['veg'] = veg
master_param['snow'] = snow

#GRIDCELL

#master_param = pd.HDFStore('master_param.h5')

soil = master_param.soil

soil['latlon'] = zip(soil[2], soil[3])
soil['st_latlon'] = soil['latlon'].astype(str)
soil = soil.set_index(soil['st_latlon'])
gridcel = soil[1]


master_param['gridcel'] = gridcel
