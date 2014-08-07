import os
import ast
import shutil

metafile = []

def make_rbm_stn(dpath, wpath, basin):

	dirfile = open(dpath, 'r')
	r = dirfile.readlines()
	h = r[:6]
	ncol = ast.literal_eval(h[0].split()[1])
	nrow = ast.literal_eval(h[1].split()[1])
	xll = ast.literal_eval(h[2].split()[1])
	yll = ast.literal_eval(h[3].split()[1])
	cellsize = ast.literal_eval(h[4].split()[1])
	nodata = ast.literal_eval(h[5].split()[1])
	
	xd = {}
	yd = {}
	
	ncol_array = range(ncol)
	nrow_array = range(nrow)
	
	for i in ncol_array:
		xd.update({(i+1) : (xll + cellsize/2 + i*cellsize)})
	
	for i in nrow_array:
		yd.update({(i+1) : (yll + cellsize/2 + i*cellsize)})
	
	lines = r[6:]
	
	li = []
	
	for i in range(len(lines)):
		sp = lines[i].split()
		for s in range(len(sp)):
			print len(sp)
			if sp[s] != '0':
				print str(nrow - i) + '_' + str(sp[s])
				li.append(tuple([s+1, nrow - i]))
	
	li = list(set(li))
	
	with open('%s/%s_rbm.stnloc' % (wpath, basin), 'w') as outfile:
		for k in li:
			outfile.write('1 %s_%s             %s %s -9999\nNONE\n' % (hex(k[1]).split('x')[1], hex(k[0]).split('x')[1], k[0], k[1]))



def gen_uh_cfg(dpath, ipath, outpath, cfgpath, basin):
	f = open(dpath, 'r')
	r = f.readlines()
	r[2] = ipath + '/%s/%s.dir' % (basin, basin) + '\n'
	r[11] = ipath + '/%s/%s.xmask' % (basin, basin) + '\n'
	r[14] = ipath + '/%s/%s.frac' % (basin, basin) + '\n' 
	r[16] = ipath + '/%s/%s_rbm.stnloc' % (basin, basin) + '\n'
	r[18] = ipath + '/%s/sym/%s/fluxes_' % (basin, 'hist') + '\n'
	r[21] = outpath + '/%s/%s_' % (basin, basin) + '\n'
	if not os.path.exists(outpath + '/' + basin):
		os.mkdir(outpath + '/' + basin)
	if not os.path.exists(outpath + '/' + basin + '/uh_s'):	
		os.mkdir(outpath + '/' + basin + '/uh_s')
	r[23] = '1949 01 2009 12\n'
	r[24] = '1949 01 2009 12\n'
	w = ''.join(r)
#	print w
	cfgwpath = cfgpath + ('/rbm_uh.%s' % (basin))
	metafile.append('./rout %s\n' % (cfgwpath))
	metafile.append('mv -f *.uh_s %s/%s/uh_s\n' % (outpath, basin))
	with open(cfgwpath, 'w') as outfile:
		outfile.write(w)
	

for fn in os.listdir('/media/melchior/BALTHASAR/nsf_hydro/VIC/output/full-energy/hist'):
	make_rbm_stn('/home/chesterlab/Bartos/VIC/input/rout/d8/%s/%s.dir' % (fn, fn), '/home/chesterlab/Bartos/VIC/input/rout/d8/%s' % (fn), fn) 
	gen_uh_cfg('/home/chesterlab/Bartos/VIC/config/rout/d8/rout_input.default_d8','/home/chesterlab/Bartos/VIC/input/rout/d8', '/home/chesterlab/Bartos/VIC/output/rbm/uh_gen/d8','/home/chesterlab/Bartos/VIC/config/rbm/uh_gen/d8' , fn)


with open('/home/chesterlab/Bartos/VIC/config/rbm/uh_gen/rbm_uh_sh_run', 'w') as wfile:
	m = ''.join(metafile)
	wfile.write(m)


##RENAME##

def rename_rbm_stn(uhpath, wpath, dpath):

	dirfile = open(dpath, 'r')
	r = dirfile.readlines()
	h = r[:6]
	ncol = ast.literal_eval(h[0].split()[1])
	nrow = ast.literal_eval(h[1].split()[1])
	xll = ast.literal_eval(h[2].split()[1])
	yll = ast.literal_eval(h[3].split()[1])
	cellsize = ast.literal_eval(h[4].split()[1])
	nodata = ast.literal_eval(h[5].split()[1])
	
	xd = {}
	yd = {}
	
	ncol_array = range(ncol)
	nrow_array = range(nrow)
	
	for i in ncol_array:
		xd.update({(i+1) : (xll + cellsize/2 + i*cellsize)})
	
	for i in nrow_array:
		yd.update({(i+1) : (yll + cellsize/2 + i*cellsize)})

	for fn in os.listdir(uhpath):


		if ' ' in fn:
			ff = fn.split(' ')[0]
		else:
			ff = fn.split('.')[0]
		fs = ff.split('_')
		print fs[0], fs[1]
		shutil.copy('%s/%s' % (uhpath, fn), '%s/%s_%s.uh_s' % (wpath, yd[int(fs[0], 16)], xd[int(fs[1], 16)]))
		#os.remove('%s/%s' % (uhpath, fn))


for u in os.listdir('/media/melchior/BALTHASAR/nsf_hydro/VIC/output/full-energy/hist'):
	rename_rbm_stn('/home/chesterlab/Bartos/VIC/output/rbm/uh_gen/d8/%s/uh_s' % (u), '/home/chesterlab/Bartos/VIC/input/rbm/run/d8/%s/uh' % (u),'/home/chesterlab/Bartos/VIC/input/rout/d8/%s/%s.dir' % (u, u))


