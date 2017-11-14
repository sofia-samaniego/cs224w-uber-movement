library(rgeos)
library(rgdal)
library(igraph)

polys <- readOGR("/Users/jvrsgsty/Documents/Stanford/ICME/CS224W/project/data/geo/washington_DC_censustracts.json", "OGRGeoJSON")
m <- gTouches(polys, byid=TRUE)
g <- graph.adjacency(m)
G <- get.edgelist(g)
# Offset the ids by 1 to make them correspond to Uber Ids
ones <- matrix(1, nrow(G), ncol(G))
GG <- as.numeric(G) + ones
# Save the file
write.table(GG, "/Users/jvrsgsty/Documents/Stanford/ICME/CS224W/project/data/geo/washington_DC_censustracts.csv", row.names = FALSE, col.names= FALSE, sep=",")
