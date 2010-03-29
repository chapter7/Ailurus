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
from lib import *

#class Open_Repogen_Website:
#    __doc__ = _('* Find more repositories on http://repogen.simplylinux.ch')
#    detail = _('This item is an auxiliary item. It will not install anything. It will open web-page http://repogen.simplylinux.ch/\n'
#               'http://repogen.simplylinux.ch/ has collected a lot of useful third party repositories.')
#    category = 'repository'
#    def installed(self): 
#        return False
#    def install(self):
#        open_web_page('http://repogen.simplylinux.ch/')
#    def remove(self):
#        pass

class _repo:
    this_class_is_a_repository = True
    category = 'repository'
    fresh_cache = False

    @classmethod
    def refresh_cache(cls):
        if not _repo.fresh_cache:
            _repo.source_settings = APTSource.get_source_contents()
            _repo.fresh_cache = True
    @classmethod
    def exists_in_source(cls, seed):
        assert isinstance(seed, str)
        seed = seed.split('#')[0].strip()
        _repo.refresh_cache()
        for contents in _repo.source_settings.values():
            for line in contents:
                if seed in line.split('#')[0]: return True
        return False
    @classmethod
    def add_to_source(cls, file_name, seed):
        assert isinstance(file_name, str)
        assert isinstance(seed, str)
        assert seed[-1]!='\n'
        _repo.refresh_cache()
        if not file_name in _repo.source_settings:
            _repo.source_settings[file_name] = []
        _repo.source_settings[file_name].append(seed+'\n')
    @classmethod
    def remove_from_source(cls, seed):
        assert isinstance(seed, str)
        seed = seed.split('#')[0].strip()
        _repo.refresh_cache()
        for contents in _repo.source_settings.values():
            for i in reversed(range(len(contents))):
                line = contents[i]
                if seed in line.split('#')[0]:
                    del contents[i]
    @classmethod
    def save_source(cls):
        for file_path, contents in _repo.source_settings.items():
            if contents == []:
                gksudo("rm -f '%s' "%file_path)
                continue
            with TempOwn(file_path) as o:
                f = open(file_path, 'w')
                f.writelines(contents)
                f.close()
    def __init__(self):
        # check
        assert isinstance(self.desc, (str,unicode) )
        assert isinstance(self.web_page, str)
        
        assert isinstance(self.apt_file, str)
        assert isinstance(self.apt_conf, list)
        for i,a in enumerate(self.apt_conf): 
            is_string_not_empty(a)
            if a.endswith('\n'): raise ValueError(a)
            if '$' in a: #variable substitution
                assert '$version' in a
                self.apt_conf[i] = a.replace('$version', Config.get_Ubuntu_version() )
        assert isinstance(self.apt_content, str)
        
        if hasattr(self, 'key_url'):
            assert isinstance(self.key_url, str)
            if self.key_url:
                assert ( self.key_url.startswith('ftp://') or
                         self.key_url.startswith('http://') or
                         self.key_url.startswith('https://') )
        
        assert isinstance(self.key_id, str)
        
        # create detail
        import StringIO
        msg = StringIO.StringIO()
        if self.desc:
            print >>msg, self.desc, '\n'
        if self.apt_content:
            print >>msg, _('<i>Install packages by:</i>'), '<b>sudo apt-get install', self.apt_content, '</b>'
        print >>msg, _('<i>Web page:</i>'), self.web_page
        print >>msg, _('<i>Source setting:</i>'), 
        for a in self.apt_conf:
            print >>msg, a
        self.__class__.detail = msg.getvalue()
    def installed(self):
        _repo.refresh_cache()
        for seed in self.apt_conf:
            if not self.exists_in_source(seed):
                return False
        return True
    def install(self):
        # change souce
        _repo.refresh_cache()
        for seed in self.apt_conf:
            self.add_to_source(self.apt_file, seed)
        self.save_source()
        _repo.fresh_cache = False
        # add key
        if hasattr(self, 'key_url'):
            if self.key_url: #if has key
                wget(self.key_url, '/tmp/key.gpg')
                gksudo('apt-key add /tmp/key.gpg')
        else:
            raise NotImplementedError
    def remove(self):
        # change source
        _repo.refresh_cache()
        for seed in self.apt_conf:
            self.remove_from_source(seed)
        self.save_source()
        _repo.fresh_cache = False
        # remove key
        if self.key_id:
            gksudo('apt-key del '+self.key_id, ignore_error=True)

class Repo_GoogleStable(_repo):
    __doc__ = _('Google Chrome, Picasa 2 and Google Desktop')
    license = 'Google Chrome Terms of Service'
    def __init__(self):
        self.desc = _('This repository contains Google Chrome, Picasa and Google Desktop. '
            'Google Chrome is a web browser. '
            'Picasa is an image management application. '
            'Google Desktop is an application for personalizing and organizing information in computer.')
        self.apt_content = 'google-chrome-beta google-desktop-linux picasa'
        self.web_page = 'http://www.google.com/linuxrepositories/'
        self.apt_file = '/etc/apt/sources.list.d/google-stable.list'
        self.apt_conf = [ 'deb http://dl.google.com/linux/deb/ stable non-free main' ]
        self.key_url = 'https://dl-ssl.google.com/linux/linux_signing_key.pub'
        self.key_id = '7FAC5991'
        _repo.__init__(self)

class Repo_Firefox_3_6(_repo):
    __doc__ = _('Firefox 3.6 (stable)')
    license = 'MPL, GNU GPL, GNU LGPL'
    logo = 'firefox.png'
    def __init__(self):
	self.desc = _('This repository contains Firefox stable version 3.6.')
        self.apt_content = 'firefox'
        self.web_page = 'http://launchpad.net/~mozillateam/+archive/firefox-stable'
        self.apt_file = '/etc/apt/sources.list.d/firefox-stable.list'
        self.apt_conf = ['deb http://ppa.launchpad.net/mozillateam/firefox-stable/ubuntu $version main']
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x9BDB3D89CE49EC21'
        self.key_id = 'CE49EC21'
        _repo.__init__(self)

class Repo_GoogleUnstable(_repo):
    __doc__ = _('Google Picasa 3')
    license = 'Google Chrome Terms of Service'
    def __init__(self):
        self.desc = _('This repository contains Picasa 3.')
        self.apt_content = 'picasa'
        self.web_page = 'http://www.google.com/linuxrepositories/testrepo.html'
        self.apt_file = '/etc/apt/sources.list.d/google-unstable.list'
        self.apt_conf = [ 'deb http://dl.google.com/linux/deb/ testing non-free' ]
        self.key_url = 'https://dl-ssl.google.com/linux/linux_signing_key.pub'
        self.key_id = '7FAC5991'
        _repo.__init__(self)

class Repo_PlayOnLinux(_repo):
    __doc__ = _('PlayOnLinux')
    license = 'GNU Lesser General Public License (LGPL)'
    def __init__(self):
        self.desc = _('PlayOnLinux is a front-end for wine. '
            'It helps to install Windows Games and softwares on Linux. ')
        self.apt_content = 'playonlinux'
        self.web_page = 'http://www.playonlinux.com/en/download.html'
        self.apt_file = '/etc/apt/sources.list.d/playonlinux.list'
        self.apt_conf = [ 'deb http://deb.playonlinux.com/ $version main' ]
        self.key_url = '' #no key
        self.key_id = '' #no key
        _repo.__init__(self)

class Repo_WINE(_repo):
    __doc__ = _('WINE')
    license = ('GNU Lesser General Public License (LGPL)'
               'see http://wiki.winehq.org/Licensing')
    logo = 'wine.png'
    def __init__(self):
        self.desc = _('This repository contains the latest version of Wine. '
            'Wine is for running Windows applications on Linux. ')
        self.apt_content = 'wine wine-gecko'
        self.web_page = 'https://launchpad.net/~ubuntu-wine/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/winehq.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/ubuntu-wine/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x5A9A06AEF9CB8DB0'
        self.key_id = 'F9CB8DB0'
        _repo.__init__(self)


class Repo_Dropbox(_repo):
    __doc__ = _('Dropbox')
    logo = 'dropbox.png'
    def __init__(self):
        self.desc = _('Dropbox is an application to store, sync, and share files among computers.')
        self.apt_content = 'nautilus-dropbox'
        self.web_page = 'https://www.dropbox.com/downloading?os=lnx'
        self.apt_file = '/etc/apt/sources.list.d/dropbox.list'
        self.apt_conf = [ 'deb http://linux.dropbox.com/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x3565780E'
        self.key_id = '3565780E'
        _repo.__init__(self)

class Repo_Ailurus(_repo):
    __doc__ = _('Ailurus')
    logo = 'ailurus.png'
    license = 'GNU Lesser General Public License (LGPL)'

    def __init__(self):
        self.desc = _('This is the repository of Ailurus.')
        self.apt_content = 'ailurus'
        self.web_page = 'https://launchpad.net/~ailurus/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/ailurus.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/ailurus/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x5A16033A9A6FE242'
        self.key_id = '9A6FE242'
        _repo.__init__(self)

class Repo_Skype(_repo):
    __doc__ = _('Skype')
    license = 'proprietary'
    def __init__(self):
        self.desc = _('With Skype you can make free calls over the Internet to other people. ')
        self.apt_content = 'skype'
        self.web_page = 'http://www.skype.com/intl/en/download/skype/linux/choose/'
        self.apt_file = '/etc/apt/sources.list.d/skype.list'
        self.apt_conf = [ 'deb http://download.skype.com/linux/repos/debian stable non-free' ]
        self.key_url = ''
        self.key_id = ''
        _repo.__init__(self)
    def support(self):
        return get_arch() == 32

class Repo_GetDeb_net(_repo):
    __doc__ = _('GetDeb.net')
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = _('GetDeb.net is an unofficial project which provides a lot of open source applications.')
        self.apt_content = ''
        self.web_page = 'http://www.getdeb.net/updates/Ubuntu/all#how_to_install'
        self.apt_file = '/etc/apt/sources.list.d/getdeb.net.list'
        self.apt_conf = [ 'deb http://archive.getdeb.net/ubuntu $version-getdeb apps' ]
        self.key_url = 'http://archive.getdeb.net/getdeb-archive.key'
        self.key_id = '46D7E7CF'
        _repo.__init__(self)
    def support(self):
        return Config.get_Ubuntu_version() == 'karmic'

class Repo_AWN_Development(_repo):
    __doc__ = _('AWN (Development version)')
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = _('AWN is a MacOS X like panel for GNOME. '
            'This repository provides the latest version of AWN. ')
        self.apt_content = 'avant-window-navigator-trunk'
        self.web_page = 'https://launchpad.net/~awn-testing/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/awn_development.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/awn-testing/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0xB0BE17C2A0C914F086B7B8327D2C7A23BF810CD5'
        self.key_id = 'BF810CD5'
        _repo.__init__(self)

class Repo_Blueman(_repo):
    __doc__ = _('Blueman')
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = _('Blueman is a graphical blue-tooth manager.')
        self.apt_content = 'blueman'
        self.web_page = 'https://launchpad.net/~blueman/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/blueman.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/blueman/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x947C4F7371932C794B153F0F6B15AB91951DC1E2'
        self.key_id = '951DC1E2'
        _repo.__init__(self)

class Repo_Christine(_repo):
    __doc__ = _('Christine')
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = _('Christine is a small media player.')
        self.apt_content = 'christine'
        self.web_page = 'https://launchpad.net/~markuz/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/christine.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/markuz/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x09B5EC6264345EE1423E3C637FE57DFD1F808920'
        self.key_id = '1F808920'
        _repo.__init__(self)

class Repo_Chromium_Daily(_repo):
    __doc__ = _('Chromium')
    license = 'BSD license, MIT License, LGPL, Ms-PL, MPL/GPL/LGPL tri-license'
    def __init__(self):
        self.desc = _('Chromium is the open source version of Google Chrome.')
        self.apt_content = 'chromium-browser'
        self.web_page = 'https://launchpad.net/~chromium-daily/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/chromium.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/chromium-daily/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0xFBEF0D696DE1C72BA5A835FE5A9BF3BB4E5E17B5'
        self.key_id = '4E5E17B5'
        _repo.__init__(self)

class Repo_GTG(_repo):
    __doc__ = _('Getting things GNOME')
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = _('"Getting things GNOME" is a simple, powerful and flexible organization tool.')
        self.apt_content = 'gtg'
        self.web_page = 'https://launchpad.net/~gtg/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/gtg.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/gtg/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x88C03D7B5195CEAFF3F9F7A7B82A968F7AC9B38F'
        self.key_id = '7AC9B38F'
        _repo.__init__(self)

class Repo_GNOMEColors(_repo):
    __doc__ = _('GNOME colors')
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = _('This repository contains some themes.')
        self.apt_content = 'arc-colors gnome-colors shiki-colors-murrine'
        self.web_page = 'https://launchpad.net/~gnome-colors-packagers/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/gnome-colors.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/gnome-colors-packagers/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x41C2359B9C2F88F0D47040322D79F61BE8D31A30'
        self.key_id = 'E8D31A30'
        _repo.__init__(self)

class Repo_GlobalMenu(_repo):
    __doc__ = _('GNOME Global Menu')
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = _('GNOME Global Menu is the globally-shared menu bar of all applications.')
        self.apt_content = 'gnome-globalmenu'
        self.web_page = 'https://launchpad.net/~globalmenu-team/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/gnome-globalmenu.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/globalmenu-team/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0xE97F4DB8F1F0EC20FF792CA37889D725DA6DEEAA'
        self.key_id = 'DA6DEEAA'
        _repo.__init__(self)

class Repo_Medibuntu(_repo):
    __doc__ = _('Medibuntu')
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = _('This is a repository providing packages which cannot be included into the Ubuntu distribution for legal reasons. '
            'There are many packages in this repository. The list of packages is in http://packages.medibuntu.org/')
        self.apt_content = ''
        self.web_page = 'http://packages.medibuntu.org/'
        self.apt_file = '/etc/apt/sources.list.d/medibuntu.list'
        self.apt_conf = [ 'deb http://packages.medibuntu.org/ $version free non-free' ]
        self.key_url = 'http://packages.medibuntu.org/medibuntu-key.gpg'
        self.key_id = '0C5A2783'
        _repo.__init__(self)

class Repo_Moovida(_repo):
    __doc__ = _('Moovida')
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = _('Moovida is a cross platform media player.')
        self.apt_content = 'moovida'
        self.web_page = 'https://launchpad.net/~moovida-packagers/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/moovida.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/moovida-packagers/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0xE478BB3B6BCD9F67C5137DF13135CD5C26C2E075'
        self.key_id = '26C2E075'
        _repo.__init__(self)

class Repo_Opera(_repo):
    __doc__ = _('Opera')
    license = 'Freeware'
    logo = 'opera.png'
    def __init__(self):
        self.desc = _('Opera is a famous web browser.')
        self.apt_content = 'opera'
        self.web_page = 'http://deb.opera.com/opera/'
        self.apt_file = '/etc/apt/sources.list.d/opera.list'
        self.apt_conf = [ 'deb http://deb.opera.com/opera/ stable non-free' ]
        self.key_url = 'https://pgp.webtru.st/pks/lookup?op=get&search=0xF9A2F76A9D1A0061'
        self.key_id = '9D1A0061'
        _repo.__init__(self)

class Repo_Shutter(_repo):
    license = 'GNU General Public License (GPL)'
    __doc__ = _('Shutter')
    def __init__(self):
        self.desc = _('Shutter is a powerful screenshot program.')
        self.apt_content = 'shutter'
        self.web_page = 'https://launchpad.net/~shutter/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/shutter.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/shutter/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x5017D4931D0ACADE295B68ADFC6D7D9D009ED615'
        self.key_id = '009ED615'
        _repo.__init__(self)

class Repo_Synapse(_repo):
    __doc__ = _('Synapse')
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = _('Synapse is an instant messager.')
        self.apt_content = 'synapse'
        self.web_page = 'http://synapse.im/download/'
        self.apt_file = '/etc/apt/sources.list.d/synapse.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/firerabbit/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x83419668F12469157BCD4BE904508D5C1654E635'
        self.key_id = '1654E635'
        _repo.__init__(self)

class Repo_X_Server_Updates(_repo):
    __doc__ = _('X server updates')
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = _('This repository provides latest versions of X.org drivers, libraries.')
        self.apt_content = ( 'fglrx-installer xfree86-driver-synaptics xserver-xorg-input-vmmouse xserver-xorg-video-ati ' +
                             'xserver-xorg-video-intel xserver-xorg-video-nv' )
        self.web_page = 'https://launchpad.net/~ubuntu-x-swat/+archive/x-updates'
        self.apt_file = '/etc/apt/sources.list.d/x_server_updates.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/ubuntu-x-swat/x-updates/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x643DC6BD56580CEB1AB4A9F63B22AB97AF1CDFA9'
        self.key_id = 'AF1CDFA9'
        _repo.__init__(self)
        
class Repo_VirtualBox(_repo):
    __doc__ = _('VirtualBox')
    license = 'Proprietary'
    logo = 'virtualbox.png'
    def __init__(self):
        self.desc = ''
        self.apt_content = 'virtualbox'
        self.web_page = 'http://download.virtualbox.org/virtualbox/debian/'
        self.apt_file = '/etc/apt/sources.list.d/virtualbox.list'
        self.apt_conf = [ 'deb http://download.virtualbox.org/virtualbox/debian $version non-free' ]
        self.key_url = 'http://download.virtualbox.org/virtualbox/debian/sun_vbox.asc'
        self.key_id = '6DFBCBAE'
        _repo.__init__(self)

class Repo_WebkitGTK(_repo):
    __doc__ = _('WebkitGTK')
    license = 'GNU Lesser General Public License (LGPL)'
    def __init__(self):
        self.desc = _('WebkitGTK is the port of Webkit to the GTK+ platform.')
        self.apt_content = 'webkit pywebkitgtk'
        self.web_page = 'https://launchpad.net/~webkit-team/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/webkit_gtk.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/webkit-team/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x612D9FE65C733A79BB2AB07D991E6CF92D9A3C5B'
        self.key_id = '2D9A3C5B'
        _repo.__init__(self)

class Repo_XBMC(_repo):
    __doc__ = _('XBMC')
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = _('XBMC is an open source software media player and entertainment hub for digital media.')
        self.apt_content = 'xbmc'
        self.web_page = 'https://launchpad.net/~team-xbmc/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/xbmc.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/team-xbmc/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x189701DA570C56B9488EF60A6D975C4791E7EE5E'
        self.key_id = '91E7EE5E'
        _repo.__init__(self)

class Repo_Oracle(_repo):
    __doc__ = _('Oracle')
    license = 'Proprietary'
    def __init__(self):
        self.desc = _('This repository provides Oracle Database Express Edition.\n'
            'After installation, please add yourself to the "dba" group, then run "sudo /etc/init.d/oracle-xe configure".')
        self.apt_content = 'oracle-xe oracle-xe-client oracle-xe-universal'
        self.web_page = 'http://oss.oracle.com/'
        self.apt_file = '/etc/apt/sources.list.d/oracle.list'
        self.apt_conf = [ 'deb http://oss.oracle.com/debian unstable main non-free' ]
        self.key_url = 'http://oss.oracle.com/el4/RPM-GPG-KEY-oracle'
        self.key_id = 'B38A8516'
        _repo.__init__(self)

class Repo_IBus(_repo):
    license = 'GNU General Public License (GPL)'
    'IBus'
    def __init__(self):
        version = Config.get_Ubuntu_version()
        self.desc = _('Next generation input method')
        self.apt_content = 'ibus ibus-table ibus-pinyin'
        self.web_page = 'https://launchpad.net/~ibus-dev/+archive/ibus-1.2-%s'%version
        self.apt_file = '/etc/apt/sources.list.d/ibus.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/ibus-dev/ibus-1.2-%s/ubuntu $version main'%version ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x72DBF294B86C9BEB7170023321C022AA985E0E11'
        self.key_id = '985E0E11'
        _repo.__init__(self)
    def support(self):
        return Config.get_Ubuntu_version() in ['jaunty', 'intrepid', 'karmic']

class Repo_Canonical_Partner(_repo):
    __doc__ = _('Partners of Canonical')
    logo = 'ubuntu.png'
    def __init__(self):
        self.desc = _('This repository provides many packages from partners of Canonical.')
        self.apt_content = 'acroread uex symphony accountz-baz'
        self.web_page = 'http://archive.canonical.com/ubuntu/dists/'
        self.apt_file = '/etc/apt/sources.list.d/partners-of-canonical.list'
        self.apt_conf = [ 'deb http://archive.canonical.com/ubuntu $version partner ' ]
        self.key_url = ''
        self.key_id = ''
        _repo.__init__(self)

class Repo_RSSOwl(_repo):
    'RSSOwl'
    license = 'Eclipse Public License'
    def __init__(self):
        self.desc = _('RSSOwl is an RSS reader.')
        self.apt_content = 'rssowl'
        self.web_page = 'http://packages.rssowl.org/README'
        self.apt_file = '/etc/apt/sources.list.d/rssowl.list'
        self.apt_conf = [ 'deb http://packages.rssowl.org/ubuntu $version main' ]
        self.key_url = 'http://packages.rssowl.org/project/rene.moser.pubkey'
        self.key_id = 'E53168C7'
        _repo.__init__(self)

class Repo_Gmchess(_repo):
    'Gmchess'
    license = 'GNU General Public License (GPL)'
    Chinese = True
    def __init__(self):
        self.desc = _('This is a Chinese chess game.')
        self.apt_content = 'gmchess'
        self.web_page = 'https://launchpad.net/~gmchess/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/gmchess.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/gmchess/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0xE71F16D021FF134C818ECAC3FA442F4B04F95913'
        self.key_id = '04F95913'
        _repo.__init__(self)

class Repo_Exaile(_repo):
    __doc__ = _('Exaile (Latest version)')
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = ''
        self.apt_content = 'exaile'
        self.web_page = 'https://launchpad.net/~exaile-devel/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/exaile-devel.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/exaile-devel/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0xB79BBC58DE219687E584187AC174A7B143CBFCC0'
        self.key_id = '43CBFCC0'
        _repo.__init__(self)

class Repo_Audacious(_repo):
    __doc__ = _('Audacious (Latest version)')
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = ''
        self.apt_content = 'audacious audacious-plugins'
        self.web_page = 'https://launchpad.net/~dupondje/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/audacious.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/dupondje/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x227B9873BAD137667B06772ACD51A93283874559'
        self.key_id = '83874559'
        _repo.__init__(self)
        
#class Repo_Tor(_repo):
#    license = 'BSD License'
#    'Tor'
#    def __init__(self):
#        self.desc = ''
#        self.apt_content = 'tor privoxy vidalia'
#        self.web_page = 'http://deb.torproject.org/'
#        self.apt_file = '/etc/apt/sources.list.d/tor.list'
#        self.apt_conf = [ 'deb http://deb.torproject.org/torproject.org $version main' ]
#        self.key_url = ''
#        self.key_id = '886DDD89'
#        _repo.__init__(self)

class Repo_RedNoteBook(_repo):
    'RedNoteBook'
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = _('This is a desktop diary application.')
        self.apt_content = 'rednotebook'
        self.web_page = 'http://robin.powdarrmonkey.net/ubuntu/'
        self.apt_file = '/etc/apt/sources.list.d/rednotebook.list'
        self.apt_conf = [ 'deb http://robin.powdarrmonkey.net/ubuntu $version/' ]
        self.key_url = 'http://robin.powdarrmonkey.net/ubuntu/repository.key'
        self.key_id = 'FF95D333'
        _repo.__init__(self)

class Repo_Pidgin_Develop(_repo):
    __doc__ = _('Pidgin (Latest version)')
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = ''
        self.apt_content = 'pidgin'
        self.web_page = 'https://launchpad.net/~pidgin-developers/+archive/ppa' 
        self.apt_file = '/etc/apt/sources.list.d/pidgin.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/pidgin-developers/ppa/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x67265EB522BDD6B1C69E66ED7FB8BEE0A1F196A8'
        self.key_id = 'A1F196A8'
        _repo.__init__(self)

class Repo_Songbird(_repo):
    __doc__ = _('Songbird (Latest version)')
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = ''
        self.apt_content = 'songbird'
        self.web_page = 'https://launchpad.net/~songbird-daily/+archive/ppa'
        self.apt_file = '/etc/apt/sources.list.d/songbird.list'
        self.apt_conf = ['deb http://ppa.launchpad.net/songbird-daily/ppa/ubuntu $version main']
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x31E0163DFE442D34A17B17BDD725E4885719E347'
        self.key_id = '5719E347'
        _repo.__init__(self)

class Repo_Mplayer_VOD(_repo):
    license = 'GNU General Public License (GPL)'
    def __init__(self):
        self.desc = 'mplayer_vod'
        self.apt_content = 'mplayer'
        self.web_page = 'https://launchpad.net/~homer-xing/+archive/mplayer-vod'
        self.apt_file = '/etc/apt/sources.list.d/mplayer-vod.list'
        self.apt_conf = [ 'deb http://ppa.launchpad.net/homer-xing/mplayer-vod/ubuntu $version main' ]
        self.key_url = 'http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0xFDC8AE7E17C96D481FEA0410D10C093AFFA63A31'
        self.key_id = 'FFA63A31'
        _repo.__init__(self)
    def support(self):
        return False
