
args <- commandArgs(trailingOnly = TRUE)
wd <- args[1]
# wd <- "G:\\SWAT\\t3"
setwd(wd)


# Read objectives from file
settings <- file("simSetting.txt",open = "r")
NSE <- RSquared <- PBIAS <- FALSE
RMSE <- MAPE <- FALSE # Abandoned
while (TRUE) {
  line <- readLines(settings, 1)
  if ( length(line) == 0 ) {
    break
  }
  cat(line,"\n")
  # read & create parameters
  seg <- unlist(strsplit(line, split = ":|,"))
  if(seg[1]=="objective"){
    for(i in seg){
      if(i=="NSE"){
        NSE <- TRUE
      }else if(i=="RSquared"){
        RSquared <- TRUE
      }else if(i=="PBIAS"){
        PBIAS <- TRUE
      }
    }
  }
  else if(seg[1]=="observation"){
    observations <- seg[-1]
  }
}
close(settings)

# Loop all observations
for (obs in observations) {
  # Observation 
  obs_path <- paste("obs_",obs,".txt",sep = '') 
  obs_data <- t(read.table(obs_path)[-1,])
  obs_data <- t(apply(obs_data,1,as.numeric))
  
  # simResult
  sim_path <- paste("single_sim_result_",obs,".dat",sep = '')
  sim_data <- read.table(sim_path)
  
  
  if(NSE){
    # calculate NSE
    sim_single <- sim_data[1,1:length(obs_data)]
    
    # start
    nse <- 1 - sum((obs_data - sim_single)^2) / sum((obs_data - rowMeans(obs_data))^2)
    
    write.table(nse,paste("NSE_single_",obs,".dat",sep = ''), col.names = F, row.names = F,append = F)
  }
  
  if(RSquared){
    # RSquared
    R2_total <- matrix(0, nrow(sim_data), 1)
    
    # calculate RSquared
    for (sim_id in c(1:nrow(sim_data))) {
      sim_single <- sim_data[sim_id,1:length(obs_data)]
      
      # start
      R2_total[sim_id] <- sum((obs_data - rowMeans(obs_data))*(sim_single - rowMeans(sim_single)))^2 / (sum((obs_data - rowMeans(obs_data))^2)*sum((sim_single - rowMeans(sim_single))^2))
    }
    write.table(R2_total,paste("RSquared_single_",obs,".dat",sep = ''), col.names = F, row.names = F,append = F)
  }
  
  if(PBIAS){
    # PBIAS
    pbias_total <- matrix(0, nrow(sim_data), 1)
    
    # calculate PBIAS
    for (sim_id in c(1:nrow(sim_data))) {
      sim_single <- sim_data[sim_id,1:length(obs_data)]
      
      # start
      pbias_total[sim_id] <- 100 * sum((obs_data - sim_single)) / sum(obs_data)
    }
    write.table(pbias_total,paste("PBIAS_single_",obs,".dat",sep = ''), col.names = F, row.names = F,append = F)
  }
  
  if(RMSE){
    # calculate RMSE
    sim_single <- sim_data[1,1:length(obs_data)]
    
    # start
    rmse <- sqrt(sum((obs_data - sim_single)^2) / length(obs_data))
    
    write.table(rmse,paste("RMSE_single_",obs,".dat",sep = ''), col.names = F, row.names = F,append = F)
  }
  
  if(MAPE){
    # calculate MAPE
    sim_single <- sim_data[1,1:length(obs_data)]
    
    # start
    mape <- sum(abs(obs_data - sim_single)*100/obs_data) / length(obs_data)
    
    write.table(mape,paste("MAPE_single_",obs,".dat",sep = ''), col.names = F, row.names = F,append = F)
  }
  
  
}


