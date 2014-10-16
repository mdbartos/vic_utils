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



rpath = '/home/chesterlab/Bartos/VIC/output/rout/valid/d8/hist'
vpath = '/media/melchior/BALTHASAR/nsf_hydro/post/validation'
wbpath = '/media/melchior/BALTHASAR/nsf_hydro/post/img/validation'


def plot_stncode_stack(stn_code, basin):
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

	fig = plt.figure()
	r2 = pd.Series(y).corr(pd.Series(x))
	n = len(x)
	plt.hist2d(x, y, bins=200, norm=LogNorm())
	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
	plt.figtext(0.15, 0.82, 'r = %.3f\nn = %s' % (r2, n), bbox=props)
	try:
		plt.colorbar()
		plt.title('Observed flow vs. modeled flow at station %s' % (stn_code))
		plt.xlabel('Observed flow (cfs)')
		plt.ylabel('Modeled flow (cfs)')
	
	#	plt.scatter(x,y)
		plt.plot(list(set(x)), list(set(x)), color='black', linewidth=0.3)
		plt.savefig('%s/%s.png' % (wbpath, stn_code), bbox_inches='tight')
		plt.clf()
	except:
		pass


#	print 1 - sum((y-x)**2)/sum((x-np.mean(x))**2)

def plot_stncode_timeseries(stn_code, basin):
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
	plt.plot(x.index, x, label='observed')
	plt.plot(y.index, y, label='modeled')
	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
	plt.figtext(0.15, 0.82, 'r = %.3f\nn = %s' % (r2, n), bbox=props)
	try:
#		plt.colorbar()
		plt.title('Observed flow vs. modeled flow at station %s' % (stn_code))
		plt.xlabel('Time')
		plt.ylabel('Discharge (cfs)')
	
	#	plt.scatter(x,y)
#		plt.plot(list(set(x)), list(set(x)), color='black', linewidth=0.3)
		plt.savefig('%s/%s.png' % (wbpath, stn_code), bbox_inches='tight')
		plt.clf()
	except:
		pass

def plot_stncode_quantile(stn_code, basin):
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
	r2 = pd.Series(y).corr(pd.Series(x))
	n = len(x)
	plt.plot(qx.index, qx, label='observed')
	plt.plot(qy.index, qy, label='modeled')
	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
	plt.figtext(0.15, 0.82, 'r = %.3f\nn = %s' % (r2, n), bbox=props)
	try:
#		plt.colorbar()
		plt.title('Observed flow vs. modeled flow at station %s' % (stn_code))
		plt.xlabel('Percentile')
		plt.ylabel('Discharge (cfs)')
		plt.xlim(0,99)	
	#	plt.scatter(x,y)
#		plt.plot(list(set(x)), list(set(x)), color='black', linewidth=0.3)
		plt.savefig('%s/%s.png' % (wbpath, stn_code), bbox_inches='tight')
		plt.clf()
	except:
		pass


def plot_stncode_monthly(stn_code, basin):
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
	print flowcol
	valid['datetime'] = pd.to_datetime(valid['datetime'])
#	valid['month'] = [i.month for i in valid['datetime']]
#	valid['day'] = [i.day for i in valid['datetime']]
	valid = valid.set_index('datetime')

	combined = pd.concat([rout, valid], axis=1, join='inner').dropna()
	combined[flowcol] = combined[flowcol].astype(float)
	x = combined.groupby(['month', 'day']).quantile(0.5).reset_index()[flowcol].astype(float) 
	y = combined.groupby(['month', 'day']).quantile(0.5).reset_index()['rout_cfs'] 
	print x, y
#	x = np.reshape(x, (len(x),))	
#	print x.shape
#	print y.shape
#	print x, y

	fig = plt.figure()
	cv = math.sqrt(np.mean((x.values - y.values)**2))/x.mean()
	print cv
	r2 = 0.8
	n = len(x)
	plt.plot(x.index, x, label='observed')
	plt.plot(y.index, y, label='modeled')
	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
	plt.figtext(0.15, 0.82, 'CV = %.3f\nn = %s' % (cv, n), bbox=props)
	try:
#		plt.colorbar()
		plt.title('Observed flow vs. modeled flow at station %s' % (stn_code))
		plt.xlabel('Day of Year')
		plt.ylabel('Discharge (cfs)')
		plt.xlim(0,366)	
	#	plt.scatter(x,y)
#		plt.plot(list(set(x)), list(set(x)), color='black', linewidth=0.3)
		plt.savefig('%s/%s.png' % (wbpath, stn_code), bbox_inches='tight')
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



b = 'baker'
basinpath = vpath + '/' + b
stnlist = [int(i.split('.')[0]) for i in os.listdir(basinpath)]

for i in stnlist:
	try:
		plot_stncode_timeseries(i, b)
	except:
		continue

