#!/usr/bin/python
# Author:yue.zhang@houzz.com
import fnmatch
import sys
import os
import os.path
import threading
import re
import subprocess
import constants
sys.dont_write_bytecode = True


class Utils:
    def __init__(self):
        pass

    def get_content_file(self, file):
        with open(file, 'r') as content_file:
            return content_file.readlines()

    def filter_files_ext(self, files, ext):
        return [a for a in files if a.endswith(ext)]

    def is_valid_email(self, email):
        if len(email) > 7:
            return bool(
                re.match(
                    "^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$",
                    email))
        return False


class Github:
    def __init__(self):
        pass

    def reset_last_commit(self):
        subprocess.check_call("git reset HEAD~", shell=True)

    def get_git_branch_name(self):
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode('utf-8').rstrip()

    def get_git_remote_revision_hash(self, branch):
        return subprocess.check_output(
            ['git', 'rev-parse', 'origin/' + branch]).decode('utf-8').rstrip()

    def get_git_revision_hash(self):
        return subprocess.check_output(
            ['git', 'rev-parse', 'HEAD']).decode('utf-8').rstrip()

    def get_unpushed_commits(self, remote_sha, local_sha):
        return subprocess.check_output(
            ["git", "rev-list", remote_sha + ".." + local_sha]).decode('utf-8')

    def get_last_commit_msg(self):
        return subprocess.check_output(
            "git log -1 --pretty=%B",
            shell=True).decode("utf-8").rstrip()

    def modify_commit_msg(self, msg):
        msg = msg.replace('"', '\\"')
        subprocess.check_call(
            "git commit --amend -m\"" +
            msg +
            "\"",
            shell=True)

    def get_commit_message(self, rev):
        return subprocess.check_output(
            "git log --format=%B -n 1 " + rev,
            shell=True).decode('utf-8')

    def get_uncommited_files(self):
        files = subprocess.check_output(
            "git status --porcelain",
            shell=True).decode('utf-8').splitlines()
        return [i.split()[1] for i in files]

    def get_git_diff_stat(self, rev, include_whitespace=True):
        command = "git diff --numstat "
        if not include_whitespace:
            command += "-w "
        return subprocess.check_output(
            command + rev + "^ " + rev,
            shell=True).decode('utf-8').splitlines()

    def get_git_staged_files(self):
        return subprocess.check_output(
            "git diff --name-only --cached",
            shell=True).decode('utf-8').splitlines()

    def get_git_repo_path(self):
        return subprocess.check_output(
            "git rev-parse --show-toplevel",
            shell=True).decode('utf-8').rstrip()

    def get_git_email(self):
        return subprocess.check_output(
            "git config user.email",
            shell=True).decode('utf-8').rstrip()

    def get_staged_file_diff(self, file):
        return subprocess.check_output(
            "git diff --cached {}".format(file),
            shell=True).decode('utf-8').splitlines()

    def get_git_commit_files(self, revision):
        try:
            return subprocess.check_output(
                "git diff-tree --no-commit-id --name-only -r {}".format(revision),
                shell=True).decode('utf-8').splitlines()
        except Exception as e:
            print(e)
            return []

    def get_submodule_sha(self, submodule):
        '''
        :param submodule:
        :return:[previous_sha, current_sha]
        '''
        hashes = []
        try:
            cmd = "git diff --cached {} | grep \"Subproject commit\"".format(submodule)
            result = subprocess.check_output(
                cmd, shell=True).decode('utf-8').splitlines()
            for line in result:
                hashes.append(line.split()[2])
        except Exception:
            return []
        return hashes

    def check_shas_order(self, pre_sha, cur_sha, submodule):
        #  os to submodule folder
        #  compare git sha
        try:
            os.chdir(self.get_git_repo_path() + "/" + submodule)
            cmd = "git rev-list --count {0}..{1}".format(pre_sha, cur_sha)
            result = subprocess.check_output(
                cmd, shell=True).decode('utf-8').rstrip()
            return result != "0"
        except Exception as e:
            print (e)
            return False

    def get_total_lines_changed(self, revs_list, include_whitespace=True):
        lines_changed = 0
        for rev in revs_list:
            line = self.get_lines_changed_commit(rev, include_whitespace)
            if line is not None:
                lines_changed = lines_changed + int(line)
        return lines_changed

    def get_lines_changed_commit(self, rev, include_whitespace=True):
        count = 0
        for line in self.get_git_diff_stat(rev, include_whitespace):
            try:
                counts = [int(s) for s in line.split() if s.isdigit()]
                count += sum(counts)
            except Exception as e:
                print(e)
                print("Error occur when counting lines changed ")
        return count


class Bypass:
    def __init__(self):
        self.github = Github()

    def bypass_code_review(self, bypass_code):
        msg = self.github.get_last_commit_msg()
        if len(re.findall(r"{bypass=\d{1}}", msg)) > 0:
            sys.exit(0)

        if bypass_code > 0:
            msg += constants.BYPASS_IMPRINT[bypass_code]
            self.github.modify_commit_msg(msg)
            sys.exit(0)


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

    def check_code_reviews_apicall(self, ids):
        json = "{\"ids\":" + str(ids) + "}"
        response_str = subprocess.check_output(
            "echo '" +
            json +
            "\' | arc call-conduit --conduit-uri https://cr.houzz.net/ differential.query",
            shell=True).decode('utf-8')
        return self.matcher.match(response_str).group(1)

    def get_review_ids_from_msg(self, revs_list):
        ids = []
        for rev in revs_list:
            for line in self.github.get_commit_message(rev).splitlines():
                if "Differential Revision:" in line:
                    ids.append(int(re.findall(r'\d+', line)[-1]))
        return ids


def syntax_check_filenames(filenames, stdout=None, stderr=None):
    try:
        return_code = subprocess.call(
            ["arc", "lint"] + filenames, stdout=stdout, stderr=stderr)
    except OSError:
        print "You must install arc before committing code"
        return False
    return return_code == 0


class SyntaxCheck:
    def __init__(self):
        self.github = Github()

    def is_php_short_tag_on(self):
        try:
            result = subprocess.check_output(
                "echo '<?php echo ini_get(\"short_open_tag\") ?>' | php",
                shell=True).decode('utf-8').rstrip()
            if result != "1":
                print("Please set 'short_tag_on' to 'On' in php.ini")
                print("Find location of php.ini by 'php --ini'")
            else:
                print("php short_tag_on is on")
        except Exception as e:
            print(e)

    def is_hhvm_installed(self):
        try:
            subprocess.check_call(
                "which hhvm", shell=True, stdout=open(
                    os.devnull, 'wb'))
            return True
        except Exception as e:
            print(e)
            return False

    def _relevant_files(self):
        return filter(os.path.isfile, self.github.get_git_staged_files())

    def _chunked_files(self, chunk_size=1000):
        files = list(self._relevant_files())
        return [files[i:i + chunk_size]
                for i in range(0, len(files), chunk_size)]

    def syntax_check_with_threads(self, chunk_size=1000):
        for i, chunk in enumerate(self._chunked_files(chunk_size), 1):
            thread = SyntaxCheckThread("Thread-{}".format(i), chunk)
            thread.daemon = True
            thread.start()

    def syntax_check(self):
        for files in self._chunked_files():
            if not syntax_check_filenames(files):
                sys.exit(1)

    def syntax_check_jenkins(self, revision):
        with open("syntax_check.log", "w") as output_file:
            for file in self._relevant_files():
                output_file.write("syntax check file {}\n".format(file))
                if not syntax_check_filenames(
                        [file], stdout=output_file, stderr=output_file):
                    print("failed")
                    sys.exit(0)


class SyntaxCheckThread(threading.Thread):
    def __init__(self, name, files):
        threading.Thread.__init__(self)
        self.name = name
        self.files = files
        self.github = Github()

    def run(self):
        syntax_check_filenames(self.files)


class MiscCheck:
    def __init__(self):
        self.utils = Utils()
        self.github = Github()
        self.bypass = Bypass()

    def repo_clean_check(self):
        git_branch = self.github.get_git_branch_name()
        try:
            rs = subprocess.check_output(
                "git log origin/" + git_branch + ".." + git_branch,
                shell=True).decode("utf-8").rstrip()
            if rs == "":
                print("Your working directory is clean.")
                sys.exit(0)
        except Exception as e:
            print(e)

    def files_owner_check(self, files):
        for file in files:
            has_owner = False
            content = self.utils.get_content_file(file)
            for line in content[:3]:
                if re.search('@owner', line, re.IGNORECASE):
                    has_owner |= True
                    break

            if not has_owner:
                print(constants.NO_OWNER_ALERT)
                sys.exit(1)

    def thrift_files_check(self):
        files = self.utils.filter_files_ext(
            self.github.get_uncommited_files(),
            constants.THRIFT_EXT)
        self.files_owner_check([file.strip() for file in files])

    def branch_check(self):
        git_branch = self.github.get_git_branch_name()
        if git_branch != "master" and git_branch != "Release":
            sys.exit(0)

    def branch_check_c2thrift(self):
        git_branch = self.github.get_git_branch_name()
        if not "master" == git_branch and not "Release" == git_branch:
            sys.exit(0)
        if git_branch == "Release":
            print("Change on Release branch is forbidden in c2thrift module.")
            sys.exit(1)

    def cherrypick_check(self, type="commit"):
        '''
        On Release branch, check if commit is a cherry-pick
        1. check commit message contains cherry-pick info
        2. check if commit sha also exist on local master branch
        :param type: commit or push
        :return: exit if not a valid cherry-pick
        '''
        git_branch = self.github.get_git_branch_name()
        if git_branch == "Release":
            msg = self.github.get_last_commit_msg()
            # print msg master change
            if "cherry picked" not in msg:
                print("***************************************************")
                print("Please append option -x while cherry-picking.")
                print(constants.BYPASS_INFO)
                print("***************************************************")
                if type == "push":
                    self.github.reset_last_commit()
                sys.exit(1)

            git_branch = self.github.get_git_branch_name()
            local_sha = self.github.get_git_revision_hash()
            remote_sha = self.github.get_git_remote_revision_hash(git_branch)
            revs_list = self.github.get_unpushed_commits(
                remote_sha, local_sha).splitlines()
            for rev in revs_list:
                if not subprocess.call(
                    "git branch --contains {} |grep -w master".format(rev),
                        shell=True):
                    print(
                        "Original commit {} is not in the master branch.".format(rev))
                    exit(1)

    def test_owner_check(self):
        files = self.utils.filter_files_ext(
            self.github.get_git_staged_files(), "Test.php")
        for file in files:
            if os.path.exists(file):
                has_owner = self.testfile_has_owner(file)
                if has_owner is not True:
                    print(constants.NO_TEST_OWNER_ALERT.format(file))
                    sys.exit(1)

    def testfile_has_owner(self, file):
        has_owner = False
        with open(file) as f:
            lines = f.readlines()
            for line in lines[:10]:
                if re.search('@owner', line, re.IGNORECASE):
                    for word in line.split(" "):
                        has_owner |= self.utils.is_valid_email(word)

        return has_owner

    def credentials_check(self):
        constains_credentials = False

        # get all staged config files
        files = self.github.get_git_staged_files()

        # get diff of those config files
        for file in files:
            if re.match(r"C2Config*.php", file):
                diffs = self.github.get_staged_file_diff(file)
                for diff in diffs:
                    # match key,secret,password..... case insensitive
                    if re.search(["key" "secret", "password"],
                                 diff, re.IGNORECASE):
                        constains_credentials = True

        # Pop up dialog
        if constains_credentials:
            sys.exit(1)

    def check_submodule_backward(self, submodule):
        '''
        1. get previous and current pointer
        2. check the order of 2 pointer
        3. throw confirmation dialog if backward
        :param submodule:
        :return: pass or reject commit
        '''
        shas = self.github.get_submodule_sha(submodule)

        if len(shas) == 0:
            return

        is_right_order = self.github.check_shas_order(
            shas[0], shas[1], submodule)

        if not is_right_order:
            print("{0} is older than {1}.".format(shas[1][0:8], shas[0][0:8]))
            print("It is not allowed to commit an older {} pointer. Commit aborted.".format(submodule))
            sys.exit(1)


class ReleaseCutoffCheck:
    def __init__(self):
        self.utils = Utils()
        self.github = Github()
        self.bypass = Bypass()

    def release_cutoff_check(self, type):
        git_branch = self.github.get_git_branch_name()
        # user = self.github.get_git_email()

        if git_branch != "Release":
            return

        # if user == constants.RELEASE_MANAGER:
        #     return

        need_reset = self.is_latest_release_version()
        if type == "merge" or type == "checkout" or type == "rebase" or type == "commit":
            if need_reset:
                print(
                    "************************************************************************")
                print("Your local Release branch is out dated after weekly cut off.")
                print(
                    "Please sync to latest Release branch by git reset --hard origin/Release.")
                user_input = raw_input("Do you want to reset now?(y/n)")
                if user_input == "y":
                    # TODO check result of git reset
                    if type == "merge":
                        subprocess.call("git reset --merge", shell=True)
                        subprocess.call("git merge --abort", shell=True)
                    subprocess.call(
                        "git reset --hard origin/Release", shell=True)
                    subprocess.call("git submodule update", shell=True)
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
                print(
                    "{} failed due to your local Release branch version is out dated.".format(type))
                print(
                    "Please sync with latest Release branch by: git reset --hard origin/Release")
                print("***************************************************")
                sys.exit(1)

    def release_version_file_check(self):
        git_branch = self.github.get_git_branch_name()
        # user = self.github.get_git_email()
        if git_branch == "Release":
            diff = subprocess.check_output(
                "git diff gitutils/ReleaseVersion.txt ",
                shell=True).decode('utf-8')
            if len(diff) > 0:
                print("***************************************************")
                print("You are not allowed to change file gitutils/ReleaseVersion.txt")
                print("***************************************************")
                sys.exit(1)

    def is_latest_release_version(self):
        if os.path.exists("gitutils/ReleaseVersion.txt"):
            diff = subprocess.check_output(
                "git diff Release:gitutils/ReleaseVersion.txt origin/Release:gitutils/ReleaseVersion.txt",
                shell=True).decode('utf-8')
            return len(diff) > 0
        else:
            return False


def show_wiki_page(type):
    print("Starting git {}".format(type))
    print("In case of any problem, please refer to the following wiki page for troubleshooting common issues:")
    print("https://cr.houzz.net/w/dev-introduction/workflow/#tips-trouble-shooting\n")
