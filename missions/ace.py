import pandas as pds
import datetime
import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as colors
import spacepy.pycdf as pycdf
import scipy.constants as constants

def loadMFI(filename, system = None):
    
    #System : Coordinate system, default value is 'GSE'
    
    if system==None:
        coord = 'GSEc'
    else :
        coord=system
        
    fcdf=pycdf.CDF(filename)
    
    time=fcdf['Epoch'][:]
    Bvec=fcdf["B"+coord][:]
    Bvec [np.where(Bvec < -1e30)[0]] = np.NaN
    
    data = pds.DataFrame ({'Bx' : Bvec[:,0], 'By' : Bvec[:,1], 'Bz' : Bvec[:,2], 'Bmag' : np.sqrt(Bvec[:,0]**2+Bvec[:,1]**2+Bvec[:,2]**2)}, index = time)
    return data

def loadSWEh0(filename, system = None):
    
        #Get V, Np and alpha proton ratio
        #System : Coordinate system, default value is 'GSE' optional values : 'GSM', 'RTN'
    
    if system==None:
        coord = 'GSE'
    else :
        coord=system
        
        
    fcdf=pycdf.CDF(filename)
    time=fcdf['Epoch'][:]
    V=fcdf["V_"+coord][:]
    Np  = fcdf ['Np'][:]
    C=fcdf['alpha_ratio'][:]
    
    Np [np.where(Np < -1e30)[0]] = np.NaN
    C [np.where(C < -1e30)[0]] = np.NaN
    V [np.where(V < -1e30)[0]] = np.NaN
    
    Vmag=np.sqrt(V[:,0]**2+V[:,1]**2+V[:,2]**2)
    
    data=pds.DataFrame({'Vx' : V[:,0], 'Vy' : V[:,1], 'Vz' : V[:,2], 'V' : Vmag, 'Np': Np, 'alpha_ratio' : C}, index=time)
    return data

def loadSWIh6(filename):
    #get Vth
    
    fcdf=pycdf.CDF(filename)
    time = fcdf ["Epoch"][:]
    Vth = fcdf ["vthH"][:]
    
    
    Vth [np.where(Vth < -1e30)[0]] = np.NaN
    
    data=pds.DataFrame({'Vth' : Vth}, index=time)
    return data