import subprocess

USER = ''
SERVER = ''
PATH = ''
FILE = './local_file.log'
RURL = "{}@{}:{}".format(USER,SERVER,PATH)

#subprocess.run(["scp", RURL , FILE ])

resp = subprocess.Popen(["scp",RURL, FILE],
                         shell=False,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
result, err = resp.communicate()
