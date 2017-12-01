# -*- coding:utf-8 -*-

from utils import SSHConnection

from deploy import Deploy
import sys
from utils.Const import Const

class UploadFile (Deploy):
    """上传文件到远程服务器"""
    srcdir = ""
    destdir = ""

    def __init__(self, config_file):
        super(UploadFile, self).__init__(config_file)
        # srcdir = Deploy.config.get(Const.CONFIG_SECTIONS_LOCAL, 'localdir')
        # destdir = Deploy.config.get(Const.CONFIG_SECTIONS_REMOTE, 'remotedir')

    def upload(self):
        remote_host = Deploy.config.get(Const.CONFIG_SECTIONS_REMOTE, 'hostname')
        remote_port = Deploy.config.getint(Const.CONFIG_SECTIONS_REMOTE, 'port')
        remote_user = Deploy.config.get(Const.CONFIG_SECTIONS_REMOTE, 'username')
        remote_passwd = Deploy.config.get(Const.CONFIG_SECTIONS_REMOTE, 'password')
        print('romote_host: ', remote_host, ", remote_user: ", remote_user)

        # 建立远程连接
        ssh = SSHConnection.SSHConnection(remote_host, remote_port, remote_user, remote_passwd)
        ssh.ssh_client()
        # 上传
        srcdir = Deploy.config.get(Const.CONFIG_SECTIONS_LOCAL, 'localdir')
        destdir = Deploy.config.get(Const.CONFIG_SECTIONS_REMOTE, 'remotedir')
        ssh.upload_dir(srcdir, destdir)


if __name__ == '__main__':
    upload = UploadFile(sys.argv[1])
    # upload.upload(upload.srcdir, upload.destdir)
    upload.upload()
