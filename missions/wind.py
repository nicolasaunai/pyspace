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