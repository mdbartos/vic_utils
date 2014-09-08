import pandas as pd
import numpy as np
import os

df = pd.read_csv('hist.8066', sep='\t')

a = df['POWER_CAP_MW']
max_val = a.max()
len_a = len(a)

b = (max_val - df['POWER_CAP_MW'])/max_val
c = b.order(ascending=False) #.reset_index()
ep = c.rank(method='min', ascending=False)/(1+len(a))
t = (1/ep)/365

plot(t, c)
