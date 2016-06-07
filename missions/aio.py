import os
import datetime as dtime
import urllib
import dateutil.parser
import spacepy.pycdf as pycdf
import pyspace.config as _cfg
import json as _json
import re as _re

_AIO_CSACOOKIE=_cfg.get_value("AIO","CSACOOKIE")
_products_list_file_name=_cfg.config_dir+"/aio_full_product_list.json"
_products_list=None

def set_csacookie(cookie):
    _cfg.set_value("AIO","CSACOOKIE",cookie)

def get_product(id,startdate,stopdate,format="CDF",force=False):
    global  _AIO_CSACOOKIE
    filename = "file_{id}_{startdate}-{stopdate}.tar".format(id=id,startdate=startdate,stopdate=stopdate)
    if not os.path.exists(filename) or force:
        if hasattr(startdate, 'strftime'):
            start=startdate.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            start=startdate
        if hasattr(stopdate, 'strftime'):
            stop=stopdate.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            stop=stopdate
        url = "https://csa.esac.esa.int/csa/aio/product-action?"
        dsid = "DATASET_ID={}&".format(id)
        sdate = "START_DATE={}&".format(start)
        edate = "END_DATE={}&".format(stop)
        deliv = "DELIVERY_INTERVAL=All&"
        delivForm = "DELIVERY_FORMAT={}&".format(format)
        NB  ="NON_BROWSER&"
        CSACOOKIE="CSACOOKIE={}".format(_AIO_CSACOOKIE)
        urltot = url+dsid+sdate+edate+NB+deliv+delivForm+NB+CSACOOKIE
        print(urltot)
        p = urllib.request.urlretrieve (urltot, filename)
        return filename

def _load_product_list():
    global _products_list_file_name
    global _products_list
    if not os.path.exists(_products_list_file_name):
        url="https://csa.esac.esa.int/csa/aio/metadata-action?PAGE_SIZE=10000&PAGE=1&SELECTED_FIELDS=MISSION.NAME,INSTRUMENT.NAME,DATASET.DATASET_ID,DATASET.START_DATE,DATASET.END_DATE,DATASET.TITLE&RESOURCE_CLASS=DATASET&EXPERIMENT.NAME=%&RETURN_TYPE=JSON"
        p = urllib.request.urlretrieve (url, _products_list_file_name)
    _products_list=_json.load(open(_products_list_file_name))['data']


def get_product_list():
    if _products_list==None:
        _load_product_list()
    return _products_list

def search_dataset(name):
    try: 
        prog = _re.compile(name) 
    except: 
        raise TypeError("name should be a string")
    if _products_list==None:
        _load_product_list()
    return [element for element in _products_list if prog.search(element['DATASET.DATASET_ID'])!=None]
