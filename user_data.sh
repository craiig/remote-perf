#!/usr/bin/env bash
# run this as root!
#
# ***** config
#enable the oracle jdk, this is needed to properly collect stack traces
# if you can't install the oracle jdk, you could try recompiling openjdk
# with -fno-omit-frame-pointer
ORACLE=1

# ***** end config


#disable ASLR so perf works?
echo 0 | sudo tee /proc/sys/kernel/randomize_va_space

#setup JAVA
#remove any old java
yum -y remove java-1.7.0-openjdk.x86_64
yum -y remove java-1.6.0-openjdk.x86_64
yum -y install java-1.8.0-openjdk.x86_64
yum -y install java-1.8.0-openjdk-devel.x86_64
if [ $ORACLE -eq 1 ]; then
#setup oracle java
wget --no-cookies --no-check-certificate --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com%2F; oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/8u66-b17/jdk-8u66-linux-x64.rpm
rpm -i jdk-8u66-linux-x64.rpm
#some systems have hardcoded 1.7 paths so we fake them
ln -sf /usr/java/latest /usr/lib/jvm/java-1.7.0
else 
#some systems have hardcoded 1.7 paths so we fake them
ln -sf /usr/lib/jvm/java-1.8.0 /usr/lib/jvm/java-1.7.0
fi

export JAVA_HOME=/usr/lib/jvm/java-1.7.0
echo "export JAVA_HOME=/usr/lib/jvm/java-1.7.0" >> ~/.bash_profile
#-----

#setup perf
yum install -y perf

#setup for perf-map-agent
yum install -y git #some machines don't come with git preloaded
yum install -y gcc gcc-c++ #or gcc
yum install -y cmake
cd /usr/lib/jvm
git clone --depth=1 https://github.com/craiig/perf-map-agent 
cd perf-map-agent
cmake .
make
cd ~

#make sure frame pointers are enabled and symbols are dumped for each java process
#echo "export _JAVA_OPTIONS=\"-XX:+PreserveFramePointer\"" >> ~/.bash_profile
echo "export JAVA_TOOL_OPTIONS=\"-XX:+PreserveFramePointer -agentpath:/usr/lib/jvm/perf-map-agent/out/libperfmap.so\"" >> ~/.bash_profile
source ~/.bash_profile
cat ~/.bash_profile

# we replace the java at /usr/bin/java to ensure that all java invocations see
# the environment variables
cat > ~/java << EOF
#!/usr/bin/env bash
source /root/.bash_profile
/etc/alternatives/java \$@
EOF
chmod +x ~/java
#rm /usr/bin/java
ln -sf ~/java /usr/bin/java

#setup jmaps for automatically mapping running java processes stack frames
wget https://raw.githubusercontent.com/craiig/remote-perf/master/java/jmaps
chmod +x jmaps
