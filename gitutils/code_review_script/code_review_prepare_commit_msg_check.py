#!/usr/bin/python
# Author:yue.zhang@houzz.com
# wiki : https://cr.houzz.net/w/dev-introduction/workflow/

import sys
from utils_code_review import MiscCheck, ReleaseCutoffCheck
misc_Check = MiscCheck()
release_cut_off_check = ReleaseCutoffCheck()
commit_type = sys.argv[1] if len(sys.argv) > 1 else 0

if __name__ == '__main__':
    release_cut_off_check.release_cutoff_check(commit_type)
