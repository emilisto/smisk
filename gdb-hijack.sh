gdb /usr/local/bin/python2.5 `ps ax| grep process.py | grep -v "grep" | cut -d " " -f 1`
