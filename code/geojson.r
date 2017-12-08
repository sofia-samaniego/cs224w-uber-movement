library(rgeos)
library(rgdal)
library(igraph)
library(geosphere)

main_path <- "/Users/jvrsgsty/Documents/Stanford/ICME/CS224W/project/data/"
cities <- c("bogota/geo/bogota_cadastral",
            "boston/geo/boston_censustracts",
            #"boston/geo/boston_taz",
            "johannesburg/geo/johannesburg_gpzones",
            "manila/geo/manila_hexes",
            "paris/geo/paris_communes",
            "paris/geo/paris_iris",
            #"sydney/geo/sydney_miz",
            "sydney/geo/sydney_tz",
            "washington/geo/washington_DC_censustracts",
            "washington/geo/washington_DC_taz")
# Generate spatial graph for adjacent polygons on the GeoJSON files
for (i in 1:length(cities)){
  print(cities[i])
  filename <- paste(main_path, cities[i], sep="")
  polys <- readOGR(paste(filename,"json", sep="."), "OGRGeoJSON")
  m <- gTouches(polys, byid=TRUE)
  g <- graph.adjacency(m)
  G <- get.edgelist(g)
  # Offset the ids by 1 to make them correspond to Uber Ids
  ones <- matrix(1, nrow(G), ncol(G))
  GG <- as.numeric(G) + ones
  
  # Compute the distances between centroids in the polygons
  centroids <- gCentroid(polys, byid=TRUE)
  write.table(centroids, paste(filename, paste("centroid", "csv", sep="."), sep="_"), row.names = FALSE, col.names= FALSE, sep=",")
  dists <- distm(centroids, centroids)
  write.table(dists, paste(filename, paste("dists", "csv", sep="."),sep="_"), row.names = FALSE, col.names= FALSE, sep=",")
  
  # Append the distances as weights to the graph
  GG <- cbind(GG, matrix(0, nrow(G),1))
  for (j in 1:nrow(GG)){
    src = GG[j,1]
    dst = GG[j,2]
    GG[j,3] = dists[src, dst]
  }
  # Save the file
  write.table(GG, paste(filename, paste("graph", "csv", sep="."),sep="_"), row.names = FALSE, col.names= FALSE, sep=",")
}
