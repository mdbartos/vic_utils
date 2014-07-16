import os

def convert_rbm(per):
	for fn in os.listdir('.'):
		if 'fluxes' in fn:
			f = open(fn, 'r')
			r = f.readlines()
			f.close()
			with open(fn, 'w') as f:
				if per == 'hist':
					f.write("# NRECS: 181160\n# DT: 24\n# STARTDATE: 1949-01-01 00:00:00\n# ALMA_OUTPUT: 0\n# NVARS: 4\n# OUT_PREC	OUT_EVAP	OUT_RUNOFF	OUT_BASEFLOW\n")
					for i in r:
						s = i.split()[3:7]
						j = '	'.join(s)
						n = j + '\n'
						f.write(n)
				elif per == 'fut':
					f.write("# NRECS: 236680\n# DT: 24\n# STARTDATE: 2010-01-01 00:00:00\n# ALMA_OUTPUT: 0\n# NVARS: 4\n# OUT_PREC	OUT_EVAP	OUT_RUNOFF	OUT_BASEFLOW\n")
					for i in r:
						s = i.split()[3:7]
						j = '	'.join(s)
						n = j + '\n'
						f.write(n)
		elif 'full_data' in fn:
			f = open(fn, 'r')
			h = f.readlines()[:4]
			f = open(fn, 'r')
			r = f.readlines()[6:]
			f.close()
			with open(fn, 'w') as f:
				for x in h:
					f.write(x)
				f.write('# NVARS: 7\n# OUT_AIR_TEMP	 OUT_VP	 OUT_SHORTWAVE	 OUT_LONGWAVE	 OUT_DENSITY	 OUT_PRESSURE	 OUT_WIND\n')
				for i in r:
					s = i.split()[3:10]
					j = '	'.join(s)
					n = j + '\n'
					f.write(n)
