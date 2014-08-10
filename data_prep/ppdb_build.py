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

CT_WECC.to_csv('CT_WECC.csv')
#####################################################

####GET STEAM TURBINES###############################
STix = b.d['eGRID_2009_gen']['ORISPL'].ix[b.d['eGRID_2009_gen']['PRMVR'].isin(['ST', 'CA', 'BT'])].drop_duplicates()
STpl_ix = b.d['eGRID_2009_plant'].drop_duplicates(subset=['ORISPL']).set_index('ORISPL').loc[STix]
ST_WECC_ll = STpl_ix.loc[STpl_ix['NERC'] == 'WECC']
Cool = b.d['EnviroEquipY09_Cool'].set_index('PLANT_CODE', drop=False).loc[pd.Series(ST_WECC_ll.index)].dropna(subset=['COOLING_ID']).drop_duplicates(subset=['PLANT_CODE'])
Cool[['COOLING_TYPE1', 'COOLING_TYPE2', 'COOLING_TYPE3', 'COOLING_TYPE4']]
CoolOps = b.d['SCHEDULE 3A 5A 8A 8B 8C 8D 8E 8F REVISED 2009 04112011_Cooling Operations'].set_index('Plant ID', drop=False).loc[pd.Series(ST_WECC_ll.index)].dropna(subset=['Year']).drop_duplicates(subset=['Plant ID'])
EW3 = b.d['EW3_main_data'].drop_duplicates(subset=['Plant Code']).set_index('Plant Code')[['Water Resource Region', 'Reported Water Source (Type)']]

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

ST_WECC_RC = ST_WECC_RC.loc[ST_WECC_RC['W_SRC'].isin(['Surface Water', 'Unknown Freshwater', 'GW/Surface Water'])]
ST_WECC_OP = ST_WECC_OP.loc[ST_WECC_OP['W_SRC'].isin(['Surface Water', 'Unknown Freshwater', 'GW/Surface Water'])]

ST_WECC_RC[['PNAME', 'LAT', 'LON', 'CAPFAC', 'NAMEPCAP', 'PLPRMFL', 'WR_REG', 'W_SRC', 'PCODE']].dropna(subset=['LAT']).to_csv('ST_WECC_RC.csv')
ST_WECC_OP[['PNAME', 'LAT', 'LON', 'CAPFAC', 'NAMEPCAP', 'PLPRMFL', 'WR_REG', 'W_SRC', 'PCODE']].dropna(subset=['LAT']).to_csv('ST_WECC_OP.csv')

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

PV_WECC.to_csv('PV_WECC.csv')

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

WN_WECC.to_csv('WN_WECC.csv')

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

'''

