#set hosts via the command line or by editing this line to point at the list of 
# hosts you want to connect to.
# format:
#  user@host:port
hosts := hosts.txt

#where the flamegraph git has been cloned
flamegraphdir := ../FlameGraph/

all:

install:
	#this version of pssh is required to support the soft kill feature 
	# needed to cleanly exit perf on the remote machines
	pip install git+https://github.com/craiig/parallel-ssh

run:
	./pssh.py -v -l ec2-user \
		--hosts=$(hosts) \
		--soft_kill \
		-i \
		-x "-oStrictHostKeyChecking=no -i ../spark-tests.pem" \
		'mkdir -p perfdata && cd perfdata && sudo perf record -ag -o perf.data -- 2> perf_output.txt'


get:
	./pssh.py -v -l ec2-user \
		--hosts=$(hosts) \
		--soft_kill \
		-i \
		-x "-oStrictHostKeyChecking=no -i ../spark-tests.pem" \
		'cd perfdata && sudo chmod a+rw * && perf script > perf.out'

	./pscp.py -v -l ec2-user \
		--hosts=$(hosts) \
		-i \
		-x "-oStrictHostKeyChecking=no -i ../spark-tests.pem" \
		perfdata/* output/perfdata


flamegraphs := $(patsubst output/perfdata/%,output/flamegraphs/%.svg,$(wildcard output/perfdata/*))
output/perfdata/%/perf.data.folded:  output/perfdata/%/perf.out
	$(flamegraphdir)/stackcollapse-perf.pl $< > $@

output/flamegraphs/%.svg: output/perfdata/%/perf.data.folded
	$(flamegraphdir)/flamegraph.pl $< > $@

output/flamegraphs/:
	mkdir -p $@

#analyze: output/flamegraphs/%.svg
analyze: output/flamegraphs/ $(flamegraphs)
	