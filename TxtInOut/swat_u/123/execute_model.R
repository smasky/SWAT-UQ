rm(list = ls())
library(sp)
library(rgdal)
library(raster)

args <- commandArgs(trailingOnly = TRUE)
wd <- args[1]
row_n <- as.numeric(args[2])
resowd <- args[3]
preExe <- args[4]
# wd <- 'G:\\SWAT\\t2\\'
# row_n <- 1
# resowd <- 'I:\\a_SWAT(SA)\\SWAT_SA_Desktop_Project\\swat-sa-project\\src\\main\\resource\\'
# preExe <- 0

setwd(wd)
source("Functions.R") ##Required functions.

# Start-up file & the required data
{
  ## For checking the SWAT results to verify the whole processes
  output.rch.file<-as.character(c("xgeswat\\Scenarios\\Default\\TxtInOut\\output.rch"))
  output.hru.file<-as.character(c("xgeswat\\Scenarios\\Default\\TxtInOut\\output.hru"))
  
  if(preExe == 1){
    ## Load original data, get uncertainty
    sample.dem <- raster('xgeswat\\Source\\original\\dem.tif') ## Original DEM
    sample.landuse <- raster('xgeswat\\Source\\original\\landuse.tif') ## Orginal LULC
    ori.lu.res <- xres(sample.landuse) ## resolution
    sample.soil <- raster('xgeswat\\Source\\original\\soil.tif') ## Original Soil datasets
    ori.so.res <- xres(sample.soil)
  }
  
  
  simRange <- unlist(strsplit(read.table("simSetting.txt")[1,1],':|-|,'))
  startYear <- as.integer(simRange[2])
  endYear <- as.integer(simRange[5])
  
}


# Read sampling parameters
{
  model.in.rows <- NULL
  model.in.sample <- NULL
  
  A <- read.csv("params_sampling.csv",header = T)
  params <- A[row_n,]
  
  # whether have UDEM or MinStream
  execWD <- 0
  # whether have hru's params
  execHru <- 0
  
  for(i in 1:length(colnames(A))){
    print(colnames(A)[i])
    if(length(params) == 1){
      print(params[1])
    }else{
      print(params[1,i])
    }
    
    # read & create parameters
    name <- colnames(A)[i]
    if(length(params) == 1){
      value <- params[1]
    }else{
      value <- params[1,i]
    }
    {
      # Watershed Delineation
      if(grepl('UDEM',name)){
        writeRaster(sample.dem, 'xgeswat\\Source\\dem.tif', overwrite=TRUE)
        execWD <- 1
        
      }else if(grepl('MinStream',name)){
        write.table(round(value), 'xgeswat\\Source\\threshold.txt', quote=FALSE, row.names = F, col.names = F)
        execWD <- 1
      }
      # HRU Creation
      else if(grepl('ULULC',name)){
        if(value > 0){
          val.rb.error.lu <- ceiling(value /ori.lu.res)*2 + 1
        }else if(value==0){
          val.rb.error.lu <- 0
        }else{
          val.rb.error.lu <- -1*ceiling((value*-1) /ori.lu.res)*2-1
        }
        new.lu <- errorband(sample.landuse, val.rb.error.lu)
        writeRaster(new.lu, 'xgeswat\\Source\\landuse.tif', overwrite=TRUE)
        execHru <- 1
        
      }else if(grepl('USoil',name)){
        if(value > 0){
          val.rb.error.so <- ceiling(value /ori.so.res)*2 + 1
        }else if(value==0){
          val.rb.error.so <- 0
        }else{
          val.rb.error.so <- -1*ceiling((value*-1) /ori.so.res)*2-1
        }
        new.soil <- errorband(sample.soil, val.rb.error.so)
        writeRaster(new.soil, 'xgeswat\\Source\\soil.tif', overwrite=TRUE)
        execHru <- 1
        
      }else if(grepl('MinLU',name)){
        write.table(value, 'xgeswat\\Source\\lumindef.txt', quote=FALSE, row.names = F, col.names = F)
        execHru <- 1
        
      }else if(grepl('MinSoil',name)){
        write.table(value, 'xgeswat\\Source\\somindef.txt', quote=FALSE, row.names = F, col.names = F)
        execHru <- 1
        
      }else if(grepl('MinSlope',name)){
        write.table(value, 'xgeswat\\Source\\slmindef.txt', quote=FALSE, row.names = F, col.names = F)
        execHru <- 1
        
      }else if(grepl('IntSlope',name)){
        write.table(round(value), 'xgeswat\\Source\\slopdef.txt', quote=FALSE, row.names = F, col.names = F)
        execHru <- 1
        
      }
      # SWAT Execution
      else if(grepl('UPREC',name)){
        
        #Precipitation error preparation
        stations <- as.character(read.table("xgeswat\\Source\\stations.txt")[,1]) 
       
        for (st in stations) {
          pcp.file <- as.character(paste("xgeswat\\Source\\original\\",st,"ori.pcp",sep = "")) ##Original precipitation 
          pcp.out.file <- as.character(paste("xgeswat\\Source\\", st, ".pcp",sep = "")) ##Precipitation for checking process
        
          ##Get precipitation and change it Vector
          pcp.head <- readLines(pcp.file, n=1)
          pp<-readLines(pcp.file)
          pp.n <- length(pp)-1
          # remove space line
          for (i in c(1:length(pp))) {
            if(pp[i] == ''){
              pp.n <- pp.n - 1
            }
          }
          
          pcp.ori <- vector(mode = 'numeric', length = pp.n)
          pcp.unc <- vector(mode = 'character', length = pp.n)
          # year <- 2013
          
          for(k in 1:pp.n){
            if(grepl('-99.0',pp[k+1])){
              pcp.ori[k] <- -99
            }else{
              pcp.ori[k] <- as.numeric(pp[k+1])
            }
          }
          
          n <- 0
          for(j in startYear:endYear){
            if((j%%4==0 & j%%100!=0)|(j%%400==0)){
              days <- 366
            }else{
              days <- 365
            }
            n <- n+days
            for(k in (n-days+1):n){
              if(pcp.ori[k] == -99){
                pcp.unc[k] <- paste(as.character(j*1000+k-n+days),'-99.0',sep = '') 
              }else{
                ori.value <- pcp.ori[k] - ((j*1000+k-n+days)*1000) 
                pcp.unc[k] <- as.character(format(signif(pcp.ori[k] + (ori.value*value/100),11), nsmall = 1))
              }
            }
            pp.n <- pp.n-days
          }
          write.table(c(pcp.head, pcp.unc), pcp.out.file, quote=FALSE, row.names=FALSE, col.names=FALSE)
          
        }
        
      }
      # related to runoff
      else if(grepl('CN2',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.mgt',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('ESCO',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.hru',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('SLSUBBSN',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.hru',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('OV_N',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.hru',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('EPCO',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.hru',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('CANMX',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.hru',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('HRU_SLP',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.hru',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('SOL_Z',name)){
        model.in.rows<- c(model.in.rows,paste(name,'().sol',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('SOL_BD',name)){
        model.in.rows<- c(model.in.rows,paste(name,'().sol',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('SOL_AWC',name)){
        model.in.rows<- c(model.in.rows,paste(name,'().sol',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('SOL_K',name)){
        model.in.rows<- c(model.in.rows,paste(name,'().sol',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('SOL_ALB',name)){
        model.in.rows<- c(model.in.rows,paste(name,'().sol',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('GW_REVAP',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.gw',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('GW_DELAY',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.gw',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('REVAPMN',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.gw',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('GWQMN',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.gw',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('ALPHA_BF',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.gw',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('RCHRG_DP',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.gw',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('CH_K2',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.rte',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('CH_N2',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.rte',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('ALPHA_BNK',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.rte',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('SMFMX',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.bsn',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('SMFMN',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.bsn',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('SFTMP',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.bsn',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('SMTMP',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.bsn',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('TIMP',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.bsn',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('SURLAG',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.bsn',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('TLAPS',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.sub',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('CH_K1',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.sub',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('CH_N1',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.sub',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }
      # related to sediment
      else if(grepl('USLE_P',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.mgt',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('SPCON',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.bsn',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('SPEXP',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.bsn',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('CH_COV1',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.rte',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('CH_COV2',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.rte',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }
      # related to Nutrients
      else if(grepl('RCN',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.bsn',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('BIOMIX',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.mgt',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('NPERCO',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.bsn',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('PPERCO',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.bsn',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('PHOSKD',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.bsn',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('ERORGN',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.hru',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }else if(grepl('ERORGP',name)){
        model.in.rows<- c(model.in.rows,paste(name,'.hru',sep = ''))
        model.in.sample <- c(model.in.sample,value)
        
      }
    }
  }
}


# Running SWAT preparation tool & SWAT
{
  if(preExe == 1){
    # Define Swat preparation program ##Developed by OpenGMS team in C#
    # prePath <- paste(resowd,"ErrorProp\\ErrorProp.exe",sep = '')
    prePath <- "ErrorProp\\ErrorProp.exe"
    if(execWD == 1 | execHru == 1 | row_n == 1){
      prefname <- c(paste(prePath,wd,1,1))
      delhrufiles('xgeswat\\Scenarios\\Default\\TxtInOut\\')
      system(prefname, show.output.on.console = F, invisible = T, wait = TRUE)
    }
  }
  
  
  efname <- paste("execSWAT_Edit.exe",paste(wd,"xgeswat\\Scenarios\\Default\\TxtInOut\\SWAT_Edit.exe",sep=""),sep=" ") 
  # efname <- c("SWAT_Edit.exe") 
  sfname <- c("swat2012.exe") 
  
  # if(length(list.files("xgeswat\\Scenarios\\Default\\TxtInOut\\Backup")) == 0) 
  #   file.copy(dir("xgeswat\\Scenarios\\Default\\TxtInOut",full.names=T),"xgeswat\\Scenarios\\Default\\TxtInOut\\Backup",recursive=F, overwrite = T) ##Copy new prepared files into backup folder
    
  if(!is.null(model.in.rows)){
    
    # init the project
    # file.copy(dir("xgeswat\\Scenarios\\Default\\TxtInOut\\Backup",full.names=T),"xgeswat\\Scenarios\\Default\\TxtInOut",recursive=F, overwrite = T) ##Copy out from backup folder
    
    model.in.file <-as.character(c("xgeswat\\Scenarios\\Default\\TxtInOut\\model.in"))
    
    write.table(model.in.sample, model.in.file, quote=FALSE, row.names=model.in.rows, col.names=FALSE,append = F)
    
    # Run SWAT_edit
    setwd(paste(wd,"xgeswat\\Scenarios\\Default\\TxtInOut\\",sep=""))
    system(efname, wait = TRUE)
  }
  
  ##Run SWAT
  setwd(paste(wd,"xgeswat\\Scenarios\\Default\\TxtInOut\\",sep=""))
  system(sfname, show.output.on.console = F, invisible = T, wait = TRUE)
  
  setwd(wd)
  ##Get result
  Qsim.data<-read.table(output.rch.file, skip=9)
  hru.data<-tryCatch({read.table(output.hru.file, skip=9)}, error = function(cond){return(-1)})
  if(is.data.frame(hru.data)){
    hru.cnt <- (nrow(hru.data))/((endYear - startYear +1)*13 +1) #Number of hru, 14 = # (year+1(year summary))+1(Total)
  }else{
    hru.cnt <- hru.data
  }
  
  
  basin.cnt <- (nrow(Qsim.data))/((endYear - startYear +1)*13 +1) #Number of basins
  
  # default is the last basin, or the basinID in  basinID.txt 
  if(file.exists("basinID.txt")){
    basinID <- as.integer(read.table("basinID.txt")[1,1])
  }else{
    basinID <- basin.cnt
  }
  
  # outletID <- as.integer(read.table("outletID.txt")[1,1])
  
  res.id <- nrow(Qsim.data)-basin.cnt+basinID
  output <- t(Qsim.data[res.id, 7])
  total.output <- do.call(cbind, Qsim.data[res.id, 7:ncol(Qsim.data)])
  
  write.table(basin.cnt,'res_basin.dat',col.names = F, row.names = F,append = T)
  write.table(hru.cnt,'res_hru.dat',col.names = F, row.names = F,append = T)
  write.table(output,'res_output.dat',col.names = F, row.names = F,append = T)
  write.table(t(apply(total.output,1,as.numeric)),'res_total_output.dat',col.names = F, row.names = F,append = T,sep = ',')
  
 
  # save the simulation result 
  simTargets <- unlist(strsplit(read.table("simSetting.txt")[3,1],':|-|,'))
  Flow <- Sed <- TN <- TP <- DO <- NO3 <- NH4 <- FALSE
  for (tar in simTargets) {
    if(tar=="Flow"){
      Flow <- TRUE
    }else if(tar=="Sed"){
      Sed <- TRUE
    }else if(tar=="TN"){
      TN <- TRUE
    }else if(tar=="TP"){
      TP <- TRUE
    }else if(tar=="DO"){
      DO <- TRUE
    }else if(tar=="NO3"){
      NO3 <- TRUE
    }else if(tar=="NH4"){
      NH4 <- TRUE
    }
  }
  
  simResult <- NULL
  for (i in seq(basinID, nrow(Qsim.data),by=basin.cnt)) {
    simResult <- rbind(simResult,Qsim.data[i,])
  }
  # delete the sum of every year and total year
  for (i in seq(13,nrow(simResult),by=13)) {
    simResult <- simResult[-i,]
  }
  # if(nrow(simResult)%%12 != 0){
    simResult <- simResult[-nrow(simResult),]
  # }
  
  if(Flow){
    fl <- t(simResult[7])
    write.table(fl,"sim_result_Flow.dat",col.names = F, row.names = F,append = T)
  }
    
  if(Sed){
    se <- t(simResult[11])
    write.table(se,"sim_result_Sed.dat",col.names = F, row.names = F,append = T)
  }
    
  if(NO3){
    no <- t(simResult[18])
    write.table(no,"sim_result_NO3.dat",col.names = F, row.names = F,append = T)
  }
  
  
  if(NH4){
    nh <- t(simResult[20])
    write.table(nh,"sim_result_NH4.dat",col.names = F, row.names = F,append = T)
  }
    
  if(DO){
    do <- t(simResult[30])
    write.table(do,"sim_result_DO.dat",col.names = F, row.names = F,append = T)
  }  
    
  if(TN){
    tn <- t(simResult[48])
    write.table(tn,"sim_result_TN.dat",col.names = F, row.names = F,append = T)
  }
  
  
  if(TP){
    tp <- t(simResult[49])
    write.table(tp,"sim_result_TP.dat",col.names = F, row.names = F,append = T)
  }
  
}
