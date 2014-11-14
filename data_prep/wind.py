import numpy as np
import pandas as pd
import pysal as ps
import os


db = ps.open('/home/akagi/GIS/usgs_wind/USGS_windturbine_201307.dbf')
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
