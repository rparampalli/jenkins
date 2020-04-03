#!/bin/bash
#scipt to back up the complete CI including plugins and credentials

cd ~
export BACKUPDIR=$JENKINS_HOME/workspace/backup;
export BACKUPTIME=$(TZ=":America/Los_Angeles" date +"%Y%m%d_%H%M%S")_$HOSTNAME;
mkdir -p $BACKUPDIR/jobs;
mkdir -p $BACKUPDIR/plugins;
cp $JENKINS_HOME/plugins/*.* $BACKUPDIR/plugins;
cp $JENKINS_HOME/config.xml $BACKUPDIR;
cp $JENKINS_HOME/org.jenkinsci.plugins.configfiles.GlobalConfigFiles.xml $BACKUPDIR;
cp $JENKINS_HOME/com.michelin.cio.hudson.plugins.maskpasswords.MaskPasswordsConfig.xml $BACKUPDIR;
cp -r $JENKINS_HOME/secret* $BACKUPDIR;
cp $JENKINS_HOME/credentials.xml $BACKUPDIR;
cd $JENKINS_HOME/jobs/; 
for file in $(find ./ -maxdepth 2 -type f -name config.xml); 
do 
	cp --parent $file $BACKUPDIR/jobs/; 
	echo 1 > $BACKUPDIR/jobs/$(dirname $file)/nextBuildNumber; 
done; 
cd $BACKUPDIR;

tar -cvf backup_$BACKUPTIME.tar *;

# Copy the tar file to GIT or local setup.

#Below are the steps to extract te backup on the new CI
#Copy the tar file to the Jenkins home directory where you want to extract
# and execute the gollowing commands
rm $JENKINS_HOME/identity.key.enc 
rm $JENKINS_HOME/org.jenkinsci.plugins.configfiles.GlobalConfigFiles.xml 
rm $JENKINS_HOME/com.michelin.cio.hudson.plugins.maskpasswords.MaskPasswordsConfig.xml
rm -rf $JENKINS_HOME/jobs
rm -rf $JENKINS_HOME/plugins
tar -xvf backup_file_name.tar
