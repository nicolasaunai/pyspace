from datetime import datetime
from dateutil import parser
import os, sys,re
import time

class TimeTable(object):
    def __init__(self,file):
        self.__timetable=[]
        timetableFile=open(file)
        lines = timetableFile.readlines()
        pattern = re.compile(r'\s+')
        for line in lines:
            line=re.sub(pattern, ' ', line).split(" ")
            self.__timetable.append([parser.parse(line[0]),parser.parse(line[1])])

    def __getitem__(self,index):
        return  self.__timetable[index]

    def __setitem__(self, key, value):
        self.__timetable[key]=value
