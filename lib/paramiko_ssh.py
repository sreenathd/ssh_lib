import paramiko
import os
import time
import logging
log = logging.getLogger(__name__)

class SSHsession():

    def __init__(self,
                 hostname="",
                 username="",
                 password="",
                 keyfile = None,
                 aws=None,
                 sftp=None,
                 port=22):
        try:
            log.info("SSH_session ip :%s, uname: %s, password :*****"  % (hostname, username))
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if keyfile:
                #print (keyfile,aws)
                keypath = '~/.ssh/' + keyfile 
                self.ssh.connect(hostname, username=username, key_filename=os.path.expanduser(keypath))
            else:
                self.ssh.connect(hostname, username=username, password=password, port=port)
                tr = self.ssh.get_transport()
                tr.default_max_packet_size = 100000000
                tr.default_window_size = 100000000
            if not sftp:
                self.shell = self.ssh.invoke_shell()
            self.password = password
            self.aws = aws
        except paramiko.AuthenticationException as e:
            log.info("Paramiko authentication exception!")
            shell = None
            print (str(e))
    
    def _read_stdout(self,stdout):
        timeout = 10
        endtime = time.time() + timeout
        while not stdout.channel.eof_received:
            time.sleep(1)
            if time.time() > endtime:
                stdout.channel.close()
                break
        return stdout.read()
                
    def send_cmd(self, cmd="ls"):
        '''
            Sends a command to ssh_session
            returns the result of the comand
            cmd : command to be executed
        '''
        try:
            log.info ("The command going to execute : ", cmd)
            stderr = None
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            stdin.close()
            line = self._read_stdout(stdout)
            log.info ("result :  " , line)
            return line
        except paramiko.SSHException as e:
            if stderr:
                print (stderr.read())
            log.info ("paramiko command execution failed...")
            log.info (str(e))
            
    def send_cmd_with_username(self, cmd="ls", usr='admin'):
        '''
            Sends a command to ssh_session
            returns the result of the command
            cmd : command to be executed
        '''
        try:
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            eusr = usr + '\n'
            stdin.write(eusr)
            stdin.flush()
            epwd = self.password + '\n'
            stdin.write(epwd)
            stdin.flush()
            stdin.close()
            line = stdout.read()
            log.info ("result : %s " % line)
            error_line = stderr.read()
            log.info ("stderr : %s " % error_line)
            return line
        
        except paramiko.SSHException as e:
            log.info (stderr.read())
            log.info ("paramiko command execution failed...")
            log.info (str(e))

    def send_cmd_with_password(self, cmd="ls"):
        '''
            Sends a command to ssh_session
            returns the result of the comand
            cmd : command to be executed
        '''
        try:
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            epwd = self.password + '\n'
            stdin.write(epwd)
            stdin.flush()
            stdin.close()
            line = stdout.read()
            log.info ("result : %s " % line)
            error_line = stderr.read()
            log.info ("stderr : %s " % error_line)
            return line
        except paramiko.SSHException as e:
            log.info (stderr.read())
            log.info ("paramiko command execution failed...")
            log.info (str(e))
            
    def send_sudo(self,cmd='ls'):
        '''
            Sends a command to ssh_session
            returns the result of the comand
            cmd : command to be executed
        '''
        if self.aws:
            return self.send_cmd(cmd=cmd)
        try:
            #print "The command going to execute : %s" % cmd
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            epwd = self.password + '\n'
            stdin.write(epwd)
            stdin.flush()
            stdin.close()
            line = stdout.read()
            log.info ("result : %s " % line)
            error_line = stderr.read()
            log.info ("stderr : %s " % error_line)
            return line
        except paramiko.SSHException as e:
            #print stderr.read()
            #print "paramiko command execution failed..."
            log.info (str(e))
    
    def send_with_password(self,cmd='ls',pass_word=''):
        '''
            Sends a command to ssh_session
            returns the result of the command
            cmd : command to be executed
        '''
        try:
            #print "The command going to execute : %s" % cmd
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            epwd = pass_word + '\n'
            stdin.write(epwd)
            stdin.flush()
            stdin.close()
            line = stdout.read()
            log.info ("result : %s " % line)
            error_line = stderr.read()
            log.info ("stderr : %s " % error_line)
            return line
        except paramiko.SSHException as e:
            #print stderr.read()
            #print "paramiko command execution failed..."
            log.info (str(e))

    def sftp_put(self, source='mongodb.list', dest='/home/ubuntu/mongodb.list'):
        '''
            Sends a file to ssh_session
        '''
        try:
            sftp = self.ssh.open_sftp()
            #print sftp, source, dest
            sftp.put( source, dest )
            sftp.close()
            #print "copied successfully!"
        except paramiko.SSHException as e:
            #print "paramiko exit failed..."
            log.info (str(e))

    def sftp_open(self):
        '''
                    download a file through ssh_session
                '''
        try:
            sftp = self.ssh.open_sftp()
            return sftp
            # print "copied successfully!"
        except paramiko.SSHException as e:
            log.info("paramiko open sftp connection failed...")
            log.info(str(e))

    def sftp_get(self, source='mongodb.list', dest='/home/ubuntu/mongodb.list'):
        '''
            download a file through ssh_session
        '''
        try:
            sftp = self.ssh.open_sftp()
            log.info ( sftp, source, dest)
            sftp.get( source, dest )
            sftp.close()
            #print "copied successfully!"
        except paramiko.SSHException as e:
            log.info ("paramiko exit failed...")
            log.info (str(e))

    def log_out(self):
        '''
            log out from ssh session
        '''
        try:
            self.ssh.close()
        except paramiko.SSHException as e:
            #print "paramiko exit failed..."
            log.info (str(e))
            
if __name__ == "__main__":
    ss = SSHsession(hostname='',keyfile='')
    print(ss.send_cmd())
