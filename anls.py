import os
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns 

file_ori = './output_mesh_w4_h4_n2_r3/log_mp.txt'
file_bab = './output_mesh_w4_h4_n2_r3/log_mp_bab.txt'

ori_list = []
with open(file_ori,'r') as fo:
    for i,line in enumerate(fo):
        if i>0 and line[80] != '-':
            ori_list.append(int(line[32:38]))
        
bab_list = []
with open(file_bab,'r') as fb:
    for i,line in enumerate(fb):
        if i>0 and line[80] != '-':
            bab_list.append(int(line[32:38]))

so = sum(ori_list)
sb = sum(bab_list)
t = []
for i in range(len(ori_list)):
    t.append((ori_list[i]-bab_list[i])/ori_list[i])
# print(ori_list)
print(np.average(t))
print((so-sb)/so)
# print(so/len(ori_list))

# fig = plt.figure(figsize=(8,6),dpi=120)
# sns.distplot(ori_list,color="#05668d",label="MDFA")
# sns.distplot(bab_list,color="#540d6e",label="Presort-MDFA")
# plt.xlabel(r"number of iterations",size=12)
# plt.legend()
# plt.show()
# ax=plt.gca()
# x=range(0,3)
# y = [18.44,39.08,49.01]
# plt.bar(x,y, alpha=1, width=0.5, color='grey', edgecolor='black',lw=3)
# plt.xticks([0,1,2],
#             ['4','5','6'])
# ax.tick_params(axis = 'both', which = 'major', labelsize = 16, width=1.5)
# for a, b in zip(x, y):
#     plt.text(a, b + 0.05, '%.2f%%' % b, ha='center', va='bottom', fontsize=16)
# plt.show()