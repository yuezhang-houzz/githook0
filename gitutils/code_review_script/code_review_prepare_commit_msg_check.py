#!/usr/bin/python
# Author:yue.zhang@houzz.com
# wiki : https://cr.houzz.net/w/dev-introduction/workflow/

import subprocess
from utils_code_review import *
misc_Check = Misc_Check()
release_cut_off_check = Release_cut_off_check()
commit_type = sys.argv[1] if len(sys.argv) > 1 else 0

if __name__ == '__main__':
    if constants.HAS_CUTOFF:
        release_cut_off_check.release_cutoff_check(commit_type)
