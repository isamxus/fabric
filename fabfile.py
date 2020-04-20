#!/usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.api import *
from fabric.operations import sudo
from config import ip,domain,username,password,gitHome,UserName,PassWord
#env.user = 'ubuntu'
#env.hosts = ['106.54.225.43']
#env.password = 'ZYMzym980413~!@'

env.user = username
env.hosts = [ip]
env.password = password
gitHome = gitHome
domain = domain
#domain = 'www.yimingz.club'


class deploySettings(object):
	UserName = UserName
	PassWord = PassWord
	#创建用户
	def createUser(self):
		Pass = False
		while not Pass:
			if not self.UserName:
				self.UserName = input('请输入用户名')
				continue
			if not self.PassWord:
				self.PassWord = input('请输入密码')
				continue
			ConfirmPassWord = input('请再次输入密码')
			if ConfirmPassWord != self.PassWord:
				print('两次输入密码不一致')
				self.UserName = None
				self.PassWord = None
				continue
			Pass = True
		with settings(warn_only=True):
			run('sudo useradd -m -s /bin/bash ' + self.UserName)
			run('sudo usermod -a -G sudo ' + self.UserName)
			run('echo sudopsw | sudo -S echo "' + self.UserName + '":"' + self.PassWord + '" | sudo chpasswd')

	#更新系统
	def updateSystem(self):
		run('sudo apt-get -y update')
		run('sudo apt-get -y upgrade')
		run('sudo apt-get -y install nginx')
		run('sudo apt-get -y install git python3 python3-pip')
		run('sudo apt-get -y install virtualenv')
		run('sudo service nginx start')

	#从仓库地址拉取项目
	def gitclone(self):
		with settings(warn_only=True):
			run('sudo git clone ' + gitHome+ ' /home/' + self.UserName + '/blogManagement')

	#安装虚拟环境
	def setupVirtualenv(self):
		run('sudo chmod 777 /home/' + self.UserName + '/')
		with cd('/home/' + self.UserName + '/'):
			run('sudo chmod 777 blogManagement/')
			run('virtualenv --python=python3 env')
			run('source env/bin/activate')

	#安装项目依赖
	def setupRequirement(self):
		with cd('/home/' + self.UserName + '/blogManagement/'):
			run('ls')
			with settings(warn_only=True):
				run('pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt')
				run('pip3 install gunicorn')		


	#放置配置文件
	def setConfig(self):
		with settings(warn_only=True):
			put('C:\\Users\\Administrator\\Desktop\\deploy\\amxusli.conf', '/home/'+ self.UserName+ '/blogManagement')
		with cd('/home/' +self.UserName + '/blogManagement'):
			run('ls')
			run('sudo mv amxusli.conf /etc/nginx/sites-available')
			run('sudo chmod 777 /etc/nginx/sites-available/amxusli.conf')
		with settings(warn_only=True):
			run('sudo ln -s /etc/nginx/sites-available/amxusli.conf /etc/nginx/sites-enabled/amxusli.conf')

	#gunicorn部署
	def gunicornSetting(self):
		with cd('/home/' + self.UserName + '/blogManagement'):
			run('../env/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt')
			run('../env/bin/pip install gunicorn')
			run('../env/bin/python3 manage.py makemigrations')
			run('../env/bin/python3 manage.py migrate')
			run('sudo service nginx stop')
			run('sudo service nginx start')
			run('../env/bin/gunicorn --bind unix:/tmp/' + domain + '.socket myblogdjango.wsgi:application')

	#执行部署函数
	def init(self):
		self.createUser()
		self.updateSystem()
		self.gitclone()
		self.setupVirtualenv()
		self.setupRequirement()
		self.setConfig()
		self.gunicornSetting()



#部署博客命令
def init():
	exp = deploySettings()
	exp.init()

#初始化博客数据
def initData():
	with cd('/home/' + UserName + '/blogManagement'):
		run('python3 InitBlogData.py')

#更新代码
def update():
	with cd('/home/' + UserName + '/blogManagement'):
		run('git fetch -v --progress "https://github.com/isamxus/blogManagement.git" ljc')
		run('git merge FETCH_HEAD')
	exp = deploySettings()
	exp.gunicornSetting()



def test():
	with cd('..'):
		local('dir')