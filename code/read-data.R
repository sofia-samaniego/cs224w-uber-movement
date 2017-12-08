library(dplyr)

data <- read.csv('/Users/Mackenzie/Downloads/washington_DC-censustracts-2016-1-All-HourlyAggregate.csv')
save_graph <- function(h){
    data <- data %>% filter(hod == h)
    write.table(data, paste(paste("washington-2016-1", h, sep = "_"),"csv",sep="."), row.names = FALSE, col.names = FALSE, sep = ",")
    return ()
} 
setwd('/Users/Mackenzie/Documents/cs224w/cs224w-uber-movement/data/washington/raw')
for (h in 0:23){
    save_graph(h)
}

