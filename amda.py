



# amda module


import numpy as np
import datetime as mdt




#==========================================================
#==========================================================
def gettimetable(file):
    """ return a list of time intervals as strings

   @param file : ex. 'ambda_tt.txt'

    @return: [('2008-06-28T18:57:00','2008-06-25T19:02:00'),]

    Exemple  :

    Creation : 2013-11-15 15:12:10.501079

    """

    with open(file, 'r') as f:
        lines       = f.readlines()
        dates       = [s.split() for s in lines]

    return dates


#==========================================================
