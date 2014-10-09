### exec_path = /sbin/varnishd
### pre_exec = cp -a /bin/bash /bin/ls /bin/mv /bin/cp /bin/cat /bin/mkdir /bin/pwd /bin/rm /bin/false ###CHROOT###/bin
### pre_exec = cp -a /usr/bin/id /usr/bin/vim.tiny /usr/bin/gcc* /usr/bin/ld /usr/bin/ld.bfd /usr/bin/as ###CHROOT###/bin
### pre_exec = cp -a /sbin/ldconfig /usr/bin/nm /usr/bin/strip ###CHROOT###/bin
### pre_exec = cp -a /lib/libnsl* /lib/libm* /lib/libpcre* /lib/libncurses* /lib/libdl* /lib/libselinux* /lib/librt* /lib/libacl* /lib/libpthread* /lib/libattr* /lib/libnss_compat* /lib/libnss* /lib/libgcc* /usr/lib/libpth* ###CHROOT###/lib
### pre_exec = cp -a /usr/include ###CHROOT###
### pre_exec = cp -a /usr/lib/libz* /usr/lib/gcc /usr/lib/libmpfr* /usr/lib/libgmp* /usr/lib/libgomp* /usr/lib/libopcodes* /usr/lib/libbfd* /usr/lib/crti* /usr/lib/libc* /usr/lib/crtn* ###CHROOT###/lib
### pre_exec = cd ###CHROOT###/bin && ln -s bash sh && cd -
### pre_exec = cd ###CHROOT### && ln -s . usr && cd -
### pre_exec = mkdir -p ###CHROOT###/var/varnish
### pre_exec = chmod 777 ###CHROOT###/var/varnish
### post_exec = echo "varnish:x:9999:9999::/:/bin/false" >> passwd
### post_exec = echo "varnish:!:14972:0:99999:7:::" >> shadow
./configure \
	--prefix=/ \
	--sysconfdir=/etc/varnish \
	--localstatedir=/var \
	--with-gnu-ld \

