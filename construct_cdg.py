import os
import sys

from sklearn import neighbors
from utils import *
import rewrite as rw
from tqdm import tqdm
from math import factorial as ft
import numpy as np
import networkx as nx
from copy import deepcopy

def construct_mesh_cdg(**kwargs):
    '''
    This function constructs a base Mesh NoC(Network on Chip) CDG(Channel Dependency Graph) 
    The Network is default to adopt XY routing algorithm

    Return
    ---------------------
    type:   MultiDiGraph
    '''
    legal_node = ['left_i','left_o','right_i','right_o','up_i','up_o','down_i','down_o','local_i','local_o']
    legal_path = [['left_i','right_o'],['left_i','up_o'],['left_i','down_o'],['right_i','left_o'],['right_i','up_o'],['right_i','down_o'],['up_i','down_o'],['down_i','up_o'],['local_i','left_o'],['local_i','right_o'],['local_i','up_o'],['local_i','down_o'],['left_i','local_o'],['right_i','local_o'],['up_i','local_o'],['down_i','local_o']]

    W = kwargs['w']
    H = kwargs['h']
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


def construct_torus_cdg(**kwargs):
    '''
    This function constructs a base Torus NoC(Network on Chip) CDG(Channel Dependency Graph) 
    The Network is default to adopt Ring XY routing algorithm

    Return
    ---------------------
    type:   MultiDiGraph
    '''
    legal_node = ['right_o_vc0','down_o_vc0','up_i_vc0','left_i_vc0','right_o_vc1','down_o_vc1','up_i_vc1','left_i_vc1','local_i','local_o']
    legal_path = [['left_i_vc0','right_o_vc0'],['left_i_vc1','right_o_vc1'],['up_i_vc0','down_o_vc0'],['up_i_vc1','down_o_vc1'],['local_i','right_o_vc0'],['local_i','down_o_vc0'],['left_i_vc0','local_o'],['left_i_vc1','local_o'],['up_i_vc0','local_o'],['up_i_vc1','local_o'],['left_i_vc0','down_o_vc0'],['left_i_vc1','down_o_vc0']]

    W = kwargs['w']
    H = kwargs['h']
    G=nx.MultiDiGraph()
    for i in range(W):
        for j in range(H):
            for k in range(len(legal_node)):
                G.add_node((i,j,legal_node[k]))
            for k in range(len(legal_path)):
                G.add_edge((i,j,legal_path[k][0]),(i,j,legal_path[k][1]))

    for j in range(H):
        G.add_edge((W-1,j,'right_o_vc0'),(0,j,'left_i_vc1'))
        for i in range(W-1):
            G.add_edge((i,j,'right_o_vc0'),(i+1,j,'left_i_vc0'))
            G.add_edge((i,j,'right_o_vc1'),(i+1,j,'left_i_vc1'))

    for i in range(W):
        G.add_edge((i,H-1,'down_o_vc0'),(i,0,'up_i_vc1'))
        for j in range(H-1):
            G.add_edge((i,j,'down_o_vc0'),(i,j+1,'up_i_vc0'))
            G.add_edge((i,j,'down_o_vc1'),(i,j+1,'up_i_vc1'))

    if not rw.find_cycle(G):
        # print("Torus construction done")
        return G
    print("Torus construction failed")
    return None


def construct_cube_cdg(**kwargs):
    '''
    This function constructs a base n-dimensional Cube NoC(Network on Chip) CDG(Channel Dependency Graph) 
    The Network is default to adopt dimension-ordered routing algorithm where dim0 gets the highest routing priority 

    Return
    ---------------------
    type:   MultiDiGraph
    '''
    D = kwargs['d'] #dimension of the cube network
    G = nx.MultiDiGraph()
    legal_node = []
    legal_path = []
    for i in range(D):
        legal_node.append('dim_'+str(i)+'_i')
        legal_node.append('dim_'+str(i)+'_o')
        legal_path.append(['dim_'+str(i)+'_i','local_o'])
        legal_path.append(['local_i','dim_'+str(i)+'_o'])
    legal_node.append('local_i')
    legal_node.append('local_o')
    for i in range(D-1):
        for j in range(i+1,D):
            legal_path.append(['dim_'+str(i)+'_i','dim_'+str(j)+'_o'])
    for i in range(2**D):
        id = dec2bin(i,bit_wide=D)
        for j in range(len(legal_node)):
            G.add_node((id,legal_node[j]))
        for j in range(len(legal_path)):
            G.add_edge((id,legal_path[j][0]),(id,legal_path[j][1]))
    for i in range(2**D):
        id = dec2bin(i,bit_wide=D)
        neigh_id_list = []
        for bit in range(D):
            neigh_id_list.append(rever_id(id,bit))
        # print(neigh_id_list)
        for j in range(len(neigh_id_list)):
            G.add_edge((id,'dim_'+str(j)+'_o'),(neigh_id_list[j],'dim_'+str(j)+'_i'))
    
    if not rw.find_cycle(G):
        # print("Cube construction done")
        return G
    print("Cube construction failed")
    return None


def set_bound_router(G,**kwargs):
    '''
    This function sets all the boundary routers according to router ID list
    Sensitive to the topology of he network
    '''
    bound_router_list = kwargs['brl']
    arch = kwargs['arch']
    D = kwargs['d']
    if arch == 'mesh':
        for i in range(len(bound_router_list)):
            x = bound_router_list[i][0]
            y = bound_router_list[i][1]
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

    elif arch == 'torus':
        for i in range(len(bound_router_list)):
            x = bound_router_list[i][0]
            y = bound_router_list[i][1]
            G.add_node((x,y,'bound_i'))
            G.add_node((x,y,'bound_o'))
            G.add_edge((x,y,'bound_i'),(x,y,'right_o_vc0'))
            G.add_edge((x,y,'bound_i'),(x,y,'down_o_vc0'))
            G.add_edge((x,y,'bound_i'),(x,y,'local_o'))
            G.add_edge((x,y,'left_i_vc0'),(x,y,'bound_o'))
            G.add_edge((x,y,'left_i_vc1'),(x,y,'bound_o'))
            G.add_edge((x,y,'up_i_vc0'),(x,y,'bound_o'))
            G.add_edge((x,y,'up_i_vc1'),(x,y,'bound_o'))
            G.add_edge((x,y,'local_i'),(x,y,'bound_o'))
    
    elif arch == 'cube':
        for i in range(len(bound_router_list)):
            id = bound_router_list[i]
            G.add_node((id,'bound_i'))
            G.add_node((id,'bound_o'))
            for j in range(D):
                G.add_edge((id,'bound_i'),(id,'dim_'+str(j)+'_o'))
                G.add_edge((id,'dim_'+str(j)+'_i'),(id,'bound_o'))
            G.add_edge((id,'bound_i'),(id,'local_o'))
            G.add_edge((id,'local_i'),(id,'bound_o'))
    
    else:
        print('invalid topology:',arch)
        sys.exit()


def set_abstract_node(G):
    '''
    This function sets the abstract node outside the target network
    '''
    G.add_node('abstract_node')


def connect_all_bound(G,**kwargs):
    '''
    This function connects all boundary routers to the abstract node
    Sensitive to the topology of he network
    '''
    bound_router_list = kwargs['brl']
    arch = kwargs['arch']
    for i in range(len(bound_router_list)):
        id = bound_router_list[i]
        if arch == 'cube':
            id = (bound_router_list[i],)
        bi = id+('bound_i',)
        bo = id+('bound_o',)
        G.add_edge(bo,'abstract_node')
        G.add_edge('abstract_node',bi)



if __name__ == '__main__':
    G=construct_cube_cdg(d=6)
    set_bound_router(G,brl=['010101'],arch='cube',d=6)
    set_abstract_node(G)
    connect_all_bound(G,brl=['010101'])
    print(is_connected(G,arch='cube',w=3,h=3,d=6))