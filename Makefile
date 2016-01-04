#set hosts via the command line or by editing this line to point at the list of 
# hosts you want to connect to.
# format:
#  user@host:port
hosts := hosts.txt
identityfile := ../spark-tests.pem
user := root

#where the flamegraph git has been cloned
flamegraphdir := ../FlameGraph/

all:

install:
	#this version of pssh is required to support the soft kill feature 
	# needed to cleanly exit perf on the remote machines
	pip install git+https://github.com/craiig/parallel-ssh

daemon-run:
	#this command below is ridiculous but neccessary:
	# sudo -b puts the command into the background properly BUT when pssh
	# disconnects, HUP gets sent and sudo hasn't finished setting up yet
	# so by adding nohup we avoid this problem!
	./pssh.py -v -l $(user) \
		--hosts=$(hosts) \
		--soft_kill \
		-i \
		-x "-oStrictHostKeyChecking=no -i $(identityfile)" \
		'echo started; mkdir -p perfdata; cd perfdata; pwd; nohup sudo -b perf record -F 99 -ag -o perf.data -- 2> perf_output.txt;'

daemon-stop:
	./pssh.py -v -l $(user) \
		--hosts=$(hosts) \
		--soft_kill \
		-i \
		-x "-oStrictHostKeyChecking=no -i $(identityfile)" \
		'sudo killall perf'

run:
	./pssh.py -v -l $(user) \
		--hosts=$(hosts) \
		--soft_kill \
		-i \
		-x "-oStrictHostKeyChecking=no -i ../spark-tests.pem" \
		'echo started; mkdir -p perfdata && cd perfdata && sudo perf record -F 99 -ag -o perf.data -- 2> perf_output.txt'
		#'echo started; ~/jmaps; mkdir -p perfdata && cd perfdata && sudo perf record -F 99 -ag -o perf.data -- 2> perf_output.txt'
get:
	./pssh.py -v -l $(user) \
		--hosts=$(hosts) \
		--soft_kill \
		-i \
		-x "-oStrictHostKeyChecking=no -i ../spark-tests.pem" \
		'cd perfdata && sudo chmod a+rw * && perf script | gzip > perf.out.gz && tar -vzcf perf-maps.tar.gz /tmp/perf-*.map'

	./pscp.py -v -l $(user) \
		--hosts=$(hosts) \
		-i \
		-x "-oStrictHostKeyChecking=no -i ../spark-tests.pem" \
		perfdata/* output/perfdata


flamegraphs := $(patsubst output/perfdata/%,output/flamegraphs/%.svg,$(wildcard output/perfdata/*))
output/perfdata/%/perf.out:  output/perfdata/%/perf.out.gz
	gzip -d -c $< > $@

output/perfdata/%/perf.data.folded:  output/perfdata/%/perf.out
	$(flamegraphdir)/stackcollapse-perf.pl $< > $@

output/flamegraphs/%.svg: output/perfdata/%/perf.data.folded
	$(flamegraphdir)/flamegraph.pl --color=java $< > $@

output/flamegraphs/:
	mkdir -p $@

#analyze: output/flamegraphs/%.svg
analyze: output/flamegraphs/ $(flamegraphs)
	
backup-perfdata:
	tar -vzcf perfdata-`date +%s`.tar.gz output/perfdata/
