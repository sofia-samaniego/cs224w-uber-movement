library(dplyr)
library(igraph)
library(ape)

global_path <- '/Volumes/BackupSofiaS/data'
# global_path <- './data'

create_textfiles <- function(city,
                             year,
                             quarter,
                             hod,
                             num_clusters){
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
    
    # edgelist <- edgelist %>% filter(weight > 0)

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
    
    # Clustering 
    # Run Girvan-Newman clustering algorithm.
    communities <- edge.betweenness.community(g, 
                                              weights = edgelist$weight,
                                              directed = TRUE,
                                              edge.betweenness = TRUE)
    
    as_phylo(communities, use.modularity = FALSE)
    
    memb <- cut_at(communities, step = 700)

    clusters <- data.frame(nodes = as.numeric(V(g)), cluster = as.numeric(memb))
    summ_table <- clusters %>% group_by(cluster) %>% summarize(num_members = n())


    file_communities <- paste(paste(prefix, 'communities', hod, sep = '_'),
                              'txt',
                              sep = '.')
    path_communities <- paste(city, 'measures', 'communities', file_communities, sep = '/')

    global_path_communities <- paste(global_path, path_communities, sep = '/')

    write.table(clusters,
                global_path_communities,
                row.names = FALSE,
                col.names = FALSE,
                sep = ",")
    return(summ_table)
}

summaries <- lapply(0:23, function(hod) create_textfiles('washington', '2016', '1', hod, num_clusters = 60))
lapply(summaries, print)
sapply(summaries, function(table) summary(table$num_members))



