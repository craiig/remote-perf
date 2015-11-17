#!/usr/bin/env bash -e
./perfscp.py -v -l ec2-user \
	--hosts=../LaunchAWS/active_instance_ips.txt \
	-i \
	-x "-oStrictHostKeyChecking=no -i ../spark-tests.pem" \
	perfdata/* perfdatatest/

#ssh -v ec2-user@`cat ../LaunchAWS/active_instance_ips.txt` \
	#-i ../spark-tests.pem \
	#-t -t \
	#-oStrictHostKeyChecking=no \
	#'sudo perf record -ag -o ~/perf.data -- 2> perf_output.txt'

