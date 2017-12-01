import os
import time
import sys
import configparser
import urllib  
import urllib.request

from utils import SSHConnection
from utils.Const import Const

class Deploy:
    
    __config_file = ''
    config = configparser.ConfigParser()

    def __init__(self, config_file):
        self.__config_file = config_file
        print('loading config file:', self.__config_file)
        self.config.read(self.__config_file)
        print('loading config file success!')

    def deploy(self):
        start = int(round(time.time() * 1000))
        now = time.strftime('%Y%m%d_%H%M%S')

        # global
        project_name = self.config.get(Const.CONFIG_SECTIONS_GLOBAL, 'project_name')
        env = self.config.get(Const.CONFIG_SECTIONS_GLOBAL, 'env')

        # local
        project_dir = self.config.get(Const.CONFIG_SECTIONS_LOCAL, 'project_dir')
        war_location = self.config.get(Const.CONFIG_SECTIONS_LOCAL, 'war_location')

        # remote
        remote_hostname = self.config.get(Const.CONFIG_SECTIONS_REMOTE, 'hostname')
        remote_port = self.config.getint(Const.CONFIG_SECTIONS_REMOTE, 'port')
        remote_username = self.config.get(Const.CONFIG_SECTIONS_REMOTE, 'username')
        remote_password = self.config.get(Const.CONFIG_SECTIONS_REMOTE, 'password')

        remote_db_username = self.config.get(Const.CONFIG_SECTIONS_REMOTE, 'db_username')
        remote_db_password = self.config.get(Const.CONFIG_SECTIONS_REMOTE, 'db_password')
        remote_db_port = self.config.get(Const.CONFIG_SECTIONS_REMOTE, 'db_port')
        remote_db_name = self.config.get(Const.CONFIG_SECTIONS_REMOTE, 'db_name')

        tmp_dir = self.config.get(Const.CONFIG_SECTIONS_REMOTE, 'tmp_dir')
        bak_dir = self.config.get(Const.CONFIG_SECTIONS_REMOTE, 'bak_dir')
        bak_db_dir = bak_dir + '/db'
        bak_app_dir = bak_dir + '/app'

        tomcat_home = self.config.get(Const.CONFIG_SECTIONS_REMOTE, 'tomcat_home')
        app_test_url = self.config.get(Const.CONFIG_SECTIONS_REMOTE, 'app_test_url')

        key_maven_home = 'MAVEN_HOME'
        maven_home = os.getenv(key_maven_home)

        if maven_home is None:
            print('没有配置环境变量[' + key_maven_home + ']')
            return

        # 本地打包
        cmd = 'mvn -f ' + project_dir + '/pom.xml clean install -Dmaven.test.skip=true -P ' + env + ' -q'
        print('Running local command:', cmd)
        os.system(cmd)
        print('Running local command success')

        # 建立远程连接
        ssh = SSHConnection.SSHConnection(remote_hostname, remote_port, remote_username, remote_password)
        ssh.ssh_client()

        # war包上传
        ssh.upload(war_location, tmp_dir + '/everobo.war')

        # 远程数据库备份
        print('backup database....')
        ssh.exec_command('mysqldump -u' + remote_db_username + ' -p' + remote_db_password + ' ' + ' -P' + remote_db_port
                         + ' ' + remote_db_name + ' > ' + bak_db_dir + '/' + now + '.sql')
        print('backup database success')

        # 远程关闭tomcat
        print('shutdown tomcat....')
        ssh.exec_command(tomcat_home + '/bin/shutdown.sh')
        print('stop tomcat success')

        print('kill tomcat process....')
        ssh.exec_command('ps -ef | grep ' + tomcat_home + ' | grep -v grep | awk \'{print $2}\' | xargs kill -15')
        print('kill tomcat process success')

        # 远程备份应用
        print('backup webapp....')
        ssh.exec_command('cp -r ' + tomcat_home + '/webapps/everobo* ' + bak_app_dir + '/' + now)
        print('backup webapp success')

        # 远程删除工程
        print('remove project....')
        ssh.exec_command('rm -rf ' + tomcat_home + '/webapps/everobo*')
        print('remove project success')

        # 远程清空缓存
        print('remove work....')
        ssh.exec_command('rm -rf ' + tomcat_home + '/work')
        print('remove work success')

        # 远程移动war到tomcat下
        print('mv war....')
        src = tmp_dir + '/everobo.war'
        dst = tomcat_home + '/webapps/'
        ssh.exec_command('mv %s %s' % (src, dst))
        print('mv war success: %s --> %s' % (src, dst))

        # 远程启动tomcat
        print('start tomcat....')
        ssh.exec_command(tomcat_home + '/bin/startup.sh')
        print('start tomcat success')

        # 关闭连接
        ssh.close()

        print('wait tomcat to starting....')
        for i in range(1, 5):
            time.sleep(1)
            print('already wait %d second ' % i)

        # 检测是否成功
        print('connectionning ', app_test_url, '....')
        response = urllib.request.urlopen(app_test_url)
        print('connection', app_test_url, ' http code:', response.getcode())
        if response.getcode() is 200:
            print('Success!')
        else:
            print('Fail !!!')

        end = int(round(time.time() * 1000))
        print('deploy %s use time %dms.' % (project_name, (end - start)))


if __name__ == '__main__':
    deploy = Deploy((sys.argv[1]))
    deploy.deploy()
