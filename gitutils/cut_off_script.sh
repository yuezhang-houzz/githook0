#!/bin/bash
# Usage :
# sh gitutils/cut_off_script -n backup_name -v "new_version_name"

RELEASE_BRANCH="Release"
MASTER_BRANCH="origin/master"
BACKUP_RELEASE_NAME=""
VERSION_NAME=""

while getopts ":n:v:kp:s" opt; do
  case "$opt" in
    n)
      BACKUP_RELEASE_NAME=$OPTARG
      ;;
    v)
      VERSION_NAME=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$opt" && exit 1
      ;;
    :)
      echo "Option -$opt requires a value" && exit 1
      ;;
  esac
done

echo $BACKUP_RELEASE_NAME
echo $VERSION_NAME

if [ -z $BACKUP_RELEASE_NAME ]; then
    echo "A backup name for current Release branch is required"
    exit 0
fi

if [ -z $VERSION_NAME ]; then
    echo "A new version name is required"
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

# add new version name to ReleaseVersion.txt
echo "add new version name"
git checkout master
echo "$VERSION_NAME" >> ReleaseVersion.txt
git commit -am "update Release version"
git pull --rebase
git push

# create new Release branch out of master
git checkout -b $RELEASE_BRANCH $MASTER_BRANCH
git push -u origin $RELEASE_BRANCH

echo "Cut off is Done! Enjoy!"

