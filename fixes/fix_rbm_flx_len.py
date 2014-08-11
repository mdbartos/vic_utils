import os

for basin in os.listdir('/home/chesterlab/Bartos/VIC/input/rbm/run/d8'):
	for sc in ['ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:
		for fn in os.listdir('/home/chesterlab/Bartos/VIC/input/rbm/run/d8/%s/flx/%s' % (basin, sc)):
			print fn
			f = open('/home/chesterlab/Bartos/VIC/input/rbm/run/d8/%s/flx/%s/%s' % (basin, sc, fn), 'r')
			r = f.readlines()
			f.close()
			rclip = r[:29591]
			rjoin = ''.join(rclip)
			with open('/home/chesterlab/Bartos/VIC/input/rbm/run/d8/%s/flx/%s/%s' % (basin, sc, fn), 'w') as fnew:
				fnew.write(rjoin)
