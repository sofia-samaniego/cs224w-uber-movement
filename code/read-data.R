library(dplyr)

save_graph <- function(data, city, year, quarter, h){
    data <- data %>% filter(hod == h)
    prefix <- paste(city, year, quarter, sep = '-')
    write.table(data, paste(paste(prefix, h, sep = "_"),"csv",sep="."), 
              row.names = FALSE, 
              col.names = FALSE,
              sep = ',')
                
    return ()
} 
read_all_data <- function(filename, city, year, quarter){
    global_path <- '/Users/Sofia/Desktop/Stanford/Autumn\ 2017/CS224W/project'
    path <- paste(global_path, filename, sep = '/')
    data <- read.csv(path)
    save_path <- paste('/Users/Sofia/Desktop/data/',city,'raw', sep = '/')
    setwd(save_path)
    for (h in 0:23){
        save_graph(data, city, year, quarter, h)
    }
}

file_list <- c('bogota-cadastral-2016-1-All-HourlyAggregate.csv',
               'boston-censustracts-2016-1-All-HourlyAggregate.csv',
               'johannesburg-gpzones-2016-1-All-HourlyAggregate.csv',
               'manila-hexes-2016-1-All-HourlyAggregate.csv',
               'paris-iris-2016-1-All-HourlyAggregate (1).csv',
               'sydney-tz-2016-1-All-HourlyAggregate.csv',
               'washington_DC-censustracts-2016-1-All-HourlyAggregate.csv')
city_list <- c('bogota',
               'boston',
               'johannesburg',
               'manila',
               'paris',
               'sydney',
               'washington')

sapply(1:7, function(i) read_all_data(file_list[i], city_list[i], 2016, 1))
