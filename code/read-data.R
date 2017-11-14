library(dplyr)

data <- read.csv('/Users/Sofia/Desktop/Stanford/Autumn\ 2017/CS224W/project/washington_DC-censustracts-2016-1-All-HourlyAggregate.csv')
save_graph <- function(h){
    data <- data %>% filter(hod == h)
    write.csv(data, paste(paste("washington-2016-1", h, sep = "_"),"csv",sep="."), row.names = FALSE, col.names = FALSE)
    return ()
} 
setwd('/Users/Sofia/Desktop/Stanford/Autumn\ 2017/CS224W/cs224w-uber-movement/data/washington')
for (h in 1:24){
    save_graph(h)
}

