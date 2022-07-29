'''
Analyze the performance difference between TRA and Fast-TRA 
'''

from audioop import reverse
import os
import numpy as np
from copy import deepcopy

file1 = './output_mesh_w4_h4_n4/mt_go1_mode0_r7.txt'
file2 = './output_mesh_w4_h4_n4/mt_go1_mode32_r6.txt'

def resort(lst,key):
    lst.sort(key=lambda dic:dic[key], reverse=False)

def cut_out(f1_data,f2_data):
    cf1_data = [] # f1_data after cut out
    for d in f1_data:
        for s in f2_data:
            if d['idx'] == s['idx']:
                cf1_data.append(d)
                break
    return cf1_data

f1_data = []
f2_data = []

# tra log file
with open(file1,'r') as f1:
    kw = ['idx','ofv','itc','time','bi'] # idx is the id to identify each bound_placement
    for i,line in enumerate(f1):
        try:
            if float(line[20:40])!=0:
                bi = line[80:].split() # boundary info (including boundary routers and boundary turn restrictions)
                vl = [int(line[0:20]),float(line[20:40]),int(line[40:60]),int(line[60:80]),bi]
                f1_data.append(dict(zip(kw,vl)))
        except:
            pass

# fast_tra log file
with open(file2,'r') as f2: 
    kw = ['idx','ofv','itc','time','bi']
    for i,line in enumerate(f2):
        try:
            if float(line[20:40])!=0:
                bi = line[80:].split() # boundary info (including boundary routers and boundary turn restrictions)
                vl = [int(line[0:20]),float(line[20:40]),int(line[40:60]),int(line[60:80]),bi]
                f2_data.append(dict(zip(kw,vl)))
        except:
            pass

resort(f1_data,'ofv')
resort(f2_data,'ofv')

print("tra raw output optimal value:",f1_data[-1]['ofv'])
print("fast_tra rawoutput optimal value:",f2_data[-1]['ofv'])

print("\n")
print("tra raw output number:",len(f1_data))
print("fast_tra raw output number:",len(f2_data))

cf1_data = cut_out(f1_data,f2_data)

print("\n")
print("tra output after cut out:",len(cf1_data))

resort(cf1_data,'idx')
resort(f2_data,'idx')

drop_list = [] # record the drops at all cases and its corresponding index
drop_sum = 0
for i in range(len(cf1_data)):
    temp_drop = (cf1_data[i]['ofv']-f2_data[i]['ofv'])/cf1_data[i]['ofv']
    temp_idx = cf1_data[i]['idx']
    drop_list.append((temp_idx,temp_drop))
    drop_sum += temp_drop

drop_list.sort(key = lambda tup:tup[1], reverse=False)

#! change the case
max_idx = drop_list[-1][0]
max_drop = drop_list[-1][1] 

print("\n")
print("max drop:",max_drop)
print("max drop happens at index:",max_idx)
print("average drop:",drop_sum/len(drop_list))


# for i in drop_list:
#     print(i)

##############################################################################
#       global analysis
##############################################################################
resort(f1_data,'ofv')
resort(f2_data,'ofv')
# for i in f1_data:
#     print(i['ofv'])
# for i in f1_data:
#     print(i['ofv'],i['idx'])
    