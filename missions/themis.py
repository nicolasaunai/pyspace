#!/Users/nicolasaunai/anaconda/bin/python
# encoding: utf-8


import urllib2 as murl
import os
import datetime as mdt
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
        print 'file already exist in the directory'
        return None


    print 'Downloading %s' % url

    u = murl.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])

    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
#
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()
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








def main():
#   themis_dl('thd','fgm','2008-06-25')
#   themis_dl('thd','esa','2008-06-25')
    themis_dl('thd','state','l1','2008-06-25')





if __name__ == '__main__':
    main()








