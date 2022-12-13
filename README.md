# ssh_lib
Fully tested python 3 library that reduce paramkio complexity
For ubuntu apt-install python-paramiko and use as shown below

```
from lib.paramiko_ssh import SSHsession
ss = SSHsession(hostname='',keyfile='')
print(ss.send_cmd())
```
