#!/usr/bin/python
# Author:yue.zhang@houzz.com

# Configuration for code review
MAX_LINES           = 0 # lines changed limit for code review
IS_CHECK_THRIFT     = False
IS_NEED_DWREVIEW    = False
NEED_CODE_REVIEW	= False
HAS_CUTOFF          = True
HAS_SYNTAX_CHECK    = True
HAS_LANG_ID_CHECK   = False
RELEASE_BRANCH 		= "newRelease"

# Constants for git hooks
REPO_NAME           = "C2"
THRIFT_EXT          = ".thrift"
PHP_EXT             = ".php"
JS_EXT              = ".js"
GOOD_STATUS = ["Accepted","Closed"]
CODE_REVIEW_STATUS = {}
CODE_REVIEW_STATUS[1] = "Congratulations! You've passed code review check!"
CODE_REVIEW_STATUS[2] = "Please request a code review,reviewers should be one of:"
CODE_REVIEW_STATUS[3] = "Your code review is not approved,please get approval by:"

BYPASS_IMPRINT = {}
BYPASS_IMPRINT[1] = "{bypass=1}"
BYPASS_IMPRINT[2] = "{bypass=2}"
BYPASS_IMPRINT[3] = "{bypass=3}"
BYPASS_IMPRINT[4] = "{bypass=4}"


# Alert content
NO_OWNER_ALERT = """
===========================================================================
Alert: You are not allowed to commit because we detected that you edited 
thrift files without owners.

Please add owners at the top of file and the standard format should be:
// @owner ownername1@houzz.com ownername1@houzz.com
===========================================================================
"""

PRE_PUSH_ALERT="""
===========================================================================
:( There are no reviewers for this change.
Code can only be pushed if it's been reviewed by at least 1 person besides committer!
===========================================================================
"""

NO_CODE_REVIEW_ALERT = """
===========================================================================
Alert: A code review is needed because thrift files were edited or created.
Please use 'arc diff' to request a code review.

Reviewers should be:
ownername1 ownername2
===========================================================================
"""

ARC_CHECK_ALERT="""
===========================================================================
You're unable to push because your arc is not installed properly. 
Arc is needed for code review purpose. 
Please follow:
https://secure.phabricator.com/book/phabricator/article/arcanist_quick_start/ 
to setup your arc properly. 

In case you have more questions,please contact with productivity@houzz.com.
===========================================================================
"""

LANG_ID_ALERT="""
===========================================================================
Changes in the "_id" field of lang files will unhook translations!
The "_id" field should not be removed or regenerated.

Use bypass=1 git commit if you're sure you need to update _id.
===========================================================================
"""







