#!/Users/nicolasaunai/anaconda/bin/python
# encoding: utf-8


#import urllib2 as murl
import urllib
import os
import datetime as mdt
import spacepy.time as mspt
import spacepy.pycdf as pycdf
import pandas as pd
import numpy as np
import numpy.ma as ma
import spacepy.time as mspt




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

    urllib.request.urlretrieve(url, file_name.split('/')[-1])

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

    fn = scname+'_' + level + '_' +instrument+ '_' + date_s #+ '_v01.cdf'

    path = os.path.join(scname,level,instrument,str(date.year),fn)

    return path
#==========================================================





#-------------------------------------------------------------
class STATE(object):

    def __init__(self, filename, silent='yes'):

        versions = ['_v%02d.cdf' % v for v in [1,2,3,4,5,6,7] ]

        for v in versions:
            filename2 = filename+v
            try:
                self.filecdf = pycdf.CDF(filename2)
                break
            except:
                if (silent.lower() == 'no'):
                    print(v + ' does not exist')

        filename = filename2
        splitFilename = filename.split('/')[-1].split('_')
        self.sc = splitFilename[0]
        self.level = splitFilename[1]
        self.date = splitFilename[3]
        self.cdfVersion = splitFilename[4]



    def time(self):
        time = self.filecdf[self.sc + '_state_time'][:]
        time = mspt.Ticktock(time, 'UNX').getUTC()
        return time



    def position(self, coord, earth_radius=True):
        """
        @param coord: gsm or gse
        @param earth_radius: True, False. If true return the position
        normalized by the Earth radius (6480km)
        @return:
        """
        pos = self.filecdf[self.sc + '_pos_' + coord][:]
        time = self.time()
        if earth_radius is True:
            Rt = 6480.  # km
        else:
            Rt = 1.
        return pd.DataFrame({'X' + coord: pos[:, 0] / Rt,
                             'Y' + coord: pos[:, 1] / Rt,
                             'Z' + coord: pos[:, 2] / Rt},
                            index=time)




#-------------------------------------------------------------
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
    def __init__(self, filename, silent='yes'):
        versions = ['_v%02d.cdf' % v for v in [1, 2, 3, 4, 5, 6, 7]]

        for v in versions:
            filename2 = filename + v
            try:
                self.filecdf = pycdf.CDF(filename2)
                break
            except:
                if (silent.lower() == 'no'):
                    print(v + ' does not exist')


        filename = filename2
        splitFilename = filename.split('/')[-1].split('_')
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





class Moments(object):
    """
    mode = ['esa', 'mom']
    """

    def __init__(self, filename, mode='esa', silent='yes'):
        versions = ['_v%02d.cdf' % v for v in [1, 2, 3, 4, 5, 6, 7]]

        for v in versions:
            filename2 = filename + v
            try:
                self.filecdf = pycdf.CDF(filename2)
                break
            except:
                if (silent.lower() == 'no'):
                    print(v + ' does not exist')

        filename = filename2
        splitFilename = filename.split('/')[-1].split('_')
        self.sc = splitFilename[0]
        self.level = splitFilename[1]
        self.date = splitFilename[3]
        self.cdfVersion = splitFilename[4]
        if mode.lower() == 'esa':
            self.temperature_name = '_magt3'
        elif mode.lower() == 'mom':
            self.temperature_name = '_t3_mag'


    def time(self, resol, species):
        time = self.filecdf[self.sc + '_pe' + species + resol + '_time'][:]
        time = mspt.Ticktock(time, 'UNX').getUTC()
        return time


    def ion_time(self, resol):
        return self.time(resol, 'i')


    def electron_time(self, resol):
        return self.time(resol, 'e')


    def density(self, resol='r', species='i'):
        """
        resol = ['r' (reduced) , 'b' (burst), 'f' (full)]
        """
        n = self.filecdf[self.sc + '_pe' + species + resol + '_density'][:]
        time = self.time(resol, species)
        return pd.Series(data=n, index=time)


    def ion_density(self, resol='r'):
        """
        resol = ['r' (reduced) , 'b' (burst), 'f' (full)]
        """
        return self.density(resol=resol)


    def electron_density(self, resol='r'):
        """
        resol = ['r' (reduced) , 'b' (burst), 'f' (full)]
        """
        return self.density(resol=resol, species='e')

    def temperature(self, resol, species):
        T = self.filecdf[self.sc + '_pe' + species + resol + self.temperature_name][:]
        time = self.time(resol, species)
        return pd.DataFrame({'tpara': T[:, 2], 'tperp1': T[:, 1], 'tperp2': T[:, 0]}, index=time)


    def ion_temperature(self, resol):
        return self.temperature(resol, species='i')


    def electron_temperature(self, resol):
        return self.temperature(resol, species='e')


    def bulkVelocity(self, resol, species, coord):
        V = self.filecdf[self.sc + '_pe' + species + resol + '_velocity_' + coord][:]
        time = self.time(resol, species)
        name = 'V' + species + '_' + coord
        V2 = V[:, 0] ** 2 + V[:, 1] ** 2 + V[:, 2] ** 2
        return pd.DataFrame({name + '_x': V[:, 0],
                             name + '_y': V[:, 1],
                             name + '_z': V[:, 2],
                             name + '_mod': np.sqrt(V2)}, index=time)


    def ion_bulkVelocity(self, resol, coord):
        return self.bulkVelocity(resol, 'i', coord)


    def electron_bulkVelocity(self, resol, coord):
        return self.bulkVelocity(resol, 'e', coord)


    def quality(self, resol, species):
        mode = self.sc + "_pe" + species + resol + "_data_quality"
        q = self.filecdf[mode][:]
        time = self.time(resol, species)
        return pd.Series(q, index=time)





class Spectrogram(object):

    def __init__(self, filename, silent='yes'):
        versions = ['_v%02d.cdf' % v for v in [1, 2, 3, 4, 5, 6, 7]]

        for v in versions:
            filename2 = filename + v
            try:
                self.filecdf = pycdf.CDF(filename2)
                break
            except:
                if (silent.lower() == 'no'):
                    print(v + ' does not exist')

        filename = filename2
        splitFilename = filename.split('/')[-1].split('_')
        self.sc = splitFilename[0]
        self.level = splitFilename[1]
        self.date = splitFilename[3]
        self.cdfVersion = splitFilename[4]


    def spectrogram(self, species, resol):
        spectro = self.filecdf[self.sc + '_pe' + species + resol + '_en_eflux'][:]
        energy = self.filecdf[self.sc + '_pe' + species + resol + '_en_eflux_yaxis'][:]
        t = self.filecdf[self.sc + '_pe' + species + resol + '_time'][:]

        spectro = ma.masked_invalid(spectro)
        energy = ma.masked_invalid(energy)
        tt = np.ndarray((t.size, energy.shape[1]), dtype=np.object)
        for i in range(energy.shape[1]):
            tt[:, i] = mspt.Ticktock(t, 'UNX').getUTC()

        return spectro, energy, tt


    def ion_spectrogram(self, resol):
        return self.spectrogram('i', resol)


    def electron_spectrogram(self, resol):
        return self.spectrogram('e', resol)







def main():
#   themis_dl('thd','fgm','2008-06-25')
#   themis_dl('thd','esa','2008-06-25')
    themis_dl('thd','state','l1','2008-06-25')





if __name__ == '__main__':
    main()








