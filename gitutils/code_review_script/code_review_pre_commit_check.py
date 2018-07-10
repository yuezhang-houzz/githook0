#!/usr/bin/python
# Author:yue.zhang@houzz.com
# This script is triggered by pre-commit git hook. Goals are checking code syntax

import sys
from utils_code_review import *
syntax_check = Syntax_Check()
release_cut_off_check = Release_cut_off_check()

if __name__ == '__main__':
    # Code syntax check via hhvm lint for all branches
    if constants.HAS_SYNTAX_CHECK:
        syntax_check.syntax_check()

    # Check if release version is correct
    if constants.HAS_CUTOFF:
        release_cut_off_check.release_cutoff_check("commit")

    sys.exit(0)
