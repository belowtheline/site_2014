@dir = '/home/btl/site/api/'

worker_processes 2
working_directory @dir

timeout 30

listen "/home/btl/run/ballot.sock"

stderr_path "/home/btl/logs/ballot.err.log"
stdout_path "/home/btl/logs/ballot.out.log"

user 'btl', 'btl'
