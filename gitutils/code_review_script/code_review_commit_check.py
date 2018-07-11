#!/usr/bin/python
# Author:yue.zhang@houzz.com
# This script is triggered by post-commit git hook. Goals are checking
# cherry-pick with '-x' and giving code review suggestion.
# wiki : https://cr.houzz.net/w/dev-introduction/workflow/

import sys,subprocess
from utils_code_review import *

sys.dont_write_bytecode = True
misc_check = Misc_Check()
github = Github()
phabricator = Phabricator()
bypass = Bypass()
code_review_check = Code_review_check()
BYPASS = sys.argv[1] if len(sys.argv) > 1 else 0



if __name__ == '__main__':
	# If otherthan master and Release, no need for code review check.
	misc_check.branch_check()

	#Bypass code review check
	if constants.NEED_CODE_REVIEW:
		bypass.bypass_code_review(int(BYPASS))

	# Check if cherry-pick with a '-x' option.
	if constants.HAS_CHERRYPICK_CHECK:
		misc_check.cherrypick_check()

	# C2thrift check, block cherry-pick if c2thrift definition changed
	if constants.IS_CHECK_THRIFT:
		code_review_check.c2thrift_CR_check_Release()


