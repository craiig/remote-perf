#support perf-map-agent to get symbols from java JIT
RUN yum groupinstall -y 'Development Tools'
RUN yum install -y git cmake gcc-c++
RUN cd ~/ && git clone --depth=1 https://github.com/craiig/perf-map-agent
RUN cd ~/perf-map-agent/ && JAVA_HOME=/usr/java/default/ cmake . && make
ENV JAVA_TOOL_OPTIONS="-XX:+PreserveFramePointer -agentpath:/root/perf-map-agent/out/libperfmap.so"
RUN echo "export JAVA_TOOL_OPTIONS=\"-XX:+PreserveFramePointer -agentpath:/root/perf-map-agent/out/libperfmap.so\"" >> ~/.bash_profile
