#!/usr/bin/python
# Author:yue.zhang@houzz.com

import sys
sys.path.append('../')
from gitUtils.code_review_script.utils_code_review import *

code_review_check = Code_review_check()
misc_check = Misc_Check()
bypass = Bypass()
BYPASS = sys.argv[1] if len(sys.argv) > 1 else 0


if __name__ == '__main__':
	#Bypass code review check
	bypass.bypass_code_review(int(BYPASS))
	
	#Check if on master or Release branch
	misc_check.branch_check_c2thrift()

	#Code_rview check
	code_review_check.c2thrift_CR_check()





