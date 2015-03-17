import numpy as np
import pandas as pd
import pysal as ps
import os


#db = ps.open('/home/akagi/GIS/usgs_wind/USGS_windturbine_201307.dbf')
db = ps.open('/home/tabris/GIS/usgs_wind/USGS_windturbine_201307.dbf')
dbpass = {col: db.by_col(col) for col in db.header}
df = pd.DataFrame(dbpass)

df = df.loc[df['MW_turbine'] != -99999.0]
df = df.loc[df['state'].isin(['WA', 'OR', 'CA', 'ID', 'NV', 'UT', 'AZ', 'CO', 'WY', 'MT', 'NM'])]

df['rated_wspd'] = 0.0

df['rated_wspd'].loc[df['manufac'] == 'Clipper'] = 11.5
df['rated_wspd'].loc[(df['manufac'] == 'GE') & (df['model'].str.contains('1.'))] = 12.0
df['rated_wspd'].loc[(df['manufac'] == 'GE') & (df['model'].str.contains('2.'))] = 14.0
df['rated_wspd'].loc[df['manufac'] == 'Gamesa'] = 13.5
df['rated_wspd'].loc[df['manufac'] == 'Mitsubishi'] = 12.5
df['rated_wspd'].loc[(df['manufac'] == 'Siemens') & (df['model'].str.contains('1.'))] = 14.0
df['rated_wspd'].loc[(df['manufac'] == 'Siemens') & (df['model'].str.contains('2.'))] = 13.5
df['rated_wspd'].loc[df['manufac'] == 'Suzlon'] = 14.0
df['rated_wspd'].loc[(df['manufac'] == 'Vestas') & (df['model'].str.contains('V8'))] = 13.0
df['rated_wspd'].loc[(df['manufac'] == 'Vestas') & (df['model'].str.contains('V90_1.8'))] = 11.0
df['rated_wspd'].loc[(df['manufac'] == 'Vestas') & (df['model'].str.contains('V90_3.0'))] = 15.0
df['rated_wspd'].loc[(df['manufac'] == 'Vestas') & (df['model'].str.contains('V100'))] = 15.0

df['rated_wspd'].loc[df['rated_wspd'] == 0.0] = 13.0

df['mpower_coeff'] = 1000000*2*df['MW_turbine']/((df['rated_wspd']**3)*df['rotor_s_a']*1.2041)

df = df.loc[df['mpower_coeff'] > 0.0]

#########################################
df['lat_grid'] = 0.0
df['lon_grid'] = 0.0

for i in df.index:

    latcells = [int(df.loc[i, 'lat_DD']) + g for g in [0.0625*j for j in [-13,-11,-9,-7,-5,-3,-1, 1,3,5,7,9,11,13]]]
    d = {}
    for k in latcells:
        d.update({abs(df.loc[i, 'lat_DD'] - k) : k})
    minlat = d[min(d.keys())]
    df.loc[i, 'lat_grid'] = minlat

    loncells = [int(df.loc[i, 'long_DD']) + g for g in [0.0625*j for j in [-13,-11,-9,-7,-5,-3,-1, 1,3,5,7,9,11,13]]]
    d = {}
    for k in loncells:
        d.update({abs(df.loc[i, 'long_DD'] - k) : k})
    minlon = d[min(d.keys())]
    df.loc[i, 'lon_grid'] = minlon

####to_csv####

data_li = list(set(['data_%s_%s' % (df.loc[i, 'lat_grid'], df.loc[i, 'lon_grid']) for i in df.index]))

forcing_path = '/media/melchior/BALTHASAR/nsf_hydro/pre/source_data/source_hist_forcings/active/master'

#TEST
[i for i in data_li if not i in os.listdir(forcing_path)]
#['data_33.8125_-102.1875', 'data_32.8125_-102.1875']
#~500 MW

####FIND LAT/LONS FOR EACH BASIN

import os
import numpy as np
import pandas as pd
import netCDF4
import pickle
import shutil

basin_masks = {}

for fn in os.listdir('/media/melchior/BALTHASAR/nsf_hydro/pre/source_data/source_proj_forcings/active'):
	if fn.endswith('nc'):
		basin = fn.split('.')[0]
		basin_masks.update({basin : {}})
		ncvar = fn.split('.')[-3]
		mask = []
		f = netCDF4.Dataset(fn, 'r')
		for i in range(len(f.variables['lat'][:])):
			for j in range(len(f.variables['lon'][:])):
				if type(f.variables[ncvar][0, i, j]) != np.ma.core.MaskedConstant:
					mask.append([i,j])
		print len(mask), len(f.variables['lat'][:])*len(f.variables['lon'][:])
		basin_masks[basin].update({'coords':['_'.join([str(float(f.variables['lat'][k[0]])), str(float(f.variables['lon'][k[1]]))]) for k in mask]})
		basin_masks[basin].update({'ix': mask})

###DUMP PICKLE
#pickle.dump(basin_masks, open('basin_masks.p', 'wb'))
basin_masks = pickle.load(open('/media/melchior/BALTHASAR/nsf_hydro/VIC/input/dict/basin_masks.p', 'r')) 

###GET WIND COORDS IN EACH BASIN
windpath = '/home/melchior/Dropbox/Southwest Heat Vulnerability Team Share/ppdb_data/USGS_wind.csv'

df = pd.read_csv(windpath)

coord_li = list(set(['%s_%s' % (df.loc[i, 'lat_grid'], df.loc[i, 'lon_grid']) for i in df.index]))

reg_d = {}

for j in basin_masks.keys():
	reg_d.update({j : {'coords':[], 'ix':[]}})

for i in coord_li:
	for j in basin_masks.keys():
		if i in basin_masks[j]['coords']:
			reg_d[j]['coords'].append(i)
			reg_d[j]['ix'].append(basin_masks[j]['ix'][basin_masks[j]['coords'].index(i)])

####EXTRACT FROM NETCDF FILES

master_path = '/media/melchior/BALTHASAR/nsf_hydro/pre/source_data/source_proj_forcings/active/master'

def extract_wind_hist(basin, inpath, outpath):
	outfile = outpath + '/hist'
	if not os.path.exists(outfile):
		os.mkdir(outfile)
	coords = reg_d[basin]['coords']
	file_li = ['data_%s' % (i) for i in coords]
	for fn in file_li:
		df = pd.read_csv('%s/%s' % (inpath, fn), sep='\t', header=None, index_col=False, names=['yr', 'mo', 'day', 'prcp', 'tmax', 'tmin', 'wind'])
		df = df[['prcp', 'tmax', 'tmin', 'wind']]
		df.to_csv('%s/%s' % (outfile, fn), sep='\t', header=False, index=False)

def extract_wind_nc(scen, model, basin, outpath):

	outfile = outpath + '/' + model + '_' + scen
	if not os.path.exists(outfile):
		os.mkdir(outfile)

	coords = reg_d[basin]['coords']
	
	for i in range(len(coords)):
		c = coords[i]
		ix = reg_d[basin]['ix'][i]
		df = pd.DataFrame()

		for y in range(2010,2100):
			year_df = pd.DataFrame()

			for v in ['prcp', 'tmax', 'tmin', 'wind']:
				f = netCDF4.Dataset('%s/%s.sres%s.%s.daily.%s.%s.nc' % (master_path, basin, scen, model, v, y) , 'r')
				s = f.variables[v][:, ix[0], ix[1]]
				year_df[v] = s
				f.close()

			year_df.index = pd.date_range(start=datetime.date(y,1,1), end=datetime.date(y,12,31))
			df = df.append(year_df)
		df = df[['prcp', 'tmax', 'tmin', 'wind']]
		df.to_csv('%s/data_%s' % (outfile, coords[i]), sep='\t', index=False, header=False)

for b in reg_d.keys():
	extract_wind_hist(b, '/media/melchior/BALTHASAR/nsf_hydro/pre/source_data/source_hist_forcings/active/master', '/home/melchior/Desktop/wind_new')

#for b in reg_d.keys():
#	for sc in ['a1b', 'a2', 'b1']:
#		for m in ['mpi_echam5.3', 'ukmo_hadcm3.1']:
#			extract_wind_nc(sc, m, b, '/home/melchior/Desktop/wind')

#### GET PARAMS

wind_d = {}

wind_d['wind'] = [tuple([float(i.split('_')[1]), float(i.split('_')[2])]) for i in os.listdir('/home/melchior/Desktop/wind_new/hist')]

outdir = '/home/melchior/Desktop/wind_new/wind_params'

#param_clip(wind_d['wind'], outdir)

#######################################
####APPLY WIND POWER EQUATION TO FORCINGS

import os
import numpy as np
import pandas as pd

windpath = '/home/melchior/Dropbox/Southwest Heat Vulnerability Team Share/ppdb_data/USGS_wind.csv'

df = pd.read_csv(windpath)

g = df.groupby(['lat_grid', 'lon_grid', 'mpower_coeff', 'rotor_s_a', 'rated_wspd']).sum()['MW_turbine']

def make_windpower(scen, rpath, wpath):
	ct = 0
	for i in g.index:
		ct = ct + 1
		
		lat = i[0]
		lon = i[1]
		mpower_coeff = i[2]
		rotor_s_a = i[3]
		rated_wspd = i[4]
		nameplate = g[i]

		rname = 'full_data_%s_%s' % (lat, lon)
		wname = 'wind_%s_%s_%s.%s' % (lat, lon, ct, scen)

		rfile = rpath + '/' + rname
		wfile = wpath + '/' + wname

		df = pd.read_csv(rfile, sep='\t', skiprows=6, names=['YEAR', 'MONTH', 'DAY', 'OUT_WIND', 'OUT_DENSITY', 'OUT_PRESSURE', 'OUT_VP', 'OUT_AIR_TEMP'])	

##########################
# INDEX TO NREL

import os
import numpy as np
import pandas as pd
import urllib2 as url

windpath = '/home/tabris/Dropbox/Southwest Heat Vulnerability Team Share/ppdb_data/USGS_wind.csv'

wn = pd.read_csv(windpath)

df = pd.read_csv('/home/tabris/site_meta.csv')

wn['nrel_idx'] = 0

for i in wn.index:
    wn['nrel_idx'].loc[i] = (((df[' Latitude'] - wn['lat_DD'][i])**2 + (df[' Longitude'] - wn['long_DD'][i])**2)**0.5).abs().idxmin()

#to_csv

############### COMPARE NREL TO CMIP

import pandas as pd
import numpy as np
import datetime

df_path = '/home/tabris/Dropbox/Southwest Heat Vulnerability Team Share/ppdb_data/USGS_wind.csv'
nrel_path = '/home/tabris/Downloads/nrel_wind'
forcing_path = '/home/tabris/Desktop/hist' 

wn = pd.read_csv(df_path)

def match_nrel(i):
    nrel_id = wn.loc[i, 'nrel_idx']
    gridcell = 'data_%s_%s' % (wn.loc[i, 'lat_grid'], wn.loc[i, 'lon_grid'])

    forcing = pd.read_csv(forcing_path + '/' + gridcell, sep='\t', names=['prcp', 'tmax', 'tmin', 'wspd'])
    forcing.index = pd.date_range(start=datetime.date(1949, 1, 1), end=datetime.date(2010,12,31), freq='D') 
    
    nrel_df = pd.DataFrame()
    for y in ['2004', '2005', '2006']:
        nrel = pd.read_csv(nrel_path + '/' + y + '/' + str(nrel_id) + '.csv').iloc[:, [0,1]]
        nrel['date'] = pd.to_datetime(nrel['Date(YYYY-MM-DD hh:mm:ss)'])
        nrel = nrel[['100m wind speed (m/s)', 'date']]
        nrel['year'] = [j.year for j in nrel['date']]
        nrel['month'] = [j.month for j in nrel['date']]
        nrel['day'] = [j.day for j in nrel['date']]
        nrel_df = nrel_df.append(nrel)
    g = nrel_df.groupby(['year', 'month', 'day']).mean()['100m wind speed (m/s)'].reset_index()
    g.index = pd.date_range(start=datetime.date(2004, 1, 1), end=datetime.date(2006,12,31), freq='D')

    cat = pd.concat([g, forcing], axis=1).dropna()[['100m wind speed (m/s)', 'wspd']]
    print cat
    scatter(cat['wspd'], cat['100m wind speed (m/s)']) 


