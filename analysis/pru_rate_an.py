'''
Analyze the performance difference between TRA and Presort-TRA 
'''

import os
import numpy as np

file1 = './output_mesh_w3_h3_n3/mt_go0_mode31_r7.txt'
file2 = './output_mesh_w3_h3_n3/mt_go0_mode27_r7.txt'

def resort(lst):
    lst.sort(key=lambda dic:dic['ofv'], reverse=False)

f1_data = []
f2_data = []
record = []

with open(file2,'r') as f2:
    kw = ['idx','ofv','itc','time']
    for i,line in enumerate(f2):
        try:
            if float(line[20:40])!=0:
                vl = [int(line[0:20]),float(line[20:40]),int(line[40:60]),int(line[60:80])]
                f2_data.append(dict(zip(kw,vl)))
                record.append(int(line[0:20]))
        except:
            pass

with open(file1,'r') as f1:
    kw = ['idx','ofv','itc','time']
    for i,line in enumerate(f1):
        try:
            # if int(line[0:20]) in record:
            if float(line[20:40])!=0:
                vl = [int(line[0:20]),float(line[20:40]),int(line[40:60]),int(line[60:80])]
                f1_data.append(dict(zip(kw,vl)))
        except:
            pass

print(len(f1_data))
print(len(f2_data))
resort(f1_data)
resort(f2_data)

# print(f1_data[-1]['ofv'])
# print(f2_data[-1]['ofv'])

a = []
for i in range(len(f1_data)):
    a.append((f1_data[i]['itc']-f2_data[i]['itc'])/f1_data[i]['itc'])

print(np.average(a))

# sum1 = 0
# sum2 = 0
# for d1 in f1_data:
#     sum1 += d1['itc']
# for d2 in f2_data:
#     sum2 += d2['itc']

# print((sum1-sum2)/sum1)
# a = []
# for i in range(len(f1_data)):
#     a.append((f1_data[i]-f2_data[i])/f1_data[i])

# print(sum(a)/len(a))