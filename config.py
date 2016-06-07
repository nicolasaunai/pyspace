import os, configparser

config_dir=os.path.expanduser('~')+'/.pyspace/'
__config_file=config_dir+'/pyspace.ini'

if not os.path.exists(config_dir):
    os.mkdir(config_dir)
if not os.path.exists(__config_file):
    os.mknod(__config_file)

__config__ = configparser.ConfigParser()
__config__.sections()
__config__.read(__config_file)

def save_conf():
    global __config__
    global __config_file
    configfile=open(__config_file, 'wt')
    __config__.write(configfile)

def get_value(section,key):
    global __config__
    if not __config__.has_section(section):
        pyspace.__config__.add_section(section)
    return __config__[section].get(key)

def set_value(section,key,value):
    global __config__
    if not __config__.has_section(section):
        pyspace.__config__.add_section(section)
    __config__[section][key]=value
    save_conf()

def has_key(section,key):
    global __config__
    if not __config__.has_section(section):
        pyspace.__config__.add_section(section)
    __config__[section][key]=value


