
rm(list = ls())

args = commandArgs(trailingOnly = TRUE)
path = args[1]
# path = 'G:\\SWAT\\t'

params <- file(paste(path,"\\paramsSum.txt",sep=""),open = "r")

p <- 0
X.labels= NULL
q.arg <- list()
while (TRUE) {
  line <- readLines(params, 1)
  if ( length(line) == 0 ) {
    break
  }
  p <- p+1
  cat(p,line,"\n")
  # read & create parameters
  seg <- unlist(strsplit(line, split = ":|,"))
  {
    # Watershed Delineation
    if(seg[1] == "UDEM"){
      X.labels = c(X.labels,paste(seg[4],"UDEM",sep = ''))
      UDEM = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(UDEM))
      
    }else if(seg[1] == "MinStream"){
      X.labels = c(X.labels,paste(seg[4],"MinStream",sep = ''))
      MinStream = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(MinStream))
      
    }
    # HRU Creation
    else if(seg[1] == "ULULC"){
      X.labels = c(X.labels,paste(seg[4],"ULULC",sep = ''))
      ULULC = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(ULULC))
      
    }else if(seg[1] == "USoil"){
      X.labels = c(X.labels,paste(seg[4],"USoil",sep = ''))
      USoil = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(USoil))
      
    }else if(seg[1] == "MinLU"){
      X.labels = c(X.labels,paste(seg[4],"MinLU",sep = ''))
      MinLU = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(MinLU))
      
    }else if(seg[1] == "MinSoil"){
      X.labels = c(X.labels,paste(seg[4],"MinSoil",sep = ''))
      MinSoil = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(MinSoil))
      
    }else if(seg[1] == "MinSlope"){
      X.labels = c(X.labels,paste(seg[4],"MinSlope",sep = ''))
      MinSlope = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(MinSlope))
      
    }else if(seg[1] == "IntSlope"){
      X.labels = c(X.labels,paste(seg[4],"IntSlope",sep = ''))
      IntSlope = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(IntSlope))
      
    }
    # SWAT Execution
    else if(seg[1] == "UPREC"){
      X.labels = c(X.labels,paste(seg[4],"UPREC",sep = ''))
      UPREC = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(UPREC))
      
    }
    # related to runoff
    else if(seg[1] == "CN2"){
      X.labels = c(X.labels,paste(seg[4],"CN2",sep = ''))
      CN2 = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(CN2))
      
    }else if(seg[1] == "ESCO"){
      X.labels = c(X.labels,paste(seg[4],"ESCO",sep = ''))
      ESCO = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(ESCO))
      
    }else if(seg[1] == "SLSUBBSN"){
      X.labels = c(X.labels,paste(seg[4],"SLSUBBSN",sep = ''))
      SLSUBBSN = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(SLSUBBSN))
      
    }else if(seg[1] == "OV_N"){
      X.labels = c(X.labels,paste(seg[4],"OV_N",sep = ''))
      OV_N = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(OV_N))
      
    }else if(seg[1] == "EPCO"){
      X.labels = c(X.labels,paste(seg[4],"EPCO",sep = ''))
      EPCO = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(EPCO))
      
    }else if(seg[1] == "CANMX"){
      X.labels = c(X.labels,paste(seg[4],"CANMX",sep = ''))
      CANMX = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(CANMX))
      
    }else if(seg[1] == "HRU_SLP"){
      X.labels = c(X.labels,paste(seg[4],"HRU_SLP",sep = ''))
      HRU_SLP = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(HRU_SLP))
      
    }else if(seg[1] == "SOL_Z"){
      X.labels = c(X.labels,paste(seg[4],"SOL_Z",sep = ''))
      SOL_Z = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(SOL_Z))
      
    }else if(seg[1] == "SOL_BD"){
      X.labels = c(X.labels,paste(seg[4],"SOL_BD",sep = ''))
      SOL_BD = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(SOL_BD))
      
    }else if(seg[1] == "SOL_AWC"){
      X.labels = c(X.labels,paste(seg[4],"SOL_AWC",sep = ''))
      SOL_AWC = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(SOL_AWC))
      
    }else if(seg[1] == "SOL_K"){
      X.labels = c(X.labels,paste(seg[4],"SOL_K",sep = ''))
      SOL_K = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(SOL_K))
      
    }else if(seg[1] == "SOL_ALB"){
      X.labels = c(X.labels,paste(seg[4],"SOL_ALB",sep = ''))
      SOL_ALB = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(SOL_ALB))
      
    }else if(seg[1] == "GW_REVAP"){
      X.labels = c(X.labels,paste(seg[4],"GW_REVAP",sep = ''))
      GW_REVAP = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(GW_REVAP))
      
    }else if(seg[1] == "GW_DELAY"){
      X.labels = c(X.labels,paste(seg[4],"GW_DELAY",sep = ''))
      GW_DELAY = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(GW_DELAY))
      
    }else if(seg[1] == "REVAPMN"){
      X.labels = c(X.labels,paste(seg[4],"REVAPMN",sep = ''))
      REVAPMN = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(REVAPMN))
      
    }else if(seg[1] == "GWQMN"){
      X.labels = c(X.labels,paste(seg[4],"GWQMN",sep = ''))
      GWQMN = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(GWQMN))
      
    }else if(seg[1] == "ALPHA_BF"){
      X.labels = c(X.labels,paste(seg[4],"ALPHA_BF",sep = ''))
      ALPHA_BF = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(ALPHA_BF))
      
    }else if(seg[1] == "RCHRG_DP"){
      X.labels = c(X.labels,paste(seg[4],"RCHRG_DP",sep = ''))
      RCHRG_DP = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(RCHRG_DP))
      
    }else if(seg[1] == "CH_K2"){
      X.labels = c(X.labels,paste(seg[4],"CH_K2",sep = ''))
      CH_K2 = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(CH_K2))
      
    }else if(seg[1] == "CH_N2"){
      X.labels = c(X.labels,paste(seg[4],"CH_N2",sep = ''))
      CH_N2 = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(CH_N2))
      
    }else if(seg[1] == "ALPHA_BNK"){
      X.labels = c(X.labels,paste(seg[4],"ALPHA_BNK",sep = ''))
      ALPHA_BNK = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(ALPHA_BNK))
      
    }else if(seg[1] == "SMFMX"){
      X.labels = c(X.labels,paste(seg[4],"SMFMX",sep = ''))
      SMFMX = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(SMFMX))
      
    }else if(seg[1] == "SMFMN"){
      X.labels = c(X.labels,paste(seg[4],"SMFMN",sep = ''))
      SMFMN = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(SMFMN))
      
    }else if(seg[1] == "SFTMP"){
      X.labels = c(X.labels,paste(seg[4],"SFTMP",sep = ''))
      SFTMP = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(SFTMP))
      
    }else if(seg[1] == "SMTMP"){
      X.labels = c(X.labels,paste(seg[4],"SMTMP",sep = ''))
      SMTMP = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(SMTMP))
      
    }else if(seg[1] == "TIMP"){
      X.labels = c(X.labels,paste(seg[4],"TIMP",sep = ''))
      TIMP = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(TIMP))
      
    }else if(seg[1] == "SURLAG"){
      X.labels = c(X.labels,paste(seg[4],"SURLAG",sep = ''))
      SURLAG = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(SURLAG))
      
    }else if(seg[1] == "TLAPS"){
      X.labels = c(X.labels,paste(seg[4],"TLAPS",sep = ''))
      TLAPS = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(TLAPS))
      
    }else if(seg[1] == "CH_K1"){
      X.labels = c(X.labels,paste(seg[4],"CH_K1",sep = ''))
      CH_K1 = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(CH_K1))
      
    }else if(seg[1] == "CH_N1"){
      X.labels = c(X.labels,paste(seg[4],"CH_N1",sep = ''))
      CH_N1 = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(CH_N1))
    }
    # related to sediment
    else if(seg[1] == "USLE_P"){
      X.labels = c(X.labels,paste(seg[4],"USLE_P",sep = ''))
      USLE_P = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(USLE_P))
      
    }else if(seg[1] == "SPCON"){
      X.labels = c(X.labels,paste(seg[4],"SPCON",sep = ''))
      SPCON = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(SPCON))
      
    }else if(seg[1] == "SPEXP"){
      X.labels = c(X.labels,paste(seg[4],"SPEXP",sep = ''))
      SPEXP = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(SPEXP))
      
    }else if(seg[1] == "CH_COV1"){
      X.labels = c(X.labels,paste(seg[4],"CH_COV1",sep = ''))
      CH_COV1 = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(CH_COV1))
      
    }else if(seg[1] == "CH_COV2"){
      X.labels = c(X.labels,paste(seg[4],"CH_COV2",sep = ''))
      CH_COV2 = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(CH_COV2))
      
    }
    # related to Nutrients
    else if(seg[1] == "RCN"){
      X.labels = c(X.labels,paste(seg[4],"RCN",sep = ''))
      RCN = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(RCN))
      
    }else if(seg[1] == "BIOMIX"){
      X.labels = c(X.labels,paste(seg[4],"BIOMIX",sep = ''))
      BIOMIX = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(BIOMIX))
      
    }else if(seg[1] == "NPERCO"){
      X.labels = c(X.labels,paste(seg[4],"NPERCO",sep = ''))
      NPERCO = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(NPERCO))
      
    }else if(seg[1] == "PPERCO"){
      X.labels = c(X.labels,paste(seg[4],"PPERCO",sep = ''))
      PPERCO = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(PPERCO))
      
    }else if(seg[1] == "PHOSKD"){
      X.labels = c(X.labels,paste(seg[4],"PHOSKD",sep = ''))
      PHOSKD = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(PHOSKD))
      
    }else if(seg[1] == "ERORGN"){
      X.labels = c(X.labels,paste(seg[4],"ERORGN",sep = ''))
      ERORGN = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(ERORGN))
      
    }else if(seg[1] == "ERORGP"){
      X.labels = c(X.labels,paste(seg[4],"ERORGP",sep = ''))
      ERORGP = list(min = as.numeric(seg[2]),max = as.numeric(seg[3]))
      q.arg = c(q.arg,list(ERORGP))
      
    }
  }
  
}
close(params)

# NEED TO GET from file

settings <- file(paste(path,"\\simSetting.txt",sep=""),open = "r")
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
    break
  }
}
close(settings)
M <- 4 
# n <- 66 #214 #Parameters selection for e-FAST (Saltelli, 1999, Technometrics)

q <- rep("qunif", p)

omega <- numeric(p)
omega[1] <- floor((n - 1)/(2 * M))
m <- floor(omega[1]/(2 * M))
if (m >= p - 1) {
  omega[-1] <- floor(seq(from = 1, to = m, length.out = p - 1))
}else {
  omega[-1] <- (0:(p - 2))%%m + 1
}

s <- 2 * pi/n * (0:(n - 1))
X <- as.data.frame(matrix(nrow = n * p, ncol = p))
colnames(X) <- X.labels
omega2 <- numeric(p)
for (i in 1:p) {
  omega2[i] <- omega[1]
  omega2[-i] <- omega[-1]
  l <- seq((i - 1) * n + 1, i * n)
  for (j in 1:p) {
    g <- 0.5 + 1/pi * asin(sin(omega2[j] * s))
    X[l, j] <- do.call(q[j], c(list(p = g), q.arg[[j]]))
  }
}


parameters <- X ##This is the defined parameter spaces
write.csv(X,paste(path,"\\params_sampling.csv",sep=""),row.names=F) 

