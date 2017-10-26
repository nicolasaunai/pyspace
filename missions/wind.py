import pandas as pds
import datetime
import numpy as np
import spacepy.pycdf as pycdf
import scipy.constants as constants

def loadMFIh0(filename, period=None, system = None): 
    
    # Get B and its rms
    #period : indicate sampling period default value is none for 1 min sampling put 1 for 1hour and 3 for 3 min
    #System : Coordinate system, default value is 'GSE'
    
    if system==None:
        coord = 'GSE'
    else :
        coord=system
    if period==None:
        period=""
    fcdf=pycdf.CDF(filename)
    Bname="B"+str(period)+coord
    BrmsName="B"+str(period)+"RMS"+coord
    time=fcdf['Epoch'][:]
    Bvec=fcdf[Bname][:]
    Bvec [np.where(Bvec < -1e30)[0]] = np.NaN  # remove creepy values
    Bmag=np.sqrt(Bvec[:,0]**2+Bvec[:,1]**2+Bvec[:,2]**2)
    Brmsvec=fcdf[BrmsName][:]
    Brmsvec [np.where(Brmsvec < -1e30)[0]] = np.NaN  # remove creepy values
    data = pds.DataFrame ({'Bx' : Bvec[:,0], 'By' : Bvec[:,1], 'Bz' : Bvec[:,2],'B' : Bmag, 'Bx_rms': Brmsvec[:,0],'By_rms': Brmsvec[:,1], 'Bz_rms': Brmsvec[:,2] }, index = time)
    return data

def loadSWEk0(filename, system = None):
    
    #Get V, Vth and Np
    #System : Coordinate system, default value is 'GSE' otherwise put 'GSM'
    
    if system==None:
        coord = 'GSE'
    else :
        coord=system

    fcdf=pycdf.CDF(filename)
    
    time=fcdf['Epoch'][:]
    
    V=fcdf["V_"+coord][:]
    V [np.where(V < -1e30)[0]] = np.NaN
    Vmag=np.sqrt(V[:,0]**2+V[:,1]**2+V[:,2]**2)
    
    Vth=fcdf['THERMAL_SPD'][:]
    Vth [np.where(Vth < -1e30)[0]] = np.NaN
    
    Np=fcdf['Np'][:]
    Np [np.where(Np < -1e30)[0]] = np.NaN
    
    data=pds.DataFrame({'Vx' : V[:,0], 'Vy' : V[:,1], 'Vz' : V[:,2], 'V' : Vmag, 'Np': Np, 'Vth' : Vth}, index=time)
    
    return data


def loadSWEh1(filename):
    
    #Get Na_nl and Np_nl (used for the Alpha proton ratio)

    fcdf=pycdf.CDF(filename)
    time = fcdf ["Epoch"][:]
    Np_nl  = fcdf ['Proton_Np_nonlin'][:]
    Na_nl  = fcdf ['Alpha_Na_nonlin'][:]
    Np_nl [np.where(Np_nl < -1e30)[0]] = np.NaN
    Na_nl [np.where(Na_nl < -1e30)[0]] = np.NaN
    Na_nl [np.where(Na_nl > 1e4)[0]] = np.NaN
    
    data= pds.DataFrame({'Np_nl' : Np_nl, 'Na_nl' : Na_nl}, index=time)
    return data

def load3DP(filename):
    
    #Get energy and flux
    
    fcdf=pycdf.CDF(filename)
    
    time = fcdf ["Epoch"][:]
    Energy = fcdf['ENERGY'][:]
    Flux   = fcdf['FLUX'][:]
    
    tdpColumnsE = []
    tdpColumnsF = []
    for i in np.arange (15):
        tdpColumnsE.append ("Range E " + str (i))
        tdpColumnsF.append ("Range F " + str (i))
        
    E = pds.DataFrame (Energy / 1000, index = time, columns = tdpColumnsE) # Conversion en keV au passage de l'énergie
    F = pds.DataFrame (Flux, index = time, columns = tdpColumnsF)
    
    data= E.join(F)
    return data