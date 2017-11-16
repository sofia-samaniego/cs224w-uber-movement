
################################################################################
# CS 224W (Fall 2017) - Project
# Uber Movement
# Authors:
# jvrsgsty@stanford.edu
# pearson3@stanford.edu
# sofiasf@stanford.edu
# Last Updated: Nov 2, 2017
################################################################################

import snap
import matplotlib.pyplot as plt
import numpy as np
import random
import scipy.stats
import time

path = '../data/washington/washington-2016-1_1.csv'

def loadGraph(path):
    """
    :param - path: path to edge list file

    return type: snap.PNGraph
    return: Graph loaded from edge list at @path

    """
    ############################################################################

    Graph = snap.LoadEdgeList(snap.PNEANet, path, 0, 1, ",")

    print('Number of nodes: %d' %Graph.GetNodes())
    print('Number of edges: %d' %snap.CntUniqUndirEdges(Graph))

    return Graph


def loadWeights(path):
    """
    :param - path: path to edge list file

    return type: dictionary (key = node pair (a,b), value = sign)
    return: Return sign associated with node pairs. Both pairs, (a,b) and (b,a)
    are stored as keys. Self-edges are NOT included.
    """
    means = {}
    sds = {}
    g_means = {}
    g_sds = {}
    with open(path, 'r') as ipfile:
        for line in ipfile:
            if line[0] != '#':
                line_arr = line.split(',')
                if line_arr[0] == line_arr[1]:
                    continue
                node1 = int(line_arr[0])
                node2 = int(line_arr[1])
                mean = float(line_arr[3])
                sd = float(line_arr[4])
                g_mean = float(line_arr[5])
                g_sd = float(line_arr[6])
                means[(node1, node2)] = mean
                sds[(node1, node2)] = sd
                g_means[(node1, node2)] = g_mean
                g_sds[(node1, node2)] = g_sd
    return means, sds, g_means, g_sds

def add_weights(graph, weights):
    Attr = "time"
    for k, v in means.iteritems():
        edge = graph.GetEI(k[0], k[1])
        graph.AddFltAttrDatE(edge, v, Attr)

    for edge in graph.Edges():
        print graph.GetFltAttrDatE(edge, Attr)

if __name__ == "__main__":
    washington = loadGraph(path)
    means, sds, g_means, g_sds = loadWeights(path)
    add_weights(washington, means)
