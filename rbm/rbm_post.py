import numpy as np
import pandas as pd
import os

class rbm_post():

	def __init__(self, op_path, rc_path, rbm_path):
		self.st_rc = pickle.load(open(rc_path, 'rb'))
		self.st_op = pickle.load(open(op_path, 'rb'))
		self.st_d = {}
		self.st_d.update({'st_rc' : self.st_rc, 'st_op' : self.st_op})
		self.rbm_path = rbm_path
		self.spat_d = {}
		self.diff_d = {}

	def make_spat_d(self):
		for fn in os.listdir(self.rbm_path):
			spat = pd.read_fwf('%s/%s/hist.Spat' % (self.rbm_path, fn), names=['reach', 'cell', 'row', 'column', 'lat', 'lon', 'ndelta']).drop_duplicates(subset=['cell'])
			self.spat_d.update({fn : spat})

	def make_diff(self):
		temp_diff_d = {}
		for p in self.st_d.keys():
			temp_diff_d.update({p : {}})
		for tech in self.st_d.keys():
			for i in self.st_d[tech].keys():
				if i in self.spat_d.keys():
					j_d = {}
			#		print os.getcwd()
					for k in self.st_d[tech][i].values:
						fn_d = {}
						j_d.update({k[1] : None})
			#			print j_d
						stn_ll = k[2]
						for spat_ll in self.spat_d[i].values:
			#				fn_d = {}
							diff = ((spat_ll[4] - stn_ll[0])**2 + (spat_ll[5] - stn_ll[1])**2)**0.5
							fn_d.update({str(tuple([spat_ll[4], spat_ll[5]])) : diff})
						cell = min(fn_d, key=fn_d.get)
						print tech, i, k[1], cell
						mi = fn_d[cell]
						j_d[k[1]] = cell		
			#		print j_d.items()
					temp_diff_d[tech].update({i : j_d})
				self.diff_d[tech] = temp_diff_d[tech]

	def read_temp():
		for i in st_rc.items():
			rpath = rbmpath + '/' + i


b = rbm_post('/media/chesterlab/My Passport/Files/VIC/input/dict/opstn.p', '/media/chesterlab/My Passport/Files/VIC/input/dict/rcstn.p', '/media/chesterlab/storage/post/rbm')

b.make_spat_d()

b.make_diff()
