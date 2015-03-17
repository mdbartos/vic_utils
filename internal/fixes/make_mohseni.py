import os

#mo = open('little_col_mohseni', 'r')
#mo_r = mo.readlines()
#tl = mo_r[1].split()[0]
#a = mo_r[3].split()[0]
#b = mo_r[3].split()[1]
#g = mo_r[3].split()[2]
#m = mo_r[3].split()[3]

#basin = open('little_col_dir.asc', 'r')
#r = basin.readlines()
#h = r[:6]
#lines = r[6:]

#with open('little_col.alpha', 'w') as outfile:
#	for i in h:
#		outfile.write(i)	
#	for i in lines:
#		sp = i.split()
#		print sp
#		sp_a = [a for x in sp]
#		j_a = ' '.join(sp_a)
#		newlin = j_a + '\n'
#		outfile.write(newlin)
#
#with open('little_col.beta', 'w') as outfile:
#	for i in h:
#		outfile.write(i)	
#	for i in lines:
#		sp = i.split()
#		print sp
#		sp_b = [b for x in sp]
#		j_b = ' '.join(sp_a)
#		newlin = j_b + '\n'
#		outfile.write(newlin)
#
#with open('little_col.gamma', 'w') as outfile:
#	for i in h:
#		outfile.write(i)	
#	for i in lines:
#		sp = i.split()
#		print sp
#		sp_g = [g for x in sp]
#		j_g = ' '.join(sp_g)
#		newlin = j_g + '\n'
#		outfile.write(newlin)
#
#with open('little_col.mu', 'w') as outfile:
#	for i in h:
#		outfile.write(i)	
#	for i in lines:
#		sp = i.split()
#		print sp
#		sp_m = [m for x in sp]
#		j_m = ' '.join(sp_m)
#		newlin = j_m + '\n'
#		outfile.write(newlin)

def make_timelag(basin, tl):
	bdir = open('%s.dir' % (basin), 'r')
	r = bdir.readlines()
	h = r[:6]
	lines = r[6:]

	with open('%s.timelag' % (basin), 'w') as outfile:
		for i in h:
			outfile.write(i)	
		for i in lines:
			sp = i.split()
			print sp
			sp_t = [tl for x in sp]
			j_t = ' '.join(sp_t)
			newlin = j_t + '\n'
			outfile.write(newlin)
