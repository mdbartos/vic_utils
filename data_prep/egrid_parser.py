from db_mash import mash_db
import pandas as pd
import numpy as np
import math
import pickle

b = mash_db('egrid')

b.import_xl()


plant_1997 = b.d['eGRID2002yr97_plant_EGRDPLNT97']
plant_1998 = b.d['eGRID2002yr98_plant_EGRDPLNT98']
plant_1999 = b.d['eGRID2002yr99_plant_EGRDPLNT99']
plant_2000 = b.d['eGRID2002yr00_plant_EGRDPLNT00']
plant_2004 = b.d['eGRID2006V2_1_year04_plant_EGRDPLNT04']
plant_2005 = b.d['eGRID2007V1_1year05_plant_PLNT05']
plant_2007 = b.d['eGRID2010V1_1_year07_PLANT_PLNT07']
plant_2009 = b.d['eGRID2012V1_0_year09_DATA_PLNT09']
plant_2010 = b.d['eGRID_9th_edition_V1-0_year_2010_Data_PLNT10']

egrid = {}

plant_1997.columns =  [i.split('\n')[0] for i in plant_1997.loc[2]]
plant_1997 = plant_1997.loc[3:]
plant_1998.columns =  [i.split('\n')[0] for i in plant_1998.loc[2]]
plant_1998 = plant_1998.loc[3:]
plant_1999.columns =  [i.split('\n')[0] for i in plant_1999.loc[2]]
plant_1999 = plant_1999.loc[3:]
plant_2000.columns =  [i.split('\n')[0] for i in plant_2000.loc[2]]
plant_2000 = plant_2000.loc[3:]
plant_2004.columns =  [i.split('\n')[0] for i in plant_2004.loc[3]]
plant_2004 = plant_2004.loc[4:]
plant_2005.columns =  [i.split('\n')[0] for i in plant_2005.loc[3]]
plant_2005 = plant_2005.loc[4:]
plant_2007.columns =  [i.split('\n')[0] for i in plant_2007.loc[3]]
plant_2007 = plant_2007.loc[4:]
plant_2009.columns =  [i.split('\n')[0] for i in plant_2009.loc[3]]
plant_2009 = plant_2009.loc[4:]
plant_2010.columns =  [i.split('\n')[0] for i in plant_2010.loc[3]]
plant_2010 = plant_2010.loc[4:]

egrid.update({'plant_1997' : plant_1997})
egrid.update({'plant_1998' : plant_1998})
egrid.update({'plant_1999' : plant_1999})
egrid.update({'plant_2000' : plant_2000})
egrid.update({'plant_2004' : plant_2004})
egrid.update({'plant_2005' : plant_2005})
egrid.update({'plant_2007' : plant_2007})
egrid.update({'plant_2009' : plant_2009})
egrid.update({'plant_2010' : plant_2010})

#pickle.dump(egrid, open('egrid_plant.p', 'wb'))

