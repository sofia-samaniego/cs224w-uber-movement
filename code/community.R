library(dplyr)

setwd('/Users/Sofia/Desktop/Stanford/Autumn 2017/CS224W/cs224w-uber-movement/data/washington')
wel <- read.csv('weighted_edgelist.csv', header = FALSE)
wel <- wel %>% filter(V3 > 0)

library(igraph)

g <- graph.data.frame(wel,directed=TRUE);

GA <- as_adjacency_matrix(G,type="both",names=TRUE,sparse=FALSE,attr="V3");

ebc <- cluster_edge_betweenness(G, weights = wel$V3, directed = TRUE,
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
g2<-delete.edges(g, ebc$removed.edges[seq(length=which.max(mods)-1)])
V(g)$color=clusters(g2)$membership

# Let's choose a layout for the graph
g$layout <- layout.fruchterman.reingold

# plot it
plot(g, vertex.label=NA)

# if we wanted to use the fastgreedy.community agorithm we would do
fc <- fastgreedy.community(g)
com<-community.to.membership(g, fc$merges, steps= which.max(fc$modularity)-1)
V(g)$color <- com$membership+1
g$layout <- layout.fruchterman.reingold
plot(g, vertex.label=NA)

membership <- data.frame(node_id = as.numeric(V(g)), comm = as.numeric(V(g)$color))
write.table(membership, "communities.txt", row.names = FALSE, col.names = FALSE, sep = ",")


mo <- cluster_leading_eigen(G, steps = -1, weights = wel$V3, start = NULL,
                            options = arpack_defaults, callback = NULL, extra = NULL,
                            env = parent.frame())
