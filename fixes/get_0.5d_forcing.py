import os
import shutil

rpath = '/run/user/1000/gvfs/ftp:host=ftp.hydro.washington.edu/pub/global/cells' 
wpath = '/home/melchior/Documents/maurer_0.5d/maurer_0.5d_hist_ascii'

for fn in os.listdir(rpath):
	if fn.endswith('tgz'):
		sp = fn.split('.')[0].split('_')
		lat0 = int(sp[1])
		lat1 = int(sp[2].replace('N', ''))
		lon0 = int(sp[3])
		lon1 = int(sp[4].replace('E', ''))

		print lat0, lat1, lon0, lon1

		if (lat0 >= 45) and (lat1 <=60) and (lon0 >= -125) and (lon1 <= -100):
			filepath = rpath + '/' + fn
			shutil.copy(filepath, wpath)
