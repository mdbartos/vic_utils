import os
import pandas as pd
import numpy as np
import urllib2 as url
from StringIO import StringIO
import pickle
from datetime import date
from datetime import timedelta as td
import ast
from scipy.optimize import curve_fit

huc_d = {\
'new_england':       '01',
'mid_atlantic':      '02', 
'south_atlantic':    '03', 
'great_lakes':       '04', 
'ohio':              '05', 
'tennessee':         '06', 
'upper_miss':        '07', 
'lower_miss':        '08', 
'souris-red':        '09', 
'missouri':          '10', 
'arkansas-red':      '11', 
'texas_gulf':        '12', 
'rio_grande':        '13', 
'upper_colorado':    '14', 
'lower_colorado':    '15', 
'great_basin':       '16', 
'pacific_northwest': '17', 
'california':        '18'}

huc_ix = {}

def get_huc_ix(basin):
	string_op = ("http://waterdata.usgs.gov/nwis/dv?referred_module=qw&huc2_cd=%s" % (huc_d[basin]))
	string_ed = "&dv_count_nu=1&index_pmcode_00010=1&group_key=NONE&format=sitefile_output&sitefile_output_format=rdb_station_file&column_name=site_no&column_name=station_nm&column_name=dec_lat_va&column_name=dec_long_va"
	conn_str = string_op + string_ed
	conn = url.urlopen(conn_str)
	r = conn.readlines()
	if len(r) < 10:
		print "no data"
	else:
		huc_ix.update({basin : {}})
		st_i = None
		for x, line in enumerate(r):
			if "No sites" in line[0]:
				print "No sites found in %s" % (x)
				break
			elif ('site_no' in line) and ('station_nm' in line):
				st_i = x
		
		if st_i != None:
			raw_li = r[(st_i + 2):]
			for u in raw_li:
				sp = u.split('\t')
				id = sp[0]
				nm = sp[1]
				lat = sp[2]
				lon = sp[3]
				huc_ix[basin].update({id : {}})
				huc_ix[basin][id].update({'nm' : nm, 'lat' : lat, 'lon' : lon})
#			raw_str = ''.join(raw_li)
#			st_input = StringIO(raw_str)
#			t = pd.read_table(st_input)
#			t = t[1:]
#			print t
#			temp_d[basin].update({i : t})


for g in huc_d.keys():
	get_huc_ix(g)

pickle.dump( huc_ix, open( "huc_ix.p", "wb" ) )

##################################################################

temp_d = {}
		
def get_usgs(basin):
	temp_d.update({basin : {}})
	for i in huc_ix[basin].keys():
		string_op = ("http://waterdata.usgs.gov/nwis/dv?referred_module=sw&search_site_no=%s" % (i))
		string_ed = "&search_site_no_match_type=exact&site_tp_cd=OC&site_tp_cd=OC-CO&site_tp_cd=ES&site_tp_cd=LK&site_tp_cd=ST&site_tp_cd=ST-CA&site_tp_cd=ST-DCH&site_tp_cd=ST-TS&index_pmcode_00010=1&group_key=NONE&sitefile_output_format=html_table&column_name=agency_cd&column_name=site_no&column_name=station_nm&range_selection=date_range&begin_date=1900-01-01&end_date=2014-07-15&format=rdb&date_format=YYYY-MM-DD&rdb_compression=value&list_of_search_criteria=search_site_no%2Csite_tp_cd%2Crealtime_parameter_selection"
		conn_str = string_op + string_ed
		conn = url.urlopen(conn_str)
		r = conn.readlines()
		if len(r) < 10:
			print "no data"
			continue
		else:
			st_i = None
			for x, line in enumerate(r):
				if "No sites" in line[0]:
					print "No sites found in %s" % (x)
					break
				elif 'agency_cd' in line:
					st_i = x
			
			if st_i != None:
				raw_li = r[st_i:]
				raw_str = ''.join(raw_li)
				st_input = StringIO(raw_str)
				t = pd.read_table(st_input)
				t = t[1:]
				print "found data"
				temp_d[basin].update({i : t})
				
for h in huc_ix.keys():
	get_usgs(h)
	
pickle.dump( temp_d, open( "basin_temps_all.p", "wb" ) )

################ VALIDATION DATASET ##########################

valid_basins = {}

for fn in os.listdir('.'):
	sp = fn.split('.')
	t = pd.read_csv(fn)
	for i, k in t.iterrows():
		valid_basins.update({sp : {}})
		valid_basins[sp].update({k['SITE_NO'] : { 'nm' : k['STATION_NAME'], 'lat' : k['LAT_SITE'], 'lon' : k['LON_SITE'] }})
	

q_d = {}
		
def get_validation_q(basin):
	q_d.update({basin : {}})
	for i in valid_basins[basin].keys():
		string_op = ("http://waterdata.usgs.gov/nwis/dv?referred_module=sw&search_site_no=%s" % (i))
		string_ed = "&search_site_no_match_type=exact&site_tp_cd=OC&site_tp_cd=OC-CO&site_tp_cd=ES&site_tp_cd=LK&site_tp_cd=ST&site_tp_cd=ST-CA&site_tp_cd=ST-DCH&site_tp_cd=ST-TS&index_pmcode_00060=1&group_key=NONE&sitefile_output_format=html_table&column_name=agency_cd&column_name=site_no&column_name=station_nm&range_selection=date_range&begin_date=1900-01-01&end_date=2014-07-15&format=rdb&date_format=YYYY-MM-DD&rdb_compression=value&list_of_search_criteria=search_site_no%2Csite_tp_cd%2Crealtime_parameter_selection"
		conn_str = string_op + string_ed
		conn = url.urlopen(conn_str)
		r = conn.readlines()
		if len(r) < 10:
			print "no data"
			continue
		else:
			st_i = None
			for x, line in enumerate(r):
				if "No sites" in line[0]:
					print "No sites found in %s" % (x)
					break
				elif 'agency_cd' in line:
					st_i = x
			
			if st_i != None:
				raw_li = r[st_i:]
				raw_str = ''.join(raw_li)
				st_input = StringIO(raw_str)
				t = pd.read_table(st_input)
				t = t[1:]
				print "found data"
				q_d[basin].update({i : t})
				
for h in valid_basins.keys():
	get_validation_q(h)
	
pickle.dump( temp_d, open( "validation_streamflows.p", "wb" ) )
