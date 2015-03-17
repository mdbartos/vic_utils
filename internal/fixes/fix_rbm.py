import os
import shutil


def convert_rbm(per, path):
	for fn in os.listdir(path):
		pfn = path + '/' + fn
		if 'fluxes' in fn:
			f = open(pfn, 'r')
			r = f.readlines()
			f.close()
			nrecs = len(r)
			with open(pfn, 'w') as f:
				if per == 'hist':
					f.write("# NRECS: %s\n# DT: 24\n# STARTDATE: 1949-01-01 00:00:00\n# ALMA_OUTPUT: 0\n# NVARS: 7\n# YEAR	MONTH	DAY	OUT_PREC	OUT_EVAP	OUT_RUNOFF	OUT_BASEFLOW\n" % (nrecs))
					for i in r:
						s = i.split()[:7]
						j = '	'.join(s)
						n = j + '\n'
						f.write(n)
				elif per == 'fut':
					f.write("# NRECS: %s\n# DT: 24\n# STARTDATE: 2010-01-01 00:00:00\n# ALMA_OUTPUT: 0\n# NVARS: 7\n# YEAR	MONTH	DAY	OUT_PREC	OUT_EVAP	OUT_RUNOFF	OUT_BASEFLOW\n" % (nrecs))
					for i in r:
						s = i.split()[:7]
						j = '	'.join(s)
						n = j + '\n'
						f.write(n)
		elif 'full_data' in fn:
			f = open(pfn, 'r')
			r = f.readlines()
			f.close()
			nrecs = len(r) - 6
			with open(pfn, 'w') as f:
				if per == 'hist':
					f.write("# NRECS: %s\n# DT: 24\n# STARTDATE: 1949-01-01 00:00:00\n# ALMA_OUTPUT: 0\n# NVARS: 7\n# OUT_AIR_TEMP	 OUT_VP	 OUT_SHORTWAVE	 OUT_LONGWAVE	 OUT_DENSITY	 OUT_PRESSURE	 OUT_WIND\n" % (nrecs))
					for i in r[6:]:
						s = i.split()[3:10]
						j = '	'.join(s)
						n = j + '\n'
						f.write(n)
				else:
					f.write("# NRECS: %s\n# DT: 24\n# STARTDATE: 2010-01-01 00:00:00\n# ALMA_OUTPUT: 0\n# NVARS: 7\n# OUT_AIR_TEMP	 OUT_VP	 OUT_SHORTWAVE	 OUT_LONGWAVE	 OUT_DENSITY	 OUT_PRESSURE	 OUT_WIND\n" % (nrecs))
					for i in r[6:]:
						s = i.split()[3:10]
						j = '	'.join(s)
						n = j + '\n'
						f.write(n)


# COPY FORCINGS

destpath = '/home/chesterlab/Bartos/VIC/input/rbm/run/d8'  
fesrcpath = '/media/melchior/BALTHASAR/nsf_hydro/VIC/output/full-energy'
flxsrcpath = '/media/melchior/BALTHASAR/nsf_hydro/VIC/output/sub-basin' 

listdir = [i for i in os.listdir('/home/chesterlab/Bartos/VIC/input/rbm/run/d8')] 

for a in listdir:
	for sc in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:
		if not os.path.exists('%s/%s/flx/%s' % (destpath, a, sc)):
			os.mkdir('%s/%s/flx/%s' % (destpath, a, sc))
		if not os.path.exists('%s/%s/fe/%s' % (destpath, a, sc)):
			os.mkdir('%s/%s/fe/%s' % (destpath, a, sc))

		nflxdest = '%s/%s/flx/%s' % (destpath, a, sc)
		nfedest = '%s/%s/fe/%s' % (destpath, a, sc)  
		nfesrc = '%s/%s/%s' % (fesrcpath, sc, a)
		nflxsrc = '%s/%s/%s' % (flxsrcpath, sc, a)
		print nflxdest
		print nfedest
		print nfesrc
		print nflxsrc
		for fn in os.listdir(nflxsrc):
			if 'fluxes' in fn:
				shutil.copy('%s/%s' % (nflxsrc, fn), '%s/%s' % (nflxdest, fn))
		for fn in os.listdir(nfesrc):
			shutil.copy('%s/%s' % (nfesrc, fn), '%s/%s' % (nfedest, fn))
		if sc == 'hist':
			convert_rbm('hist', nflxdest)
			convert_rbm('hist', nfedest)
		else:
			convert_rbm('fut', nflxdest)
			convert_rbm('fut', nfedest)




# CONVERT

#convert_rbm('hist', '/home/chesterlab/Bartos/VIC/input/rbm/run/d8/brigham/flx/hist')
#convert_rbm('hist', '/home/chesterlab/Bartos/VIC/input/rbm/run/d8/brigham/fe/hist')

#for b in ['ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:
#	convert_rbm('fut', '/home/chesterlab/Bartos/VIC/input/rbm/run/d8/brigham/flx/%s' % (b))
#	convert_rbm('fut', '/home/chesterlab/Bartos/VIC/input/rbm/run/d8/brigham/fe/%s' % (b))
