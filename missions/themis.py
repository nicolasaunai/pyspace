#!/Users/nicolasaunai/anaconda/bin/python
# encoding: utf-8


import urllib2 as murl
import urllib
import os
import datetime as mdt
import spacepy.time as mspt
import spacepy.pycdf as pycdf
import pandas as pd
import numpy as np



#==========================================================
#==========================================================
def themis_dl(sc, instrument, l,date,dest_dir=None):
    """download the data from themis website

    @param sc 'th[a,b,c,d]'
    @param instrument : 'fgm', etc.
    @param date '2008-06-25'

    Creation : 2013-11-06 20:48:23.410828

    """

    url = 'http://themis.ssl.berkeley.edu/data/themis/'
    year,month,day = date.split('-')
    fn = filename(sc, l, instrument, mdt.datetime(int(year),int(month),int(day)))

    url = os.path.join(url,sc,l,instrument,year,sc+'_'+l+'_'+instrument+'_'+year+month+day+'_v01.cdf')

    file_name = fn #url.split('/')[-1]

    if os.path.isfile(file_name):
        print('file already exist in the directory')
        return None


    print("Downloading {}".format(url))

    urllib.urlretrieve(url, file_name.split('/')[-1])

#==========================================================






#==========================================================
#==========================================================
def filename(scname, level, instrument, date):
    """returns a themis cdf file name

    @param scname : name of the spacecraft
    @param level  : 'l0', 'l1' or 'l2'
    @instrument   : ex. 'fgm' or 'esa'
    @param date   : datetime object

    @return: a themis cdf filename

    Exemple  : themis.filename(scname, 'l2', 'fgm', self._dates[0])

    Creation : 2013-11-14 12:24:35.659824

    """
    date_s = mdt.datetime.strftime(date,'%Y%m%d') # converts to string

    # now create the filename
    # an example : thd_l1_state_20080625_v01.cdf

    fn = scname+'_' + level + '_' +instrument+ '_' + date_s + '_v01.cdf'

    path = os.path.join(scname,level,instrument,str(date.year),fn)

    return path
#==========================================================





class FGM(object):
    """
    Fluxgate Magnetometer (FGM) data:
    The Level 2 file includes FGE (engineering) magnetic field,
    FGH (high-resolution) magnetic field,
    FGL (low-resolution) magnetic field,
    and FGS (spin-resolution) magnetic field.
    The FGH, FGL, and FGE data are given in Spinning Spacecraft (SSL),
    Despun Spacecraft (DSL), Geocentric Solar Ecliptic (GSE) and Geocentric Solar Magnetospheric (GSM) coordinates.
    The FGS data is given in DSL, GSE, and GSM coordinates. Units are nanotesla.
    """
    def __init__(self, filename):
        try:
            self.filecdf = pycdf.CDF(filename)
        except:
            print(filename + ' does not exist')


        splitFilename = filename.split('_')
        self.sc = splitFilename[0]
        self.level = splitFilename[1]
        self.date = splitFilename[3]
        self.cdfVersion = splitFilename[4]



    def time(self, resol, coord):
        time = self.filecdf[self.sc + '_' + resol + '_time'][:]
        time = mspt.Ticktock(time, 'UNX').getUTC()
        return time



    def magnetic(self, resol, coord):
        """
        @param resol: 'fgs' (spin), 'fge' (engineering), 'fgh' (high resolution), 'fgl' (low resolution)
        @param coord: 'dsl', 'gse', 'gsm', 'ssl'
        @return:
        """
        if resol.lower() == 'fgs' and coord.lower() == 'ssl':
            raise NameError('fgs resolution has no ssl coordinate')


        B = self.filecdf[self.sc + '_' + resol + '_' + coord][:, :]
        time = self.time(resol, coord)
        B2 = B[:, 0] ** 2 + B[:, 1] ** 2 + B[:, 2] ** 2
        return pd.DataFrame({'Bx_' + coord: B[:, 0],
                             'By_' + coord: B[:, 1],
                             'Bz_' + coord: B[:, 2],
                             'B_' + coord: np.sqrt(B2)},
                            index=time)




def main():
#   themis_dl('thd','fgm','2008-06-25')
#   themis_dl('thd','esa','2008-06-25')
    themis_dl('thd','state','l1','2008-06-25')





if __name__ == '__main__':
    main()








