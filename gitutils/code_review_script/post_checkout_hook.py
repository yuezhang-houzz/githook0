#!/usr/bin/python
# Author:yue.zhang@houzz.com

import sys,os,os.path,threading,re,subprocess,constants
from utils_code_review import *

misc_Check = Misc_Check()
release_cut_off_check = Release_cut_off_check()
sys.dont_write_bytecode = True

if __name__ == '__main__':
    release_cut_off_check.release_cutoff_check("checkout")