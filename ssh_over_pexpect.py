import pexpect

def tries(c):
    for tries in range(5):
        c.send('\r')
        cli = c.expect([pexpect.TIMEOUT, '$ ' , 'T440:~$ '], timeout=1)
        if cli!=0: 
            break

c = pexpect.spawn('/usr/bin/ssh sreenath@127.0.0.1', timeout=120)
fout = open("/tmp/mylog", "bw")
c.logfile = fout
c.expect('password:', timeout=120)
c.sendline('siddharth')
tries(c)
#print(c.before)
c.sendline('ls -latr')
tries(c)
fout.close()
