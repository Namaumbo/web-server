import os

from pip._vendor.distlib.compat import raw_input

project = raw_input(u'name of project')
domain = raw_input(u'enter doamin')
docroot = raw_input(u'enter root folder')

virtualhost = u"""
<VirtualHost *:80>
    DocumentRoot /%(docroot)s/%(project)s
    ServerName %(project)s.%(domain)s.com
    ErroLog logs/%(project)s.com-error_log
    CustomLog logs/%(project)s.com-access_log common
    </virtualHost>"""
f = open(u'/etc/httpd/conf/httpd.conf', u'a')
f.write(virtualhost % dict(project=project, docroot=docroot, domain=domain))
f.close()


