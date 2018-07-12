#!/usr/bin/python
# Author:yue.zhang@houzz.com
import os
import os.path
import re
import subprocess
import sys
import threading
import json
import constants

from utils_code_review import *

sys.dont_write_bytecode = True

class Utils:
	def __init__(self):
		pass

	def get_content_file(self,file):
		with open(file, 'r') as content_file:return content_file.readlines()

	def filter_files_ext(self,files, ext):
		return [a for a in files if a.endswith(ext)]


class Github:
	def __init__(self):
		pass

	def reset_last_commit(self):
		subprocess.check_call("git reset HEAD~",shell=True)

	def get_git_branch_name(self):
		return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode('utf-8').rstrip()

	def get_git_remote_revision_hash(self, branch):
		return subprocess.check_output(['git', 'rev-parse', 'origin/' + branch]).decode('utf-8').rstrip()

	def get_git_revision_hash(self):
		return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').rstrip()

	def get_unpushed_commits(self, remote_sha, local_sha):
		return subprocess.check_output(["git", "rev-list", remote_sha + ".." + local_sha]).decode('utf-8')

	def get_last_commit_msg(self):
		return subprocess.check_output("git log -1 --pretty=%B", shell=True).decode("utf-8").rstrip()

	def modify_commit_msg(self, msg):
		subprocess.check_call("git commit --amend -m\"" + msg + "\"", shell=True)

	def get_commit_message(self,rev):
		return subprocess.check_output("git log --format=%B -n 1 " + rev, shell=True).decode('utf-8')

	def get_uncommited_files(self):
		files = subprocess.check_output("git status --porcelain", shell=True).decode('utf-8').splitlines()
		return [i.split()[1] for i in files]

	def get_git_diff_stat(self,rev):
		return subprocess.check_output("git diff --numstat " + rev + "^ " + rev, shell=True).decode('utf-8').splitlines()

	def get_git_staged_files(self,**kwargs):
		cmd = "git diff --name-only --cached"
		cmd += ' -G"'+ kwargs['regex'] +'"' if 'regex' in kwargs else ''
		cmd += ' '+ kwargs['path'] if 'path' in kwargs else ''
		return subprocess.check_output(cmd,shell=True).decode('utf-8').splitlines()

	def get_git_changed_files(self,rev):
		return subprocess.check_output("git diff --name-only "+rev + "^ " + rev,shell=True).decode('utf-8').rstrip().splitlines()

	def get_git_repo_path(self):
		return subprocess.check_output("git rev-parse --show-toplevel",shell=True).decode('utf-8').rstrip()

	def get_git_commit_files(self,revision):
		try:
			return subprocess.check_output("git diff-tree --no-commit-id --name-only -r {}".format(revision),shell=True).decode('utf-8').splitlines()
		except Exception as e:
			print(e)
			return []

	def get_all_changed_files(self):
		branch = self.get_git_branch_name()
		files = subprocess.check_output("git diff --stat origin/{}..".format(branch),shell=True).decode('utf-8').splitlines()
		return [i.split()[0] for i in files]


	def get_total_lines_changed(self,revs_list):
		lines_changed = 0
		for rev in revs_list:
			line = self.get_lines_changed_commit(rev)
			if line is not None:
				lines_changed = lines_changed + int(line)
		return lines_changed

	def get_lines_changed_commit(self,rev):
		count = 0
		for line in self.get_git_diff_stat(rev):
			try:
				counts = [int(s) for s in line.split() if s.isdigit()]
				count += sum(counts)
			except Exception as e:
				print("Error occur when counting lines changed")
		return count


class Bypass:
	def __init__(self):
		self.github = Github()
		self.bypass_imprint = {}
		self.bypass_imprint[1] = "{bypass=1}"
		self.bypass_imprint[2] = "{bypass=2}"
		self.bypass_imprint[3] = "{bypass=3}"
		self.bypass_imprint[4] = "{bypass=4}"
		self.bypass_info = """In case of emergent production issue,please use:bypass=4 git commit -m'msg' to bypass all githooks. 
More info please refer : https://cr.houzz.net/w/dev-introduction/workflow/#how-to-bypass-code-revie"""

	def bypass_code_review(self, bypass_code, msg_path=None):
		msg = self.get_last_commit_msg(msg_path)
		if len(re.findall(r"{bypass=\d{1}}", msg)) > 0:
			sys.exit(0)

		if bypass_code > 0:
			msg += self.bypass_imprint[bypass_code]
			self.append_bypass_to_commit_msg(msg, msg_path)
			sys.exit(0)

	def get_last_commit_msg(self, msg_path):
		if msg_path:
			with open(msg_path, 'r') as file:
				return file.read()
		else:
			return self.github.get_last_commit_msg()

	def append_bypass_to_commit_msg(self, msg, msg_path):
		if msg_path:
			with open(msg_path, 'w') as file:
				file.write(msg)
		else:
			self.github.modify_commit_msg(msg)

class Phabricator:
	def __init__(self):
		self.matcher = re.compile(r"""
^[^\{]*          # Starting from the beginning of the string, match anything that isn't an opening bracket
       (         # Open a group to record what's next
        \{.+\}   # The JSON substring
       )         # close the group
 [^}]*$          # at the end of the string, anything that isn't a closing bracket
""", re.VERBOSE)
		self.github = Github()

	def check_code_reviews_apicall(self,ids):
		json = "{\"ids\":" + str(ids) + "}"
		response_str = subprocess.check_output("echo '" + json + "\' | arc call-conduit --conduit-uri https://cr.houzz.net/ differential.query",shell=True).decode('utf-8')
		return self.matcher.match(response_str).group(1)

	def get_review_ids_from_msg(self,revs_list):
		ids = []
		for rev in revs_list:
			for line in self.github.get_commit_message(rev).splitlines():
				if "Differential Revision:" in line:
					ids.append(int(re.findall(r'\d+', line)[-1]))
		return ids

CHUNK_SIZE = 1000
class Syntax_Check:
	def __init__(self):
		self.github = Github()

	def is_hhvm_installed(self):
		try:
			subprocess.check_call("which hhvm",shell=True)
			return True
		except Exception as e:
			print(e)
			return False

	def filter_files_ext(self,files, ext):
		return [a for a in files if a.endswith(ext)]

	def syntax_check_with_threads(self):
		files = self.filter_files_ext(self.github.get_git_staged_files(),".php")
		chunks = [files[i:i + CHUNK_SIZE] for i in xrange(0, len(files), CHUNK_SIZE)]
		for i in range(len(chunks)):
			thread = Syntax_Check_Thread("Thread-{}".format(i+1),chunks[i])
			thread.daemon = True
			thread.start()

	def syntax_check(self):
		if self.is_hhvm_installed():
			files = self.filter_files_ext(self.github.get_git_staged_files(),".php")
			for file in files:
				if os.path.exists(file):
					return_code = subprocess.call("hhvm -l '{}'".format(file),shell=True)
					if return_code is not 0:
						sys.exit(1)

	def syntax_check_jenkins(self,revision):
		output_file=open("syntax_check.log","w+")
		files = self.filter_files_ext(self.github.get_git_commit_files(revision),".php")
		for file in files:
			output_file.write("syntax check file {}\n".format(file))
			if os.path.exists(file) and subprocess.call("hhvm -l '{}'".format(file),stdout=output_file,stderr=output_file,shell=True) is not 0:
				output_file.close()
				print("failed")
				sys.exit(0)
		output_file.close()

class Syntax_Check_Thread(threading.Thread):
	def __init__(self,name,files):
		threading.Thread.__init__(self)
		self.name = name
		self.files = files
		self.github = Github()

	def run(self):
		for file in self.files:
			if os.path.exists(file):
				subprocess.call("hhvm -l '{}'".format(file),shell=True)


class Misc_Check:
	def __init__(self):
		self.utils = Utils()
		self.github = Github()
		self.bypass = Bypass()

	def repo_clean_check(self):
		git_branch = self.github.get_git_branch_name()
		try:
			rs = subprocess.check_output("git log origin/"+git_branch+".."+git_branch,shell=True).decode("utf-8").rstrip()
			if rs == "":
				print("Your working directory is clean.")
				sys.exit(0)
		except Exception as e:
			print(e)

	def files_owner_check(self,files):
		for file in files:
			has_owner = False
			content = self.utils.get_content_file(file)
			for line in content[:3]:
				if "@owner" in line:
					has_owner |= True
					break

			if not has_owner:
				print(constants.NO_OWNER_ALERT)
				sys.exit(1)

	def thrift_files_check(self):
		files = self.utils.filter_files_ext(self.github.get_uncommited_files(), constants.THRIFT_EXT)
		self.files_owner_check([file.strip() for file in files])

	def branch_check(self):
		git_branch = self.github.get_git_branch_name()
		if git_branch != "master" and git_branch != constants.RELEASE_BRANCH:
			sys.exit(0)

	def branch_check_c2thrift(self):
		git_branch = self.github.get_git_branch_name()
		if not "master" == git_branch and not constants.RELEASE_BRANCH == git_branch:
			sys.exit(0)
		if git_branch == constants.RELEASE_BRANCH:
			print("Change on Release branch is forbidden in c2thrift module.")
			sys.exit(1)

	def cherrypick_check(self):
		git_branch = self.github.get_git_branch_name()
		if git_branch == constants.RELEASE_BRANCH:
			msg = self.github.get_last_commit_msg()
			# print msg
			if not "cherry picked" in msg:
				print("***************************************************")
				print("Please append option -x while cherry-picking.")
				print(self.bypass.bypass_info)
				print("***************************************************")
				self.github.reset_last_commit()
				sys.exit(1)

	def lang_id_check(self):
		lines = self.github.get_git_staged_files(path='**/*.lang',regex="\\\"_id\\\"")
		if lines:
			print(constants.LANG_ID_ALERT)
			sys.exit(1)


class Code_review_check:
	def __init__(self):
		self.utils = Utils()
		self.github = Github()
		self.phabricator = Phabricator()


	def CR_check(self):
		#Extract code review id from commit msg
		git_branch 		= self.github.get_git_branch_name()
		local_sha  		= self.github.get_git_revision_hash()
		remote_sha 		= self.github.get_git_remote_revision_hash(git_branch)
		revs_list 		= self.github.get_unpushed_commits(remote_sha,local_sha).splitlines()
		ids 			= self.phabricator.get_review_ids_from_msg(revs_list)

		need_approval 	= self.check_if_reviewed(ids)

		#Show code review alert if need
		if need_approval:
			print(constants.PRE_PUSH_ALERT)
			sys.exit(1)
		else:
			print("Great job! Your code is ready to go!")

	def code_review_check(self):
		# If needs code review
		needs_code_review = self.needs_code_review()
		if needs_code_review is not True:
			print("No need for code review.")
			return
		# code review valid
		pass_code_review = self.check_if_reviewed(ids)
		# Show code review suggestion
		if pass_code_review:
			print("Great job! Your code is ready to go!")
		else:
			print(constants.PRE_PUSH_ALERT)
			sys.exit(1)

	def needs_code_review(self):
		git_branch 		= self.github.get_git_branch_name()
		local_sha  		= self.github.get_git_revision_hash()
		remote_sha 		= self.github.get_git_remote_revision_hash(git_branch)
		revs_list 		= self.github.get_unpushed_commits(remote_sha,local_sha).splitlines()

		if git_branch == constants.RELEASE_BRANCH:
			return True

		lines_changed 	= self.github.get_total_lines_changed(revs_list)

		if lines_changed >= constants.MAX_LINES:
			return True

		return False

	def passed_code_review(self):
		git_branch 		= self.github.get_git_branch_name()
		local_sha  		= self.github.get_git_revision_hash()
		remote_sha 		= self.github.get_git_remote_revision_hash(git_branch)
		revs_list 		= self.github.get_unpushed_commits(remote_sha,local_sha).splitlines()
		ids 			= self.phabricator.get_review_ids_from_msg(revs_list)

		if len(ids) == 0:
			return False

		is_reviwed = self.check_if_reviewed(ids)

		if is_reviwed is not True:
			return False

		if constants.IS_NEED_DWREVIEW:
			return False


	def c2thrift_CR_check(self):
		# check how many thrift files have been changed.
		files = self.utils.filter_files_ext(self.github.get_all_changed_files(), constants.THRIFT_EXT)

		if len(files) == 0:
			sys.exit(0)

		#Extract code review id from commit msg
		git_branch = self.github.get_git_branch_name()
		local_sha  = self.github.get_git_revision_hash()
		remote_sha = self.github.get_git_remote_revision_hash(git_branch.rstrip())
		revs_list  = self.github.get_unpushed_commits(remote_sha.rstrip(),local_sha.rstrip()).splitlines()
		ids 	   = self.phabricator.get_review_ids_from_msg(revs_list)

		#Call phabricate to check if code review approved
		status = self.approval_check(ids)

		#Give code review suggestion accordingly
		self.give_code_review_msg(status,files)

	def c2thrift_CR_check_Release(self):
		git_branch      = self.github.get_git_branch_name()
		local_revision  = self.github.get_git_revision_hash()
		remote_revision = self.github.get_git_remote_revision_hash(git_branch.rstrip())
		revs_list 		= self.github.get_unpushed_commits(remote_revision.rstrip(),local_revision.rstrip()).splitlines()
		if git_branch == constants.RELEASE_BRANCH:
			for rev in revs_list:
				changed_files = self.github.get_git_changed_files(rev)
				for file in changed_files:
					if file == "c2thrift":
						print("***************************************************")
						print("Commit failed ><")
						print("Cherry-pick contains c2thrift definition is forbidden.")
						print("Please separate it from your commit.")
						print("***************************************************")
						self.github.reset_last_commit()
						sys.exit(1)


	def approval_check(self,ids):
		if len(ids) == 0: return 2

		need_approval = False
		try:
			result = json.loads(self.phabricator.check_code_reviews_apicall(ids))
			for code_review in result["response"]:
				if code_review["authorPHID"] in code_review["reviewers"]:
					reviewers = code_review["reviewers"]
					print(reviewers)
					reviewers.pop(code_review["authorPHID"],None)#remove committer itself
					print(reviewers)
					if not reviewers:
						return 3
				need_approval |= (code_review["statusName"] not in constants.GOOD_STATUS)
		except Exception as e:
			raise e

		if need_approval: return 3
		return 1

	def check_if_reviewed(self,ids):
		if len(ids) == 0: return True
		need_approval = False
		try:
			result = json.loads(self.phabricator.check_code_reviews_apicall(ids))
			for code_review in result["response"]:
				if code_review["authorPHID"] in code_review["reviewers"]:
					reviewers = code_review["reviewers"]
					reviewers.pop(code_review["authorPHID"],None)#remove committer itself
					if not reviewers:
						return True
				need_approval |= (code_review["statusName"] not in constants.GOOD_STATUS)
		except Exception as e:
			raise e

		return need_approval

	def give_code_review_msg(self,status,files):
		#1 get all thrift files names
		if status == 1:
			print(constants.CODE_REVIEW_STATUS[status])
			sys.exit(0)

		#2 get all onwers list
		owners = self.extract_onwers(files)
		#3 Give code review suggestion
		print ("===========================================================================")
		print (constants.CODE_REVIEW_STATUS[status])
		print (owners)
		print ("===========================================================================")
		sys.exit(1)

	def extract_onwers(self,files):
		owners = ["Kenneth"]
		for file in files:
			content = self.utils.get_content_file(file)
			for line in content[:3]:
				owners.extend(a.replace("@houzz.com","") for a in line.split() if a.endswith("@houzz.com"))
		return list(set(owners))


class Release_cut_off_check:
	def __init__(self):
		self.utils = Utils()
		self.github = Github()
		self.bypass = Bypass()

	def release_cutoff_check(self,type):
		git_branch = self.github.get_git_branch_name()
		# user = self.github.get_git_email()

		if git_branch != constants.RELEASE_BRANCH:
			return

		# if user == constants.RELEASE_MANAGER:
		#     return

		need_reset = self.is_latest_release_version()
		if type == "merge" or type == "checkout" or type == "rebase" or type == "commit":
			if need_reset:
				print("************************************************************************")
				print("Your local Release branch is out dated after weekly cut off.")
				print("Please sync to latest Release branch by git reset --hard origin/Release.")
				user_input = raw_input("Do you want to reset now?(y/n)")
				if user_input == "y":
					#TODO check result of git reset
					if type == "merge":
						subprocess.call("git reset --merge",shell=True)
						subprocess.call("git merge --abort",shell=True)
					subprocess.call("git reset --hard origin/{}".format(constants.RELEASE_BRANCH),shell=True)
					subprocess.call("git submodule update",shell=True)
					print("Switch to latest Release branch :)")
					sys.exit(1)
				else:
					print("***************************************************")
					print("Please Switch to latest Release branch manually by run:")
					print("git reset --hard origin/Release")
					print("Otherwise you are not allowed to commit and push :(")
					print("***************************************************")
					sys.exit(1)

		elif type == "push":
			if need_reset > 0:
				print("***************************************************")
				print("{} failed due to your local Release branch version is out dated.".format(type))
				print("Please sync with latest Release branch by: git reset --hard origin/Release")
				print("***************************************************")
				sys.exit(1)

	def is_latest_release_version(self):
		diff = subprocess.check_output("git diff {0}:gitutils/ReleaseVersion.txt origin/{1}:gitutils/ReleaseVersion.txt".format(constants.RELEASE_BRANCH,constants.RELEASE_BRANCH), shell=True).decode('utf-8')
		return len(diff) > 0

	def release_version_file_check(self):
		git_branch = self.github.get_git_branch_name()
		# user = self.github.get_git_email()
		if git_branch == constants.RELEASE_BRANCH:
			diff = subprocess.check_output("git diff gitutils/ReleaseVersion.txt ", shell=True).decode('utf-8')
			if len(diff) > 0:
				print("***************************************************")
				print("You are not allowed to change file gitutils/ReleaseVersion.txt")
				print("***************************************************")
				sys.exit(1)

	def is_latest_release_version(self):
		if os.path.exists("gitutils/ReleaseVersion.txt"):
			diff = subprocess.check_output("git diff {0}:gitutils/ReleaseVersion.txt origin/{1}:gitutils/ReleaseVersion.txt".format(constants.RELEASE_BRANCH,constants.RELEASE_BRANCH), shell=True).decode('utf-8')
			return len(diff) > 0
		else:
			return False