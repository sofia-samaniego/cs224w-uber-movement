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
from collections import defaultdict
i=1

base_path = '..'
base_path = '/Volumes/G-DRIVE XBSGS'
path_adjacency = base_path + '/data/washington/washington_DC_censustracts.csv'
path_weights = base_path + '/data/washington/washington-2016-1_{}.csv'.format(i)
file_save_edgelist = base_path + '/data/washington/weighted_edgelist.csv'
path_distances = base_path + '/data/washington/washington_DC_censustracts-dists.csv'
path_longlat = base_path + '/data/washington/washington_DC_censustracts_centroid.csv'
path_communities = base_path + '/data/washington/communities.txt'
path_hits = base_path + '/data/washington/HITS.txt'
path_closeness = base_path + '/data/washington/closeness.txt'

def loadPNEANGraph(path):
    """
    :param - path: path to edge list file

    return type: snap.PNEANGraph
    return: Graph loaded from edge list at @path

    """
    ############################################################################

    Graph = snap.LoadEdgeList(snap.PNEANet, path, 0, 1, ",")

    # print('Number of nodes: %d' %Graph.GetNodes())
    # print('Number of edges: %d' %snap.CntUniqUndirEdges(Graph))

    return Graph


def loadNGraph(path):
    """
    :param - path: path to edge list file

    return type: snap.pngraph
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
            line_arr = line.split(',')
            if line_arr[0] == line_arr[1]:
                continue
            node1 = int(line_arr[0])
            node2 = int(line_arr[1])
            mean = float(line_arr[3])
            # sd = float(line_arr[4])
            # g_mean = float(line_arr[5])
            # g_sd = float(line_arr[6])
            means[(node1, node2)] = mean
            # sds[(node1, node2)] = sd
            # g_means[(node1, node2)] = g_mean
            # g_sds[(node1, node2)] = g_sd
    return means#, sds, g_means, g_sds

def loadDists(path):
    """
    :param - path: path to a distance matrix csv file

    return type: dictionary (key = node pair (a,b), value = weight)
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

def saveWeights(graph, Attr, filename):
    """
    :param - graph: weighted graph of type snap.PNEANGraph
    :param - filename: path to file where weighted edgelist will be stored
    """
    f = open(filename, 'w')
    for EdgeI in graph.Edges():
        s = EdgeI.GetSrcNId()
        d = EdgeI.GetDstNId()
        w = graph.GetFltAttrDatE(EdgeI, Attr)
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
    InDegree = {}
    for nodeI in graph.Nodes():
        indeg = 0
        node1 = nodeI.GetId()
        for node2 in nodeI.GetInEdges():
            indeg += graph.GetFltAttrDatE(graph.GetEI(node2, node1), Attr)
        InDegree[node1] = indeg
    return InDegree

def computeWeightedOutDegree(graph, Attr):
    """
    :param - graph: weighted graph of type snap.PNEANGraph

    return type: dictionary
    return: a dictionary mapping node id to out degree
    """
    OutDegree = {}
    for nodeI in graph.Nodes():
        outdeg = 0
        node1 = nodeI.GetId()
        for node2 in nodeI.GetOutEdges():
            outdeg += graph.GetFltAttrDatE(graph.GetEI(node1, node2), Attr)
        OutDegree[node1] = outdeg
    return OutDegree

def fromR(path_closeness, path_communities, path_hits):
    """
    :param - path_closeness: path to csv file with closeness weighted node list
    :param - path_communities: path to csv file with communities weighted node list
    :param - path_hits: path to csv file with hubs and authorities weighted node list

    return type: dictionary
    return: 4 dictionaries mapping node to weight
    """

    closeness = np.genfromtxt(path_closeness, delimiter=',')
    closeness_dict = {}
    for c in closeness:
        closeness_dict[c[0]] = c[1]

    communities = np.genfromtxt(path_communities, delimiter=',')
    communities_dict = {}
    for c in communities:
        communities_dict[c[0]] = c[1]

    hits = np.genfromtxt(path_hits, delimiter=',')
    hubs_dict = {}
    for c in hits:
        hubs_dict[c[0]] = c[1]

    authorities_dict = {}
    for c in hits:
        authorities_dict[c[0]] = c[2]

    return closeness_dict, communities_dict, hubs_dict, authorities_dict

def graphViz(graph, nodeWeight, latlong, Attr, plot_name, format='png'):
    """
    :param - graph: weighted graph of type snap.PNEANGraph
    :param - nodeWeight: dictionary with key: node id, value: weight
    :param - attr: string equal to the type of weights used to
    compute the betweenessCentr. For example: "mean_time"

    return: saves a plot
    """
    G=nx.Graph()

    # Use default dict when doing step 3, and 4
    nodeWeight = defaultdict(float, nodeWeight)
    for NodeI in graph.Nodes():
        nodeID = NodeI.GetId()
        G.add_node(nodeID, nodeWeight = nodeWeight[NodeI.GetId()]+1, pos = (latlong[nodeID-1][0], latlong[nodeID-1][1]))
    for EdgeI in graph.Edges():
        N1 = EdgeI.GetSrcNId()
        N2 = EdgeI.GetDstNId()
        G.add_edge(N1, N2, edgeWeight = graph.GetFltAttrDatE(EdgeI, Attr))

    nodes, nodeWeight = zip(*nx.get_node_attributes(G,'nodeWeight').items())
    edges, edgeWeight = zip(*nx.get_edge_attributes(G,'edgeWeight').items())

    pos = nx.spring_layout(G,k=0.5,iterations=20)
    nx.draw(G, nx.get_node_attributes(G, 'pos'), arrows = True, node_shape = '.', with_labels = False, nodelist=nodes, node_color=nodeWeight, \
        node_size=150, edge_list=edges, edge_color = '#92cae2', width=.5, cmap=plt.cm.tab20c) #
    plt.savefig(plot_name + '.' + format, transparent=True, format=format)
    plt.clf()
#edge_color = [np.log(y+1) for y in edgeWeight]
if __name__ == "__main__":

    cities = {}
    cities["washington"] = "washington_DC_censustracts"
    cities["sydney"] = "sydney_tz"
    cities["paris"] = "paris_communes"
    cities["manila"] = "manila_hexes"
    cities["johannesburg"] = "johannesburg_gpzones"
    cities["boston"] = "boston_censustracts"
    cities["bogota"] = "bogota_cadastral"

    for city, city_name in cities.iteritems():
        print city

        # Grab graph with edges only between geographically adjacent nodes and their lat/longitude
        path_adjacency = base_path + '/data/{}/geo/{}_graph.csv'.format(city, city_name)
        path_latlong = base_path + '/data/{}/geo/{}_centroid.csv'.format(city, city_name)
        geoGraph = loadPNEANGraph(path_adjacency)
        latlong = np.genfromtxt(path_latlong, delimiter=',')

        for week in ["wkday"]:#, "wkend"]:
            print week

            for i in range(0,24):
                print i

                # Construct weighted graph, where edges are only between geographically adjacent nodes
                path_weights = base_path + '/data/{}/raw/{}-2017-3-{}_{}.csv'.format(city, city, week, i)
                means = loadWeights(path_weights)
                weightedGeoGraph = add_weights(geoGraph, means, "mean_time")

                ################## STEP 1
                # Save Edge Lists
                # save_path_edgelist = base_path + '/data/{}/weighted_edgelist/{}-2017-3-{}_edgelist_{}.csv'.format(city, city, week, i)
                # saveWeights(weightedGeoGraph, "mean_time", save_path_edgelist)

                ################## STEP 2
                # Betweenness Centrality
                # betweenCentr = computeWeightedBetweennessCentr(weightedGeoGraph, "mean_time")
                # plot_name = base_path + '/data/{}/measures/betweenness/{}-2017-3-{}_betweenness_{}'.format(city, city, week, i)
                # graphViz(weightedGeoGraph, betweenCentr, latlong, "mean_time", plot_name)

                # # In Degree
                # indeg = computeWeightedInDegree(weightedGeoGraph, "mean_time")
                # plot_name = base_path + '/data/{}/measures/in_degree/{}-2017-3-{}_in_degree_{}'.format(city, city, week, i)
                # graphViz(weightedGeoGraph, indeg, latlong, "mean_time", plot_name)

                # # Out Degree
                # outdeg = computeWeightedOutDegree(weightedGeoGraph, "mean_time")
                # plot_name = base_path + '/data/{}/measures/out_degree/{}-2017-3-{}_out_degree_{}'.format(city, city, week, i)
                # graphViz(weightedGeoGraph, outdeg, latlong, "mean_time", plot_name)

                # # Page Rank
                # pagerank = computePageRank(weightedGeoGraph, "mean_time")
                # plot_name = base_path + '/data/{}/measures/pagerank/{}-2017-3-{}_pagerank_{}'.format(city, city, week, i)
                # graphViz(weightedGeoGraph, pagerank, latlong, "mean_time", plot_name)


                ################## STEP 3 Need to run create-R-files for wkday and wkend

                path_closeness = base_path + '/data/{}/measures/closeness/{}-2017-3-{}_closeness_{}.txt'.format(city, city, week, i)
                path_communities = base_path + '/data/{}/measures/communities/{}-2017-3-{}_communities_{}.txt'.format(city, city, week, i)
                path_HITS = base_path + '/data/{}/measures/HITS/{}-2017-3-{}_HITS_{}.txt'.format(city, city, week, i)
                #
                closeness_dict, communities_dict, hubs_dict, authorities_dict = fromR(path_closeness, path_communities, path_HITS)
                # plt_path_closeness = base_path + '/data/{}/measures/closeness/{}-2017-3-{}_closeness_{}'.format(city, city, week, i)
                plt_path_communities = base_path + '/data/{}/measures/communities/{}-2017-3-{}_communities_{}'.format(city, city, week, i)
                # plt_path_hubs = base_path + '/data/{}/measures/HITS/{}-2017-3-{}_hubs_{}'.format(city, city, week, i)
                # plt_path_authorities = base_path + '/data/{}/measures/HITS/{}-2017-3-{}_authorities_{}'.format(city, city, week, i)
                #
                # graphViz(weightedGeoGraph, closeness_dict, latlong, "mean_time", plt_path_closeness, format='eps')
                # graphViz(weightedGeoGraph, hubs_dict, latlong, "mean_time", plt_path_hubs, format='eps')
                # graphViz(weightedGeoGraph, authorities_dict, latlong, "mean_time", plt_path_authorities, format='eps')
                #
                # ################## STEP 4
                graphViz(weightedGeoGraph, communities_dict, latlong, "mean_time", plt_path_communities, format='eps')

# geoGraph = loadPNEANGraph(path_adjacency)
# means, sds, g_means, g_sds = loadWeights(path_weights)
# weightedGeoGraph = add_weights(geoGraph, means, "mean_time")
# pageRank = computePageRank(weightedGeoGraph, "mean_time")
# betweenCentr = computeWeightedBetweennessCentr(weightedGeoGraph, "mean_time")
#
#
# graphViz(weightedGeoGraph, pageRank, "mean_time", "pageRank")
# graphViz(weightedGeoGraph, betweenCentr, "mean_time", "betweenCentr")
# graphViz(weightedGeoGraph, closeness_dict, "mean_time", "closeness")
#
#
# graphViz(weightedGeoGraph, communities_dict, "mean_time", "communities")
#
#
#
# indeg = computeWeightedInDegree(weightedGeoGraph, "mean_time")
# outdeg = computeWeightedOutDegree(weightedGeoGraph, "mean_time")
# #
# print sorted(indeg, key=lambda x: x[1], reverse = True)[:5]
# # print "#########"
# print sorted(outdeg, key=lambda x: x[1], reverse = True)[:5]

# graphViz(weightedGeoGraph, closeness_dict, "mean_time")
# graphViz(weightedGeoGraph, betweenCentr, "mean_time")
