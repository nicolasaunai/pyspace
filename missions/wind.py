import pandas as pds
import datetime
import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as colors
import spacepy.pycdf as pycdf
import scipy.constants as constants

class WindData:
# Use this class to create a dataframe of Wind data between startTime and endTime and for a required list of instruments (array of strings)
    def __init__ (self, startTime, endTime, instruments):
        self.quiet= False
        self.numinstr=len(instruments)
        self.dateRange=[d for d in pds.date_range (startTime, endTime)]
        self.complete=instruments
        self.instruments=[i[0] for i in [i.split("_") for i in instruments]]
        self.instrMethod=[i[1] for i in [i.split("_") for i in instruments]]
        self.startTime=startTime
        self.endTime=endTime
        
    def makeFilename(self, instrument): # Create a list of filename for the considered time interval and for a specified instrument
        [instr, method]=instrument.split("_")
        filename=[]
        for day in self.dateRange:
            tmpfile= "data/wind/" +instr+"/"+instrument+ "/%d/wi_" % (day.year)+ method+"_"+instr+"_%d%02d%02d_v" % (day.year, day.month, day.day)
            filename.append(tmpfile)
        return filename