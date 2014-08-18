import numpy as np
import pandas as pd
import os
import pickle

class rbm_post():

	def __init__(self, op_path, rc_path, rbm_path):
		self.st_rc = pickle.load(open(rc_path, 'rb'))
		self.st_op = pickle.load(open(op_path, 'rb'))
		self.st_d = {}
		self.st_d.update({'st_rc' : self.st_rc, 'st_op' : self.st_op})
		self.rbm_path = rbm_path
		self.spat_d = {}
		self.cell_d = {}
		self.ll_d = {}

	def make_spat_d(self):
		for fn in os.listdir(self.rbm_path):
			spat = pd.read_fwf('%s/%s/hist.Spat' % (self.rbm_path, fn), names=['reach', 'cell', 'row', 'column', 'lat', 'lon', 'ndelta']).drop_duplicates(subset=['cell'])
			self.spat_d.update({fn : spat})

	def make_diff(self):
		temp_cell_d = {}
		temp_ll_d = {}
		for p in self.st_d.keys():
			temp_cell_d.update({p : {}})
			temp_ll_d.update({p : {}})
		for tech in self.st_d.keys():
			for i in self.st_d[tech].keys():
				if i in self.spat_d.keys():
					jcell_d = {}
					jll_d = {}
			#		print os.getcwd()
					for k in self.st_d[tech][i].values:
						cell_d = {}
						ll_d = {}
						jcell_d.update({k[1] : None})
						jll_d.update({k[1] : None})
			#			print j_d
						stn_ll = k[2]
						for spat_ll in self.spat_d[i].values:
			#				fn_d = {}
							diff = ((spat_ll[4] - stn_ll[0])**2 + (spat_ll[5] - stn_ll[1])**2)**0.5
							cell_d.update({spat_ll[1] : diff})	
							ll_d.update({str(tuple([spat_ll[4], spat_ll[5]])) : diff})
						cell = min(cell_d, key=cell_d.get)
						ll = min(ll_d, key=ll_d.get)
						print tech, i, k[1], cell
						mi = cell_d[cell]
						jcell_d[k[1]] = cell
						jll_d[k[1]] = ll
			#		print j_d.items()
					temp_cell_d[tech].update({i : jcell_d})
					temp_ll_d[tech].update({i : jll_d})
				self.cell_d[tech] = temp_cell_d[tech]
				self.ll_d[tech] = temp_ll_d[tech]

	def read_temp(self, scen):
		for tech in self.st_d.keys():
			for i, k in self.cell_d[tech].items():
				rpath = self.rbm_path + '/' + i
				with open('%s/%s.Temp' % (rpath, scen), 'rb') as tempfile:
					for cell in self.cell_d[tech][i].values():
						for line in tempfile:
							sp = line.split()
							if sp[3] == str(cell).split('.')[0]: 
								print line
	
	def get_atmos(self):
		for i, k in self.cell_d[tech]:
			pass


b = rbm_post('/media/chesterlab/My Passport/Files/VIC/input/dict/opstn.p', '/media/chesterlab/My Passport/Files/VIC/input/dict/rcstn.p', '/media/chesterlab/storage/post/rbm')

b.make_spat_d()

b.make_diff()
