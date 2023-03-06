import pexpect

class sshPexpect:
    def __init__(self,username, passwd, servername, logfile = "/tmp/mylog" ):
        self.username = username
        self.password = passwd
        self.servername = servername
        self.log_file = open(logfile, "w")
    
    def tries(self,c):
        for tries in range(5):
            c.send('\r')
            cli = c.expect([pexpect.TIMEOUT, '$ ' , '~$ '], timeout=1)
            if cli!=0: 
                break
                
    def connect(self):
        self.c = pexpect.spawn('/usr/bin/ssh ' + self.username+ '@' + self.servername, timeout=120)
        self.c.logfile = self.log_file
        self.c.expect('password:', timeout=120)
        self.c.sendline(self.password)
        self.tries(self.c)
    
    def send_cmd(self, cmd):
        self.c.sendline(cmd)
        self.tries(self.c)
        
    def send_cmd_passwd(self, cmd, passwd=None):
        self.c.sendline(cmd)
        prompt = self.username + ':'
        self.c.expect(prompt, timeout=120)
        if passwd:
            self.c.sendline(passwd)
        else:
            self.c.sendline(self.password)
        self.tries(self.c)
        
    def close_session(self):
        self.c.close()
        self.log_file.close()
        
def compare_logfiles(files):
    #this function compare all the log files and prints the output to console
    ref_list = []
    with open (files[0], 'r') as ref:
        for line in ref:
            ref_list.append(line)
    for file in files[1:]:
        ref_file_list = []
        comp_file_list = []
        with open (file, 'r') as efil:
            index = 0
            for line in efil:
                if len(line)>1:
                    if line.startswith ('ls -latr'):
                       print("Now comparing diff of folder : %s"%(line.split()[-1]))

                    compser = line.split()
                    if len(compser) >= 8  and 'fxall fxall' in line and file not in files[0]:
                        refserv = ref_list[index].split()
                        #try:
                        #print(len(compser))
                        if len(compser) == 9 and len(refserv)==9 and compser[8] in refserv[8]:
                            comp_file_list.append(compser[8])
                            ref_file_list.append(refserv[8])
                           #print("comparing failed index:%s, %s:%s and %s:%s "%(index,file,refserv[-1],files[0],compser[-1]))
                        if len(compser) == 11 and len(refserv)==11:
                            if compser[10] not in refserv[10]:
                                comp_file_list.append(' '.join(compser[8:]))
                                ref_file_list.append(' '.join(refserv[8:]))
                               #print("comparing failed  index:%s,%s:%s and %s:%s "%(index,file,refserv[8:],files[0],compser[8:]))
                        #except :
                            #print("error")
                index = index + 1
        print("differences between server : %s and server : %s"%(file, files[0]))
        print (list(set(comp_file_list).difference(set(ref_file_list))))
        
if __name__ == '__main__':
    server_list = ['127.0.0.1']
    log_file_list = ['/tmp/' + i for i in server_list]
    for server in server_list:
        sh_shell = sshPexpect('user','pswd',server, logfile = '/tmp/' + server)
        sh_shell.connect()
        sh_shell.send_cmd_passwd('sudo su - fxall')
        sh_shell.send_cmd('ls -latr')
    compare_logfiles(log_file_list)
            
    
