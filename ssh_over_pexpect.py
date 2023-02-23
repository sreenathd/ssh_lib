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
            cli = c.expect([pexpect.TIMEOUT, '$ ' , '*~$ '], timeout=1)
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
        self.c.expect('password:', timeout=120)
        if passwd:
            self.c.sendline(passwd)
        else:
            self.c.sendline(self.password)
        self.tries(self.c)
        
    def close_session(self):
        self.c.close()
        self.log_file.close()

if __name__ == '__main__':
    server_list = [127.0.0.1]
    for server in server_list:
        sh_shell = sshPexpect('user','pswd',server)
        sh_shell.connect()
        sh_shell.send_cmd('sudo su fxall')
        sh_shell.send_cmd('ls -latr')
    
