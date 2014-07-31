import os
import numpy as np
import pandas as pd
import netCDF4
from datetime import date
import pysal as ps
import pickle

##########################################
#LOWER COLORADO
##########################################
dirlist = {
'lees_f': '/GIS/glen_canyon/vic_grid/vic_grid.dbf',
'davis': '/GIS/abv_davis/vic_grid/abv_davis_vic_grid.dbf',
'gc': '/GIS/abv_gc/vic_grid/abv_gc_vic_grid.dbf',
'hoover': '/GIS/abv_hoover/vic_grid/abv_hoover_vic_grid.dbf',
'imperial': '/GIS/abv_imperial/vic_grid/abv_imp_vic_grid.dbf',
'parker': '/GIS/abv_parker/vic_grid/abv_parker_vic_grid.dbf',
'billw': '/GIS/bill_williams/vic_grid/billw_vic_grid.dbf',
'little_col': '/GIS/little_col/vic_grid/little_co_vic_grid.dbf',
'paria': '/GIS/paria/vic_grid/paria_vic_grid.dbf',
'virgin': '/GIS/virgin/vic_grid/virgin_vic_grid.dbf',
}

latlon_d = {}

for key, val in dirlist.items():
	db = ps.open(val)
	dbpass = {col: db.by_col(col) for col in ['calc_lat', 'calc_lon']}
	dbdf = pd.DataFrame(dbpass)
	dbdf['calc_lon_r'] = [round(j, 4) for j in dbdf.calc_lon]
	dbdf['latlon'] = zip(dbdf.calc_lat, dbdf.calc_lon_r)
	latlon_d.update({key : list(dbdf['latlon'])})

pickle.dump( latlon_d, open( "colo_basins.p", "wb" ) )

##########################################
#CALIFORNIA
##########################################

dirlist = {
'castaic': '/GIS/CA_contrib_area/intersect/castaic_int.dbf',
'corona': '/GIS/CA_contrib_area/intersect/corona_int.dbf',
'cottonwood': '/GIS/CA_contrib_area/intersect/cottonwood_int.dbf',
'coyotecr': '/GIS/CA_contrib_area/intersect/coyotecr_int.dbf',
'kern': '/GIS/CA_contrib_area/intersect/kern_int.dbf',
'pitt': '/GIS/CA_contrib_area/intersect/pitt_int.dbf',
'redmtn': '/GIS/CA_contrib_area/intersect/redmtn_int.dbf',
'riohondo': '/GIS/CA_contrib_area/intersect/riohondo_int.dbf',
'rushcr': '/GIS/CA_contrib_area/intersect/rushcr_int.dbf',
'tulare': '/GIS/CA_contrib_area/intersect/tulare_int.dbf',
'gila_imp': '/GIS/gila_imp/intersect/gila_imp_int.dbf',
}

latlon_d = {}

for key, val in dirlist.items():
	db = ps.open(val)
	dbpass = {col: db.by_col(col) for col in ['calc_lat', 'calc_lon']}
	dbdf = pd.DataFrame(dbpass)
	dbdf['calc_lat_r'] = [round(j, 4) for j in dbdf.calc_lat]
	dbdf['calc_lon_r'] = [round(j, 4) for j in dbdf.calc_lon]
	dbdf['latlon'] = zip(dbdf.calc_lat_r, dbdf.calc_lon_r)
	latlon_d.update({key : list(dbdf['latlon'])})

pickle.dump( latlon_d, open( "ca_sr_basins.p", "wb" ) )

##########################################
#WECC
##########################################

dirlist = {
'colstrip': '/GIS/WECC_contrib_area/ri/colstrip_ri.dbf',
'comanche': '/GIS/WECC_contrib_area/ri/comanche_ri.dbf',
'eaglept': '/GIS/WECC_contrib_area/ri/eaglept_ri.dbf',
'guer': '/GIS/WECC_contrib_area/ri/guernsey_ri.dbf',
'irongate': '/GIS/WECC_contrib_area/ri/irongate_ri.dbf',
'pawnee': '/GIS/WECC_contrib_area/ri/pawnee_ri.dbf',
'peck': '/GIS/WECC_contrib_area/ri/peck_ri.dbf',
'sodasprings': '/GIS/WECC_contrib_area/ri/sodasprings_ri.dbf',
'wauna': '/GIS/WECC_contrib_area/ri/wauna_ri.dbf'
}

latlon_d = {}

for key, val in dirlist.items():
	db = ps.open(val)
	dbpass = {col: db.by_col(col) for col in ['calc_lat', 'calc_lon']}
	dbdf = pd.DataFrame(dbpass)
	dbdf['calc_lat_r'] = [round(j, 4) for j in dbdf.calc_lat]
	dbdf['calc_lon_r'] = [round(j, 4) for j in dbdf.calc_lon]
	dbdf['latlon'] = zip(dbdf.calc_lat_r, dbdf.calc_lon_r)
	latlon_d.update({key : list(dbdf['latlon'])})

pickle.dump( latlon_d, open( "wecc_basins.p", "wb" ) )

##########################################
#UTPP
##########################################

dirlist = {
'baker': '/GIS/UT_contrib_area/ri/baker_ri.dbf',
'brigham': '/GIS/UT_contrib_area/ri/brigham_ri.dbf',
'elwha': '/GIS/UT_contrib_area/ri/elwha_ri.dbf',
'hmjack': '/GIS/UT_contrib_area/ri/hmjack_ri.dbf',
'intermtn': '/GIS/UT_contrib_area/ri/intermtn_ri.dbf',
'lahontan': '/GIS/UT_contrib_area/ri/lahontan_ri.dbf',
'salton': '/GIS/UT_contrib_area/ri/salton_ri.dbf',
'wabuska': '/GIS/UT_contrib_area/ri/wabuska_ri.dbf',
'yelm': '/GIS/UT_contrib_area/ri/yelm_ri.dbf',
'glenn': '/GIS/PP_contrib_area/ri/glenn_ri.dbf',
'paper': '/GIS/PP_contrib_area/ri/paper_ri.dbf'
}

latlon_d = {}

for key, val in dirlist.items():
	db = ps.open(val)
	dbpass = {col: db.by_col(col) for col in ['calc_lat', 'calc_lon']}
	dbdf = pd.DataFrame(dbpass)
	dbdf['calc_lat_r'] = [round(j, 4) for j in dbdf.calc_lat]
	dbdf['calc_lon_r'] = [round(j, 4) for j in dbdf.calc_lon]
	dbdf['latlon'] = zip(dbdf.calc_lat_r, dbdf.calc_lon_r)
	latlon_d.update({key : list(dbdf['latlon'])})

pickle.dump( latlon_d, open( "utpp_basins.p", "wb" ) )
