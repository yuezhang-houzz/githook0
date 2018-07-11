#!/usr/bin/python
# Author:yue.zhang@houzz.com

import sys
from utils_code_review import *

code_review_check = Code_review_check()
misc_check = Misc_Check()
github = Github()
phabricator = Phabricator()
bypass = Bypass()
release_cut_off_check = Release_cut_off_check()
BYPASS = sys.argv[1] if len(sys.argv) > 1 else 0


if __name__ == '__main__':
	# No need for check review if repo is clean
	misc_check.repo_clean_check()

	# Check if release version is correct
	if constants.HAS_CUTOFF:
		release_cut_off_check.release_cutoff_check("push")

	# Force code review
	misc_check.branch_check()

	# Bypass code review check on master branch
	bypass.bypass_code_review(int(BYPASS))

	# Check if approved
	if constants.NEED_CODE_REVIEW:
		code_review_check.CR_check()