library(dplyr)
library(igraph)

global_path <- '/Users/Mackenzie/Documents/cs224w/cs224w-uber-movement/data'
# global_path <- './data'

create_textfiles <- function(city,
                             year,
                             quarter,
                             hod,
                             num_remove = 'NA',
                             maxmod = FALSE){
    print(hod)
    # Set working directory
    setwd(paste(global_path, city, sep = '/'))
    prefix <- paste(city, year, quarter, sep = '-')

    # Read in weighted edgelist
    file_edgelist <- paste(paste(prefix, 'edgelist', hod, sep = '_'),
                           'csv',
                           sep = '.')
    path_edgelist <- paste(city, 'weighted_edgelist', file_edgelist, sep = '/')

    global_path_edgelist <- paste(global_path, path_edgelist, sep = '/')
    edgelist <- read.csv(global_path_edgelist, header = FALSE)
    names(edgelist) <- c('s_id', 'd_id', 'weight')
    edgelist <- edgelist %>% filter(weight > 0)

    # Create graph
    g <- graph.data.frame(edgelist, directed=TRUE)

    # Compute closeness centrality and save to file
    closeness <- closeness(g, vids = V(g),
                           mode = "all",
                           weights = edgelist$weight,
                           normalized = TRUE)

    closeness_df <- data.frame(nid = as.numeric(V(g)),
                               c_all = closeness)
    file_closeness <- paste(paste(prefix, 'closeness', hod, sep = '_'),
                           'txt',
                           sep = '.')
    path_closeness <- paste(city, 'measures', 'closeness', file_closeness, sep = '/')

    global_path_closeness <- paste(global_path, path_closeness, sep = '/')

    write.table(closeness_df,
                global_path_closeness,
                row.names = FALSE,
                col.names = FALSE,
                sep = ",")

    # Compute HITS and save to file
    HITS_df <- data.frame(nid = as.numeric(V(g)),
                       Hubs = hub_score(g, weights = edgelist$weight)$vector,
                       Authorities = authority_score(g, weights = edgelist$weight)$vector)

    file_HITS <- paste(paste(prefix, 'HITS', hod, sep = '_'),
                            'txt',
                            sep = '.')
    path_HITS <- paste(city, 'measures', 'HITS', file_HITS, sep = '/')

    global_path_HITS <- paste(global_path, path_HITS, sep = '/')


    write.table(HITS_df,
                global_path_HITS,
                row.names = FALSE,
                col.names = FALSE,
                sep = ",")

    # Compute communities using G-N algorithm and save it to file
    GA <- as_adjacency_matrix(g,type="both",
                              names=TRUE,
                              sparse=FALSE,
                              attr="weight");

    ebc <- cluster_edge_betweenness(g,
                                    weights = edgelist$weight,
                                    directed = TRUE,
                                    edge.betweenness = TRUE,
                                    merges = TRUE,
                                    bridges = TRUE,
                                    modularity = TRUE,
                                    membership = TRUE)

    # Now we have the merges/splits and we need to calculate the modularity
    # for each merge for this we'll use a function that for each edge
    # removed will create a second graph, check for its membership and use
    # that membership to calculate the modularity

    mods <- sapply(0:ecount(g), function(i){
        g2 <- delete.edges(g, ebc$removed.edges[seq(length=i)])
        cl <- clusters(g2)$membership
        modularity(g,cl)
    })

    if(maxmod){
        g2 <- delete.edges(g, ebc$removed.edges[seq(length=which.max(mods)-1)])
    } else{
        g2 <- delete.edges(g, ebc$removed.edges[seq(length=num_remove)])
    }

    communities <- data.frame(node_id = as.numeric(V(g)),
                              comm = clusters(g2)$membership)
    file_communities <- paste(paste(prefix, 'communities', hod, sep = '_'),
                              'txt',
                              sep = '.')
    path_communities <- paste(city, 'measures', 'communities', file_communities, sep = '/')

    global_path_communities <- paste(global_path, path_communities, sep = '/')

    write.table(communities,
                global_path_communities,
                row.names = FALSE,
                col.names = FALSE,
                sep = ",")
}

sapply(0:23, function(hod) create_textfiles('washington', '2016', '1', hod, maxmod = TRUE))

#create_textfiles('washington', '2016', '1', 1, 2500)
