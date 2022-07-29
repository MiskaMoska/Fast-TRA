'''
Analyze the difference of the routing table between TRA and Fast-TRA
Only for 2D-mesh networks with size no more than 9 * 9
'''

import os
import re
import sys
import numpy as np
from copy import deepcopy
import networkx as nx
import rewrite as rw

W = 4
H = 4
BRN = 4 # boundary router number 
file1 = './output_mesh_w4_h4_n4/mt_go0_mode0_r8.txt'
file2 = './output_mesh_w4_h4_n4/mt_go0_mode32_r6.txt'

def construct_cdg(W,H):
    '''
    This function constructs a base Mesh NoC(Network on Chip) CDG(Channel Dependency Graph) 
    The Network is default to adopt XY routing algorithm

    Return
    ---------------------
    type:   MultiDiGraph
    '''
    legal_node = ['left_i','left_o','right_i','right_o','up_i','up_o','down_i','down_o','local_i','local_o']
    legal_path = [['left_i','right_o'],['left_i','up_o'],['left_i','down_o'],['right_i','left_o'],['right_i','up_o'],['right_i','down_o'],['up_i','down_o'],['down_i','up_o'],['local_i','left_o'],['local_i','right_o'],['local_i','up_o'],['local_i','down_o'],['left_i','local_o'],['right_i','local_o'],['up_i','local_o'],['down_i','local_o']]

    G=nx.MultiDiGraph()
    for i in range(W):
        for j in range(H):
            for k in range(len(legal_node)):
                G.add_node((i,j,legal_node[k]))
            for k in range(len(legal_path)):
                G.add_edge((i,j,legal_path[k][0]),(i,j,legal_path[k][1]))

    for i in range(W-1):
        for j in range(H):
            G.add_edge((i,j,'right_o'),(i+1,j,'left_i'))
            G.add_edge((i+1,j,'left_o'),(i,j,'right_i'))

    for i in range(W):
        for j in range(H-1):
            G.add_edge((i,j+1,'up_o'),(i,j,'down_i'))
            G.add_edge((i,j,'down_o'),(i,j+1,'up_i'))

    if not rw.find_cycle(G):
        # print("Mesh construction done")
        return G
    print("Mesh construction failed")
    return None

def set_bound_router(G,brl):
    '''
    This function sets all the boundary routers according to router ID list
    Sensitive to the topology of he network
    '''
    for i in range(len(brl)):
        x = brl[i][0]
        y = brl[i][1]
        G.add_node((x,y,'bound_i'))
        G.add_node((x,y,'bound_o'))
        G.add_edge((x,y,'bound_i'),(x,y,'left_o'))
        G.add_edge((x,y,'bound_i'),(x,y,'right_o'))
        G.add_edge((x,y,'bound_i'),(x,y,'up_o'))
        G.add_edge((x,y,'bound_i'),(x,y,'down_o'))
        G.add_edge((x,y,'bound_i'),(x,y,'local_o'))
        G.add_edge((x,y,'left_i'),(x,y,'bound_o'))
        G.add_edge((x,y,'right_i'),(x,y,'bound_o'))
        G.add_edge((x,y,'up_i'),(x,y,'bound_o'))
        G.add_edge((x,y,'down_i'),(x,y,'bound_o'))
        G.add_edge((x,y,'local_i'),(x,y,'bound_o'))

def set_bound_restriction(G,btrl):
    '''
    This function places the boundary turn restrictions on the cdg
    '''
    for btr in btrl:
        G.remove_edge(btr[0],btr[1])

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

def print_bound_info(f_data,idx):
    for item in f_data[idx]['bi']:
        print(item)

def get_brl(brl_str):
    '''
    extract the boundary router list from raw strings
    '''
    brl = []
    for i in brl_str:
        brl.append((int(i[1]),int(i[3])))
    return brl

def get_btrl(btrl_str):
    '''
    extract the boundary turn restriction list from raw strings
    '''
    btrl = []
    for tr in btrl_str:
        nl = re.findall(r"\d+",tr)
        ll = re.findall(r"[a-z]+\w[a-z]+",tr)
        source = (int(nl[0]),int(nl[1]),ll[0],)
        target = (int(nl[2]),int(nl[3]),ll[1],)
        btrl.append((source,target,))
    return btrl

def get_bound_table(G,brl):
    '''
    get the boundary (inbound and outbound) routing table 
    from boundary router list (brl) and boundary turn restriction list (btrl)
    '''

    # inbound and outbound router containers
    brc_ib = {}
    brc_ob = {}
    for br in brl:
        key_b = str(br[0]) + " " + str(br[1])
        brc_ob[key_b] = []
        brc_ib[key_b] = []

    # inbound scan
    for x in range(W):
        for y in range(H):
            ib_dn = (x,y,'local_o')
            dst = {}
            onehot_key_b = ""

            cnt = 0
            for br in brl:
                key_b = str(br[0]) + " " + str(br[1])
                ib_sn = (br[0],br[1],'bound_i')
                if nx.has_path(G,ib_sn,ib_dn):
                    dst[key_b] = nx.shortest_path_length(G,source=ib_sn,target=ib_dn)
                    onehot_key_b = key_b
                    cnt += 1

            if cnt == 0:
                print("Error:CDG not connected")
                sys.exit()

            if cnt == 1:
                brc_ib[onehot_key_b].append((x,y,))
            
            else:
                shortest_key_b = min(zip(dst.values(),dst.keys()))[1] # find the bound that has the shortest distance
                brc_ib[shortest_key_b].append((x,y,))

    return brc_ib
######################################################################################################################

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

# brl_str = cf1_data[0]['bi'][0:BRN]
# brl = get_brl(brl_str)
# print(brl)
# btrl_str = cf1_data[0]['bi'][BRN:]
# btrl = get_btrl(btrl_str)
# print(btrl)

cnt = 0
for i in range(len(cf1_data)):
    brl_1_str = cf1_data[i]['bi'][0:BRN]
    btrl_1_str = cf1_data[i]['bi'][BRN:]
    brl_2_str = f2_data[i]['bi'][0:BRN]
    btrl_2_str = f2_data[i]['bi'][BRN:]
    brl_1 = get_brl(brl_1_str)
    brl_2 = get_brl(brl_2_str)
    btrl_1 = get_btrl(btrl_1_str)
    btrl_2 = get_btrl(btrl_2_str)

    print("\n\nAnalyzing case",i+1,"with index",cf1_data[i]['idx'])
    cdg_1 = construct_cdg(W,H)
    set_bound_router(cdg_1,brl_1)
    set_bound_restriction(cdg_1,btrl_1)
    brc_1 = get_bound_table(cdg_1,brl_1)

    print("\nboundary router container for TRA:")
    for k,v in brc_1.items():
        print(k,"\t\t",v)

    cdg_2 = construct_cdg(W,H)
    set_bound_router(cdg_2,brl_2)
    set_bound_restriction(cdg_2,btrl_2)
    brc_2 = get_bound_table(cdg_2,brl_2)

    print("\nboundary router container for Fast-TRA:")
    for k,v in brc_2.items():
        print(k,"\t\t",v)

    if brc_1 == brc_2:
        cnt += 1
    
    print("same:",cnt)

    # if i > 10:
    #     break