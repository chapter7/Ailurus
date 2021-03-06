#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Ailurus - make Linux easier to use
#
# Copyright (C) 2007-2010, Trusted Digital Technology Laboratory, Shanghai Jiao Tong University, China.
#
# Ailurus is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ailurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ailurus; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

from __future__ import with_statement
import sys, os
from ailurus.lib import *
from ailurus.libapp import *

if not ( Config.is_Ubuntu() or Config.is_Mint() ):
    raise Exception

class Alice(_path_lists):
    __doc__ = _('Alice: A new way to learn programming')
    detail = (
              _('A storytelling application, especially appropriate for middle school students.') +'\n' + 
              _('Official site: <span color="blue"><u>http://www.alice.org/</u></span> .') + 
              _(' This application depends on Java.') )
    category = 'education'
    def __init__(self):
        self.dir = '/opt/Alice 2.2'
        self.shortcut = '/usr/share/applications/alice.desktop'
        self.paths = [ self.dir, self.shortcut ]
    def install(self):
        if get_arch()==32:
            f = R(
['http://tdt.sjtu.edu.cn/S/Alice2.2b_i386.tar.bz2',],
296544228, '0c6340a5b52d72abc12c394561d61c3ccba21ca7').download()
        else:
            f = R(
['http://tdt.sjtu.edu.cn/S/Alice2.2b_x86_64.tar.bz2',],
296519582, '7558fa7f22d13f8d18671b3efc44374541c5a506').download()

        import os
        if not os.path.exists('/opt'):
            run_as_root('mkdir /opt')
        own_by_user('/opt')
        with Chdir('/opt') as o:
            run('tar jxf '+f)
            assert os.path.exists(self.dir)
            create_file(self.shortcut, '''[Desktop Entry]
Name=Alice
Exec=bash "/opt/Alice 2.2/Required/alice.sh"
Path=/opt/Alice 2.2/Required/
Encoding=UTF-8
StartupNotify=true
Terminal=false
Type=Application
Categories=Education;Science; ''')

class AliPayFirefoxPlugin(I):
    __doc__ = _('Alipay ( Zhi Fu Bao ) security plugin for Firefox')
    detail = _("Official site: <span color='blue'><u>http://blog.alipay.com/301.html</u></span>")
    category = 'firefox'
    Chinese = True
    def __init__(self):
        import os
        self.path = os.path.expanduser('~/.mozilla/plugins')
    def install(self):
#        open_web_page('http://blog.alipay.com/301.html')
        file = '/tmp/aliedit.tar.gz'
        run('wget --timeout=60 http://blog.alipay.com/wp-content/2008/10/aliedit.tar.gz -O /tmp/aliedit.tar.gz')
        path = self.path
        import os
        if not os.path.exists(path):
            run('mkdir -p %s'%path)
        with Chdir(path) as o:
            run('tar zxf %s'%file)
    def installed(self):
        import os
        return (
          (os.path.exists(self.path+'/aliedit.so') and os.path.exists(self.path+'/aliedit.xpt'))
             or
          (os.path.exists('/usr/lib/firefox-addons/plugins/aliedit.so')
             and os.path.exists('/usr/lib/firefox-addons/plugins/aliedit.xpt'))
          )
    def remove(self):
        run('rm -f %s'%(self.path+'/aliedit.so') )
        run('rm -f %s'%(self.path+'/aliedit.xpt') )
        if os.path.exists('/usr/lib/firefox-addons/plugins/aliedit.so'):
            run_as_root('rm -f /usr/lib/firefox-addons/plugins/aliedit.so')
        if os.path.exists('/usr/lib/firefox-addons/plugins/aliedit.xpt'):
            run_as_root('rm -f /usr/lib/firefox-addons/plugins/aliedit.xpt')
    def support(self):
        import os
        return os.path.exists('/usr/bin/firefox')

class AstroMenace(_path_lists):
    'AstroMenace'
    detail = _('Drive a spaceship and battle against invaders! Collect money during the combat. Upgrade armaments and weapons. '
       'This is a full 3d style space shooter game. '
       'It supports mouse, keyboard and joystick control. '
       'Official site: http://www.viewizard.com/')
    category = 'game'
    def __init__(self):
        self.paths = ['/opt/astromenace', '/usr/share/applications/astromenace.desktop']
    def install(self):
        f = R(
['http://www.viewizard.com/download/amenace12.tar.bz2'],
35948638, '752d6faec7a4432f991055ab788b1e7dba004995').download()

        import os
        if not os.path.exists('/opt'): run_as_root('mkdir /opt')
        run_as_root('chown $USER:$USER /opt')
        with Chdir('/opt') as o:
            run('tar xf %s'%f)
            create_file('/usr/share/applications/astromenace.desktop', 
'''[Desktop Entry]
Name=AstroMenace
Exec=/opt/astromenace/game_launcher
Path=/opt/astromenace/
Icon=/opt/astromenace/astromenace_64.png
Encoding=UTF-8
StartupNotify=true
Terminal=false
Type=Application
Categories=Game;''')

#class EIOffice:
#    __doc__ = _('Evermore Integrated Office 2009 free version')
#    detail = _('It is able to edit text, spreadsheets, and slides. '
#       'Official site: <span color="blue"><u>http://www.evermoresw.com.cn/webch/download/downEIOPersonal.jsp</u></span>')
#    category='office'
#    Chinese = True
#    time=112
#    size=217428*1000
#    def install(self):
#        with Chdir('/tmp') as o:
#            f = R('http://218.90.147.70/EverMore/EIOPersonal/EIOffice_Personal_Lin.tar.gz').download()
#            run('tar xf %s' % f)
#            run('chmod a+x EIOffice_Personal_Lin/setup')
#            run_as_root("EIOffice_Personal_Lin/setup")
#            
#            msgs = ( 
#                     _('Clipboard arts are to be installed.'),
#                     _('Help files are to be installed.'),
#                     _('Science editor images are to be installed.'),
#                     _('Templates are to be installed.')
#                        )
#            for file, msg in zip(
#               ['http://218.90.147.70/EverMore/EIOPersonal/Resource/EIOffice_Clipart.tar.gz',
#                'http://218.90.147.70/EverMore/EIOPersonal/Resource/EIOffice_HelpFiles.tar.gz',
#                'http://218.90.147.70/EverMore/EIOPersonal/Resource/EIOffice_ScienceEditorImages.tar.gz',
#                'http://218.90.147.70/EverMore/EIOPersonal/Resource/EIOffice_Templates.tar.gz',], msgs):
#                    wget(file, '/tmp/eio.tar.gz') 
#                    run("tar zxf /tmp/eio.tar.gz")
#                    notify( _('Installing EIOffice'), msg )
#                    run_as_root("./setup")
#    def installed(self):
#        import os
#        return os.path.exists('/usr/bin/eio')
#    def remove(self):
#        import os
#        if os.path.exists('/usr/bin/rmeio'):
#            run_as_root('/usr/bin/rmeio')

class ChineseAcademyofSciencesTeXTemplate(_download_one_file) :
    # cannot find out which license it is released under
    __doc__ = _('LaTeX Thesis Templates by Chinese Academy of Sciences')
    import os
    detail = _('After installation, a file "CASthesis.zip" is placed in the folder "%s".')%os.path.expanduser('~')
    category = 'latex'
    Chinese = True
    def __init__(self):
        self.R = R(
['http://tdt.sjtu.edu.cn/S/CASthesis-v0.1j.zip',],
244765, 'dc84597ee626b7a2dcd3ee8825d2e374f6822197')
        import os
        self.file = os.path.expanduser('~/CASthesis.zip')
     
class XJTUTeXTemplate(_download_one_file) :
    # cannot find out which license it is released under
    __doc__ = _("LaTeX Thesis Templates by Xi\'an Jiaotong University, China")
    import os
    detail = _('After installation, a file "XJTUthesis.rar" is placed in the folder "%s".')%os.path.expanduser('~')
    category = 'latex'
    Chinese = True
    def __init__(self):
        self.R = R(
['http://tdt.sjtu.edu.cn/S/XJTUthesis.rar',],
3009431, '88ce43f6396d76fff56b597a2a35487548fdaa54')
        import os
        self.file = os.path.expanduser('~/XJTUthesis.rar')

class HITTeXTemplate(_download_one_file) :
    # cannot find out which license it is released under
    __doc__ = _('LaTeX Thesis Templates by Harbin Institute of Technology, China')
    import os
    detail = _('After installation, a file "HITthesis.rar" is placed in the folder "%s".')%os.path.expanduser('~')
    category = 'latex'
    Chinese = True
    def __init__(self):
        self.R = R(
['http://plutothesis.googlecode.com/files/PlutoThesis_UTF8_1.9.2.20090424.zip'],
2710034, 'aee937bf0a09936d78f57cd45616997af7a1ef3c')
        import os
        self.file = os.path.expanduser('~/HITthesis.rar')

class FFJavaScriptDebugger(_ff_extension): # cannot find out which license it is released under
    __doc__ = _('JavaScript Debugger: a powerful JavaScript debugger')
    category = 'firefoxdev'
    def __init__(self):
        self.desc = ''
        self.download_url = 'https://addons.mozilla.org/en-US/firefox/addon/216'
        self.range = '0.9~3.7'
        self.name = u'JavaScript Debugger'
        self.R = R(['http://releases.mozilla.org/pub/mozilla.org/addons/216/javascript_debugger-0.9.87.4-fx+tb+sb+sm.xpi'],
                      217578,'3369de2b98b747c4d1c79803819b2d727b9083f6')
        _ff_extension.__init__(self)

class FFMacOSXTheme(_ff_extension): # cannot find out which license it is released under
    __doc__ = _('Mac OS X Theme')
    def __init__(self):
        self.desc = ''
        self.download_url = 'https://addons.mozilla.org/en-US/firefox/addon/7172'
        self.range = '3.0.*~3.7.*'
        self.name = u'MacOSX Theme'
        self.R = R(['http://releases.mozilla.org/pub/mozilla.org/addons/7172/macosx_theme-0.6.8-fx.jar'],
    689344, '4b58d1c49ae123e50a76cb41bc6a1162d1bcaaf8')
        _ff_extension.__init__(self)

class FFNetVideoHunter(_ff_extension): # cannot find out which license it is released under
    __doc__ = _('NetVideoHunter: Download videoclips from video-sharing web sites')
    def __init__(self):
        self.desc = ''
        self.download_url = 'https://addons.mozilla.org/en-US/firefox/addon/7447'
        self.range = '2.0~3.7'
        self.name = u'NetVideoHunter'
        self.R = R(['http://releases.mozilla.org/pub/mozilla.org/addons/7447/netvideohunter-0.4.3-fx.xpi'],
                    44541, '3d47e726587743758097a069358ed306df63bc3a')
        _ff_extension.__init__(self)

class FFPersonas(_ff_extension): # cannot find out which license it is released under
    __doc__ = _('Personas: One-click changing Firefox skin')
    def __init__(self):
        self.desc = _('Theme your browser according to your mood, hobby or season.')
        self.download_url = 'https://addons.mozilla.org/en-US/firefox/addon/10900'
        self.range = '3.0~3.6.*'
        self.name = u'Personas'
        self.R = R(['http://releases.mozilla.org/pub/mozilla.org/addons/10900/personas-1.4-fx+tb.xpi'],
    275501, 'ac6de4e93270e0650fc06a88cf5fe639e8a879fb')
        _ff_extension.__init__(self)
        
class GoogleEarth(I):
    __doc__ = _('Google Earth')
    detail = _('Please install it in /opt/google-earch. Otherwise it cannot be detected.')
    category = 'game'
    def install(self):
        f = R('http://dl.google.com/earth/client/current/GoogleEarthLinux.bin', 25989559, 'e64f2840bf7161b9860c4d99e9de0c27f960e131').download()
        os.system('chmod a+x ' + f)
        run_as_root_in_terminal(f)
    def installed(self):
        return os.path.exists('/opt/google-earth')
    def remove(self):
        run_as_root_in_terminal('/opt/google-earth/uninstall')