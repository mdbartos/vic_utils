import os
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import datetime

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


def plot_stncode(stn_code, basin):
	fn = base62_encode(stn_code)
	fpad = ''.join([' ' for j in range(5-len(str(fn)))])
	spad = ''.join(['0' for j in range(8-len(str(stn_code)))])  
	
	stn_code = spad + str(stn_code)
	fn = basin + '_' + fn + fpad + '.day'
			
	rout = pd.read_fwf('%s/%s/%s' % (rpath, basin, fn), header=None, widths=[12, 12, 12, 13])
	rout.columns = ['year', 'month', 'day', 'rout_cfs']
	mkdate = lambda x: datetime.date(int(x['year']), int(x['month']), int(x['day']))
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

	print 1 - sum((y-x)**2)/sum((x-np.mean(x))**2)

def plot_stncode_month(stn_code, basin):
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








#for basin in os.listdir(rpath):

for basin in ['guer']:
	for fn in os.listdir('%s/%s' % (rpath, basin)):
		if fn.endswith('day'):

	
			stn_code = base62_decode(fn.split('.')[0].split('_')[-1].split()[0])
			fpad = ''.join(['0' for j in range(8-len(str(stn_code)))])
		
			stn_code = fpad + str(stn_code) + '.csv'

			if stn_code in os.listdir(vpath + '/' + basin):
				print stn_code

				rout = pd.read_fwf('%s/%s/%s' % (rpath, basin, fn), header=None, widths=[12, 12, 12, 13])
				rout.columns = ['year', 'month', 'day', 'rout_cfs']
				mkdate = lambda x: datetime.date(int(x['year']), int(x['month']), int(x['day']))
				rout['date'] = rout.apply(mkdate, axis=1)
				rout = rout.set_index('date')
	
				valid = pd.read_csv('%s/%s/%s' % (vpath, basin, stn_code))
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
				plt.savefig('%s/%s.png' % (wbpath, stn_code.split('.')[0]), bbox_inches='tight')
				plt.clf()
			
	#		xy = np.vstack([x, y])
	#		z = gaussian_kde(xy)(xy)

	#		plt.figure()
	#		plt.scatter(x, y, c=z, s=100, edgecolor='')	
	#		plt.savefig('%s/%s.png' % (wbpath, stn_code), bbox_inches='tight')
	#		plt.clf()
			print len(x), len(y)





#### CREATE PLOT

			nullfmt   = NullFormatter()         # no labels
			
			# definitions for the axes
			left, width = 0.1, 0.65
			bottom, height = 0.1, 0.65
			bottom_h = left_h = left+width+0.02
			
			rect_scatter = [left, bottom, width, height]
			rect_histx = [left, bottom_h, width, 0.2]
			rect_histy = [left_h, bottom, 0.2, height]
			
			# start with a rectangular Figure
			plt.figure(1, figsize=(8,8))
			
			axScatter = plt.axes(rect_scatter)
			axHistx = plt.axes(rect_histx)
			axHisty = plt.axes(rect_histy)
			
			# no labels
			axHistx.xaxis.set_major_formatter(nullfmt)
			axHisty.yaxis.set_major_formatter(nullfmt)
			
			# the scatter plot:
			axScatter.scatter(x, y)
			
			# now determine nice limits by hand:
			binwidth = 0.25
			xymax = np.max( [np.max(np.fabs(x)), np.max(np.fabs(y))] )
			lim = ( int(xymax/binwidth) + 1) * binwidth
			
			axScatter.set_xlim( (-lim, lim) )
			axScatter.set_ylim( (-lim, lim) )
			
			bins = np.arange(-lim, lim + binwidth, binwidth)
			axHistx.hist(x, bins=bins)
			axHisty.hist(y, bins=bins, orientation='horizontal')
			
			axHistx.set_xlim( axScatter.get_xlim() )
			axHisty.set_ylim( axScatter.get_ylim() )

			plt.savefig('%s/%s.png' % (wbpath, stn_code), bbox_inches='tight')
			break
			#plt.show()
