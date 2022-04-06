import os
import sys
import rewrite as rw
from tqdm import tqdm
from math import factorial as ft
import numpy as np
import networkx as nx
from copy import deepcopy
from scipy.special import comb


def dec2bin(dec_num, bit_wide=16):    
    '''
    This function transfrom a number to binary form with given width
    '''
    _, bin_num_abs = bin(dec_num).split('b')    
    if len(bin_num_abs) > bit_wide:        
        raise ValueError 
    else:        
        if dec_num >= 0:            
            bin_num = bin_num_abs.rjust(bit_wide, '0')        
        else:            
            _, bin_num = bin(2**bit_wide + dec_num).split('b')    
    return bin_num 


def is_connected(G,**kwargs):
    '''
    This function checks whether the CDG is connected to the abstract node
    Must be performed after setting boundary routers and connecting bounds
    Senitive to the topology of the network

    Return
    ---------------------
    type:   bool(True: connected;False: not connected)
    '''
    arch = kwargs['arch']
    W = kwargs['w']
    H = kwargs['h']
    D = kwargs['d']

    if arch == 'mesh' or arch == 'torus':
        for x in range(W):
            for y in range(H):
                if nx.has_path(G,(x,y,'local_i'),'abstract_node'):
                    if nx.has_path(G,'abstract_node',(x,y,'local_o')):
                        pass
                    else:
                        # print("'abstract_node' to ("+str(x)+","+str(y)+",'local_o') not connected")
                        return False
                else:
                    # print("("+str(x)+","+str(y)+",'local_i') to 'abstract_node' not connected")
                    return False
        return True

    elif arch == 'cube':
        for i in range(2**D):
            id = dec2bin(i,bit_wide=D)
            if nx.has_path(G,(id,'local_i'),'abstract_node'):
                if nx.has_path(G,'abstract_node',(id,'local_o')):
                    pass
                else:
                    # print("'abstract_node' to ("+id+",'local_o') not connected")
                    return False
            else:
                # print("("+id+",'local_i') to 'abstract_node' not connected")
                return False
        return True

    else:
        print('invalid topology:',arch)
        sys.exit()


def init_b_turns(**kwargs):
    '''
    This function initializes all the candidate boundary turns according to a certain boundary
    router placement pattern and returns a list of the turns
    Must be performed after setting boundary routers and connecting bounds
    Sensitive to the topology of the network

    Return
    ---------------------
    type:   list(list of initial candidate boundary turns)
    '''
    b_turns = []
    W = kwargs['w']
    H = kwargs['h']
    D = kwargs['d']
    bound_router_list = kwargs['brl']
    arch = kwargs['arch']
    if arch == 'mesh':
        for i in range(len(bound_router_list)):
            rid = bound_router_list[i]
            if rid[0] != 0: #not at left bound
                b_turns.append(((rid[0],rid[1],'bound_i'),(rid[0],rid[1],'left_o')))
                b_turns.append(((rid[0],rid[1],'left_i'),(rid[0],rid[1],'bound_o')))
            if rid[0] != W-1: #not at right bound
                b_turns.append(((rid[0],rid[1],'bound_i'),(rid[0],rid[1],'right_o')))
                b_turns.append(((rid[0],rid[1],'right_i'),(rid[0],rid[1],'bound_o')))
            if rid[1] != 0: #not at up bound
                b_turns.append(((rid[0],rid[1],'bound_i'),(rid[0],rid[1],'up_o')))
                b_turns.append(((rid[0],rid[1],'up_i'),(rid[0],rid[1],'bound_o')))
            if rid[1] != H-1: #not at down bound
                b_turns.append(((rid[0],rid[1],'bound_i'),(rid[0],rid[1],'down_o')))
                b_turns.append(((rid[0],rid[1],'down_i'),(rid[0],rid[1],'bound_o')))
        return b_turns

    elif arch == 'torus':
        for i in range(len(bound_router_list)):
            rid = bound_router_list[i]
            b_turns.append(((rid[0],rid[1],'bound_i'),(rid[0],rid[1],'right_o_vc0')))
            b_turns.append(((rid[0],rid[1],'bound_i'),(rid[0],rid[1],'down_o_vc0')))
            b_turns.append(((rid[0],rid[1],'left_i_vc0'),(rid[0],rid[1],'bound_o')))
            b_turns.append(((rid[0],rid[1],'left_i_vc1'),(rid[0],rid[1],'bound_o')))
            b_turns.append(((rid[0],rid[1],'up_i_vc0'),(rid[0],rid[1],'bound_o')))
            b_turns.append(((rid[0],rid[1],'up_i_vc1'),(rid[0],rid[1],'bound_o')))
        return b_turns
    
    elif arch == 'cube':
        for i in range(len(bound_router_list)):
            rid = bound_router_list[i]
            for j in range(D):
                b_turns.append(((rid,'bound_i'),(rid,'dim_'+str(j)+'_o')))
                b_turns.append(((rid,'dim_'+str(j)+'_i'),(rid,'bound_o')))
        return b_turns

    else:
        print('invalid topology:',arch)
        sys.exit()


def avg_bound_dist(G,**kwargs):
    '''
    This function calculates the average bound distance for a given CDG
    Must on the condition of given width and height of network
    Sensitive to the topology of the network

    Return
    ---------------------
    type:   float
    '''
    arch = kwargs['arch']
    W = kwargs['w']
    H = kwargs['h']
    D = kwargs['d']
    avg_dist = 0

    if arch == 'mesh' or arch == 'torus':
        for i in range(W):
            for j in range(H):
                i_node = (i,j,'local_i')
                o_node = (i,j,'local_o')
                i_2_o_dist = nx.shortest_path_length(G,source=i_node,target='abstract_node')
                o_2_i_dist = nx.shortest_path_length(G,source='abstract_node',target=o_node)
                avg_dist +=  i_2_o_dist + o_2_i_dist
        return avg_dist

    elif arch == 'cube':
        for i in range(2**D):
            id = dec2bin(i,bit_wide=D)
            i_node = (id,'local_i')
            o_node = (id,'local_o')
            i_2_o_dist = nx.shortest_path_length(G,source=i_node,target='abstract_node')
            o_2_i_dist = nx.shortest_path_length(G,source='abstract_node',target=o_node)
            avg_dist += i_2_o_dist + o_2_i_dist
        return avg_dist

    else:
        print('invalid topology:',arch)
        sys.exit()


def avg_bound_reach(G,**kwargs):
    '''
    This function calculates the average bound reachability for a given CDG
    Must on the condition of given width and height of the network and the number of boundary routers
    Sensitive to the topology of the network

    Return
    ---------------------
    type:   float
    '''
    avg_reach = 0
    arch = kwargs['arch']
    W = kwargs['w']
    H = kwargs['h']
    D = kwargs['d']
    bound_router_list = kwargs['brl']
    brl_len = len(bound_router_list)

    if arch == 'mesh' or arch == 'torus':
        for r in range(brl_len):
            r_i_node = bound_router_list[r]+('bound_i',)
            r_o_node = bound_router_list[r]+('bound_o',)
            r_i_reach = 0
            r_o_reach = 0
            for i in range(W):
                for j in range(H):
                    i_node = (i,j,'local_i')
                    o_node = (i,j,'local_o')
                    if nx.has_path(G,i_node,r_o_node):
                        r_o_reach += 1
                    if nx.has_path(G,r_i_node,o_node):
                        r_i_reach += 1
            avg_reach += r_i_reach + r_o_reach
        # avg_reach /= brl_len
        return avg_reach
    
    elif arch == 'cube':
        for r in range(brl_len):
            r_i_node = (bound_router_list[r],'bound_i')
            r_o_node = (bound_router_list[r],'bound_o')
            r_i_reach = 0
            r_o_reach = 0
            for i in range(2**D):
                id = dec2bin(i,bit_wide=D)
                i_node = (id,'local_i')
                o_node = (id,'local_o')
                if nx.has_path(G,i_node,r_o_node):
                    r_o_reach += 1
                if nx.has_path(G,r_i_node,o_node):
                    r_i_reach += 1
            avg_reach += r_i_reach + r_o_reach
            avg_reach /= brl_len
        return avg_reach

    else:
        print('invalid topology:',arch)
        sys.exit()


def sort_all_turns(G,**kwargs):
    '''
    This function sorts all candidate turns according to their object function value,
    used to achieve our-proposed BAB-MDFA
    '''
    act = kwargs['act'] # all candidate turns
    cl = [] 

    for i in range(len(act)):
        cdg = deepcopy(G)
        cdg.remove_edges_from([act[i]])
        ad = avg_bound_dist(cdg,**kwargs)
        ofv = 1/ad
        cl.append((act[i],ofv))
        cl.sort(key=lambda tup:tup[1], reverse=False) # order matters, False: real BAB, True: fake BAB

    temp = []
    for i in range(len(cl)):
        temp.append(cl[i][0])
        print(cl[i][0],"---",cl[i][1])
    return temp


def complete_comb(n,r):
    '''
    This function returns the iteration number of a complete combination
    '''
    cnt = 0
    for i in range(0,r):
        cnt += comb(n,r-i)
    return int(cnt)


def rever_id(id,bit):
    '''
    This function reverses the bit'th bit of id(str) and returns the reversed id rid(str)
    '''
    rid = ''
    for i in range(len(id)):
        if i==bit:
            rid += str(1-int(id[bit]))
        else:
            rid += id[i]
    return rid