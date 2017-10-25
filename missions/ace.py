import pandas as pds
import datetime
import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as colors
import spacepy.pycdf as pycdf
import scipy.constants as constants

class AceData:
# Use this class to create a dataframe of Ace data between startTime and endTime 
    def __init__ (self, startTime, endTime):
        self.quiet= False
        self.dateRange=[d for d in pds.date_range (startTime, endTime)]
        self.startTime=startTime
        self.endTime=endTime
        
    def makeFilename(self, instrument): # make the lists of filenames for each instrument data
        [instr, method]=instrument.split("_")
        filenames=[]
        for day in self.dateRange:
            tmpfile= "data/ace/" +instrument+ "/%d/ac_" % (day.year)+ method+"_"+instr+"_%d%02d%02d_v" % (day.year, day.month, day.day)
            try:
                tmpfile=glob.glob (tmpfile+ "*.cdf") [-1]
                filenames.append(tmpfile)
            except IndexError:
                print ("No "+instrument+" file at date " + str (day))    
        return filenames
    
    def loadMFI(self, instrument): #Load MFI files and create the appropriate characteristics (B)
        filenames= self.makeFilename(instrument)
        mfiTimeArray = np.empty (0, dtype = datetime.datetime)
        Bx           = np.empty (0)
        By           = np.empty (0)
        Bz           = np.empty (0)
        for files in filenames:
            mfiCDF=(pycdf.CDF(files))
            mfiTime = mfiCDF ['Epoch'][:]
            #mfiTime = np.asarray ([t[0] for t in mfiTime])
            mfiTimeArray = np.concatenate ((mfiTimeArray, mfiTime))
            BGSE = mfiCDF ['BGSEc'][:]
            Bx = np.concatenate ((Bx, BGSE[:,0]))
            By = np.concatenate ((By, BGSE[:,1]))
            Bz = np.concatenate ((Bz, BGSE[:,2]))
        Bx [np.where(Bx < -1e30)[0]] = np.NaN  # remove creepy values
        By [np.where(By < -1e30)[0]] = np.NaN
        Bz [np.where(Bz < -1e30)[0]] = np.NaN
        self.B = pds.DataFrame ({'Bx' : Bx, 'By' : By, 'Bz' : Bz}, index = mfiTimeArray)
        
    def loadSWEh0(self,instrument): #Get V, Np and alpha ratio
        filenames= self.makeFilename(instrument)
        sweh0TimeArray = np.empty (0, dtype = datetime.datetime)
        Vx           = np.empty (0)
        Vy           = np.empty (0)
        Vz           = np.empty (0)
        Np           = np.empty (0)
        C            = np.empty (0)
        for files in filenames:
            sweh0CDF=(pycdf.CDF(files))
            sweh0TimeArray = np.concatenate ((sweh0TimeArray, sweh0CDF ["Epoch"][:]))
            VGSE = sweh0CDF ["V_GSE"][:]
            Vx = np.concatenate ((Vx, VGSE[:,0]))
            Vy = np.concatenate ( (Vy, VGSE[:,1]))        
            Vz = np.concatenate ( (Vz, VGSE[:,2]))
            Np  = np.concatenate ((Np, sweh0CDF ['Np'][:]))
            C=np.concatenate((C,sweh0CDF['alpha_ratio'][:]))
        Vx [np.where(Vx < -1e30)[0]] = np.NaN
        Vy [np.where(Vy < -1e30)[0]] = np.NaN
        Vz [np.where(Vz < -1e30)[0]] = np.NaN
        Np [np.where(Np < -1e30)[0]] = np.NaN
        C  [np.where(C < -1e30)[0]] = np.NaN
        self.V = pds.DataFrame ({'Vx' : Vx, 'Vy' : Vy, 'Vz' : Vz}, index = sweh0TimeArray)
        self.Np = pds.Series (Np, name = 'Np', index = sweh0TimeArray)
        self.C=pds.Series(Np,name='Alpha ratio', index=sweh0TimeArray)
        
    def loadSWI(self,instrument): #Get Vth
        filenames= self.makeFilename(instrument)
        swih6TimeArray = np.empty (0, dtype = datetime.datetime)
        Vth          = np.empty (0)
        for files in filenames:
            swiCDF=(pycdf.CDF(files))
            swih6TimeArray = np.concatenate ((swih6TimeArray, swiCDF ["Epoch"][:]))
            Vth = np.concatenate ((Vth, swiCDF ["vthH"][:]))
        Vth [np.where(Vth < -1e30)[0]] = np.NaN
        self.Vth = pds.Series (Vth, name = 'Vth', index = swih6TimeArray)
        
        
        ## Additional instruments might be added  particularly particle ratio and fluxes
        
        
    def interpolate(self): # put features on the same timescale ( work only for MFI,SWEh1 and SWEk0 for the moment)
        tmpV = pds.concat ([self.V, pds.DataFrame (columns = self.V.axes [1].values, index = self.B.index)])
        tmpV = tmpV.groupby (tmpV.index).first ().sort_index ().interpolate (method = "time")
        tmpDict = {}
        for elt in self.V.axes [1].values:
            tmpDict [elt] = tmpV [elt][self.B.index]
        self.V = pds.DataFrame (tmpDict, index = self.B.index)

        tmpVth = pds.concat ([self.Vth, pds.Series (index = self.B.index)])
        tmpNp = pds.concat ([self.Np, pds.Series (index = self.B.index)])              
        self.Vth = tmpVth.groupby (tmpVth.index).first ().sort_index ().interpolate (method = "time") [self.B.index]
        self.Vth.name = "Vth"
        self.Np = tmpNp.groupby (tmpNp.index).first ().sort_index ().interpolate (method = "time") [self.B.index]
        self.Np.name = "Np"
                
                # Interpolation de C
        tmpC = pds.concat ([self.C, pds.Series (index = self.B.index)])
        self.C = tmpC.groupby (tmpC.index).first ().sort_index ().interpolate (method = "time") [self.B.index]
        self.C.name = "C"
                #Interpolation de B
        self.B = self.B.interpolate (method = "time")
        
    def computeExtraFeatures(self): #Add extraFeatures such as |b|, P, beta, B rotation. Additional features might be added here ( RMSBob, Particle ratio, DST)
        self.B['B2'] = self.B['Bx']**2 + self.B['By']**2 + self.B['Bz']**2
        self.V['V2'] = self.V['Vx']**2 + self.V['Vy']**2 + self.V['Vz']**2
        self.B['B'] = pds.Series (np.sqrt (self.B['B2']), index = self.B.index, name = "B")
        self.V['V'] = pds.Series (np.sqrt (self.V['V2']), index = self.V.index, name = "V")
        self.B['Btheta']    = np.arctan2 (np.sqrt(self.B['Bx']**2 + self.B['By']**2), self.B['Bz']) * 180 / np.pi
        self.B['Bphi']      = (np.arctan2 (self.B['By'], self.B['Bx']) + np.pi) * 180 / np.pi
        
        # Set angle value between 0 and 360
        i = 1
        while i < self.B.index.size:
            if self.B['Bphi'][i] - self.B['Bphi'][i - 1] > 300:
                self.B['Bphi'][i] = self.B['Bphi'][i] - 360
            elif self.B['Bphi'] [i] - self.B['Bphi'][i - 1] < -300:
                self.B['Bphi'][i] = self.B['Bphi'][i] + 360
            if self.B['Btheta'][i] - self.B['Btheta'][i - 1] > 300:
                self.B['Btheta'][i] = self.B['Btheta'][i] - 360
            elif self.B['Btheta'] [i] - self.B['Btheta'][i - 1] < -300:
                self.B['Btheta'][i] = self.B['Btheta'][i] + 360
            i += 1
            
        self.P = pds.Series ((1e3)**2 * self.Vth * self.Vth * 0.5 * constants.m_p * self.Np * 1e6 , index = self.Vth.index, name = "P")
        self.Beta = pds.Series (2 * self.P * constants.mu_0 / ( (1e-9)**2 * self.B['B2']), name = "Beta")
        