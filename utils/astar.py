#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 20:21:07 2023

@author: tjards
"""

# betweenness centrality: expresses the significance of a node to network connectivity
#   count the number of times a node appears on the shortest path between any two other vertices


# import stuff
# ------------

import numpy as np
import random
from collections import defaultdict

# parameters
# ----------
r       = 5
nNodes  = 10


# # random adj matrix
# # -----------------
# A = np.ones((10,10))

# for i in range(0,10):
    
#     A[random.randint(0, A.shape[0]-1),random.randint(0, A.shape[0]-1)] = 0
#     A[random.randint(0, A.shape[0]-1),random.randint(0, A.shape[0]-1)] = 0

# for i in range(0,A.shape[0]):
#     A[i,i] = 0
    

data = 10*np.random.rand(3,nNodes)

#%% build Graph (as dictionary)
# ----------------------------
def build_graph(data):
    G = {}
    nNodes  = data.shape[1]     # number of agents (nodes)
    # for each node
    for i in range(0,nNodes):
        # create a set of edges
        set_i = set()
        # search through neighbours (will add itself)
        for j in range(0,nNodes):
            # compute distance
            dist = np.linalg.norm(data[0:3,j]-data[0:3,i])
            # if close enough
            if dist < r:
                # add to set_i
                set_i.add(j)
            #else:
            #    print("debug: ", i," is ", dist, "from ", j)
        G[i] = set_i
    return G

G = build_graph(data)

# define djikstra (shortest path)
# -------------------------------

# accepts a Graph (dictionary) and starting node
def search_djikstra(G, source):
    
    closed = set()                              # set of nodes not to visit (or already visited)
    parents = {}                                # stores the path back to source 
    costs = defaultdict(lambda: float('inf'))   # store the cost, with a default value of inf for unexplored nodes
    costs[source] = 0
    que = []                                    # to store cost to the node from the source
    
    
    return parents, costs
    
parents, costs = search_djikstra(G, 0)
