import os, configparser

config_dir=os.path.expanduser('~')+'/.pyspace/'
_config_file=config_dir+'/pyspace.ini'

if not os.path.exists(config_dir):
    os.mkdir(config_dir)
if not os.path.exists(_config_file):
    os.mknod(_config_file)

_config = configparser.ConfigParser()
_config.sections()
_config.read(_config_file)

def save_conf():
    global _config
    global _config_file
    configfile=open(_config_file, 'wt')
    _config.write(configfile)

def get_value(section,key):
    global _config
    if not _config.has_section(section):
        pyspace._config.add_section(section)
    return _config[section].get(key)

def set_value(section,key,value):
    global _config
    if not _config.has_section(section):
        pyspace._config.add_section(section)
    _config[section][key]=value
    save_conf()

def has_key(section,key):
    global _config
    if not _config.has_section(section):
        pyspace._config.add_section(section)
    _config[section][key]=value


