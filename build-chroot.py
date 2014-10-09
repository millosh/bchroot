#!/usr/bin/python
# -*- coding: utf-8 -*-

# TODO
# /etc/init.d/...
## check scripts for the names (provides: ...)!!!
## update-rc.d <package> defaults
# libnss je u /lib/i386...
# logrotate
# various timezones for localtime
# fix /etc/hosts ###server###.###domain###
# filename.from_system => take file from the system; /etc/localtime.from_system
# pecl install.... nisam postavio da se ti fajlovi ubacuju u sistem

import re, sys, os, time, getopt
from os.path import *
from commands import getoutput as go

def usage():
	usage  = "Usage: \n"
	usage += "./build-chroot -h|--help\n"
	usage += "./build-chroot -a|--arch=<arch> -b|--base -c|--chroot=<chroot dir> --delete --etc --fake -p|--pkgs=<packages> -t|--tar\n"
	usage += "-a, --arch=: CPU architecture; see ./confgure --help\n"
	usage += "\tfrom particular packages; presently used only for\n"
	usage += "\tnaming the tarball.\n"
	usage += "-b, --base: If used, base chroot system would be built.\n"
	usage += "\tYou want to use this option, usually.\n"
	usage += "-c, --chroot=: Directory name for chroot system.\n"
	usage += "\tThis option is mandatory.\n"
	usage += "--delete: Should the chroot dir be delete if exists.\n"
	usage += "\tUseful for trial-and-error approach.\n"
	usage += "--etc: If used, /etc system will be built in chroot.\n"
	usage += "\tYou want to use this option, usually.\n"
	usage += "--fake: Fake building the package.\n"
	usage += "\tUseful for trial-and-error approach.\n"
	usage += "-h, --help: This message.\n"
	usage += "-p, --pkgs=: The list of packages separated by comma.\n"
	usage += "\t\texample: nginx,php\n"
	usage += "\tEvery package could have one, two or four parts\n"
	usage += "\tseparated by semicolon (:). The first one and mandatory\n"
	usage += "\tone is package name, which corresponds with the\n"
	usage += "\tsubdirectory inside of the \"software\" subdirectory.\n"
	usage += "\tThe second one is used for the different build dir.\n"
	usage += "\tThe third one is used for different source dir and the\n"
	usage += "\tfourth one is used for different configuration file.\n"
	usage += "-t, --tar: Build tarball at the end.\n"
	usage += "\n"
	usage += "Note that you have to have the line:\n"
	usage += "\n"
	usage += "### exec_path = /path/to/exec\n"
	usage += "\n"
	usage += "-- inside of the configuraiton file. Exec path is the\n"
	usage += "executable inside of the chroot system.\n"
	usage += "\n"
	usage += "Program to be executed before ./configure && make && make\n"
	usage += "install is also supported with the line:\n"
	usage += "\n"
	usage += "### pre_exec = <command>\n"
	usage += "\n"
	usage += "-- inside of the configuration file. You can have as many\n"
	usage += "as you want pre_exec commands.\n"
	usage += "\n"
	usage += "You should have unpacked source inside of the directory\n"
	usage += "software/<package>/build. Inside of that directory you\n"
	usage += "should have configuraiton file named \"default.sh\".\n"
	usage += "If you want to add some files to /etc directory inside\n"
	usage += "of chroot system, create software/<package>/etc dir and\n"
	usage += "put there configuration files.\n"
	usage += "\n"
	usage += "Usually, you want to run program with options like those below:\n"
	usage += "./build-chroot.py -a pentium4 -b -c /chroot/my_chroot --delete --etc --dev -p nginx,php -t\n"
	print usage

def setoptions(options):
	# defs
	options['arch'] = False
	options['base'] = False
	options['chroot'] = False
	options['delete'] = False
	options['etc'] = False
	options['fake'] = False
	options['dev'] = False
	options['pkgs'] = False
	options['tar'] = False
	options['verbose'] = False
	# vars
	options['software'] = options['mydir'] + "/software"
	options['system'] = options['mydir'] + "/system"
	return options

def getoptions(options):
	try:
		opts, args = getopt.getopt(sys.argv[1:], "a:bc:hp:tv",
			[
				"base", "delete", "dev", "etc", "fake", "help", "tar", "verbose",
				"arch=", "chroot=", "pkgs=",
			]
		)
	except getopt.GetoptError,err:
		print str(err)
		usage()
		sys.exit(2)
	options = setoptions(options)
	for opt, arg in opts:
		if opt in ('-a', '--arch'):
			options['arch'] = arg
		elif opt in ('-b', '--base'):
			options['base'] = True
		elif opt in ('-c', '--chroot'):
			options['chroot'] = arg
		elif opt in ('--delete'):
			options['delete'] = True
		elif opt in ('--dev'):
			options['dev'] = True
		elif opt in ('--etc'):
			options['etc'] = True
		elif opt in ('--fake'):
			options['fake'] = True
		elif opt in ('-h', '--help'):
			usage()
			sys.exit()
		elif opt in ('-p', '--pkgs'):
			options['pkgs'] = arg
		elif opt in ('-t', '--tar'):
			options['tar'] = True
		elif opt in ('-v', '--verbose'):
			options['verbose'] = True
		else:
			assert False, "unhandled option"
	return options

def mkdir(dr):
	if not isdir(dr):
		cmd = "mkdir -p \"" + dr + "\""
		print cmd
		os.system(cmd)

def mknod(dr,dev,tp,minor,major):
	cmd  = "mknod \"" + dr + "/" + dev + "\" "
	cmd += tp + " " + minor + " " + major
	print cmd
	os.system(cmd)

def mkdev(drs):
	cmd = "mkdir -p \"" + drs['dev'] + "\""
	print cmd
	os.system(cmd)
	mknod(drs['dev'],'null','c','1','3')
	mknod(drs['dev'],'random','c','1','8')
	mknod(drs['dev'],'urandom','c','1','9')

def mkchroot(options):
	if not options['chroot']:
		usage()
		sys.exit()
	if isdir(options['chroot']):
		if options['delete']:
			answer = 'y'
		else:
			answer = raw_input("Directory " + options['chroot'] + " exists. Should it be deleted? (y/n) ")
		if answer in [ 'y', 'Y', 'yes', 'YES', ]:
			cmd = "rm -rf \"" + options['chroot'] + "\""
			print cmd
			os.system(cmd)
	mkdir(options['chroot'])
	drs = {
		'bin': options['chroot'] + '/bin', 
		'lib': options['chroot'] + '/lib', 
		'logs': options['chroot'] + '/logs', 
		'var': options['chroot'] + '/var', 
		'var/run': options['chroot'] + '/var/run', 
		'var/lock': options['chroot'] + '/var/lock', 
		'var/log': options['chroot'] + '/var/log', 
		'tmp': options['chroot'] + '/tmp',
		'www': options['chroot'] + '/www',
	}
	for dr in drs:
		cmd = "mkdir -p \"" + drs[dr] + "\""
		print cmd
		os.system(cmd)
	lnks = {
		options['chroot'] + '/lib64': '/lib',
	}
	for ln in lnks:
		cmd = "ln -s \"" + lnks[ln] + "\" \"" + ln + "\""
		print cmd
		os.system(cmd)
	cmd = "cd " + drs['lib'] + "; ln -s . i386-linux-gnu; cd -"
	print cmd
	os.system(cmd)
	if options['etc']:
		drs['etc'] = options['chroot'] + '/etc'
		cmd = "mkdir -p \"" + drs['etc'] + "\""
		print cmd
		os.system(cmd)
		etc_dir = options['system'] + "/etc"
		cmd = "cp -a " + etc_dir + "/* \"" + drs['etc'] + "\""
		print cmd
		os.system(cmd)
		### find better way for /etc/localtime!
		copies = {
			'/etc/localtime': drs['etc'],
		}
		for copy in copies:
			cmd = "cp \"" + copy + "\" \"" + copies[copy] + "\""
			print cmd
			os.system(cmd)
	if options['dev']:
		drs['dev'] = options['chroot'] + '/dev'
		mkdev(drs)

def build_pdir(build_dir):
	pconf = build_dir + "/default.sh"
	cmd = "find " + build_dir + "/* -maxdepth 0 -type d 2> /dev/null"
	print cmd
	sdirs = go(cmd).split("\n")
	if sdirs[-1] != '':
		pdir = sdirs[-1]
	else:
		print "You should unpack software inside of the build dir (" + build_dir + ")."
		usage()
		sys.exit()
	return pconf, pdir

def chvars(options,text):
	keyvars = {
		'###CHROOT###': options['chroot']
	}
	for key in keyvars:
		text = re.sub(key,keyvars[key],text)
	return text

def build(options,names,toadd):
	packages = options['pkgs'].split(',')
	for package in packages:
		parts = re.split(":",package)
		software = parts[0]
		base_dir = options['software'] + '/' + software
		pkg_etc = base_dir + "/etc"
		if len(parts) == 1:
			build_dir = base_dir + '/build'
			pconf, pdir = build_pdir(build_dir)
		elif len(parts) == 2:
			build_dir = parts[1]
			pconf, pdir = build_pdir(build_dir)
		else:
			build_dir = parts[1]
			pdir = parts[2]
			pconf = parts[3]
		if isdir(pkg_etc) and options['etc']:
			cmd = "cp -a " + pkg_etc + "/* " + options['chroot'] + "/etc"
			print cmd
			os.system(cmd)
		cmd = "cp " + pconf + " " + options['chroot'] + "/" + software + "-" + pconf.split("/")[-1]
		print cmd
		os.system(cmd)
		names.append(pdir.split("/")[-1])
		pconf_content = open(pconf).read()
		prefix = re.findall("\s+--prefix=(.+?)\s+",pconf_content)[0]
		if not options['fake']:
			print "Processing package " + pdir + " with config " + pconf + "..."
			exec_path = re.findall("###\s*exec_path\s*=\s*(.+?)\n",pconf_content)[0]
			pre_execs = re.findall("###\s*pre_exec\s*=\s*(.+?)\n",pconf_content)
			for pre_exec in pre_execs:
				pre_exec = chvars(options,pre_exec)
				print pre_exec
				os.system(pre_exec)
			cmd  = "cd " + pdir + "; "
			cmd += "make clean; "
			print pconf
			cmd += "sh " + pconf + " && "
			cmd += "make && make install; "
			cmd += "cd -"
			print cmd
			os.system(cmd)
			exe = prefix + exec_path
			toadd.append(exe)
			toadd = mkldd(exe,toadd)
			post_execs = re.findall("###\s*post_exec\s*=\s*(.+?)\n",pconf_content)
			for post_exec in post_execs:
				post_exec = chvars(options,post_exec)
				print post_exec
				os.system(post_exec)
	
	return names, toadd

def prelibs(options,toadd):
	lss = [
		'libnss*', 'libnsl*', 'ld-linux.so.2',
	]
	dirs = "/lib /usr/lib"
	for ls in lss:
		fds = go("find " + dirs + " -name \"" + ls + "\" 2> /dev/null")
		if fds != '':
			toadd += fds.split("\n")
	return toadd

def testlink(lib,toadd):
	toadd.append(lib)
	if islink(lib):
		realib = realpath(lib)
		toadd.append(realib)
	return toadd

def mkldd(fd,toadd):
	cmd = "ldd " + fd
	ldds = go(cmd).split("\n")
	for ldd in ldds:
		libs = re.split("\s+",ldd)
		for lib in libs:
			if lib != '':
				if lib[0] == '/':
					toadd = testlink(lib,toadd)
	return toadd

def addfd(options,fd):
	if "/lib" in fd:
		ldir = "/lib"
	elif ("/bin" in fd) or ("/sbin" in fd):
		ldir = "/bin"
	else:
		print "something fishing there: " + fd
		sys.exit(1)
	ldir = options['chroot'] + ldir
	mkdir(ldir)
	ldest = ldir + '/' + re.split("/",fd)[-1]
	cmd = "cp -a " + fd + " " + ldest
	print cmd
	os.system(cmd)
	if not islink(ldest):
		cmd = "strip " + ldest
		print cmd
		os.system(cmd)

def ldconfig(options):
	cmd = "cp /sbin/ldconfig " + options['chroot'] + "/bin"
	print cmd
	os.system(cmd)
	cmd = "/usr/sbin/chroot " + options['chroot'] + " /bin/ldconfig"
	print cmd
	os.system(cmd)
	cmd = "rm -f " + options['chroot'] + "/bin/ldconfig"

def mktarball(options):
	datetime = time.strftime("%Y%m%d%H%M")
	prechroot = "/".join(re.split("/",options['chroot'])[0:-1])
	chroot_name = re.split("/",options['chroot'])[-1]
	debian_version = open("/etc/debian_version").read().split("\n")[0].replace("/","_")
	package_name  = chroot_name + "-" + options['arch'] + "-" + debian_version + "-"
	package_name += "-".join(names) + "-" + datetime
	tarname = package_name + ".tar.bz2"
	cmd  = "cd " + prechroot + "; "
	#cmd += "mv " + options['chroot'] + " " + package_name + "; "
	cmd += "tar jcf " + tarname + " " + chroot_name + "; "
	cmd += "cd -"
	print cmd
	os.system(cmd)

if __name__ == "__main__":
	exes = []
	toadd = []
	names = []
	options = {}
	options['mydir'] = realpath("/".join(re.split("/",sys.argv[0])[0:-1]))
	options = getoptions(options)
	if options['base']:
		mkchroot(options)
		toadd = prelibs(options,toadd)
	names, toadd = build(options,names,toadd)
	for ta in toadd:
		addfd(options,ta)
	if options['base']:
		ldconfig(options)
	if options['tar']:
		mktarball(options)

