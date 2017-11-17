library(dplyr)

setwd('/Users/Sofia/Desktop/Stanford/Autumn 2017/CS224W/cs224w-uber-movement/data/washington')
wel <- read.csv('weighted_edgelist.csv', header = FALSE)
wel <- wel %>% filter(V3 > 0) 

# Get rid of outliers 
#wel <- wel[order(wel$V3, decreasing = TRUE),]
#wel <- wel[5:nrow(wel),]

library(igraph)

g <- graph.data.frame(wel, directed=TRUE);

GA <- as_adjacency_matrix(g,type="both",names=TRUE,sparse=FALSE,attr="V3");

ebc <- cluster_edge_betweenness(g, weights = wel$V3, directed = TRUE,
                               edge.betweenness = TRUE, merges = TRUE, bridges = TRUE,
                               modularity = TRUE, membership = TRUE)

# Now we have the merges/splits and we need to calculate the modularity
# for each merge for this we'll use a function that for each edge
# removed will create a second graph, check for its membership and use
# that membership to calculate the modularity
mods <- sapply(0:ecount(g), function(i){
    g2 <- delete.edges(g, ebc$removed.edges[seq(length=i)])
    cl <- clusters(g2)$membership
    # March 13, 2014 - compute modularity on the original graph g 
    # (Thank you to Augustin Luna for detecting this typo) and not on the induced one g2. 
    modularity(g,cl)
})

# we can now plot all modularities
plot(mods, pch=20)

# Now, let's color the nodes according to their membership
#g2<-delete.edges(g, ebc$removed.edges[seq(length=which.max(mods)-1)])
g2<-delete.edges(g, ebc$removed.edges[seq(length=2500)])
V(g)$color=clusters(g2)$membership

g$layout <- layout.fruchterman.reingold

# plot it
# plot(g)
plot(g, vertex.label=NA)

# save it to file for plotting in python 
membership <- data.frame(node_id = as.numeric(V(g)), comm = as.numeric(V(g)$color))
write.table(membership, "communities.txt", row.names = FALSE, col.names = FALSE, sep = ",")


# Hubs and Authorities

HITS <- data.frame(nid =as.numeric(V(g)), 
                   Hubs = hub_score(g, weights = wel$V3)$vector,
                   Authorities = authority_score(g, weights = wel$V3)$vector)
write.table(HITS, "HITS.txt", row.names = FALSE, col.names = FALSE, sep = ",")


closeness_in <- closeness(g, vids = V(g), mode = "in",
                weights = wel$V3, normalized = TRUE)

closeness_out <- closeness(g, vids = V(g), mode = "out",
                       weights = wel$V3, normalized = TRUE)

closeness_all <- closeness(g, vids = V(g), mode = "all",
                           weights = wel$V3, normalized = TRUE)

closeness <- data.frame(nid =as.numeric(V(g)), 
                        c_in = closeness_in ,
                        c_out = closeness_out, 
                        c_all = closeness_all)
