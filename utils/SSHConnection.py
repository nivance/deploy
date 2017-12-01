import os
import paramiko

class SSHConnection:

    __hostname = ''
    __port = 22
    __username = ''
    __password = ''
    __ssh = ''

    def __init__(self, hostname, port, username, password):
        self.__hostname = hostname
        self.__port = port
        self.__username = username
        self.__password = password

    def ssh_client(self):
        print('ssh %s@%s ....' % (self.__username, self.__hostname))
        try:
            self.__ssh = paramiko.SSHClient()
            self.__ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__ssh.connect(hostname=self.__hostname, username=self.__username, port=self.__port,
                               password=self.__password)
            print('ssh %s@%s success!!!' % (self.__username, self.__hostname))
        except Exception as e:
            print('ssh %s@%s: %s' % (self.__username, self.__hostname, e))
            return

    def exec_command(self, command):
        # print('command:', command)
        stdin, stdout, stderr = self.__ssh.exec_command(command)
        err_list = stderr.readlines()
        if len(err_list) > 0:
            print('ssh exec remote command [%s] error: %s' % (command, err_list[0]))
            return False
        else:
            return True

    def upload(self, src, dst):
        try:
            sftp = self.__ssh.open_sftp()
        except Exception as e:
            print('open sftp failed:', e)
            return

        try:
            print('uploading file: %s --> %s' % (src, dst))
            sftp.put(src, dst)
            print('uploaded file: %s --> %s' % (src, dst))
            sftp.close()
        except Exception as e:
            print('uploading file failed:', e)
            return

    def close(self):
        self.__ssh.close()

    def upload_dir(self, srcdir, dstdir):
        try:
            sftp = self.__ssh.open_sftp()
        except Exception as e:
            print('open sftp failed:', e)
            return

        try:
            print('starting to upload dir: %s -->>> %s' % (srcdir, dstdir))
            for dirpath, dirnames, filenames in os.walk(srcdir):
                if dirpath.find(".") > 0:   # 隐藏文件忽略
                    continue
                else:
                    # print("dirpath:", dirpath)
                    for dirname in dirnames:
                        if dirname.startswith(".") > 0: # 隐藏文件忽略
                            continue
                        # print("dirname:", dirname)
                    for filename in filenames:
                        # print("filename:", filename)
                        if filename.startswith(".") is False:     # 过滤隐藏文件(.开头的文件)
                            localpath = os.path.join(dirpath, filename)
                            remotefile = str(dstdir + localpath[len(srcdir):len(localpath)]).replace('\\', '/')
                            if self.check_remote_dir_exit(remotefile) is True:
                                sftp.put(localpath, remotefile)
                                print('uploaded file::::: %s -->>>> %s' % (localpath, remotefile))
            sftp.close()
        except Exception as e:
            print('uploading file failed:', e)
            return

    def check_remote_dir_exit(self, remotefile):
        command = 'ls ' + os.path.dirname(remotefile)
        try:
            if self.exec_command(command) is True:
                # print('parant dir: [%s] exist' % os.path.dirname(remotefile))
                return True
            else:
                # print('parant dir: [%s] not exist' % os.path.dirname(remotefile))
                command = 'mkdir ' + os.path.dirname(remotefile)
                if self.exec_command(command) is True:
                    print('parant dir: [%s] is created' % os.path.dirname(remotefile))
                    return True
                else:
                    print('parant dir: [%s] created fail.' % os.path.dirname(remotefile))
                    raise Exception('[%s] created fail' % os.path.dirname(remotefile))
        except Exception as e:
            raise Exception('execute command::: %s ::: failed.' % command, e)



