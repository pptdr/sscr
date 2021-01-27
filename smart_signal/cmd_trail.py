
import os, subprocess

cmd = 'aws s3 ls'
res = os.popen('ls').read()
print(res)
#try:
#    output = subprocess.check_output([cmd],shell=True).decode()
#    print("cmd_output:",output)
#except CalledProcessError as exec:#    output = exec.output   print("in exception block:",output)
