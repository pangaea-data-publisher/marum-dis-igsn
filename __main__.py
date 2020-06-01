#!/usr/bin/env python3

import configparser as ConfigParser
import os
from logging.config import fileConfig
from translate import Translate


def main():
    XML_DIR = config['SYSTEM']['xml_dir']
    HTML_DIR = config['SYSTEM']['html_dir']
    translateObj = Translate(XML_DIR, HTML_DIR)
    translateObj.parseXMLs()
    translateObj.generate_sitemap()

if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    my_path = os.path.abspath(os.path.dirname(__file__))
    ini_path = os.path.join(my_path, 'config', 'igsn.ini')
    config.read(ini_path)
    log_config_path = os.path.join(my_path, 'config', 'logging.ini')
    log_directory = os.path.join(my_path, 'logs')
    log_file_path = os.path.join(log_directory, 'igsn.log')

    if not os.path.exists(log_directory):
        os.makedirs(log_directory, exist_ok=True)
    fileConfig(log_config_path, defaults={'logfilename': log_file_path.replace("\\", "/")})
    #logger = logging.getLogger()  # use this form to initialize the root logger
    main()
