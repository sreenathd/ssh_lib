from csv import reader, writer 
import csv
import pexpect
import subprocess
from itertools import izip_longest

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
        #self.c.expect('password:', timeout=120)
        #self.c.sendline(self.password)
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

def compare_logfiles(files):
    #this function compare all the log files and prints the output to console
    missing_dict = {}
    for file in files:
        server_name = file#file.split('/')[-1].split('_')[0]
        file_path = '/tmp/' + file
        with open (file_path, 'r') as efil:
            missing_dict[file] = {}
            ls_lines = []
            for line in efil:
                if len(line)>1:
                    if 'ls -latr' in line and line.split()[-1] not in ls_lines:
                        ls_lines.append(line.split()[-1])
                        folder = line.split()[-1]
                        if line.split()[-1] not in missing_dict[file].keys():
                            missing_dict[file][folder] = []
                    line = line.replace('\x1b[0m','').replace('\x1b[01;34m','').replace('\x1b[01;36m','').replace('\x1b[01;32m','').replace('\x1b[01;31m','').replace('\x1b[K','')
                    line = line.replace('\x1b[40;31;01m','').replace('\x1b[01;05;37;41m','')
                    compser = line.split()
                    if len(compser) > 8  and 'fxall fxall' in line and not line.startswith('d'):
                        if len(compser) == 9 and compser[8] not in ['.','..']:
                            if compser[8] not in missing_dict[file][folder]:
                                missing_dict[file][folder].append(compser[8])
                        if len(compser) == 11 and compser[10] not in ['.','..']:
                            link_name = ' '.join(compser[8:])
                            if compser[8] not in missing_dict[file][folder]:
                                missing_dict[file][folder].append(link_name)
    return missing_dict

def Diff(li1, li2):
    li_dif = []
    for i in li1 + li2:
        if i not in li1:
            if '->' in i:
                flag = True
                for afile in li1:
                    if afile.split('->')[0] == i.split('->')[0]:
                        li_dif.append('(D)' + i)
                        flag = False
                if flag:
                    li_dif.append('(A)' + i)   
            else:
                li_dif.append('(A)' + i)
        if i not in li2 :
            if  '->' in i:
                li_dif.append('(M)' + i)
            else:
                li_dif.append('(M)' + i)   
    if len(li_dif) == 0:
        li_dif.append('Match')  
    #li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

if __name__ == '__main__':
    server00 = readServer00()
    print ('connecting to Server00 and reading the content')
    server00.read_server00_contents()
    server00.process_server00_log()
    #creating the list of servers, append new servers to the list below
    server_list = ['nycdev00', 'nycdev01','nycdev02','nycdev03','nycdev04']
    #server_list = ['nycdev01','nycdev02','nycdev03','nycdev04','nycdev05','nycdev06','nycdev07','nycdev08' ,'nycdev09']
    #the below loop connect to each servers and send the commands and collect the logs to /tmp folder
    for server in server_list:
        print ('connecting to the server:%s and listing the content'%(server))
        sh_shell = sshPexpect('fxall','',server, logfile = '/tmp/' + server)
        try:
            sh_shell.connect()
            #sh_shell.send_cmd_passwd('sudo su - fxall')
            sh_shell.send_cmd('ls -latr /opt/fxall/core/apps')
            sh_shell.send_cmd('ls -latr /opt/fxall/core/commands')
            sh_shell.send_cmd('ls -latr /opt/fxall/core/tools')
            sh_shell.close_session()
        except Exception, e:
            print ('There is an error: %s when connecting over ssh to server:%s '%(str(e), server))
    
    server_contents = compare_logfiles(server_list)
    folder_list = ['/opt/fxall/core/apps','/opt/fxall/core/commands','/opt/fxall/core/tools']
    line = ''
    
    for folder in folder_list:
        print ('now comparing folder:%s '%(folder))
        csv_name = folder.split('/')[-1] + '.csv'
        with open(csv_name, 'w') as csvfile:
            line = folder + ',#of files' + ','.join([',' for x in server_contents[server_list[0]][folder]]) +  '\n'
            csvfile.write(line)
            line = server_list[0] + ',' + str(len(server_contents[server_list[0]][folder])) + ',' + ','.join(server_contents[server_list[0]][folder]) + '\n'
            csvfile.write(line)
            for server in server_list[1:]:
                print ('now process diff for server:%s '%(server))
                diff_l = Diff(server_contents[server_list[0]][folder],server_contents[server][folder])
                print ('diff between server:%s and server:%s is: [ %s ]'%(server_list[0], server, ','.join(diff_l)))
                line = server + ',' + str(len(server_contents[server][folder])) + ',' + ','.join(diff_l) + '\n'
                csvfile.write(line)

        with open('out_' + csv_name, 'wb') as outfile, open(csv_name, 'rb') as infile:
            a = izip_longest(*csv.reader(infile))
            csv.writer(outfile).writerows(a)
