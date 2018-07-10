#!/usr/bin/env bash

RELEASE_BRANCH="newRelease"
# TODO should be origin/master
MASTER_BRANCH="master"
BACKUP_RELEASE_NAME=""

while getopts ":n" opt; do
  case "$opt" in
    n)
      BACKUP_RELEASE_NAME=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$opt" && exit 1
      ;;
    :)
      echo "Option -$opt requires a value" && exit 1
      ;;
  esac
done

if [ -n ARCHIVE_NAME ]; then
    echo "A backup name for current Release branch is required"
    exit 0
fi

# check current branch name is Release
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$current_branch" != "$RELEASE_BRANCH"  ]; then
    echo "Please switch to Release branch first."
    exit 0
fi

# archive old Release branch
echo "start to archive current Release branch"
git branch -m $BACKUP_RELEASE_NAME
git push origin :$RELEASE_BRANCH $BACKUP_RELEASE_NAME
git push -u origin $BACKUP_RELEASE_NAME


# create new Release branch out of master
git checkout -b $RELEASE_BRANCH origin/master
git push -u origin $RELEASE_BRANCH

echo "Cut off is Done! Enjoy!"

