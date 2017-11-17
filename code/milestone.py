################################################################################
# CS 224W (Fall 2017) - Project
# Uber Movement
# Authors:
# jvrsgsty@stanford.edu
# pearson3@stanford.edu
# sofiasf@stanford.edu
# Last Updated: Nov 16, 2017
################################################################################

import snap
import matplotlib.pyplot as plt
import numpy as np
import random
import scipy.stats
import time
import collections
import networkx as nx
import operator

path_adjacency = '../data/washington/washington_DC_censustracts.csv'
path_weights = '../data/washington/washington-2016-1_1.csv'
file_save_edgelist = '../data/washington/weighted_edgelist.csv'
path_distances = '../data/washington/washington_DC_censustracts-dists.csv'
path_longlat = '../data/washington/washington_DC_censustracts_centroid.csv'
path_communities = '../data/washington/communities.txt'
path_hits = '../data/washington/HITS.txt'
path_closeness = '../data/washington/closeness.txt'

def loadPNEANGraph(path):
    """
    :param - path: path to edge list file

    return type: snap.PNEANGraph
    return: Graph loaded from edge list at @path

    """
    ############################################################################

    Graph = snap.LoadEdgeList(snap.PNEANet, path, 0, 1, ",")

    print('Number of nodes: %d' %Graph.GetNodes())
    print('Number of edges: %d' %snap.CntUniqUndirEdges(Graph))

    return Graph


def loadNGraph(path):
    """
    :param - path: path to edge list file

    return type: snap.PNGraph
    return: Graph loaded from edge list at @path
    """
    ############################################################################

    Graph = snap.LoadEdgeList(snap.PUNGraph, path, 0, 1, ",")

    print('Number of nodes: %d' %Graph.GetNodes())
    print('Number of edges: %d' %snap.CntUniqUndirEdges(Graph))

    return Graph


def loadWeights(path):
    """
    :param - path: path to edge list file

    return type: dictionary (key = node pair (a,b), value = weight)
    return: Return 4 weights associated with node pairs: mean, standard
            deviation, geometric mean and geometric standard deviation of time
            of travel
    """
    means = collections.defaultdict(float)
    sds = collections.defaultdict(float)
    g_means = collections.defaultdict(float)
    g_sds = collections.defaultdict(float)
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

def loadDists(path):
    """
    :param - path: path to a distance matrix csv file

    return type: dictionary (key = node pair (a,b), value = sign)
    return: A dictionary of distances (in meters) between centroids of nodes
    """
    dists = collections.defaultdict(float)
    with open(path, 'r') as ipfile:
        i = 0
        for line in ipfile:
            if line[0] != '#':
                line_arr = line.split(',')
                for j in range(i+1):
                    dists[(i+1,j+1)] = float(line_arr[j])
                    dists[(j+1,i+1)] = float(line_arr[j])
                i += 1
    return dists

def add_weights(graph, weights, Attr):
    """
    :param - graph: graph of type snap.PNEANGraph
    :param - weights: defaultdict mapping pairs of nodes to weight
    :param - attr: string equal to the type of weights being added
             For example:  "mean_time"

    return type: snap.PNEANGraph
    return: graph with edges weighted using param: weights
    """
    for EdgeI in graph.Edges():
        N1 = EdgeI.GetSrcNId()
        N2 = EdgeI.GetDstNId()
        graph.AddFltAttrDatE(EdgeI, means[(N1, N2)], Attr)

    return graph

def saveWeights(graph, weights, filename):
    """
    :param - graph: graph of type snap.PNGraph
    :param - weights: defaultdict mapping pairs of nodes to weight
    :param - filename: path to file where weighted edgelist will be stored
    """
    f = open(filename, 'w')
    for EdgeI in graph.Edges():
        s = EdgeI.GetSrcNId()
        d = EdgeI.GetDstNId()
        w = weights[(s, d)]
        if w != 0:
            f.write(str(s) + ',' + str(d) + ',' + str(w) + "\n")
    f.close()

def computePageRank(graph, Attr):
    """
    :param - graph: weighted graph of type snap.PNEANGraph
    :param - attr: string equal to the type of weights used to
    compute the pageRank. For example: "mean_time"

    return type: snap.TIntFltH()
    return: a dictionary mapping node id to page rank
    """
    PRankH = snap.TIntFltH()
    snap.GetWeightedPageRank(graph, PRankH, Attr, 0.85, 1e-4, 100)
    return PRankH

def computeWeightedBetweennessCentr(graph, Attr):
    """
    :param - graph: weighted graph of type snap.PNEANGraph
    :param - attr: string equal to the type of weights used to
    compute the betweenessCentr. For example: "mean_time"

    return type: snap.TIntFltH()
    return: a dictionary mapping node id to betweeness centrality measure
    """
    NIdBtwH = snap.TIntFltH()
    EdgeBtwH = snap.TIntPrFltH()

    attr = snap.TFltV()
    for edge in graph.Edges():
        attr.Add(graph.GetFltAttrDatE(edge, Attr))

    snap.GetWeightedBetweennessCentr(graph, NIdBtwH, EdgeBtwH, attr, 1.0, True)

    return NIdBtwH

def computeWeightedInDegree(graph, Attr):
    """
    :param - graph: weighted graph of type snap.PNEANGraph

    return type: dictionary
    return: a dictionary mapping node id to in degree
    """
    InDegree = []
    for nodeI in graph.Nodes():
        indeg = 0
        node1 = nodeI.GetId()
        for node2 in nodeI.GetInEdges():
            indeg += graph.GetFltAttrDatE(graph.GetEI(node2, node1), Attr)
        InDegree.append((node1, indeg))
    return InDegree

def computeWeightedOutDegree(graph, Attr):
    """
    :param - graph: weighted graph of type snap.PNEANGraph

    return type: dictionary
    return: a dictionary mapping node id to out degree
    """
    OutDegree = []
    for nodeI in graph.Nodes():
        outdeg = 0
        node1 = nodeI.GetId()
        for node2 in nodeI.GetOutEdges():
            outdeg += graph.GetFltAttrDatE(graph.GetEI(node1, node2), Attr)
        OutDegree.append((node1, outdeg))
    return OutDegree

def graphViz(graph, nodeWeight, Attr, plt_name):
    """
    :param - graph: weighted graph of type snap.PNEANGraph
    :param - nodeWeight: dictionary with key: node id, value: weight
    :param - attr: string equal to the type of weights used to
    compute the betweenessCentr. For example: "mean_time"

    return: saves a plot
    """
    G=nx.Graph()
    latlong = np.genfromtxt(path_longlat, delimiter=',')

    for NodeI in graph.Nodes():
        nodeID = NodeI.GetId()
        G.add_node(nodeID, nodeWeight = nodeWeight[NodeI.GetId()], pos = (latlong[nodeID-1][0], latlong[nodeID-1][1]))
    for EdgeI in graph.Edges():
        N1 = EdgeI.GetSrcNId()
        N2 = EdgeI.GetDstNId()
        G.add_edge(N1, N2, edgeWeight = graph.GetFltAttrDatE(EdgeI, Attr))

    nodes, nodeWeight = zip(*nx.get_node_attributes(G,'nodeWeight').items())
    edges, edgeWeight = zip(*nx.get_edge_attributes(G,'edgeWeight').items())

    pos = nx.spring_layout(G,k=0.5,iterations=20)
    nx.draw(G, nx.get_node_attributes(G, 'pos'), arrows = True, node_shape = '.', with_labels = False, nodelist=nodes, node_color=nodeWeight, \
        edge_list=edges, edge_color=[np.log(y+1) for y in edgeWeight], width=.5, cmap=plt.cm.tab20c)
    plt.savefig("../{}.png".format(plt_name))

if __name__ == "__main__":
    geoGraph = loadPNEANGraph(path_adjacency)
    means, sds, g_means, g_sds = loadWeights(path_weights)
    weightedGeoGraph = add_weights(geoGraph, means, "mean_time")
    pageRank = computePageRank(weightedGeoGraph, "mean_time")
    betweenCentr = computeWeightedBetweennessCentr(weightedGeoGraph, "mean_time")
    closeness = np.genfromtxt(path_closeness, delimiter=',')
    closeness_dict = {}
    for c in closeness:
        closeness_dict[c[0]] = c[1]
    graphViz(weightedGeoGraph, pageRank, "mean_time", "pageRank")
    graphViz(weightedGeoGraph, betweenCentr, "mean_time", "betweenCentr")
    graphViz(weightedGeoGraph, closeness_dict, "mean_time", "closeness")
    #
    # communities = np.genfromtxt(path_communities, delimiter=',')
    # communities_dict = {}
    # for c in communities:
    #     communities_dict[c[0]] = c[1]
    # graphViz(weightedGeoGraph, communities_dict, "mean_time", "communities")
    #
    #
    # hits = np.genfromtxt(path_hits, delimiter=',')
    # hubs_dict = {}
    # for c in hits:
    #     hubs_dict[c[0]] = c[1]
    #
    # authorities_dict = {}
    # for c in hits:
    #     authorities_dict[c[0]] = c[2]

    indeg = computeWeightedInDegree(weightedGeoGraph, "mean_time")
    outdeg = computeWeightedOutDegree(weightedGeoGraph, "mean_time")
    #
    print sorted(indeg, key=lambda x: x[1], reverse = True)[:5]
    # print "#########"
    print sorted(outdeg, key=lambda x: x[1], reverse = True)[:5]

    # graphViz(weightedGeoGraph, closeness_dict, "mean_time")
    # graphViz(weightedGeoGraph, betweenCentr, "mean_time")
