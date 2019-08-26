# !/bin/bash

echo "Creating release folder"
mkdir ~/houzz/release-cut
cd ~/houzz/release-cut
echo "git clone all the repos"
git clone git@github.com:Houzz/jukwaa-core.git
git clone git@github.com:Houzz/jukwaa-ui.git
git clone git@github.com:Houzz/jukwaa-shared-components.git
git clone git@github.com:Houzz/jukwaa.git
git clone git@github.com:Houzz/graphouzz.git
echo "git clone finished"
echo "========================================================"
echo "Updating jukwaa-core"
echo "********************************************************"
cd ~/houzz/release-cut/jukwaa-core
git checkout master
git reset --hard origin/master
git pull origin master
git checkout Release
git reset --hard origin/Release
git pull origin Release
git checkout master
cp ~/houzz/cut_off_script.sh ~/houzz/release-cut/jukwaa-core/gitutils
echo "jukwaa-core updated"
echo "********************************************************"
echo "cutting jukwaa-core"
sh gitutils/cut_off_script.sh -n "backup_Fresno_2019_08_22" -v "Release - Glendale (2019-08-26)" -t "Release_Fresno_2019_08_22"
echo "************          jukwaa-core CUT DONE       **************"


echo "Updating jukwaa-ui"
echo "********************************************************"
cd ~/houzz/release-cut/jukwaa-ui
git checkout master
git reset --hard origin/master
git pull origin master
git checkout Release
git reset --hard origin/Release
git pull origin Release
git checkout master
cp ~/houzz/cut_off_script.sh ~/houzz/release-cut/jukwaa-ui/gitutils
echo "jukwaa-ui updated"
echo "********************************************************"
echo "cutting jukwaa-ui"
sh gitutils/cut_off_script.sh -n "backup_Fresno_2019_08_22" -v "Release - Glendale (2019-08-26)" -t "Release_Fresno_2019_08_22"
echo "************          jukwaa-ui CUT DONE       **************"

echo "Updating jukwaa-shared-components"
echo "********************************************************"
cd ~/houzz/release-cut/jukwaa-shared-components
git checkout master
git reset --hard origin/master
git pull origin master
git checkout Release
git reset --hard origin/Release
git pull origin Release
git checkout master
cp ~/houzz/cut_off_script.sh ~/houzz/release-cut/jukwaa-shared-components/gitutils
echo "jukwaa-shared-components updated"
echo "********************************************************"
echo "cutting jukwaa-shared-components"
sh gitutils/cut_off_script.sh -n "backup_Fresno_2019_08_22" -v "Release - Glendale (2019-08-26)" -t "Release_Fresno_2019_08_22"
echo "************          jukwaa-shared-components CUT DONE       **************"

echo "Updating graphouzz"
echo "********************************************************"
cd ~/houzz/release-cut/graphouzz
git checkout Release
git reset --hard origin/Release
git pull origin Release
echo "graphouzz updated"
echo "********************************************************"


echo "Updating jukwaa"
echo "********************************************************"
cd ~/houzz/release-cut/jukwaa
git checkout master
git reset --hard origin/master
git pull origin master
git submodule update
git checkout Release
git reset --hard origin/Release
git pull origin Release
git submodule update
git checkout master
git submodule update
cp ~/houzz/cut_off_script.sh ~/houzz/release-cut/jukwaa/gitutils
echo "jukwaa updated"
echo "********************************************************"
echo "cutting jukwaa"
sh gitutils/cut_off_script.sh -n "backup_Fresno_2019_08_22" -v "Release - Glendale (2019-08-26)" -t "Release_Fresno_2019_08_22"
echo "************          jukwaa CUT DONE       **************"

echo "------ Init c2thrift -----";
git checkout master
git submodule init
git submodule update
echo "------ update c2thrift for master -----";
cd c2thrift
git checkout master
git pull
cd ..
git add .
git commit -m 'update thrift pointer'
git pull --rebase;
git push
echo "------ update c2thrift for master DONE-----";
echo "------ update c2thrift for Release -----";
git checkout Release
git submodule update
cd c2thrift
git checkout master
git pull
cd ..
git add .
git commit -m 'update thrift pointer'
git pull --rebase;
git push
echo "------ update c2thrift for Release DONE-----";


echo "------ updating package version -----";

cd ~/houzz/release-cut/jukwaa
git checkout Release
git pull

# Get jukwaa-core version
JUKWAA_CORE_PACKAGE_VERSION=$(cat /houzz/release-cut/jukwaa-core/package.json \
  | grep version \
  | head -1 \
  | awk -F: '{ print $2 }' \
  | sed 's/[",]//g' \
  | tr -d '[[:space:]]')


# Get jukwaa-ui version
JUKWAA_UI_PACKAGE_VERSION=$(cat /houzz/release-cut/jukwaa-ui/package.json \
  | grep version \
  | head -1 \
  | awk -F: '{ print $2 }' \
  | sed 's/[",]//g' \
  | tr -d '[[:space:]]')

# Get jukwaa-shared-components version
JUKWAA_SHARED_COMPONENTS_PACKAGE_VERSION=$(cat /houzz/release-cut/jukwaa-shared-components/package.json \
  | grep version \
  | head -1 \
  | awk -F: '{ print $2 }' \
  | sed 's/[",]//g' \
  | tr -d '[[:space:]]')

# Get graphouzz version
GRAPHOUZZ_PACKAGE_VERSION=$(cat /houzz/release-cut/graphouzz/package.json \
  | grep version \
  | head -1 \
  | awk -F: '{ print $2 }' \
  | sed 's/[",]//g' \
  | tr -d '[[:space:]]')

NEW_CORE='"jukwaa-core": "'$JUKWAA_CORE_PACKAGE_VERSION'"'
OLD_CORE='"jukwaa-core": "\*"'

NEW_SHARED='"jukwaa-shared-components": "'$JUKWAA_SHARED_COMPONENTS_PACKAGE_VERSION'"'
OLD_SHARED='"jukwaa-shared-components": "\*"'

NEW_UI='"jukwaa-ui": "'$JUKWAA_UI_PACKAGE_VERSION'"'
OLD_UI='"jukwaa-ui": "\*"'

NEW_G='"graphouzz": "'$GRAPHOUZZ_PACKAGE_VERSION'"'
OLD_G='"graphouzz": ".*"'

PUBLISH_CORE='hzbot jpubr jukwaa-core'

PUBLISH_UI='hzbot jpubr jukwaa-ui'

PUBLISH_SHARED='hzbot jpubr jukwaa-shared-components'

PUBLISH_GRAPHOUZZ='hzbot jpubr grahouzz'

echo $PUBLISH_CORE

echo $PUBLISH_UI

echo $PUBLISH_SHARED

echo $PUBLISH_GRAPHOUZZ

sed "s/$OLD_CORE/$NEW_CORE/g" /houzz/release-cut/jukwaa/package.json > package_temp.json && mv package_temp.json /houzz/release-cut/jukwaa/package.json
sed "s/$OLD_SHARED/$NEW_SHARED/g" /houzz/release-cut/jukwaa/package.json > package_temp.json && mv package_temp.json /houzz/release-cut/jukwaa/package.json
sed "s/$OLD_UI/$NEW_UI/g" /houzz/release-cut/jukwaa/package.json > package_temp.json && mv package_temp.json /houzz/release-cut/jukwaa/package.json
sed "s/$OLD_G/$NEW_G/g" /houzz/release-cut/jukwaa/package.json > package_temp.json && mv package_temp.json /houzz/release-cut/jukwaa/package.json

git add .
git commit -m 'lock packages version'
git pull --rebase
git push

# echo "clean up cut folder"
# rm -rf ~/houzz/release-cut
echo "All finished"