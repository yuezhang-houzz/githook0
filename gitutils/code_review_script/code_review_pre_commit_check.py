#!/usr/bin/python
# Author:yue.zhang@houzz.com
# This script is triggered by pre-commit git hook. Goals are checking code
# syntax

import sys
import constants
from utils_code_review import SyntaxCheck
from utils_code_review import ReleaseCutoffCheck
from utils_code_review import MiscCheck
import utils_code_review as utils

syntax_check = SyntaxCheck()
release_cut_off_check = ReleaseCutoffCheck()
misc_check = MiscCheck()

if __name__ == '__main__':

    # show Tips & Trouble Shooting link
    utils.show_wiki_page("commit")

    # Code syntax check via hhvm lint for all branches
    syntax_check.syntax_check()

    # Check if release version is correct
    release_cut_off_check.release_cutoff_check("commit")

    # Check test owner
    if constants.HAS_TESTOWNER_CHECK:
        misc_check.test_owner_check()

    # Check if add credential in config
    if constants.IS_CHECK_CREDENCIAL:
        misc_check.credentials_check()

    if constants.IS_CHECK_C2THRIFT_POINTER:
        misc_check.check_submodule_backward("c2thrift")

    sys.exit(0)
