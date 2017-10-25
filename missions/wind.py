class WindData:
# Use this class to create a dataframe of Wind data between startTime and endTime and for a required list of instruments (array of strings)
    def __init__ (self, startTime, endTime):
        self.quiet= False
        self.dateRange=[d for d in pds.date_range (startTime, endTime)]
        self.startTime=startTime
        self.endTime=endTime
        
    def makeFilename(self, instrument): # make the lists of filenames for each instrument data
        [instr, method]=instrument.split("_")
        filenames=[]
        for day in self.dateRange:
            tmpfile= "data/wind/" +instr+"/"+instrument+ "/%d/wi_" % (day.year)+ method+"_"+instr+"_%d%02d%02d_v" % (day.year, day.month, day.day)
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
            mfiTime = np.asarray ([t[0] for t in mfiTime])
            mfiTimeArray = np.concatenate ((mfiTimeArray, mfiTime))
            BGSE = mfiCDF ['BGSE'][:]
            Bx = np.concatenate ((Bx, BGSE[:,0]))
            By = np.concatenate ((By, BGSE[:,1]))
            Bz = np.concatenate ((Bz, BGSE[:,2]))
            Bx [np.where(Bx < -1e30)[0]] = np.NaN  # remove creepy values
            By [np.where(By < -1e30)[0]] = np.NaN
            Bz [np.where(Bz < -1e30)[0]] = np.NaN
        self.B = pds.DataFrame ({'Bx' : Bx, 'By' : By, 'Bz' : Bz}, index = mfiTimeArray)
    
    def loadSWEk0(self,instrument): #Get V, Vth and Np
        filenames= self.makeFilename(instrument)
        swek0TimeArray = np.empty (0, dtype = datetime.datetime)
        Vx           = np.empty (0)
        Vy           = np.empty (0)
        Vz           = np.empty (0)
        Vth          = np.empty (0)
        Np           = np.empty (0)
        for files in filenames:
            swek0CDF=(pycdf.CDF(files))
            swek0TimeArray = np.concatenate ((swek0TimeArray, swek0CDF ["Epoch"][:]))
            VGSE = swek0CDF ["V_GSE"][:]
            Vx = np.concatenate ((Vx, VGSE[:,0]))
            Vy = np.concatenate ( (Vy, VGSE[:,1]))        
            Vz = np.concatenate ( (Vz, VGSE[:,2]))
            Vth = np.concatenate ((Vth, swek0CDF ["THERMAL_SPD"][:]))        
            Np  = np.concatenate ((Np, swek0CDF ['Np'][:]))
        Vx [np.where(Vx < -1e30)[0]] = np.NaN
        Vy [np.where(Vy < -1e30)[0]] = np.NaN
        Vz [np.where(Vz < -1e30)[0]] = np.NaN
        Np [np.where(Np < -1e30)[0]] = np.NaN
        Vth [np.where(Vth < -1e30)[0]] = np.NaN
        self.V = pds.DataFrame ({'Vx' : Vx, 'Vy' : Vy, 'Vz' : Vz}, index = swek0TimeArray)
        self.Np = pds.Series (Np, name = 'Np', index = swek0TimeArray)
        self.Vth = pds.Series (Vth, name = 'Vth', index = swek0TimeArray)
        
    def loadSWEh1(self,instrument): #Get V, Vth and Np
        filenames= self.makeFilename(instrument)
        sweh1TimeArray = np.empty (0, dtype = datetime.datetime)
        Np_nl           = np.empty (0)
        Na_nl           = np.empty (0)
        for files in filenames:
            sweh1CDF=(pycdf.CDF(files))
            sweh1TimeArray = np.concatenate ((sweh1TimeArray, sweh1CDF ["Epoch"][:]))       
            Np_nl  = np.concatenate ((Np_nl, sweh1CDF ['Proton_Np_nonlin'][:]))
            Na_nl  = np.concatenate ((Na_nl, sweh1CDF ['Alpha_Na_nonlin'][:]))
        Np_nl [np.where(Np_nl < -1e30)[0]] = np.NaN
        Na_nl [np.where(Na_nl < -1e30)[0]] = np.NaN
        Na_nl [np.where(Na_nl > 1e4)[0]] = np.NaN
        self.Np_nl = pds.Series (Np_nl, name = 'Np_nl', index = sweh1TimeArray)
        self.Na_nl = pds.Series (Na_nl, name = 'Na_nl', index = sweh1TimeArray)
        
    def load3dp(self,instrument): #Energy and electron flux
        filenames= self.makeFilename(instrument)
        tdpTimeArray = np.empty (0, dtype = datetime.datetime)
        Energy       = np.empty ((0,15))
        Flux         = np.empty ((0,15))
        for files in filenames:
            tdpCDF = pycdf.CDF(files)
            tdpTimeArray = np.concatenate ((tdpTimeArray, tdpCDF ["Epoch"][:]))
            Energy = np.concatenate ((Energy, tdpCDF['ENERGY'][:]))
            Flux   = np.concatenate ((Flux, tdpCDF['FLUX'][:]))
        tdpColumnsE = []
        tdpColumnsF = []
        for i in np.arange (15):
            tdpColumnsE.append ("Range E " + str (i))
            tdpColumnsF.append ("Range F " + str (i))
        self.E = pds.DataFrame (Energy / 1000, index = tdpTimeArray, columns = tdpColumnsE) # Conversion en keV au passage de l'énergie
        self.F = pds.DataFrame (Flux, index = tdpTimeArray, columns = tdpColumnsF)
        self.E = self.E.reset_index().drop_duplicates (subset='index').set_index('index')
        self.F = self.F.reset_index().drop_duplicates (subset='index').set_index('index')
        
        
## Additional instruments might be added 

    def interpolate(self): # put features on the same timescale ( work only for MFI,SWEh1 and SWEk0 for the moment)
        tmpV = pds.concat ([self.V, pds.DataFrame (columns = self.V.axes [1].values, index = self.B.index)])
        tmpV = tmpV.groupby (tmpV.index).first ().sort_index ().interpolate (method = "time")
        tmpDict = {}
        for elt in self.V.axes [1].values:
            tmpDict [elt] = tmpV [elt][self.B.index]
        self.V = pds.DataFrame (tmpDict, index = self.B.index)
                
                # Interpolation des series P, Vth et Np
        tmpVth = pds.concat ([self.Vth, pds.Series (index = self.B.index)])
        tmpNp = pds.concat ([self.Np, pds.Series (index = self.B.index)])              
        self.Vth = tmpVth.groupby (tmpVth.index).first ().sort_index ().interpolate (method = "time") [self.B.index]
        self.Vth.name = "Vth"
        self.Np = tmpNp.groupby (tmpNp.index).first ().sort_index ().interpolate (method = "time") [self.B.index]
        self.Np.name = "Np"
                
                # Interpolation des séries Np_nl et Na_nl
        tmpNp_nl = pds.concat ([self.Np_nl, pds.Series (index = self.B.index)])
        tmpNa_nl = pds.concat ([self.Na_nl, pds.Series (index = self.B.index)])
        self.Np_nl = tmpNp_nl.groupby (tmpNp_nl.index).first ().sort_index ().interpolate (method = "time") [self.B.index]
        self.Np_nl.name = "Np_nl"
        self.Na_nl = tmpNa_nl.groupby (tmpNa_nl.index).first ().sort_index ().interpolate (method = "time") [self.B.index]
        self.Na_nl.name = "Na_nl"
                #Interpolation de B
        self.B = self.B.interpolate (method = "time")
        
    def computeExtraFeatures(self): #Add extraFeatures such as |b|, P, beta, B rotation. Additional features might be added here ( RMSBob, Particle ratio, DST)
        self.B['B2'] = self.B['Bx']**2 + self.B['By']**2 + self.B['Bz']**2
        self.V['V2'] = self.V['Vx']**2 + self.V['Vy']**2 + self.V['Vz']**2
        self.B['B'] = pds.Series (np.sqrt (self.B['B2']), index = self.B.index, name = "B")
        self.V['V'] = pds.Series (np.sqrt (self.V['V2']), index = self.V.index, name = "V")
        self.C = pds.Series (self.Na_nl / self.Np_nl, name = "C")
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
        tmpP = pds.concat ([self.P, pds.Series (index = self.B.index)])
        PonBIndex = tmpP.groupby (tmpP.index).first ().sort_index ().interpolate (method = "time") [self.B.index]
        self.P = PonBIndex
        self.P.name = "P"
        self.Beta = pds.Series (2 * PonBIndex * constants.mu_0 / ( (1e-9)**2 * self.B['B2']), name = "Beta")