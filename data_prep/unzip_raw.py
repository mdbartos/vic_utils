import os
import subprocess as sub
import ast
import shutil

os.chdir("C:/Users/Matt Bartos/Desktop/cmip3_hydro_inputs")

dir_li = ['tmax', 'tmin', 'prcp', 'wind']
reg_li = ['ark', 'cali', 'color', 'crb', 'grb', 'mo', 'rio']

def master_forcing(model):
	if not os.path.exists(model):
		os.mkdir(model)
	for r in reg_li:
		for t in dir_li:
			os.chdir('./%s/%s/%s' % (r, model, t))
			for fn in os.listdir('.'):
				if fn[-3:] == 'zip':
					if ast.literal_eval(fn[-11:-7]) >= 2010:
#						print fn
						sub.call([r"C:\Program Files\7-Zip\7z", "e", "%s" % (fn), "-oC:/Users/Matt Bartos/Desktop/cmip3_hydro_inputs/%s" % (model)])
			os.chdir("C:/Users/Matt Bartos/Desktop/cmip3_hydro_inputs")
