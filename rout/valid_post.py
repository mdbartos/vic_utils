import os
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import datetime
from matplotlib.colors import LogNorm
from pylab import *

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def base62_encode(num, alphabet=ALPHABET):
    """Encode a number in Base X

    `num`: The number to encode
    `alphabet`: The alphabet to use for encoding
    """
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)

def base62_decode(string, alphabet=ALPHABET):
    """Decode a Base X encoded string into the number

    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for encoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1

    return num

plotbasins = {
'lees_f' : {
        'yampa hw' : 9251000,
        'yampa' : 9260000,
        'little snake' : 9257000,
        'green hw' : 9199500,
        'green' : 9261000,
        'duchesne' : 9288180,
        'white' : 9306500,
        'san rafael' : 9328000,
        'green blw san rafael' : 9315000,
        'dolores' : 9180000,
        'dolores2' : 9177000,
        'dolores3' : 9175500,
        'gunnison' : 9132500,
        'colorado hw' : 9093700,
        'colorado hw2' : 9070000,
        'colorado hw3' : 9089500,
        'san juan hw' : 9344000,
        'san juan' : 9368000
    },
'pitt' : {
        'sacramento' : 11350500,
        'feather mf' : 11391500,
        'stony cr' : 11388500,
        'cache cr' : 11453500,
        'yuba' : 11408501,
        'american sf' : 11439500,
        'tuolumne' : 11286500,
        'tuolumne2' : 11277000,
        'merced' : 11266500,
        'kings' : 11214000,
        'kings2' : 11218500
    },

'wauna' : {
    'henrys fk' : 13055000,
    'snake hw' : 13011900,
    'big wood' : 13141000,
    'owyhee' : 13181000,
    'payette' : 13235000,
    'payette2': 13237500,
    'salmon' : 13317000,
    'grande ronde' : 13330000,
    'clearwater' : 13336500,
    'blackfoot/clark fk' : 12340000,
    'blackfoot2' : 12354500,
    'blackfoot3' : 12344000,
    'flathead' : 12370000,
    'spokane' : 12413000,
    'spokane2' : 12414500,
    'spokane3' : 12433000,
    'wilamette' : 14157500,
    'willamette2' : 14150300,
    'willamette3' : 14200000,
    'willamette4' : 14198500,
    'stehekin' : 12451000,
    'methow' : 12447390

    },

'peck' : {

        'marias' : 6092000,
        'marias2' : 6099500,
        'jefferson' : 6034500,
        'ruby' : 6019500,
        'sun' : 6089000,
        'musselshell' : 6115500,
        'musselshell2' : 6127500
        },

'colstrip' : {
        'yellowstone' : 6191500,
        'yellowstone2' : 6214500,
        'yellowstone3' : 6192500,
        'bighorn' : 6259500
        },

'guer' : {
        'n platte' : 6627000,
        'n platte2' : 6630000,
        },

'pawnee' : {
        's platte' : 6725500,
        's platte 2' : 6727000,
        's platte 3' : 6729500,
        's platte 4' : 6736500,
        's platte 5' : 6752000
        },

'comanche' : {
        'arkred' : 7081200,
        'arkred2' : 7084500
        }
}

#rpath = '/home/chesterlab/Bartos/VIC/output/rout/valid/d8/hist'
#vpath = '/media/melchior/BALTHASAR/nsf_hydro/post/validation'
#wbpath = '/media/melchior/BALTHASAR/nsf_hydro/post/img/validation'


def plot_stncode_stack(stn_code, basin):
	fn = base62_encode(stn_code)
	fpad = ''.join([' ' for j in range(5-len(str(fn)))])
	spad = ''.join(['0' for j in range(8-len(str(stn_code)))])  

        ncode = stn_code
        stn_name = pd.read_csv(namespath + '/' + basin + '_' + 'valid.csv', sep='\t', header=None).set_index(1).loc[ncode, 2]


	stn_code = spad + str(stn_code)
	fn = basin + '_' + fn + fpad + '.day'
			
	rout = pd.read_fwf('%s/%s/%s' % (rpath, basin, fn), header=None, widths=[12, 12, 12, 13])
	rout.columns = ['year', 'month', 'day', 'rout_cfs']
	rout = rout.loc[rout['month'].isin([1,2,3,4,5,6,7,8,9,10,11,12])]
	mkdate = lambda x: datetime.date(int(x['year']), int(x['month']), int(x['day']))
	rout['date'] = rout.apply(mkdate, axis=1)
	rout = rout.set_index('date')

	valid = pd.read_csv('%s/%s/%s.csv' % (vpath, basin, stn_code))
	flowcol = [i for i in valid.columns if i[0] in ['0','1','2','3','4','5','6','7','8','9'] and i[-1] != 'd']
	print flowcol
	if len(flowcol) > 1:
		flowcol = [i for i in flowcol if i[-1] == '3']
	valid['datetime'] = pd.to_datetime(valid['datetime'])
	valid = valid.set_index('datetime')

	combined = pd.concat([rout, valid], axis=1, join='inner').dropna()

	x = combined[flowcol].astype(float).values
	y = combined['rout_cfs'].values
#	print x, y
	x = np.reshape(x, (len(x),))	
#	print x.shape
#	print y.shape
#	print x, y

	fig = plt.figure()
	r2 = pd.Series(y).corr(pd.Series(x))
	n = len(x)
	plt.hist2d(x, y, bins=200, norm=LogNorm())
	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
	plt.figtext(0.15, 0.82, 'r = %.3f\nn = %s' % (r2, n), bbox=props)
	try:
		plt.colorbar()
		plt.title('Observed flow vs. modeled flow at station %s,\n %s' % (stn_code, stn_name))
		plt.xlabel('Observed flow (cfs)')
		plt.ylabel('Modeled flow (cfs)')
	
	#	plt.scatter(x,y)
		plt.plot(list(set(x)), list(set(x)), color='black', linewidth=0.3)
		plt.savefig('%s/hs_%s.png' % (wbpath, stn_code), bbox_inches='tight')
		plt.clf()
	except:
		pass


#	print 1 - sum((y-x)**2)/sum((x-np.mean(x))**2)

def plot_stncode_timeseries(stn_code, basin):
	fn = base62_encode(stn_code)
	fpad = ''.join([' ' for j in range(5-len(str(fn)))])
	spad = ''.join(['0' for j in range(8-len(str(stn_code)))])  

        ncode = stn_code
        stn_name = pd.read_csv(namespath + '/' + basin + '_' + 'valid.csv', sep='\t', header=None).set_index(1).loc[ncode, 2]


	stn_code = spad + str(stn_code)
	fn = basin + '_' + fn + fpad + '.day'
			
	rout = pd.read_fwf('%s/%s/%s' % (rpath, basin, fn), header=None, widths=[12, 12, 12, 13])
	rout.columns = ['year', 'month', 'day', 'rout_cfs']
	rout = rout.loc[rout['month'].isin([1,2,3,4,5,6,7,8,9,10,11,12])]
	mkdate = lambda x: datetime.date(int(x['year']), int(x['month']), int(x['day']))
	rout['date'] = rout.apply(mkdate, axis=1)
	rout = rout.set_index('date')

	valid = pd.read_csv('%s/%s/%s.csv' % (vpath, basin, stn_code))
	flowcol = [i for i in valid.columns if i[0] in ['0','1','2','3','4','5','6','7','8','9'] and i[-1] != 'd']
	print flowcol
	if len(flowcol) > 1:
		flowcol = [i for i in flowcol if i[-1] == '3']
	valid['datetime'] = pd.to_datetime(valid['datetime'])
	valid = valid.set_index('datetime')

	combined = pd.concat([rout, valid], axis=1, join='inner').dropna()

	x = combined[flowcol].astype(float)
	y = combined['rout_cfs']
#	print x, y
	x = np.reshape(x, (len(x),))	
#	print x.shape
#	print y.shape
#	print x, y

	fig = plt.figure()
	r2 = pd.Series(y).corr(pd.Series(x))
	n = len(x)
	plt.plot(x.index, x, color='black', label='observed')
	plt.plot(y.index, y, color='red', linestyle='--', label='modeled')
        plt.legend()
#	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
#	plt.figtext(0.15, 0.82, 'r = %.3f\nn = %s' % (r2, n), bbox=props)
	try:
#		plt.colorbar()
		plt.title('Observed flow vs. modeled flow at station %s,\n %s' % (stn_code, stn_name))
		plt.xlabel('Time')
		plt.ylabel('Discharge (cfs)')
	
	#	plt.scatter(x,y)
#		plt.plot(list(set(x)), list(set(x)), color='black', linewidth=0.3)
		plt.savefig('%s/ts_%s.png' % (wbpath, stn_code), bbox_inches='tight')
		plt.clf()
	except:
		pass

def plot_stncode_quantile(stn_code, basin):
	fn = base62_encode(stn_code)
	fpad = ''.join([' ' for j in range(5-len(str(fn)))])
	spad = ''.join(['0' for j in range(8-len(str(stn_code)))])  
        
        ncode = stn_code
        stn_name = pd.read_csv(namespath + '/' + basin + '_' + 'valid.csv', sep='\t', header=None).set_index(1).loc[ncode, 2]


	stn_code = spad + str(stn_code)
	fn = basin + '_' + fn + fpad + '.day'
			
	rout = pd.read_fwf('%s/%s/%s' % (rpath, basin, fn), header=None, widths=[12, 12, 12, 13])
	rout.columns = ['year', 'month', 'day', 'rout_cfs']
	rout = rout.loc[rout['month'].isin([1,2,3,4,5,6,7,8,9,10,11,12])]
	mkdate = lambda x: datetime.date(int(x['year']), int(x['month']), int(x['day']))
	rout['date'] = rout.apply(mkdate, axis=1)
	rout = rout.set_index('date')

	valid = pd.read_csv('%s/%s/%s.csv' % (vpath, basin, stn_code))
	flowcol = [i for i in valid.columns if i[0] in ['0','1','2','3','4','5','6','7','8','9'] and i[-1] != 'd']
	print flowcol
	if len(flowcol) > 1:
		flowcol = [i for i in flowcol if i[-1] == '3']
	valid['datetime'] = pd.to_datetime(valid['datetime'])
	valid = valid.set_index('datetime')

	combined = pd.concat([rout, valid], axis=1, join='inner').dropna()

	x = combined[flowcol].astype(float)
	y = combined['rout_cfs']
#	print x, y
#	x = np.reshape(x, (len(x),))	
#	print x.shape
#	print y.shape
#	print x, y

	qx = pd.Series([x.quantile(i/100.0) for i in range(1,101)])
	qy = pd.Series([y.quantile(i/100.0) for i in range(1,101)])

	print qx
	print qy

	fig = plt.figure()
        ax = fig.add_subplot()
	r2 = pd.Series(y).corr(pd.Series(x))
	n = len(x)
	plt.semilogy(qx.index, qx, color='black', label='observed')
	plt.semilogy(qy.index, qy, color='red', linestyle='--', label='modeled')
#	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
#	plt.figtext(0.15, 0.82, 'r = %.3f\nn = %s' % (r2, n), bbox=props)
	try:
#		plt.colorbar()
		plt.title('Observed flow vs. modeled flow at station %s,\n %s' % (stn_code, stn_name))
		plt.xlabel('Percentile')
		plt.ylabel('Discharge (cfs)')
		plt.xlim(0,100)
                plt.legend()
	#	plt.scatter(x,y)
#		plt.plot(list(set(x)), list(set(x)), color='black', linewidth=0.3)
		plt.savefig('%s/qt_%s.png' % (wbpath, stn_code), bbox_inches='tight')
		plt.clf()
	except:
		pass


def plot_stncode_monthly(stn_code, basin):
	fn = base62_encode(stn_code)
	fpad = ''.join([' ' for j in range(5-len(str(fn)))])
	spad = ''.join(['0' for j in range(8-len(str(stn_code)))])  
	ncode = stn_code

	stn_code = spad + str(stn_code)
	fn = basin + '_' + fn + fpad + '.day'
	
        stn_name = pd.read_csv(namespath + '/' + basin + '_' + 'valid.csv', sep='\t', header=None).set_index(1).loc[ncode, 2]

	rout = pd.read_fwf('%s/%s/%s' % (rpath, basin, fn), header=None, widths=[12, 12, 12, 13])
	rout.columns = ['year', 'month', 'day', 'rout_cfs']
	rout = rout.loc[rout['month'].isin([1,2,3,4,5,6,7,8,9,10,11,12])]
	mkdate = lambda x: datetime.date(int(x['year']), int(x['month']), int(x['day']))
	rout['date'] = rout.apply(mkdate, axis=1)
	rout = rout.set_index('date')

	valid = pd.read_csv('%s/%s/%s.csv' % (vpath, basin, stn_code))
	flowcol = [i for i in valid.columns if i[0] in ['0','1','2','3','4','5','6','7','8','9'] and i[-1] != 'd']
	print flowcol
	if len(flowcol) > 1:
		flowcol = [i for i in flowcol if i[-1] == '3']
	print flowcol
	valid['datetime'] = pd.to_datetime(valid['datetime'])
#	valid['month'] = [i.month for i in valid['datetime']]
#	valid['day'] = [i.day for i in valid['datetime']]
	valid = valid.set_index('datetime')

	combined = pd.concat([rout, valid], axis=1, join='inner').dropna()
	combined[flowcol] = combined[flowcol].astype(float)
	x = combined.groupby(['month', 'day']).quantile(0.5).reset_index()[flowcol].astype(float) 
	y = combined.groupby(['month', 'day']).quantile(0.5).reset_index()['rout_cfs'] 

        xall = combined[flowcol].iloc[:,0].astype(float) 
	yall = combined['rout_cfs'] 
        
        print xall, type(xall)
        print yall, type(yall)

#	print x, y
#	x = np.reshape(x, (len(x),))	
#	print x.shape
#	print y.shape
#	print x, y

	fig = plt.figure()
        n = len(xall)
#	nrmse = math.sqrt(np.mean((xall.values - yall.values)**2))/(xall.max() - xall.min())
        r = pd.Series(yall).corr(pd.Series(xall))
	plt.plot(x.index, x, color='black', label='observed')
	plt.plot(y.index, y, color='red', linestyle='--', label='modeled')
	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
	plt.figtext(0.15, 0.82, 'r = %.3f\nn = %s' % (r, n), bbox=props)
	try:
#		plt.colorbar()
		plt.title('Observed flow vs. modeled flow at station %s,\n %s' % (stn_code, stn_name))
		plt.xlabel('Day of Year')
		plt.ylabel('Discharge (cfs)')
		plt.xlim(0,366)
                plt.legend()
	#	plt.scatter(x,y)
#		plt.plot(list(set(x)), list(set(x)), color='black', linewidth=0.3)
		plt.savefig('%s/mo_%s.png' % (wbpath, stn_code), bbox_inches='tight')
		plt.clf()
	except:
		pass


def plot_stncode_stack_month(stn_code, basin):
	fn = base62_encode(stn_code)
	fpad = ''.join([' ' for j in range(5-len(str(fn)))])
	spad = ''.join(['0' for j in range(8-len(str(stn_code)))])  
	
	stn_code = spad + str(stn_code)
	fn = basin + '_' + fn + fpad + '.month'
			
	rout = pd.read_fwf('%s/%s/%s' % (rpath, basin, fn), header=None, widths=[12, 12, 13])
	rout.columns = ['year', 'month', 'rout_cfs']
	mkdate = lambda x: datetime.date(int(x['year']), int(x['month']), 15)
	rout['date'] = rout.apply(mkdate, axis=1)
	rout = rout.set_index('date')

	valid = pd.read_csv('%s/%s/%s.csv' % (vpath, basin, stn_code))
	flowcol = [i for i in valid.columns if i[0] in ['0','1','2','3','4','5','6','7','8','9'] and i[-1] != 'd']
	print flowcol
	if len(flowcol) > 1:
		flowcol = [i for i in flowcol if i[-1] == '3']
        valid['datetime'] = pd.to_datetime(valid['datetime'])
	valid = valid.set_index('datetime')

	combined = pd.concat([rout, valid], axis=1, join='inner').dropna()

	x = combined[flowcol].astype(float).values
	y = combined['rout_cfs'].values
	print x, y
	x = np.reshape(x, (len(x),))	
	print x.shape
	print y.shape
	print x, y
	plt.scatter(x,y)
	plt.plot(x,x)
	plt.savefig('%s/%s.png' % (wbpath, stn_code), bbox_inches='tight')
	plt.clf()


rpath = '/home/chesterlab/VIC/output/rout/valid/d8/hist'
vpath = '/home/chesterlab/post/validation'
wbpath = '/home/chesterlab/post/img/validation'
namespath = '/home/chesterlab/post/img/validation/validation_data'

b = 'comanche'

for j in plotbasins[b].keys():
    plot_stncode_monthly(plotbasins[b][j], b)
    plot_stncode_stack(plotbasins[b][j], b)
    plot_stncode_timeseries(plotbasins[b][j], b)
    plot_stncode_quantile(plotbasins[b][j], b)

b = 'pawnee'
basinpath = vpath + '/' + b
stnlist = [int(i.split('.')[0]) for i in os.listdir(basinpath)]

for i in stnlist:
	try:
		plot_stncode_monthly(i, b)
	except:
		continue

r_d = {}

def get_r_map(stn_code, basin):
	fn = base62_encode(stn_code)
	fpad = ''.join([' ' for j in range(5-len(str(fn)))])
	spad = ''.join(['0' for j in range(8-len(str(stn_code)))])  
	
	stn_code = spad + str(stn_code)
	fn = basin + '_' + fn + fpad + '.day'
			
	rout = pd.read_fwf('%s/%s/%s' % (rpath, basin, fn), header=None, widths=[12, 12, 12, 13])
	rout.columns = ['year', 'month', 'day', 'rout_cfs']
	rout = rout.loc[rout['month'].isin([1,2,3,4,5,6,7,8,9,10,11,12])]
	mkdate = lambda x: datetime.date(int(x['year']), int(x['month']), int(x['day']))
	rout['date'] = rout.apply(mkdate, axis=1)
	rout = rout.set_index('date')

	valid = pd.read_csv('%s/%s/%s.csv' % (vpath, basin, stn_code))
	flowcol = [i for i in valid.columns if i[0] in ['0','1','2','3','4','5','6','7','8','9'] and i[-1] != 'd']
	print flowcol
	if len(flowcol) > 1:
		flowcol = [i for i in flowcol if i[-1] == '3']
	valid['datetime'] = pd.to_datetime(valid['datetime'])
	valid = valid.set_index('datetime')

	combined = pd.concat([rout, valid], axis=1, join='inner').dropna()

	x = combined[flowcol].astype(float).values
	y = combined['rout_cfs'].values
#	print x, y
	x = np.reshape(x, (len(x),))	
#	print x.shape
#	print y.shape
#	print x, y

	r = pd.Series(y).corr(pd.Series(x))
        if not basin in r_d:
            r_d.update({basin : {}})

        r_d[basin].update({stn_code : [r, combined[flowcol].astype(float).mean()[0]]})


rpath = '/home/chesterlab/VIC/output/rout/valid/d8/hist'
vpath = '/home/chesterlab/post/validation'


for j in os.listdir(rpath):
    b = j
    basinpath = vpath + '/' + b
    stnlist = [int(i.split('.')[0]) for i in os.listdir(basinpath)]

    for i in stnlist:
    	try:
		get_r_map(i, b)
	except:
		continue


#############################
#MAP TO VALID STATIONS LATLON
#############################

import numpy as np
import pandas as pd
import pickle

r_d = pickle.load(open('r_map_d.p', 'rb'))

master_df = pd.DataFrame()

for basin in r_d.keys():
    stnlocs = pd.read_csv('%s_valid.csv' % (basin), sep='\t', names=['id', 'stn_code', 'name', 'lat', 'lon']).set_index('stn_code')

    stn_r = pd.DataFrame.from_dict(r_d[basin], orient='index')
    stn_r.columns = ['r', 'meanflow']
    stn_r.index = [int(i) for i in stn_r.index]

    cat_df = pd.concat([stnlocs, stn_r], axis=1)

    print cat_df
    master_df = master_df.append(cat_df)
