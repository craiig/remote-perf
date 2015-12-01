#!/usr/bin/env bash
#we need perf
yum install -y perf

yum -y install java-1.8.0-openjdk.x86_64
yum -y install java-1.8.0-openjdk-devel.x86_64
yum -y remove java-1.7.0-openjdk.x86_64
yum -y remove java-1.6.0-openjdk.x86_64

#some systems have hardcoded 1.7 paths
ln -sf /usr/lib/jvm/java-1.8.0 /usr/lib/jvm/java-1.7.0

#make sure frame pointers are enabled
echo "export _JAVA_OPTIONS=\"-XX:+PreserveFramePointer\"" >> ~/.bash_profile
echo "export JAVA_TOOL_OPTIONS=\"-XX:+PreserveFramePointer\"" >> ~/.bash_profile
echo "export JAVA_HOME=/usr/lib/jvm/java-1.7.0" >> ~/.bash_profile
echo "source ~/.bash_profile" >> ~/.bashrc
source ~/.bash_profile

#setup for perf-map-agent
yum install -y cmake
cd /usr/lib/jvm
git clone --depth=1 https://github.com/jrudolph/perf-map-agent 
cd perf-map-agent
cmake .
make
cd ~

#setup jmaps for automatically mapping running java processes stack frames
wget https://raw.githubusercontent.com/craiig/remote-perf/master/java/jmaps
chmod +x jmaps
