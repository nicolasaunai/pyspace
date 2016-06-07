from datetime import datetime
from dateutil import parser
import os, sys,re
import time

class TimeTable(object):
    def __init__(self,file):
        self._timetable=[]
        pattern = re.compile(r'\s+')
        with open(file,'r') as f:
            for line in f:
                line=re.sub(pattern, ' ', line).split(" ")
                self._timetable.append([parser.parse(line[0]),parser.parse(line[1])])

    def __getitem__(self,index):
        return  self._timetable[index]

    def __setitem__(self, key, value):
        self._timetable[key]=value
