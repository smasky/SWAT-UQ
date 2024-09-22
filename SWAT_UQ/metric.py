import numpy as np
from scipy.stats import pearsonr

def func_NSE_inverse(yTrue, ySim):
    yTrue=yTrue.ravel()
    ySim=ySim.ravel()
    ss_res = np.sum(np.square(yTrue - ySim))
    ss_tot = np.sum(np.square(yTrue - np.mean(yTrue)))
    r_squared = 1 - (ss_res / ss_tot)
    return -1*r_squared

def func_RMSE(yTrue, ySim):
    return np.sqrt(np.mean(np.square(yTrue-ySim)))

def func_PCC_inverse(yTrue, ySim):
    return -1*np.corrcoef(yTrue.ravel(), ySim.ravel())[0,1]

def func_Pbias(yTrue, ySim):
    return np.sum(np.abs(yTrue-ySim)/yTrue)*100

def func_KGE_inverse(yTrue, ySim):
    yTrue=yTrue.ravel()
    ySim=ySim.ravel()
    r, _ = pearsonr(yTrue, ySim)
    beta = np.std(ySim) / np.std(yTrue)
    gamma = np.mean(ySim) / np.mean(yTrue)
    kge = 1 - np.sqrt((r - 1)**2 + (beta - 1)**2 + (gamma - 1)**2)
    return -1*kge

OBJ_FUNC={1: func_NSE_inverse, 2: func_RMSE, 3: func_PCC_inverse, 4: func_Pbias, 5: func_KGE_inverse}