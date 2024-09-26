##Functions
errorband <- function(x, width){ ##Functions for epsilon band
  if(width>0){
    w <- matrix(1,nrow=width, ncol=width) 
    r <- focal(x, w=w, fun=max, na.rm = F)
  }
  else if(width==0){
    r <- x
  }
  else{
    width <- -1*width
    w <- matrix(1,nrow=width, ncol=width) 
    r <- focal(x, w=w, fun=min, na.rm = F)
  }
  return(r)
}


delhrufiles <- function(path){
  # path <- 'G:\\SWAT\\t2\\xgeswat\\Scenarios\\Default\\TxtInOut\\'
  files <- list.files(path)
  for (i in c(1:length(files))) {
    f <- files[i]
    if(!grepl("swat",tolower(f))){
      unlink(paste(path,f,sep = ''))
    }
  }
  return(TRUE)
}


SAFun <- function(sim.i){
  ##Required libraries
  # library(raster)
  # library(sensitivity)
  
  
  i <- sim.i
  # output <- 99
  # total.output <- matrix(1:6,  nrow= 2) ##all results
  # basin.cnt <- 99
  # hru.cnt <- 99
  # res <- list(basin.cnt, hru.cnt, output, total.output)
  # hru.cnt[i] <- 99
  # # globalenv$hru.cnt[i] <- 99
  # 
  # return (res)
 
  # copy folder
  test0 <- "F:\\SWAT\\ProgTest\\"
  testi <- paste("F:\\SWAT\\ProgTest", as.character(i),"\\", sep = "")
  if(dir.exists(testi)) { 
    unlink(testi, recursive=TRUE)
    dir.create(testi)
  }else{
    dir.create(testi)
  }
  list.of.files <- paste(test0,list.files(test0),sep = "")
  file.copy(list.of.files,testi,recursive = TRUE)
  
  setwd(testi)
  source("Functions.R") ##Required functions.
  
  ##Define Swat preparation program ##Developed by OpenGMS team in C#
  prefname <- c(paste("ErrorProp/ErrorProp/bin/Debug/ErrorProp.exe",i))
  
  bfname<-c("xgeswat\\Scenarios\\Default\\runSample.bat")
  
  batch.text.template<- paste('@echo off
  F: 
  cd ', testi, 'xgeswat\\Scenarios\\Default\\TxtInOut"
  start /w SWAT_Edit.exe
  swat2012.exe
  if %errorlevel% == 0 exit 0
  echo.', sep = "")
  
  write(batch.text.template, bfname)
  
  ##For checking the SWAT results to verify the whole processes
  output.rch.file<-as.character(c("xgeswat\\Scenarios\\Default\\TxtInOut\\output.rch"))
  output.hru.file<-as.character(c("xgeswat\\Scenarios\\Default\\TxtInOut\\output.hru"))
  
  ##Input uncertainty setting
  sample.dem <- raster('xgeswat\\Source\\original\\dem.tif') ##Original DEM
  sample.landuse <- raster('xgeswat\\Source\\original\\landuse.tif') ##Orginal LULC
  ori.lu.res <- xres(sample.landuse)
  sample.soil <- raster('xgeswat\\Source\\original\\soil.tif') ##Original Soil datasets
  ori.so.res <- xres(sample.soil)
  
  #Precipitation error preparation
  pcp.file <- as.character(c("xgeswat\\Source\\323103ori.pcp")) ##Original precipitation 
  pcp.out.file <- as.character(c("xgeswat\\Source\\323103.pcp")) ##Precipitation for checking process
  
  ##Get precipitation and change it Vector
  pcp.head <- readLines(pcp.file, n=4)
  pp<-readLines(pcp.file)
  pp.n <- length(pp)-4
  pcp.ori <- vector(mode = 'numeric', length = pp.n)
  pcp.unc <- vector(mode = 'character', length = pp.n)
  year <- 2013
  
  for(k in 1:pp.n){
    pcp.ori[k] <- as.numeric(pp[k+4])
  }
  
  
  
  ##Delineation definition (P2)
  write.table(round(parameters[i, 2]), 'xgeswat\\Source\\threshold.txt', quote=FALSE, row.names = F, col.names = F)
  
  #Landuse Error (P3)
  if(parameters[i,3] > 0){
    val.rb.error.lu <- ceiling(parameters[i,3] /ori.lu.res)*2 + 1
  }else if(parameters[i,3]==0){
    val.rb.error.lu <- 0
  }else{
    val.rb.error.lu <- -1*ceiling((parameters[i,3]*-1) /ori.lu.res)*2-1
  }
  new.lu <- errorband(sample.landuse, val.rb.error.lu)
  writeRaster(new.lu, 'xgeswat\\Source\\landuse.tif', overwrite=TRUE)
  
  #Soil Error (P4)
  if(parameters[i,4] > 0){
    val.rb.error.so <- ceiling(parameters[i,4] /ori.so.res)*2 + 1
  }else if(parameters[i,4]==0){
    val.rb.error.so <- 0
  }else{
    val.rb.error.so <- -1*ceiling((parameters[i,4]*-1) /ori.so.res)*2-1
  }
  new.soil <- errorband(sample.soil, val.rb.error.so)
  writeRaster(new.soil, 'xgeswat\\Source\\soil.tif', overwrite=TRUE)
  
  
  ##Landuse min definition (P5)
  write.table(parameters[i, 5], 'xgeswat\\Source\\lumindef.txt', quote=FALSE, row.names = F, col.names = F)
  
  ##Soil min definition (P6)
  write.table(parameters[i, 6], 'xgeswat\\Source\\somindef.txt', quote=FALSE, row.names = F, col.names = F)
  
  ##Slope min definition (P7)
  write.table(parameters[i, 7], 'xgeswat\\Source\\slmindef.txt', quote=FALSE, row.names = F, col.names = F)
  
  ##Slope defintion (P8)
  write.table(round(parameters[i, 8]), 'xgeswat\\Source\\slopdef.txt', quote=FALSE, row.names = F, col.names = F)
  
  #Precipitation error (P9)
  for(k in 1:pp.n){
    ori.value <- pcp.ori[k] - ((year*1000+k)*1000) 
    pcp.unc[k] <- as.character(format(round(pcp.ori[k] + (ori.value*parameters[i,9]/100),1), nsmall = 1))
  }
  write.table(c(pcp.head, pcp.unc), pcp.out.file, quote=FALSE, row.names=FALSE, col.names=FALSE)
  
  
  #Running SWAT preparation tool
  system(prefname, show.output.on.console = F, invisible = F)
  
  
  #Creating SWAT datasets for running SWAT
  file.copy(dir("xgeswat\\Scenarios\\Default\\TxtInOut",full.names=T),"xgeswat\\Scenarios\\Default\\TxtInOut\\Backup",recursive=F, overwrite = T) ##Copy new prepared files into backup folder
  model.in.rows<- c("v__ALPHA_BF.gw", "v__GW_DELAY.gw", "r__CN2.mgt", "v__ESCO.hru", "v__RCN.bsn", "v__NPERCO.bsn")
  
  model.in.file <-as.character(c("xgeswat\\Scenarios\\Default\\TxtInOut\\model.in"))
  
  ##P10-13
  sample.n <- c(t(parameters[i,10:15]))
  write.table(sample.n, model.in.file, quote=FALSE, row.names=model.in.rows, col.names=FALSE)
  
  ##Run SWAT
  system(bfname, show.output.on.console = T)
  
  ##Get result
  Qsim.data<-read.table(output.rch.file, skip=9)
  hru.data<-tryCatch({read.table(output.hru.file, skip=9)}, error = function(cond){return(-1)})
  if(is.data.frame(hru.data)){
    hru.cnt <- (nrow(hru.data))/14 #Number of hru, 14 = # (year+1(year summary))+1(Total)
  }else{
    hru.cnt <- hru.data
  }
  
  
  basin.cnt <- (nrow(Qsim.data))/14 #Number of basins
  
  res.id <- nrow(Qsim.data)-basin.cnt+1
  output <- t(Qsim.data[res.id, 7])
  total.output <- do.call(cbind, Qsim.data[res.id, 7:ncol(Qsim.data)])
  print(paste("Completed ", i, " of the total ", ": ", Sys.time()))
  
  res <- list(basin.cnt, hru.cnt, output, total.output)
  
  unlink(testi,recursive = TRUE)
  return (res)
}
