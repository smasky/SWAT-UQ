
rm(list = ls())
library(sensitivity)

args <- commandArgs(trailingOnly = TRUE)
wd <- args[1]
# wd <- 'G:\\SWAT\\t4\\'

setwd(wd)

basin.cnt.dat <- read.table('res_basin.dat')
hru.cnt.dat <- read.table('res_hru.dat')
output.dat <- read.table('res_output.dat')
total.output.dat <- read.table('res_total_output.dat',sep = ',')

sim.n <- length(basin.cnt.dat[,1])

params <- read.csv("params_sampling.csv",header = T)
p <- length(params[1,])

# Read simTimes n from file
settings <- file("simSetting.txt",open = "r")
Flow <- Sed <- TN <- TP <- DO <- NO3 <- NH4 <- FALSE
while (TRUE) {
  line <- readLines(settings, 1)
  if ( length(line) == 0 ) {
    break
  }
  cat(line,"\n")
  # read & create parameters
  seg <- unlist(strsplit(line, split = ":|,"))
  if(seg[1]=="simTimes"){
    n <- as.numeric(seg[2])
  }else if(seg[1]=="simTargets"){
    for(i in seg){
      if(i=="Flow"){
        Flow <- TRUE
      }else if(i=="Sed"){
        Sed <- TRUE
      }else if(i=="TN"){
        TN <- TRUE
      }else if(i=="TP"){
        TP <- TRUE
      }else if(i=="DO"){
        DO <- TRUE
      }else if(i=="NO3"){
        NO3 <- TRUE
      }else if(i=="NH4"){
        NH4 <- TRUE
      }
    }
  }
}
close(settings)
M <- 4
# n <- 65 #214 #Parameters selection for e-FAST (Saltelli, 1999, Technometrics)
omega <- numeric(p)
omega[1] <- floor((n - 1)/(2 * M))
m <- floor(omega[1]/(2 * M))
if (m >= p - 1) {
  omega[-1] <- floor(seq(from = 1, to = m, length.out = p - 1))
}else {
  omega[-1] <- (0:(p - 2))%%m + 1
}
s <- 2 * pi/n * (0:(n - 1))

n.var <- 45 ## Number of SWAT output variables 
##Define vectors to store analysis results
output <- vector('numeric', length = sim.n)
total.output <- matrix(0,  nrow= sim.n, ncol=n.var) ##all results
basin.cnt <- vector('numeric', length = sim.n) ##watershed counts
hru.cnt <- vector('numeric', length = sim.n) ##hru counts

for (i in seq(1, sim.n)) {
  basin.cnt[i] = basin.cnt.dat[i,1]
  hru.cnt[i] = hru.cnt.dat[i,1]
  output[i] = output.dat[i,1]
  # total.output[i,] = total.output.dat[i,]
}
total.output <- data.matrix(total.output.dat)
##Simulation result
fast99.result <- list(basin.cnt, hru.cnt, output, total.output)


##After simulation.
## define the result to "fast99" class to use tell and related functions
x <- list(model = NULL, M = M, s = s, omega = omega, X = params, r =fast99.result, call = match.call())
class(x) <- "fast99"

# Flow 7-6=1 <- Sed 11-6=5 <- NO3 18-6=12 <- NH4 20-6=14 <- DO 30-6=24 <- TN 48-6=42 <- TP 49-6=43

if(Flow){
  x$y <- x$r[[4]][,1] ##flow Here the code is overwritten
  ##Calculate main and interaction effects
  tell(x)
  S <- rbind(x$D1/x$V, 1 - x$Dt/x$V - x$D1/x$V)
  colnames(S) <- colnames(x$X)
  rownames(S) <- c("mainEffect", "interactions")
  write.csv(S,"SA_score_Flow.csv")
}

if(Sed){
  x$y <- x$r[[4]][,5] 
  tell(x)
  S <- rbind(x$D1/x$V, 1 - x$Dt/x$V - x$D1/x$V)
  colnames(S) <- colnames(x$X)
  rownames(S) <- c("mainEffect", "interactions")
  write.csv(S,"SA_score_Sed.csv")
}

if(NO3){
  x$y <- x$r[[4]][,12] ##NO3
  tell(x)
  S <- rbind(x$D1/x$V, 1 - x$Dt/x$V - x$D1/x$V)
  colnames(S) <- colnames(x$X)
  rownames(S) <- c("mainEffect", "interactions")
  write.csv(S,"SA_score_NO3.csv")
}


if(NH4){
  x$y <- x$r[[4]][,14] ##NH4
  tell(x)
  S <- rbind(x$D1/x$V, 1 - x$Dt/x$V - x$D1/x$V)
  colnames(S) <- colnames(x$X)
  rownames(S) <- c("mainEffect", "interactions")
  write.csv(S,"SA_score_NH4.csv")
}

if(DO){
  x$y <- x$r[[4]][,24] 
  tell(x)
  S <- rbind(x$D1/x$V, 1 - x$Dt/x$V - x$D1/x$V)
  colnames(S) <- colnames(x$X)
  rownames(S) <- c("mainEffect", "interactions")
  write.csv(S,"SA_score_DO.csv")
}

if(TN){
  x$y <- x$r[[4]][,42] 
  tell(x)
  S <- rbind(x$D1/x$V, 1 - x$Dt/x$V - x$D1/x$V)
  colnames(S) <- colnames(x$X)
  rownames(S) <- c("mainEffect", "interactions")
  write.csv(S,"SA_score_TN.csv")
}

if(TP){
  x$y <- x$r[[4]][,43] ##TP
  tell(x)
  S <- rbind(x$D1/x$V, 1 - x$Dt/x$V - x$D1/x$V)
  colnames(S) <- colnames(x$X)
  rownames(S) <- c("mainEffect", "interactions")
  write.csv(S,"SA_score_TP.csv")
}




