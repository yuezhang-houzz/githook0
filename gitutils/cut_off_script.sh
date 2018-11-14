#!/bin/bash
# Usage :
# sh gitutils/cut_off_script -n backup_name -v "new_version_name" -t "previous_release_tag"

RELEASE_BRANCH="Release"
MASTER_BRANCH="origin/master"
BACKUP_RELEASE_NAME=""
VERSION_NAME=""
PREVIOUS_RELEASE_TAG=""
ROOT_DIR=$(git rev-parse --show-toplevel)

while getopts ":n:v:t:" opt; do
  case "$opt" in
    n)
      BACKUP_RELEASE_NAME=$OPTARG
      ;;
    v)
      VERSION_NAME=$OPTARG
      ;;
    t)
      PREVIOUS_RELEASE_TAG=$OPTARG
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

if [ -z $PREVIOUS_RELEASE_TAG ]; then
    echo "Tag name for the previous release is required"
    exit 0
fi

read -p "Please make sure $RELEASE_BRANCH branch is not protected, then press enter to continue"
# tag the current Release branch
echo "tag the current Release branch"
git checkout $RELEASE_BRANCH
git pull
git tag $PREVIOUS_RELEASE_TAG
git push origin $PREVIOUS_RELEASE_TAG --no-verify
if [ $? = 0 ] ; then
    echo "Successfully tagged Release branch"
else
    echo "Failed to tag Release branch."
    exit 1
fi


# archive old Release branch
echo "start to archive current Release branch"
git branch -m $BACKUP_RELEASE_NAME
git push origin :$RELEASE_BRANCH $BACKUP_RELEASE_NAME --no-verify
if [ $? != 0 ] ; then
    echo "Failed to archive Release branch."
    exit 1
fi
git push -u origin $BACKUP_RELEASE_NAME --no-verify
if [ $? != 0 ] ; then
    echo "Failed to archive Release branch."
    exit 1
fi

# add new version name to ReleaseVersion.txt
echo "add new version name"
git checkout master
echo "$VERSION_NAME" >> $ROOT_DIR/gitutils/ReleaseVersion.txt
git commit -am "update Release version $VERSION_NAME" --no-verify
if [ $? != 0 ] ; then
    echo "Failed to update version."
    exit 1
fi
git pull --rebase
git push --no-verify

# create new Release branch out of master
git checkout -b $RELEASE_BRANCH $MASTER_BRANCH
git push -u origin $RELEASE_BRANCH --no-verify
if [ $? != 0 ] ; then
    echo "Failed to create new Release branch."
    exit 1
fi

echo "Cut off is Done! Enjoy!"
