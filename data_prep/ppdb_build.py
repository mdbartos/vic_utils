from db_mash import mash_db
import pickle
import pandas as pd
import numpy as np

b = mash_db('ppdb')
b.import_csv()
b.import_xl()


#egrid9 = b.d['eGRID_2009_plant']['ORISPL'].drop_duplicates()
#egrid9 = b.d['eGRID_2009_gen']['ORISPL'].drop_duplicates()
#eia860p = b.d['PlantY09']['PLANT_CODE'].drop_duplicates()

rlatlon = pickle.load( open('region_latlon.p', 'rb'))
rlldf = pd.DataFrame.from_dict(rlatlon)

rlldict = {}

for i in rlldf.columns:
	lat = '%s_lat' % (i)
	lon = '%s_lon' % (i)
	rlldict[lat] = [g[0] for g in rlldf[i].dropna() if type(g) == tuple]
	rlldict[lon] = [g[1] for g in rlldf[i].dropna() if type(g) == tuple]

#

basins = list(set([i.split('_')[0] for i in rlldict.keys()]))
basincent = {}

for i in basins:	
	mlat = np.mean(rlldict['%s_lat' % (i)])
	mlon = np.mean(rlldict['%s_lon' % (i)])
	basincent.update({i : tuple([mlat, mlon])})

wrrdict = pd.Series({
'Arkansas-White-Red' : 'ark',
'Great Lakes' : 'glakes',
'Texas-Gulf' : 'gulf',
'California' : 'cali',
'Lower Colorado' : 'color',
'Upper Colorado' : 'color',
'Missouri' : 'mo',
'Upper Mississippi': 'up',
'Pacific Northwest' : 'crb',
'Rio Grande' : 'rio',
'Great Basin': 'grb',
'Lower Mississippi' : 'low',
'Ohio': 'ohio',
'New England': 'east',
'South Atlantic Gulf' : 'east',
'Tennessee' : 'east',
'Mid Atlantic' : 'east',
'Alaska' : np.nan,
'Souris Red Rainy' : 'glakes',
'Hawaii' : np.nan,
})



post_pp_d = {}


####SET UP GENERATOR EFFICIENCY TABLES##############

b.d['SCHEDULE 3A 5A 8A 8B 8C 8D 8E 8F REVISED 2009 04112011_Generator'].columns = list(b.d['SCHEDULE 3A 5A 8A 8B 8C 8D 8E 8F REVISED 2009 04112011_Generator'].loc[2].values)

b.d['SCHEDULE 3A 5A 8A 8B 8C 8D 8E 8F REVISED 2009 04112011_Generator'] = b.d['SCHEDULE 3A 5A 8A 8B 8C 8D 8E 8F REVISED 2009 04112011_Generator'].loc[3:]

b.d['SCHEDULE 3A 5A 8A 8B 8C 8D 8E 8F REVISED 2009 04112011_Boiler'].columns = list(b.d['SCHEDULE 3A 5A 8A 8B 8C 8D 8E 8F REVISED 2009 04112011_Boiler'].loc[2].values)

b.d['SCHEDULE 3A 5A 8A 8B 8C 8D 8E 8F REVISED 2009 04112011_Boiler'] = b.d['SCHEDULE 3A 5A 8A 8B 8C 8D 8E 8F REVISED 2009 04112011_Boiler'].loc[3:]


####GET COMBUSTION TURBINES##########################
CTix = b.d['eGRID_2009_gen']['ORISPL'].ix[b.d['eGRID_2009_gen']['PRMVR'].isin(['IG', 'IC', 'GT', 'CT'])].drop_duplicates()

CTpl_ix = b.d['eGRID_2009_plant'].drop_duplicates(subset=['ORISPL']).set_index('ORISPL').loc[CTix]
CT_WECC_ll = CTpl_ix.loc[CTpl_ix['NERC'] == 'WECC']
CT_WRR = b.d['EW3_main_data'].drop_duplicates(subset=['Plant Code']).set_index('Plant Code').loc[pd.Series(CT_WECC_ll.index).values]['Water Resource Region'].dropna()
CT_WRR = b.d['EW3_main_data'].drop_duplicates(subset=['Plant Code']).set_index('Plant Code').loc[pd.Series(CT_WECC_ll.index).values][['Water Resource Region', 'Reported Water Source (Type)']].dropna(subset=['Reported Water Source (Type)'])
CT_WECC = pd.concat([CT_WECC_ll['PNAME'], CT_WECC_ll['LAT'], CT_WECC_ll['LON'], CT_WECC_ll['CAPFAC'], CT_WECC_ll['NAMEPCAP'], CT_WECC_ll['PLPRMFL'], CT_WRR['Water Resource Region'], CT_WRR['Reported Water Source (Type)']], axis=1)

CT_WECC['WR_REG'] = CT_WECC['Water Resource Region'].map(wrrdict)
del CT_WECC['Water Resource Region']
CT_WECC['W_SRC'] = CT_WECC['Reported Water Source (Type)']
del CT_WECC['Reported Water Source (Type)']
CT_WECC['PCODE'] = CT_WECC.index


for i, k in CT_WECC['WR_REG'].loc[CT_WECC['WR_REG'].isnull()].iteritems():
#	print i, k
	fn_d = {}
	for x, z in basincent.items():
		blat = z[0]
		blon = z[1]
		slat = CT_WECC['LAT'][i]
		slon = CT_WECC['LON'][i]
		diff = ((blat - slat)**2 + (blon - slon)**2)**0.5
		fn_d.update({x : diff})
	cell = min(fn_d, key=fn_d.get)
	CT_WECC['WR_REG'][i] = cell

ct_wecc_stix = [i for i in CT_WECC.index]

ct_tot_gen = b.d['GeneratorY09_Exist'].set_index('PLANT_CODE', drop=False).loc[ct_wecc_stix].groupby('PLANT_CODE').sum()
ct_ct_gen = b.d['GeneratorY09_Exist'].set_index('PLANT_CODE', drop=False).loc[ct_wecc_stix]
ct_ct_gen = ct_ct_gen.loc[ct_ct_gen['PRIME_MOVER'].isin(['IG', 'IC', 'GT', 'CT'])].groupby('PLANT_CODE').sum()

CT_WECC['CAP_FRAC'] = ct_ct_gen['NAMEPLATE']/ct_tot_gen['NAMEPLATE']

post_pp_d.update({'ct' : CT_WECC})


#ct_gen_monthly = b.d['SCHEDULE 3A 5A 8A 8B 8C 8D 8E 8F REVISED 2009 04112011_Generator'].set_index('Plant ID').loc[CT_WECC.index] 

#ct_boil_gen = b.d['EnviroAssocY09_Boiler_Gen'].set_index('PLANT_CODE').loc[CT_WECC.index].dropna(subset=['UTILITY_ID'])

#ct_boil_cool = b.d['EnviroAssocY09_Boiler_Cool'].set_index('PLANT_CODE').loc[CT_WECC.index].dropna(subset=['UTILITY_ID'])

#CT_WECC.to_csv('CT_WECC.csv')

#####################################################

####GET STEAM TURBINES###############################



STix = b.d['eGRID_2009_gen']['ORISPL'].ix[b.d['eGRID_2009_gen']['PRMVR'].isin(['ST', 'CA', 'BT'])].drop_duplicates()
STpl_ix = b.d['eGRID_2009_plant'].drop_duplicates(subset=['ORISPL']).set_index('ORISPL').loc[STix]
ST_WECC_ll = STpl_ix.loc[STpl_ix['NERC'] == 'WECC']

Cool = b.d['EnviroEquipY09_Cool'].set_index('PLANT_CODE', drop=False).loc[pd.Series(ST_WECC_ll.index)].dropna(subset=['COOLING_ID']).drop_duplicates(subset=['PLANT_CODE'])

Cool_all = b.d['EnviroEquipY09_Cool'].set_index('PLANT_CODE', drop=False).loc[pd.Series(ST_WECC_ll.index)].dropna(subset=['COOLING_ID'])  
Cool_all['PLANT_CODE'] = [int(i) for i in Cool_all['PLANT_CODE']]
Cool_all['COOL_CAT_ID'] = Cool_all['PLANT_CODE'].map(str) + '_' + Cool_all['COOLING_ID'] 
#Cool = Cool.set_index('COOLING_ID')

Gen = b.d['GeneratorY09_Exist']
#Gen['PLANT_CODE'] = [float(i) for i in Gen['PLANT_CODE']]
Gen = Gen.set_index('PLANT_CODE', drop=False).loc[pd.Series(ST_WECC_ll.index)].dropna(subset=['NAMEPLATE']) 

CoolOps = b.d['SCHEDULE 3A 5A 8A 8B 8C 8D 8E 8F REVISED 2009 04112011_Cooling Operations'].set_index('Plant ID', drop=False).loc[pd.Series(ST_WECC_ll.index)].dropna(subset=['Year']).drop_duplicates(subset=['Plant ID'])
EW3 = b.d['EW3_main_data'].drop_duplicates(subset=['Plant Code']).set_index('Plant Code')[['Water Resource Region', 'Reported Water Source (Type)']]


Assoc_B_G = b.d['EnviroAssocY09_Boiler_Gen']
Assoc_B_G['CAT_ID'] = Assoc_B_G['PLANT_CODE'].map(str) + '_' + Assoc_B_G['BOILER_ID']
Assoc_B_G = Assoc_B_G.set_index('CAT_ID')
Assoc_B_C = b.d['EnviroAssocY09_Boiler_Cool']
Assoc_B_C['CAT_ID'] = Assoc_B_C['PLANT_CODE'].map(str) + '_' + Assoc_B_C['BOILER_ID']
Assoc_B_C = Assoc_B_C.set_index('CAT_ID')
Assoc = Assoc_B_G.merge(Assoc_B_C, how='outer')
Assoc['PLANT_CODE'] = [int(i) for i in Assoc['PLANT_CODE']]
Assoc['GEN_CAT_ID'] = Assoc['PLANT_CODE'].map(str) + '_' + Assoc['GENERATOR_ID'] 

#Assoc = pd.concat([Assoc_B_G, Assoc_B_C], axis=1)


ST_WECC = pd.concat([ST_WECC_ll, Cool, CoolOps, EW3], axis=1)
ST_WECC['WR_REG'] = ST_WECC['Water Resource Region'].map(wrrdict)
del ST_WECC['Water Resource Region']

for i, k in ST_WECC['WR_REG'].loc[ST_WECC['WR_REG'].isnull()].iteritems():
#	print i, k
	fn_d = {}
	for x, z in basincent.items():
		blat = z[0]
		blon = z[1]
		slat = ST_WECC['LAT'][i]
		slon = ST_WECC['LON'][i]
		diff = ((blat - slat)**2 + (blon - slon)**2)**0.5
		fn_d.update({x : diff})
	cell = min(fn_d, key=fn_d.get)
	ST_WECC['WR_REG'][i] = cell

ST_WECC['W_SRC'] = ST_WECC['Reported Water Source (Type)']
del ST_WECC['Reported Water Source (Type)']

ST_WECC_RC = ST_WECC.loc[ST_WECC['COOLING_TYPE1'].isin(['HRC', 'HRF', 'HRI', 'RC', 'RF', 'RI', 'RN'])]
ST_WECC_OP = ST_WECC.loc[ST_WECC['COOLING_TYPE1'].isin(['OC', 'OF', 'OS'])]

#
STtyp = []

STtyp.extend([i for i in ST_WECC_RC.index])
STtyp.extend([i for i in ST_WECC_OP.index])

ST_WECC_UN = ST_WECC.loc[[i for i in ST_WECC.index if i not in STtyp]]

UN_CTECH = b.d['EW3_main_data'].set_index('Plant Code', drop=False).loc[pd.Series(ST_WECC_UN.index)].dropna(subset=['Plant Code']).drop_duplicates(subset=['Plant Code'])[['Cooling Technology', 'Water Resource Region']]

ST_WECC_UN = pd.concat([ST_WECC_UN, UN_CTECH], axis=1)

ST_WECC_UN = ST_WECC_UN.drop(ST_WECC_UN[['Cooling Technology', 'PLPRMFL']].ix[ST_WECC_UN['Cooling Technology'] == 'None'].index)
ST_WECC_UN = ST_WECC_UN.drop(ST_WECC_UN[['Cooling Technology', 'PLPRMFL']].ix[ST_WECC_UN['Cooling Technology'] == 'Dry Cooled'].index)

#Get probable cooling systems (pretty much all RC)
ST_WECC_UN.groupby(['PLPRMFL', 'Cooling Technology']).count()

t = pd.Series({'Recirculating' : 'RU', 'Once-Through' : 'OC', '#not designated' : 'RU'})

ST_WECC_UN['COOLING_TYPE1'] = ST_WECC_UN['Cooling Technology'].map(t)

RU_add = ST_WECC_UN.loc[ST_WECC_UN['COOLING_TYPE1'] == 'RU'][list(ST_WECC_RC.columns)]
OC_add = ST_WECC_UN.loc[ST_WECC_UN['COOLING_TYPE1'] == 'OC'][list(ST_WECC_OP.columns)]

ST_WECC_RC = pd.concat([ST_WECC_RC, RU_add], axis=0)
ST_WECC_OP = pd.concat([ST_WECC_OP, OC_add], axis=0)
ST_WECC_RC['PCODE'] = ST_WECC_RC.index
ST_WECC_OP['PCODE'] = ST_WECC_OP.index

#Uncomment to get only SW RC systems

#ST_WECC_RC = ST_WECC_RC.loc[ST_WECC_RC['W_SRC'].isin(['Surface Water', 'Unknown Freshwater', 'GW/Surface Water'])]
ST_WECC_OP = ST_WECC_OP.loc[ST_WECC_OP['W_SRC'].isin(['Surface Water', 'Unknown Freshwater', 'GW/Surface Water'])]

#NEW

ST_WECC_RC = ST_WECC_RC.dropna(subset=['LAT'])
ST_WECC_OP = ST_WECC_OP.dropna(subset=['LAT'])

st_wecc_rc_stix = [int(i) for i in ST_WECC_RC.index]
st_wecc_op_stix = [int(i) for i in ST_WECC_OP.index]


#USING FUEL

st_rc_fuel_monthly = b.d['f923_gen_fuel'].set_index('Plant ID', drop=False).loc[st_wecc_rc_stix]
st_rc_fuel_all = st_rc_fuel_monthly.groupby('Plant ID').sum()
st_rc_fuel_monthly = st_rc_fuel_monthly.loc[st_rc_fuel_monthly['Reported Prime Mover'].isin(['ST', 'CA', 'BT'])].groupby('Plant ID').sum()

st_rc_fuel_monthly['GEN_FRACTION'] =  st_rc_fuel_monthly['NET GENERATION (megawatthours)']/st_rc_fuel_all['NET GENERATION (megawatthours)']  

heat_cols = [i for i in list(st_rc_fuel_monthly.columns) if 'ELEC_MMBTUS' in str(i)] 
elec_cols = [i for i in list(st_rc_fuel_monthly.columns) if 'NETGEN_' in str(i)]

for j, k in enumerate(heat_cols):
	mo = k.split('_')[-1]
	inp = heat_cols[j]
	elec = elec_cols[j]
	print inp, elec
	st_rc_fuel_monthly['ELEC_EFF_%s' % (mo)] = (st_rc_fuel_monthly[elec]/0.29307)/st_rc_fuel_monthly[inp]

#st_rc_fuel_monthly['ELEC_EFF_AVG'] = (st_rc_fuel_monthly['NET GENERATION (megawatthours)']/0.29307)/st_rc_fuel_monthly['ELEC FUEL CONSUMPTION MMBTUS'] 

st_rc_fuel_monthly.replace(to_replace=[np.inf, -np.inf], value=np.nan, inplace=True)
st_rc_fuel_monthly[st_rc_fuel_monthly.iloc[:, 87:99] > 1] = np.nan
st_rc_fuel_monthly[st_rc_fuel_monthly.iloc[:, 87:99] < 0] = np.nan

st_rc_fuel_monthly['ELEC_EFF_AVG'] = st_rc_fuel_monthly.iloc[:, 87:99].mean(axis=1) 

st_rc_capacities = b.d['GeneratorY09_Exist'].set_index('PLANT_CODE', drop=False).loc[st_wecc_rc_stix].groupby('PLANT_CODE').sum()[['NAMEPLATE', 'SUMMER_CAPABILITY', 'WINTER_CAPABILITY']]



st_op_fuel_monthly = b.d['f923_gen_fuel'].set_index('Plant ID', drop=False).loc[st_wecc_op_stix]
st_op_fuel_all = st_op_fuel_monthly.groupby('Plant ID').sum()
st_op_fuel_monthly = st_op_fuel_monthly.loc[st_op_fuel_monthly['Reported Prime Mover'].isin(['ST', 'CA', 'BT'])].groupby('Plant ID').sum()

st_op_fuel_monthly['GEN_FRACTION'] =  st_op_fuel_monthly['NET GENERATION (megawatthours)']/st_op_fuel_all['NET GENERATION (megawatthours)']  

heat_cols = [i for i in list(st_op_fuel_monthly.columns) if 'ELEC_MMBTUS' in str(i)] 
elec_cols = [i for i in list(st_op_fuel_monthly.columns) if 'NETGEN_' in str(i)]

for j, k in enumerate(heat_cols):
	mo = k.split('_')[-1]
	inp = heat_cols[j]
	elec = elec_cols[j]
	print inp, elec
	st_op_fuel_monthly['ELEC_EFF_%s' % (mo)] = (st_op_fuel_monthly[elec]/0.29307)/st_op_fuel_monthly[inp]

#st_op_fuel_monthly['ELEC_EFF_AVG'] = (st_op_fuel_monthly['NET GENERATION (megawatthours)']/0.29307)/st_op_fuel_monthly['ELEC FUEL CONSUMPTION MMBTUS'] 

st_op_fuel_monthly.replace(to_replace=[np.inf, -np.inf], value=np.nan, inplace=True)
st_op_fuel_monthly[st_op_fuel_monthly.iloc[:, 87:99] > 1] = np.nan
st_op_fuel_monthly[st_op_fuel_monthly.iloc[:, 87:99] < 0] = np.nan

st_op_fuel_monthly['ELEC_EFF_AVG'] = st_op_fuel_monthly.iloc[:, 87:99].mean(axis=1) 

st_op_capacities = b.d['GeneratorY09_Exist'].set_index('PLANT_CODE', drop=False).loc[st_wecc_op_stix].groupby('PLANT_CODE').sum()[['NAMEPLATE', 'SUMMER_CAPABILITY', 'WINTER_CAPABILITY']]

ST_WECC_RC = pd.concat([ST_WECC_RC, st_rc_fuel_monthly, st_rc_capacities], axis=1)
ST_WECC_OP = pd.concat([ST_WECC_OP, st_op_fuel_monthly, st_op_capacities], axis=1)


st_rc_tot_gen = b.d['GeneratorY09_Exist'].set_index('PLANT_CODE', drop=False).loc[st_wecc_rc_stix].groupby('PLANT_CODE').sum()
st_rc_st_rc_gen = b.d['GeneratorY09_Exist'].set_index('PLANT_CODE', drop=False).loc[st_wecc_rc_stix]
#st_rc_st_rc_gen['GEN_CAT_ID'] = st_rc_st_rc_gen['PLANT_CODE'].map(str) + '_' + st_rc_st_rc_gen['GENERATOR_ID']

#st_rc_st_rc_gen = st_rc_st_rc_gen.merge(Assoc, how='left', on='GEN_CAT_ID') ###################
#st_rc_st_rc_gen['COOL_CAT_ID'] = st_rc_st_rc_gen['PLANT_CODE_x'].map(str) + '_' + st_rc_st_rc_gen['COOLING_ID']  
#st_rc_st_rc_gen = st_rc_st_rc_gen.merge(Cool_all, how='left', on='COOL_CAT_ID')

st_rc_st_rc_gen = st_rc_st_rc_gen.loc[st_rc_st_rc_gen['PRIME_MOVER'].isin(['ST', 'CA', 'BT'])].groupby('PLANT_CODE').sum()
#st_rc_st_rc_gen = st_rc_st_rc_gen.loc[st_rc_st_rc_gen['PRIME_MOVER'].isin(['ST', 'CA', 'BT'])].loc[st_rc_st_rc_gen['COOLING_TYPE1'].isin(['HRC', 'HRF', 'HRI', 'RC', 'RF', 'RI', 'RN', 'RU'])].groupby('PLANT_CODE').sum()

ST_WECC_RC['CAP_FRAC'] = st_rc_st_rc_gen['NAMEPLATE']/st_rc_tot_gen['NAMEPLATE']


st_op_tot_gen = b.d['GeneratorY09_Exist'].set_index('PLANT_CODE', drop=False).loc[st_wecc_op_stix].groupby('PLANT_CODE').sum()
st_op_st_op_gen = b.d['GeneratorY09_Exist'].set_index('PLANT_CODE', drop=False).loc[st_wecc_op_stix]
st_op_st_op_gen['GEN_CAT_ID'] = st_op_st_op_gen['PLANT_CODE'].map(str) + '_' + st_op_st_op_gen['GENERATOR_ID']

st_op_st_op_gen = st_op_st_op_gen.merge(Assoc, how='left', on='GEN_CAT_ID') ###################
st_op_st_op_gen['COOL_CAT_ID'] = st_op_st_op_gen['PLANT_CODE_x'].map(str) + '_' + st_op_st_op_gen['COOLING_ID']  
st_op_st_op_gen = st_op_st_op_gen.merge(Cool_all, how='left', on='COOL_CAT_ID').drop_duplicates(subset=['COOL_CAT_ID'])

st_op_st_op_gen = st_op_st_op_gen.loc[st_op_st_op_gen['PRIME_MOVER'].isin(['ST', 'CA', 'BT'])].loc[st_op_st_op_gen['COOLING_TYPE1'].isin(['OC', 'OF', 'OS'])].groupby('PLANT_CODE').sum()

ST_WECC_OP['CAP_FRAC'] = st_op_st_op_gen['NAMEPLATE']/st_op_tot_gen['NAMEPLATE']
ST_WECC_OP['INTAKE_RATE_AT_100_PCT'] = st_op_st_op_gen['INTAKE_RATE_AT_100_PCT']
ST_WECC_OP['CAP_FRAC'] = ST_WECC_OP['CAP_FRAC'].fillna(1.0)


## ADD 767 DATA

eia_767 = b.d['F767_GENERATOR'].set_index('PLANT_CODE', drop=False)
eia_767['TEMP_RISE_AT_100_PCT'] = eia_767['TEMP_RISE_AT_100_PCT'].replace(to_replace={'EN' : np.nan, 'NA': np.nan, ' NA':np.nan}).astype(float)
eia_767['WATER_FLOW_100_PCT'] = eia_767['WATER_FLOW_100_PCT'].replace(to_replace={'EN' : np.nan, 'NA': np.nan, ' NA':np.nan, '10,000':10000}).astype(float) 
eia_767['FLOW_RISE'] = eia_767['TEMP_RISE_AT_100_PCT']*eia_767['WATER_FLOW_100_PCT']


water_flow_rc = eia_767.loc[st_wecc_rc_stix].groupby('PLANT_CODE').sum()['WATER_FLOW_100_PCT']
temp_rise_rc = (eia_767.loc[st_wecc_rc_stix].groupby('PLANT_CODE').sum()['FLOW_RISE'])/water_flow_rc
rc_water = pd.concat([water_flow_rc, temp_rise_rc], axis=1)
rc_water['WATER_FLOW'] = rc_water[0]
rc_water['TEMP_RISE'] = rc_water[1]
del rc_water[0]
del rc_water[1]

ST_WECC_RC = pd.concat([ST_WECC_RC, rc_water], axis=1)
ST_WECC_RC = ST_WECC_RC[['PNAME', 'LAT', 'LON', 'CAPFAC', 'NAMEPCAP', 'NAMEPLATE', 'PLPRMFL', 'WR_REG', 'W_SRC', 'PCODE', 'CAP_FRAC', 'SUMMER_CAPABILITY', 'WINTER_CAPABILITY', 'Intake Peak Winter Temperature', 'Outlet Peak Winter Temperature', 'Intake Peak Summer Temperature', 'Outlet Peak Summer Temperature', 'INTAKE_RATE_AT_100_PCT', 'TOWER_WATER_RATE_PCT', 'WATER_FLOW', 'TEMP_RISE', 'ELEC_EFF_JAN', 'ELEC_EFF_FEB', 'ELEC_EFF_MAR', 'ELEC_EFF_APR', 'ELEC_EFF_MAY', 'ELEC_EFF_JUN', 'ELEC_EFF_JUL', 'ELEC_EFF_AUG', 'ELEC_EFF_SEP', 'ELEC_EFF_OCT', 'ELEC_EFF_NOV', 'ELEC_EFF_DEC', 'ELEC_EFF_AVG']]
ST_WECC_RC.fillna(np.nan, inplace=True)

kos_map = lambda x: 0.12 if x['PLPRMFL'] in ['ANT', 'BIT', 'LIG', 'SUB', 'SC', 'RC', 'WC'] else 0 if x['PLPRMFL'] in ['NUC', 'GEO'] else 0.2

ST_WECC_RC['Kos'] = ST_WECC_RC.apply(kos_map, axis=1)


ST_WECC_RC['WCIRC_CALC'] = (ST_WECC_RC['NAMEPLATE']*ST_WECC_RC['CAP_FRAC']*(1-ST_WECC_RC['ELEC_EFF_AVG'] - ST_WECC_RC['Kos'])/ST_WECC_RC['ELEC_EFF_AVG'])/(0.004179*ST_WECC_RC['TEMP_RISE']/1.8)/28.32

ST_WECC_RC['WCIRC_CALC'].replace(to_replace={np.inf : np.nan, -np.inf : np.nan}, inplace=True)

water_flow_op = eia_767.loc[st_wecc_op_stix].groupby('PLANT_CODE').sum()['WATER_FLOW_100_PCT']
temp_rise_op = (eia_767.loc[st_wecc_op_stix].groupby('PLANT_CODE').sum()['FLOW_RISE'])/water_flow_op
op_water = pd.concat([water_flow_op, temp_rise_op], axis=1)
op_water['WATER_FLOW'] = op_water[0]
op_water['TEMP_RISE'] = op_water[1]
del op_water[0]
del op_water[1]

ST_WECC_OP = pd.concat([ST_WECC_OP, op_water], axis=1)
ST_WECC_OP = ST_WECC_OP[['PNAME', 'LAT', 'LON', 'CAPFAC', 'NAMEPCAP', 'NAMEPLATE', 'PLPRMFL', 'WR_REG', 'W_SRC', 'PCODE', 'CAP_FRAC', 'SUMMER_CAPABILITY', 'WINTER_CAPABILITY','Intake Peak Winter Temperature', 'Outlet Peak Winter Temperature', 'Intake Peak Summer Temperature', 'Outlet Peak Summer Temperature', 'INTAKE_RATE_AT_100_PCT', 'TOWER_WATER_RATE_PCT', 'WATER_FLOW', 'TEMP_RISE', 'ELEC_EFF_JAN', 'ELEC_EFF_FEB', 'ELEC_EFF_MAR', 'ELEC_EFF_APR', 'ELEC_EFF_MAY', 'ELEC_EFF_JUN', 'ELEC_EFF_JUL', 'ELEC_EFF_AUG', 'ELEC_EFF_SEP', 'ELEC_EFF_OCT', 'ELEC_EFF_NOV', 'ELEC_EFF_DEC', 'ELEC_EFF_AVG']]
ST_WECC_OP.fillna(np.nan, inplace=True)

ST_WECC_OP['Kos'] = ST_WECC_OP.apply(kos_map, axis=1)

ST_WECC_OP['WCOND_CALC'] = (ST_WECC_OP['NAMEPLATE']*ST_WECC_OP['CAP_FRAC']*(1-ST_WECC_OP['ELEC_EFF_AVG'] - ST_WECC_OP['Kos'])/ST_WECC_OP['ELEC_EFF_AVG'])/(0.004179*ST_WECC_OP['TEMP_RISE']/1.8)/28.32

ST_WECC_OP['WCOND_CALC'].replace(to_replace={np.inf : np.nan, -np.inf : np.nan}, inplace=True)

post_pp_d.update({'st_rc' : ST_WECC_RC})
post_pp_d.update({'st_op' : ST_WECC_OP})


ST_WECC_RC.iloc[:, 308:321].mean()
ST_WECC_OP.iloc[:, 308:321].mean()
#ST_WECC_RC[['PNAME', 'LAT', 'LON', 'CAPFAC', 'NAMEPCAP', 'PLPRMFL', 'WR_REG', 'W_SRC', 'PCODE']].dropna(subset=['LAT']).to_csv('ST_WECC_RC.csv')
#ST_WECC_OP[['PNAME', 'LAT', 'LON', 'CAPFAC', 'NAMEPCAP', 'PLPRMFL', 'WR_REG', 'W_SRC', 'PCODE']].dropna(subset=['LAT']).to_csv('ST_WECC_OP.csv')


####GET SOLAR PV##########################

PVix = b.d['eGRID_2009_gen']['ORISPL'].ix[b.d['eGRID_2009_gen']['PRMVR'] == 'PV'].drop_duplicates()
#WECC_PV = b.d['eGRID_2009_plant'].loc[(b.d['eGRID_2009_plant']['PLPRMFL'] == 'SUN') & (b.d['eGRID_2009_plant']['NERC'] == 'WECC')]
WECC_PV = b.d['eGRID_2009_plant'].loc[b.d['eGRID_2009_plant']['NERC'] == 'WECC']

PV_WECC_ll = WECC_PV.drop_duplicates(subset=['ORISPL']).set_index('ORISPL').loc[PVix].dropna(subset=['SEQPLT09'])

PV_WRR = b.d['EW3_main_data'].drop_duplicates(subset=['Plant Code']).set_index('Plant Code').loc[pd.Series(PV_WECC_ll.index).values][['Water Resource Region', 'Reported Water Source (Type)']].dropna(subset=['Reported Water Source (Type)'])

PV_WECC = pd.concat([PV_WECC_ll['PNAME'], PV_WECC_ll['LAT'], PV_WECC_ll['LON'], PV_WECC_ll['CAPFAC'], PV_WECC_ll['NAMEPCAP'], PV_WECC_ll['PLPRMFL'], PV_WRR['Water Resource Region'], PV_WRR['Reported Water Source (Type)']], axis=1)

PV_WECC['WR_REG'] = PV_WECC['Water Resource Region'].map(wrrdict)
del PV_WECC['Water Resource Region']
PV_WECC['W_SRC'] = PV_WECC['Reported Water Source (Type)']
del PV_WECC['Reported Water Source (Type)']
PV_WECC['PCODE'] = PV_WECC.index

for i, k in PV_WECC['WR_REG'].loc[PV_WECC['WR_REG'].isnull()].iteritems():
#	print i, k
	fn_d = {}
	for x, z in basincent.items():
		blat = z[0]
		blon = z[1]
		slat = PV_WECC['LAT'][i]
		slon = PV_WECC['LON'][i]
		diff = ((blat - slat)**2 + (blon - slon)**2)**0.5
		fn_d.update({x : diff})
	cell = min(fn_d, key=fn_d.get)
	PV_WECC['WR_REG'][i] = cell

pv_wecc_stix = [i for i in PV_WECC.index]

pv_tot_gen = b.d['GeneratorY09_Exist'].set_index('PLANT_CODE', drop=False).loc[pv_wecc_stix].groupby('PLANT_CODE').sum()
pv_pv_gen = b.d['GeneratorY09_Exist'].set_index('PLANT_CODE', drop=False).loc[pv_wecc_stix]
pv_pv_gen = pv_pv_gen.loc[pv_pv_gen['PRIME_MOVER'] == 'PV'].groupby('PLANT_CODE').sum()

PV_WECC['CAP_FRAC'] = pv_pv_gen['NAMEPLATE']/pv_tot_gen['NAMEPLATE']

post_pp_d.update({'pv' : PV_WECC})


#PV_WECC.to_csv('PV_WECC.csv')

######GET WIND TURBINES######################################

WNix = b.d['eGRID_2009_gen']['ORISPL'].ix[b.d['eGRID_2009_gen']['PRMVR'] == 'WT'].drop_duplicates()
#WECC_WN = b.d['eGRID_2009_plant'].loc[(b.d['eGRID_2009_plant']['PLPRMFL'] == 'WND') & (b.d['eGRID_2009_plant']['NERC'] == 'WECC')]
WECC_WN = b.d['eGRID_2009_plant'].loc[b.d['eGRID_2009_plant']['NERC'] == 'WECC']

WN_WECC_ll = WECC_WN.drop_duplicates(subset=['ORISPL']).set_index('ORISPL').loc[WNix].dropna(subset=['SEQPLT09'])

WN_WRR = b.d['EW3_main_data'].drop_duplicates(subset=['Plant Code']).set_index('Plant Code').loc[pd.Series(WN_WECC_ll.index).values][['Water Resource Region', 'Reported Water Source (Type)']].dropna(subset=['Reported Water Source (Type)'])

WN_WECC = pd.concat([WN_WECC_ll['PNAME'], WN_WECC_ll['LAT'], WN_WECC_ll['LON'], WN_WECC_ll['CAPFAC'], WN_WECC_ll['NAMEPCAP'], WN_WECC_ll['PLPRMFL'], WN_WRR['Water Resource Region'], WN_WRR['Reported Water Source (Type)']], axis=1)

WN_WECC['WR_REG'] = WN_WECC['Water Resource Region'].map(wrrdict)
del WN_WECC['Water Resource Region']
WN_WECC['W_SRC'] = WN_WECC['Reported Water Source (Type)']
del WN_WECC['Reported Water Source (Type)']
WN_WECC['PCODE'] = WN_WECC.index


for i, k in WN_WECC['WR_REG'].loc[WN_WECC['WR_REG'].isnull()].iteritems():
#	print i, k
	fn_d = {}
	for x, z in basincent.items():
		blat = z[0]
		blon = z[1]
		slat = WN_WECC['LAT'][i]
		slon = WN_WECC['LON'][i]
		diff = ((blat - slat)**2 + (blon - slon)**2)**0.5
		fn_d.update({x : diff})
	cell = min(fn_d, key=fn_d.get)
	WN_WECC['WR_REG'][i] = cell



wn_wecc_stix = [i for i in WN_WECC.index]

wn_tot_gen = b.d['GeneratorY09_Exist'].set_index('PLANT_CODE', drop=False).loc[wn_wecc_stix].groupby('PLANT_CODE').sum()
wn_wn_gen = b.d['GeneratorY09_Exist'].set_index('PLANT_CODE', drop=False).loc[wn_wecc_stix]
wn_wn_gen = wn_wn_gen.loc[wn_wn_gen['PRIME_MOVER'] == 'WT'].groupby('PLANT_CODE').sum()

WN_WECC['CAP_FRAC'] = wn_wn_gen['NAMEPLATE']/wn_tot_gen['NAMEPLATE']

post_pp_d.update({'wn' : WN_WECC})




pickle.dump(post_pp_d, open('post_pp_d.p', 'wb'))


### ALL WECC NAEMPLATE EXCEPT HYDRO

all_wecc = pd.Series([float(i) for i in b.d['eGRID_2009_plant']['NAMEPCAP'].loc[b.d['eGRID_2009_plant']['NERC'] == 'WECC'].loc[b.d['eGRID_2009_plant']['PLPRMFL'] != 'WAT'].str.replace(',', '')])

#WN_WECC.to_csv('WN_WECC.csv')

'''
#############
hydroelectric
#############
PCODE
LAT
LON

PNAME
CAPACITY
ANNUAL GENERATION

#############
solar
#############
PCODE
LAT
LON

PNAME
CAPACITY
ANNUAL GENERATION

#############
wind
#############
PCODE
LAT
LON

PNAME
CAPACITY
ANNUAL GENERATION

#############
thermo -- combustion turbine
#############
PCODE					[eGRID] / [860_Plant: PlantY09]
LAT					[eGRID]
LON					[eGRID]

PNAME					[eGRID]
CAPACITY
ANNUAL GENERATION

#############
thermo -- steam turbine
#############
PCODE					[eGRID] / [860_Plant: PlantY09]
LAT					[eGRID]
LON					[eGRID]

NERC REGION				[860_Plant: PlantY09]
PRIME MOVER				[860_Generator: Exist]
COOLING SYSTEM TYPE			[860_EnviroEquip:Cool]
COOLING SYSTEM MAX INTAKE		[860_EnviroEquip:Cool]
INLET/OUTLET WATER TEMPS		[923_Sched_3A: Cooling Operations]
FUEL SOURCE				[eGRID] / [923_Mon_TS]
PNAME					[860_Plant: PlantY09]
CAPACITY				[eGRID] / [860_Plant: PlantY09]
ANNUAL GENERATION			[eGRID]
EFFICIENCY/CHANGES
	|-Monthly Elect Output		[923_Mon_TS: Page 1]
	|-Monthly Heat Input		[923_Mon_TS: Page 1]
Dry Air Mass Flow Rate			[
Heat Load				[923_Mon_TS: Page 1]
Boiler Efficiency at 100% Load		[EnviroEquip:Boiler]			
CHP Export				[]
(FLUE STACK PROPERTIES)			[860_EnviroEquip:SF, FGP, FGD] 
(STEAM FLOW)				[860_EnviroEquip: Boiler]
(WASTE HEAT INPUT)			[860_EnviroEquip: Boiler]
'''

'''
Form 860

Table 7a: Cooling System Type Codes	
	
Code	Cooling System Type Description
DC	Dry (air) cooling system
HRC	Hybrid: recirculating cooling pond(s) or canal(s) with dry cooling
HRF	Hybrid: recirculating with forced draft cooling tower(s) with dry cooling
HRI	Hybrid: recirculating with induced draft cooling tower(s) with dry cooling
OC	Once through with cooling pond(s) or canal(s)
OF	Once through, fresh water
OS	Once through, saline water
RC	Recirculating with cooling pond(s) or canal(s)
RF	Recirculating with forced draft cooling tower(s)
RI	Recirculating with induced draft cooling tower(s)
RN	Recirculating with natural draft cooling tower(s)
OT	Other
	
Table 7b: Cooling Tower Type Codes	
	
Code	Cooling Tower Type Description
MD	Mechanical draft, dry process
MW	Mechanical draft, wet process
ND	Natural draft, dry process
NW	Natural draft, wet process
WD	Combination wet and dry process
OT	Other

Outlet enthalpy:
http://www.che.com/nl/YToyOntpOjA7czo0OiI4OTQ5IjtpOjE7czo4NjoicHJvY2Vzc2luZ19hbmRfaGFuZGxpbmcvdGhlcm1hbF9hbmRfZW5lcmd5X21nbXQvaGVhdF9leGNoYW5nZXJzX2NvbmRlbnNlcnNfYW5kX2Nvb2xlcnMiO30=/
'''

