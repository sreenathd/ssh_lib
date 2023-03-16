import pexpect
import subprocess

class readServer00:
    def __init__(self):
        self.server00_file_list = []
        self.server00_log_file = 'server00.log'

    def read_server00_contents(self):
        #This function execute extract rpm and list the content to a logfile.
        cmd_list = [['ls', '-latr','/opt/fxall/core/apps'],['ls','-latr','/opt/fxall/core/commands'], ['ls','-latr','/opt/fxall/core/tools']]
        with open(self.server00_log_file, 'w') as logfile:
            for cmd in cmd_list:
                subprocess.call(cmd, stdout=logfile, shell=False)

    def process_server00_log(self):
        #This function will read the rpm content file and create a data structure of file name and size.
        with open (self.server00_log_file, 'r') as efil:
            index = 0
            for line in efil:
                if len(line)>1:
                    if line.startswith ('ls -latr'):
                       print("Now reading the folder : %s"%(line.split()[-1]))
                    # line = line.replace('template/', '')
                    compser = line.split()
                    if len(compser) >= 8  and compser[8] not in ['.','..'] and not line.startswith('d'):
                        if len(compser) == 9 :
                            self.server00_file_list.append(compser[8] + "=" + compser[4])
                        if len(compser) == 11 :
                            self.server00_file_list.append(' '.join(compser[8:]) + "=" + compser[4])


class sshPexpect:
    #initalizations the common variables
    def __init__(self,username, passwd, servername, logfile = "/tmp/mylog" ):
        self.username = username
        self.password = passwd
        self.servername = servername
        self.log_file = open(logfile, "w")

    def tries(self,c):
        #this function send the retuen key for 5 times and wait for the prompt
        for tries in range(5):
            c.send('\r')
            cli = c.expect([pexpect.TIMEOUT, '$ ' , '~$ '], timeout=1)
            if cli!=0:
                break

    def connect(self):
        #this function create a new ssh connection to the server using password authentication
        self.c = pexpect.spawn('/usr/bin/ssh ' + self.username+ '@' + self.servername, timeout=120)
        self.c.logfile = self.log_file
        self.c.expect('password:', timeout=120)
        self.c.sendline(self.password)
        self.tries(self.c)

    def send_cmd(self, cmd):
        #this function sends commands to the already open ssh session
        self.c.sendline(cmd)
        self.tries(self.c)

    def send_cmd_passwd(self, cmd, passwd=None):
        #this function sends commands to the already open ssh session with sudo password
        self.c.sendline(cmd)
        prompt = self.username + ':'
        self.c.expect(prompt, timeout=120)
        if passwd:
            self.c.sendline(passwd)
        else:
            self.c.sendline(self.password)
        self.tries(self.c)

    def close_session(self):
        #this function close the ssh session
        self.c.close()
        self.log_file.close()

def compare_logfiles(files, referece_list):
    #this function compare all the log files and prints the output to console
    reference_file_name_list = [item.split('=')[0] for item in referece_list]
    # print (reference_file_name_list)
    for file in files:
        flag = 1
        ref_file_list = []
        comp_file_list = []
        server_name = file.split('/')[-1].split('_')[0]
        if flag:
            print('No difference found for server: %s'%(server_name))
        with open (file, 'r') as efil:
            ls_lines = []
            for line in efil:
                if len(line)>1:
                    if 'ls -latr' in line and line.split()[-1] not in ls_lines:
                       ls_lines.append(line.split()[-1])
                       print("Now comparing diff of server : %s for folder : %s"%(server_name, line.split()[-1]))
                    line = line.replace('\x1b[0m','').replace('\x1b[01;34m','').replace('\x1b[01;36m','').replace('\x1b[01;32m','').replace('\x1b[01;31m','').replace('\x1b[K','')
                    compser = line.split()
                    if len(compser) > 8  and 'fxall fxall' in line and not line.startswith('d'):
                        if len(compser) == 9 and compser[8] not in ['.','..']:
                            if compser[8] in reference_file_name_list:
                                #print (compser[8])
                                for item in referece_list:
                                    if 'compser[8]' in item:
                                        if compser[4] in item.split('=')[1]:
                                            pass
                                        else:
                                            print("comparing failed for server: %s file_name: %s for size diff"%(server_name, compser[8]))
                            else:
                                flag = 0
                                print("comparing failed for server: %s file_name: %s "%(server_name, compser[8]))

                        if len(compser) == 11 and compser[10] not in ['.','..']:
                            link_name = ' '.join(compser[8:])
                            if link_name in reference_file_name_list:
                                pass
                            else:
                                flag = 0
                                print("comparing failed for server: %s file_name: %s "%(server_name, link_name))
            
def remove_extra_characters(files):
    for file in files:
        with open( '/tmp/' + file + '_', 'w') as logfile:
            file = '/tmp/' + file
            cmd = ['cat' , file ]
            subprocess.call(cmd, stdout=logfile, shell=False)

if __name__ == '__main__':
    server00 = readServer00()
    print ('connecting to Server00 and reading the content')
    server00.read_server00_contents()
    server00.process_server00_log()
    #print(server00.server00_file_list)
    #creating the list of servers, append new servers to the list below
    server_list = ['nycdev01','nycdev02']
    #remove_extra_characters(server_list)
    #log_file_list = ['/tmp/' + i + '_' for i in server_list]
    #the below loop connect to each servers and send the commands and collect the logs to /tmp folder
    for server in server_list:
        print ('connecting to the server:%s and listing the content'%(server))
        sh_shell = sshPexpect('uc507032','Startedlseg@2022',server, logfile = '/tmp/' + server)
        sh_shell.connect()
        sh_shell.send_cmd_passwd('sudo su - fxall')
        sh_shell.send_cmd('ls -latr /opt/fxall/core/apps')
        sh_shell.send_cmd('ls -latr /opt/fxall/core/commands')
        sh_shell.send_cmd('ls -latr /opt/fxall/core/tools')
        sh_shell.close_session()
    remove_extra_characters(server_list)
    log_file_list = ['/tmp/' + i + '_' for i in server_list]
    compare_logfiles(log_file_list,server00.server00_file_list)
