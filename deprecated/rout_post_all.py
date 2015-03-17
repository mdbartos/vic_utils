import numpy as np
import pandas as pd
import os
import ast
import pickle

latlon_c = pickle.load( open('hydrostn.p', 'rb'))

#for i, v in latlon_c.items():
#	v['slug'] = [str(j) for j in v['PNAME']]
#	v['slug'] = [k.split(' ')[0] for k in v['slug']]
#	v['slug'] = [k[:5] for k in v['slug']]
#	vd = v.ix[v.duplicated(cols='slug')]

#latlon_c['coyotecr'] = latlon_c['coyotecr'].drop_duplicates(cols='slug')

#latlon_c['pitt'] = latlon_c['pitt'].drop_duplicates(cols='slug')

#latlon_c['corona'] = latlon_c['corona'].drop([6])

#latlon_c['kern'] = latlon_c['kern'].drop_duplicates(cols='slug')
	
#latlon_c['cottonwood'] = latlon_c['cottonwood'].drop_duplicates(cols='slug')

#latlon_c['tulare'] = latlon_c['tulare'].drop_duplicates(cols='slug')

#latlon_c['castaic'].drop([17])

	
######################################################

hist_datum_day = pd.read_csv('hist_datum_day.csv')
fut_datum_day = pd.read_csv('fut_datum_day.csv')
hist_datum_month = pd.read_csv('hist_datum_month.csv')
fut_datum_month = pd.read_csv('fut_datum_month.csv')

inflow_o = {}

def rout_tables(basin, scen, typ):
	inflow_d = {}
	slugtable = latlon_c[basin].set_index('slug')
	print slugtable
	for fn in os.listdir('./%s' % (scen)):
		sp = fn.split('.')
		if typ == 'd':
			if (sp[1] == 'day') and (sp[0][:-5] == basin) and (sp[0][-5:].split()[0] in slugtable.index):
				n = pd.read_fwf('./%s/%s' % (scen, fn), header=None, widths=[12, 12, 12, 13])
				n.columns = ['year', 'month', 'day', 'cfs']
				inflow_d.update({slugtable['PCODE'].ix[sp[0][-5:].split()[0]]: n})

#			elif (sp[1] == 'day') and (sp[0] == basin) and (sp[0][-5:].split()[0]) in slugtable.index:
#				n = pd.read_fwf('./%s/%s' % (scen, fn), header=None, widths=[12, 12, 12, 13])
#				n.columns = ['year', 'month', 'day', 'cfs']
#				inflow_d.update({slugtable['PCODE'].ix[sp[0][-5:].split()[0]]: n})
		
		if typ == 'm':
			if (sp[1] == 'month') and (sp[0][:-5] == basin) and (sp[0][-5:].split()[0] in slugtable.index):
				n = pd.read_fwf('./%s/%s' % (scen, fn), header=None, widths=[12, 12, 13])
				n.columns = ['year', 'month', 'cfs']
				inflow_d.update({slugtable['PCODE'].ix[sp[0][-5:].split()[0]]: n})

#			elif (sp[1] == 'month') and (sp[0] == basin) and (sp[0][-5:].split()[0] in slugtable.index):
#				n = pd.read_fwf('./%s/%s' % (scen, fn), header=None, widths=[12, 12, 13])
#				n.columns = ['year', 'month', 'cfs']
#				inflow_d.update({slugtable['PCODE'].ix[sp[0][-5:].split()[0]]: n})


	s_li = []
	
	if typ == 'd' and scen == 'hist':
		s_li.append(hist_datum_day['year'])
		s_li.append(hist_datum_day['month'])
		s_li.append(hist_datum_day['day'])
	if typ == 'm' and scen =='hist':
		s_li.append(hist_datum_month['year'])
		s_li.append(hist_datum_month['month'])
	if typ == 'd' and scen == 'a1b':
		s_li.append(fut_datum_day['year'])
		s_li.append(fut_datum_day['month'])
		s_li.append(fut_datum_day['day'])
	if typ == 'm' and scen =='a1b':
		s_li.append(fut_datum_month['year'])
		s_li.append(fut_datum_month['month'])
	if typ == 'd' and scen == 'a2':
		s_li.append(fut_datum_day['year'])
		s_li.append(fut_datum_day['month'])
		s_li.append(fut_datum_day['day'])
	if typ == 'm' and scen =='a2':
		s_li.append(fut_datum_month['year'])
		s_li.append(fut_datum_month['month'])
	if typ == 'd' and scen == 'b1':
		s_li.append(fut_datum_day['year'])
		s_li.append(fut_datum_day['month'])
		s_li.append(fut_datum_day['day'])
	if typ == 'm' and scen =='b1':
		s_li.append(fut_datum_month['year'])
		s_li.append(fut_datum_month['month'])
		
	for i, v in inflow_d.items():
		v[i] = v['cfs']
		s_li.append(v[i])
#		print s_li
	cct = pd.concat([i for i in s_li], axis=1)
	inflow_o.update({'%s-%s-%s' % (basin, scen, typ): cct})
#	cct.to_csv('%s_%s_%s.csv' % (basin, scen, typ))
		
		
for i in latlon_c.keys():
	rout_tables(i, 'hist', 'm')
	rout_tables(i, 'a1b', 'm')
	rout_tables(i, 'hist', 'd')
	rout_tables(i, 'a1b', 'd')
	rout_tables(i, 'a2', 'm')
	rout_tables(i, 'a2', 'd')
	rout_tables(i, 'b1', 'm')
	rout_tables(i, 'b1', 'd')
	
##########################################	

for i, k in inflow_o.items():
	sp_agg = i.split('-')
	print sp_agg
	if sp_agg[0] == 'hoover':
		inflow_o[i][154] = inflow_o[i][154] + inflow_o['lees_f-%s-%s' % (sp_agg[1], sp_agg[2])][153] + inflow_o['little_col-%s-%s' % (sp_agg[1], sp_agg[2])][-9999] + inflow_o['gc-%s-%s' % (sp_agg[1], sp_agg[2])][-9999] + inflow_o['virgin-%s-%s' % (sp_agg[1], sp_agg[2])][-9999]

for i, k in inflow_o.items():
	sp_agg = i.split('-')
	if sp_agg[0] == 'davis':
		inflow_o[i][152] = inflow_o[i][152] + inflow_o['hoover-%s-%s' % (sp_agg[1], sp_agg[2])][154]

for i, k in inflow_o.items():
	sp_agg = i.split('-')
	if sp_agg[0] == 'parker':
		inflow_o[i][447] = inflow_o[i][447] + inflow_o['davis-%s-%s' % (sp_agg[1], sp_agg[2])][152]

for i, k in inflow_o.items():
	sp_agg = i.split('-')
	if sp_agg[0] == 'imperial':
		inflow_o[i][-9999] = inflow_o[i][-9999] + inflow_o['parker-%s-%s' % (sp_agg[1], sp_agg[2])][447] + inflow_o['gila_imp-%s-%s' % (sp_agg[1], sp_agg[2])][100]


##########################################

for i, k in inflow_o.items():
	k.to_csv('./tables_raw/%s/%s.csv' % (i.split('-')[1], i))
###########################################


inflow_m = {}

for i, k in inflow_o.items():
	if 'hist' in i:
#		print i
#		print k.mean()
#		print k
#		print k/k.mean()
		inflow_m.update({'%s-mean' % (i) : k.mean()})

inflow_n = {}

for i, k in inflow_o.items():
	for j, v in inflow_m.items():
		o = i.split('-')
		m = j.split('-')
		if o[0] == m[0] and o[-1] == m[-2]:
			norm = k/v
			norm['year'] = k['year']
			norm['month'] = k['month']
			if 'day' in norm.columns:
				norm['day'] = k['day']
			inflow_n.update({'%s-normalized' % (i) : norm})
			
#for i, k in inflow_n.items():
#	k.to_csv('%s.csv' % (i))

######

inflow_a = {}

for i, k in inflow_n.items():
	if ('castaic' in i) or ('corona' in i) or ('riohondo' in i) or ('coyotecr' in i) or ('redmtn' in i):
		newmel = inflow_n['pitt-%s-%s-normalized' % (i.split('-')[1], i.split('-')[2])][6158]
		bishp = inflow_n['cottonwood-%s-%s-normalized' % (i.split('-')[1], i.split('-')[2])][326]
		gila = inflow_n['imperial-%s-%s-normalized' % (i.split('-')[1], i.split('-')[2])][-9999]
		transf = pd.concat([newmel, bishp, gila], axis=1)
		n = k
		print n
		ncol = [p for p in n.columns if type(p) == float]
		for x in ncol:
			n[x] = n[x]*0.396 + newmel*0.255 + bishp*0.089 + gila*0.264
		inflow_a.update({i : n})
	elif ('tulare' in i):
		newmel = inflow_n['pitt-%s-%s-normalized' % (i.split('-')[1], i.split('-')[2])][6158]
		friant = inflow_n['pitt-%s-%s-normalized' % (i.split('-')[1], i.split('-')[2])][50393]
		transf = pd.concat([newmel, friant], axis=1)
		n = k
		ncol = [p for p in n.columns if type(p) == float]
		for x in ncol:
			n[x] = n[x]*0.678 + newmel*0.22 + friant*0.102
		inflow_a.update({i : n})
	else:
		inflow_a.update({i : k})			
		
for i, k in inflow_a.items():
	k.to_csv('./tables_normalized/%s/%s.csv' % (i.split('-')[1], i))

##########################

cali_basins = ['castaic', 'corona', 'cottonwood', 'coyotecr', 'kern', 'pitt', 'redmtn', 'riohondo', 'rushcr', 'tulare']
colo_basins = ['billw', 'davis', 'gc', 'hoover', 'imperial', 'lees_f', 'little_col', 'paria', 'parker', 'virgin', 'gila_imp']

calicct = {'hist': [], 'a1b': [], 'a2': [], 'b1': []}
colocct = {'hist': [], 'a1b': [], 'a2': [], 'b1': []}

for q in inflow_o.keys():
	psp = q.split('.')[0]
	ssp = q.split('-')
	if (ssp[0] in cali_basins) and (ssp[2] == 'd'):
		calicct[ssp[1]].append(inflow_o[q])
	if (ssp[0] in cali_basins) and (ssp[2] == 'd'):
		colocct[ssp[1]].append(inflow_o[q])

for a in calicct.keys():
	t = pd.concat(calicct[a], axis=1)
	tc = t.columns
	stc = (set(tc))
	dupr = sorted([list(tc).index(i) for i in stc])
	print dupr
	t = t.iloc[:, dupr]
	t.to_csv('./combined_tables_raw/%s/%s_cali.csv' % (a, a))

for a in colocct.keys():
	t = pd.concat(colocct[a], axis=1)
	tc = t.columns
	stc = (set(tc))
	dupr = sorted([list(tc).index(i) for i in stc])
	print dupr
	t = t.iloc[:, dupr]
	t.to_csv('./combined_tables_raw/%s/%s_colo.csv' % (a, a))

###########################

for q in inflow_a.keys():
	psp = q.split('.')[0]
	ssp = q.split('-')
	if (ssp[0] in cali_basins) and (ssp[2] == 'd'):
		calicct[ssp[1]].append(inflow_a[q])
	if (ssp[0] in cali_basins) and (ssp[2] == 'd'):
		colocct[ssp[1]].append(inflow_a[q])

for a in calicct.keys():
	t = pd.concat(calicct[a], axis=1)
	tc = t.columns
	stc = (set(tc))
	dupr = sorted([list(tc).index(i) for i in stc])
	print dupr
	t = t.iloc[:, dupr]
	t.to_csv('./combined_tables_norm/%s/%s_cali.csv' % (a, a))

for a in colocct.keys():
	t = pd.concat(colocct[a], axis=1)
	tc = t.columns
	stc = (set(tc))
	dupr = sorted([list(tc).index(i) for i in stc])
	print dupr
	t = t.iloc[:, dupr]
	t.to_csv('./combined_tables_norm/%s/%s_colo.csv' % (a, a))
	
