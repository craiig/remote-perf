#!/usr/bin/env bash -e
./perfssh.py -v -l ec2-user \
	--hosts=../LaunchAWS/active_instance_ips.txt \
	--soft_kill \
	-i \
	-x "-oStrictHostKeyChecking=no -i ../spark-tests.pem" \
	'mkdir -p perfdata && cd perfdata && sudo perf record -ag -o perf.data -- 2> perf_output.txt'

#ssh -v ec2-user@`cat ../LaunchAWS/active_instance_ips.txt` \
	#-i ../spark-tests.pem \
	#-t -t \
	#-oStrictHostKeyChecking=no \
	#'sudo perf record -ag -o ~/perf.data -- 2> perf_output.txt'
