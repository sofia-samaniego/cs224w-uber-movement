library(dplyr)

save_graph <- function(data, city, year, quarter, day_type, h){
    data <- data %>% filter(hod == h)
    prefix <- paste(city, year, quarter, day_type, sep = '-')
    write.table(data, paste(paste(prefix, h, sep = "_"),"csv",sep="."), 
              row.names = FALSE, 
              col.names = FALSE,
              sep = ',')
                
    return ()
} 
read_all_data <- function(filename, city, year, quarter, day_type){
    global_path <- '/Volumes/BackupSofiaS/data/raw-uber-movement'
    path <- paste(global_path, filename, sep = '/')
    data <- read.csv(path)
    save_path <- paste( '/Volumes/BackupSofiaS/data',city,'raw', sep = '/')
    setwd(save_path)
    for (h in 0:23){
        save_graph(data, city, year, quarter, day_type, h)
    }
}

file_list_wkday <- c('bogota-cadastral-2017-3-OnlyWeekdays-HourlyAggregate.csv',
                     'boston-censustracts-2017-3-OnlyWeekdays-HourlyAggregate.csv',
                     'johannesburg-gpzones-2017-3-OnlyWeekdays-HourlyAggregate.csv',
                     'manila-hexes-2017-3-OnlyWeekdays-HourlyAggregate.csv', 
                     'paris-communes-2017-3-OnlyWeekdays-HourlyAggregate.csv',
                     'sydney-tz-2017-3-OnlyWeekdays-HourlyAggregate.csv',
                     'washington_DC-censustracts-2017-3-OnlyWeekdays-HourlyAggregate.csv')

file_list_wkend <- c('bogota-cadastral-2017-3-OnlyWeekends-HourlyAggregate.csv',
                     'boston-censustracts-2017-3-OnlyWeekends-HourlyAggregate.csv',
                     'johannesburg-gpzones-2017-3-OnlyWeekends-HourlyAggregate.csv',
                     'manila-hexes-2017-3-OnlyWeekends-HourlyAggregate.csv',
                     'paris-communes-2017-3-OnlyWeekends-HourlyAggregate.csv',
                     'sydney-tz-2017-3-OnlyWeekends-HourlyAggregate.csv',
                     'washington_DC-censustracts-2017-3-OnlyWeekends-HourlyAggregate.csv')

city_list <- c('bogota',
               'boston',
               'johannesburg',
               'manila',
               'paris',
               'sydney',
               'washington')

sapply(7:7, function(i) read_all_data(file_list_wkday[i], city_list[i], 2017, 3, 'wkday'))
sapply(7:7, function(i) read_all_data(file_list_wkend[i], city_list[i], 2017, 3, 'wkend'))
