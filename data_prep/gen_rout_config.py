import os

metafile = []

def gen_cfg_rout(dpath, ipath, outpath, cfgpath, scen, basin):
	f = open(dpath, 'r')
	r = f.readlines()
	r[2] = ipath + '/%s/%s.dir' % (basin, basin) + '\n'
	r[11] = ipath + '/%s/%s.xmask' % (basin, basin) + '\n'
	r[14] = ipath + '/%s/%s.frac' % (basin, basin) + '\n' 
	r[16] = ipath + '/%s/%s.stnloc' % (basin, basin) + '\n'
	r[18] = ipath + '/%s/sym/%s/fluxes_' % (basin, scen) + '\n'
	r[21] = outpath + '/%s/%s' % (scen, basin) + '\n'
	if scen == 'hist':
		r[23] = '1949 01 2009 12\n'
		r[24] = '1949 01 2009 12\n'
 	else:
		r[23] = '2010 01 2099 12\n'
		r[24] = '2010 01 2099 12\n'
	w = ''.join(r)
	print w
	cfgwpath = cfgpath + ('/%s/rout_input.%s.%s' % (scen, scen, basin))
	metafile.append('./rout %s\n' % (cfgwpath))
	metafile.append('mv *.uh_s %s/%s/uh_s\n' % (ipath, basin))
	with open(cfgwpath, 'w') as outfile:
		outfile.write(w)


for fn in os.listdir('/home/chesterlab/Bartos/VIC/input/rout/d16'):
	for s in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 	'echam_b1']:
		gen_cfg_rout('/home/chesterlab/Bartos/VIC/config/rout/d16/rout_input.default', '/home/chesterlab/Bartos/VIC/input/rout/d16', '/home/chesterlab/Bartos/VIC/output/rout/d16', '/home/chesterlab/Bartos/VIC/config/rout/d16', s, fn)

with open('/home/chesterlab/Bartos/VIC/config/rout/d16/rout_sh_run', 'w') as wfile:
	m = ''.join(metafile)
	wfile.write(m)
