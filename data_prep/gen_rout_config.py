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
	r[21] = outpath + '/%s/%s/%s_' % (scen, basin, basin) + '\n'
	if not os.path.exists(outpath + '/' + scen):
		os.mkdir(outpath + '/' + scen)
	if not os.path.exists(outpath + '/' + scen + '/' + basin):	
		os.mkdir(outpath + '/' + scen + '/' + basin)
	if scen == 'hist':
		r[23] = '1949 01 2009 12\n'
		r[24] = '1949 01 2009 12\n'
 	else:
		r[23] = '2010 01 2099 12\n'
		r[24] = '2010 01 2099 12\n'
	w = ''.join(r)
#	print w
	if not os.path.exists(cfgpath + '/' + scen):
		os.mkdir(cfgpath + '/' + scen)
	cfgwpath = cfgpath + ('/%s/rt_in.%s' % (scen, basin))
	metafile.append('./rout %s\n' % (cfgwpath))
	metafile.append('mv -f *.uh_s %s/%s/uh_s\n' % (ipath, basin))
	with open(cfgwpath, 'w') as outfile:
		outfile.write(w)


#1/16 degree
for fn in os.listdir('/home/chesterlab/Bartos/VIC/input/rout/d16'):
	for s in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 	'echam_b1']:
		gen_cfg_rout('/home/chesterlab/Bartos/VIC/config/rout/d16/rout_input.default_d16', '/home/chesterlab/Bartos/VIC/input/rout/d16', '/home/chesterlab/Bartos/VIC/output/rout/d16', '/home/chesterlab/Bartos/VIC/config/rout/d16', s, fn)

with open('/home/chesterlab/Bartos/VIC/config/rout/d16/rout_sh_run_d16', 'w') as wfile:
	m = ''.join(metafile)
	wfile.write(m)

metafile = []

#1/8 degree
for fn in os.listdir('/home/chesterlab/Bartos/VIC/input/rout/d8'):
	for s in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 	'echam_b1']:
		gen_cfg_rout('/home/chesterlab/Bartos/VIC/config/rout/d8/rout_input.default_d8', '/home/chesterlab/Bartos/VIC/input/rout/d8', '/home/chesterlab/Bartos/VIC/output/rout/d8', '/home/chesterlab/Bartos/VIC/config/rout/d8', s, fn)

with open('/home/chesterlab/Bartos/VIC/config/rout/d8/rout_sh_run_d8', 'w') as wfile:
	m = ''.join(metafile)
	wfile.write(m)


########################
## RBM CONFIG
########################

DA_metafile = []

def gen_inpDA_rbm(dpath, ipath, cfgpath, scen, basin, perlpath, routpath):
	f = open(dpath, 'r')
	r = f.readlines()
	r[2] = ipath + '/%s/%s.dir' % (basin, basin) + '\n'
	r[11] = ipath + '/%s/%s.xmask' % (basin, basin) + '\n'
	r[14] = ipath + '/%s/%s.frac' % (basin, basin) + '\n' 
	r[19] = ipath + '/%s/Rout.Cells' % (basin) + '\n'
	r[22] = ipath + '/%s/flx/%s/fluxes_' % (basin, scen) + '\n'
	r[23] = ipath + '/%s/fe/%s/full_data_' % (basin, scen) + '\n'
	if not os.path.exists(ipath + '/' + basin +'/da'):
		os.mkdir(ipath + '/' + basin + '/da')
	if not os.path.exists(ipath + '/' + basin + '/da/' + scen):
		os.mkdir(ipath + '/' + basin + '/da/' + scen) 
	r[26] = ipath + '/%s/da/%s/%s.DA_flow' % (basin, scen, basin) + '\n'
	r[27] = ipath + '/%s/da/%s/%s.DA_heat' % (basin, scen, basin) + '\n'
	if scen == 'hist':
		r[29] = '1949 01 01 2009 12 31    VIC flux\n'
		r[30] = '1949 01 01 2009 12 31   VIC full_data\n'
		r[31] = '1949 01 01 2009 12 31   write output\n'
 	else:
		r[29] = '2010 01 01 2090 12 31    VIC flux\n'
		r[30] = '2010 01 01 2090 12 31    VIC full_data\n'
		r[31] = '2010 01 01 2090 12 31    write output\n'
	r[33] = '/home/chesterlab/Bartos/VIC/config/rout/UH.all\n'
	r[35] = ipath + '/%s/uh/' % (basin) + '\n' 

	w = ''.join(r)
#	print w
	if not os.path.exists(cfgpath + '/' + scen):
		os.mkdir(cfgpath + '/' + scen)
	cfgwpath = cfgpath + ('/%s/%s.inp_DA' % (scen, basin))
	DA_metafile.append('cd %s/%s\n' % (ipath, basin))
	DA_metafile.append('perl %s/build_network_beta.pl %s/%s/%s.dir %s/%s/%s.Topology\n' % (perlpath, ipath, basin, basin, ipath, basin, basin))
	DA_metafile.append('perl %s/build_input.pl %s/%s/%s\n' % (perlpath, cfgpath, scen, basin))
#	DA_metafile.append('mv -f %s/Rout.Cells %s/%s\n' % (perlpath, ipath, basin))
#	DA_metafile.append('mv -f %s/Rout.Cells.init %s/%s\n' % (perlpath, ipath, basin))
	DA_metafile.append('%s/rout %s\n' % (routpath, cfgwpath))
	with open(cfgwpath, 'w') as outfile:
		outfile.write(w)

Ctrl_metafile = []

def gen_control_rbm(dpath, ipath, outpath, cfgpath, scen, basin, rbmpath):
	f = open(dpath, 'r')
	r = f.readlines()
	idir = ipath + '/' + basin + '/'
	odir = outpath + '/' + basin + '/'

	if scen == 'hist':
		r[3] = 'Starting Date:            19490101\n'
		r[4] = 'Ending Date:              20091231\n'
 	else:
		r[3] = 'Starting Date:            20100101\n'
		r[4] = 'Ending Date:              20901231\n'
	r[6] = 'Input directory:          ' + idir + '\n'
	r[7] = 'Output directory:         ' + odir + '\n' 
	r[8] = 'Topology File:            ' + idir + basin + '.Topology\n'
	r[11] = 'Network File:             ' + idir + scen + '_Network\n'
	r[14] = 'Flow File:                ' + idir + 'da/%s/' % (scen) + basin + '.DA_flow\n'
	r[17] = 'Heat File:                ' + idir + 'da/%s/' % (scen) + basin + '.DA_heat\n'
	r[20] = 'Mohseni Parameters:       ' + idir + basin + ': grid\n'
	w = ''.join(r)
#	print w
	if not os.path.exists(cfgpath + '/' + scen):
		os.mkdir(cfgpath + '/' + scen)
	cfgwpath = cfgpath + ('/%s/%s.Control' % (scen, basin))
	Ctrl_metafile.append('%s/rbm10_VIC %s%s %s%s\n' % (rbmpath, idir, scen, odir, scen))
	#metafile.append('mv -f *.uh_s %s/%s/uh_s\n' % (ipath, basin))
	with open(cfgwpath, 'w') as outfile:
		outfile.write(w)

#TEST

for a in os.listdir('/home/chesterlab/Bartos/VIC/input/rbm/run/d8'):
	for sc in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 	'echam_b1']: 
		gen_inpDA_rbm('/home/chesterlab/Bartos/VIC/config/rbm/run/default.inp_DA', '/home/chesterlab/Bartos/VIC/input/rbm/run/d8', '/home/chesterlab/Bartos/VIC/config/rbm/run/d8', sc, a, '/home/chesterlab/Bartos/VIC/VIC_RBM/Perl_Scripts', '/home/chesterlab/Bartos/VIC/VIC_RBM/rout_DA')
		gen_control_rbm('/home/chesterlab/Bartos/VIC/config/rbm/run/default.Control', '/home/chesterlab/Bartos/VIC/input/rbm/run/d8', '/home/chesterlab/Bartos/VIC/input/rbm/run/d8', '/home/chesterlab/Bartos/VIC/config/rbm/run/d8', sc, a,'/home/chesterlab/Bartos/VIC/VIC_RBM/RBM')


with open('/home/chesterlab/Bartos/VIC/config/rbm/run/d8/rtDA_sh_run_d8', 'w') as wfile:
	m = ''.join(DA_metafile)
	wfile.write(m)
with open('/home/chesterlab/Bartos/VIC/config/rbm/run/d8/rbm_sh_run_d8', 'w') as wfile:
	m = ''.join(Ctrl_metafile)
	wfile.write(m)
