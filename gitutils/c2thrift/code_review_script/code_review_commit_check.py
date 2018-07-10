# !/usr/bin/python
# @owner yue.zhang@houzz.com

import sys
sys.path.append('../')
from gitUtils.code_review_script.utils_code_review import *

misc_check = Misc_Check()
bypass = Bypass()

BYPASS = sys.argv[1] if len(sys.argv) > 1 else 0
sys.dont_write_bytecode = True


if __name__ == '__main__':
	#CHECK if arc installed and path set properly.
	# utils.arc_installed_check()

	#Check if on master or Release branch
    misc_check.branch_check_c2thrift()

    #Bypass code review check
    bypass.bypass_code_review(int(BYPASS))

	#Check if thrift files was changed
    misc_check.thrift_files_check()



