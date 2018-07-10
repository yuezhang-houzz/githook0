#!/usr/bin/python
# Author:yue.zhang@houzz.com
# This script is triggered by pre-commit git hook.
# wiki : https://cr.houzz.net/w/dev-introduction/workflow/

import sys,subprocess
from utils_code_review import *

sys.dont_write_bytecode = True
misc_check = Misc_Check()
bypass = Bypass()

MSG_PATH = sys.argv[1] if len(sys.argv) > 1 else ''
BYPASS = sys.argv[2] if len(sys.argv) > 2 else 0

if __name__ == '__main__':

    # Bypass code review check
    bypass.bypass_code_review(int(BYPASS), MSG_PATH)

    # Check if lang file ids have been tampered with
    if constants.HAS_LANG_ID_CHECK:
        misc_check.lang_id_check()

