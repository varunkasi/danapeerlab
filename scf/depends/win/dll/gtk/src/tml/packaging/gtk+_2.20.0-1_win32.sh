# This is a shell script that calls functions and scripts from
# tml@iki.fi's personal work envíronment. It is not expected to be
# usable unmodified by others, and is included only for reference.

MOD=gtk+
VER=2.20.0
REV=1
ARCH=win32

THIS=${MOD}_${VER}-${REV}_${ARCH}

RUNZIP=${MOD}_${VER}-${REV}_${ARCH}.zip
DEVZIP=${MOD}-dev_${VER}-${REV}_${ARCH}.zip

HEX=`echo $THIS | md5sum | cut -d' ' -f1`
TARGET=c:/devel/target/$HEX

usedev
usemsvs6

(

set -x

DEPS=`latest --arch=${ARCH} glib pkg-config atk cairo freetype fontconfig pango libpng zlib`
PROXY_LIBINTL=`latest --arch=${ARCH} proxy-libintl`

PKG_CONFIG_PATH=
for D in $DEPS; do
    PATH=/devel/dist/${ARCH}/$D/bin:$PATH
    [ -d /devel/dist/${ARCH}/$D/lib/pkgconfig ] && PKG_CONFIG_PATH=/devel/dist/${ARCH}/$D/lib/pkgconfig:$PKG_CONFIG_PATH
done

LIBPNG=`latest --arch=${ARCH} libpng`
ZLIB=`latest --arch=${ARCH} zlib`

patch -p0 <<'EOF'
--- configure
+++ configure
@@ -24344,8 +24344,7 @@
 CFLAGS="$saved_cflags"
 LDFLAGS="$saved_ldflags"
 
-# Pull in gio-unix for GDesktopAppInfo usage, see at least gdkapplaunchcontext-x11.c
-GDK_PACKAGES="$PANGO_PACKAGES gio-unix-2.0 $X_PACKAGES cairo-$cairo_backend"
+GDK_PACKAGES="$PANGO_PACKAGES cairo-$cairo_backend"
 GDK_DEP_LIBS="$GDK_EXTRA_LIBS `$PKG_CONFIG --libs $GDK_PIXBUF_PACKAGES $GDK_PACKAGES` $GDK_PIXBUF_EXTRA_LIBS"
 GDK_DEP_CFLAGS="`$PKG_CONFIG --cflags  gthread-2.0 $GDK_PIXBUF_PACKAGES $GDK_PACKAGES` $GDK_PIXBUF_EXTRA_CFLAGS $GDK_EXTRA_CFLAGS"
 #
EOF

# Don't do any relinking and don't use any wrappers in libtool. It
# just causes trouble, IMHO.

sed -e 's/need_relink=yes/need_relink=no # no way --tml/' \
    -e 's/wrappers_required=yes/wrappers_required=no # no thanks --tml/' \
    <ltmain.sh >ltmain.temp && mv ltmain.temp ltmain.sh

lt_cv_deplibs_check_method='pass_all' \
CC='gcc -mthreads' \
CPPFLAGS="-I/devel/dist/${ARCH}/${LIBPNG}/include \
-I/devel/dist/${ARCH}/${ZLIB}/include \
-I/devel/dist/${ARCH}/${PROXY_LIBINTL}/include" \
LDFLAGS="-L/devel/dist/${ARCH}/${LIBPNG}/lib \
-L/devel/dist/${ARCH}/${ZLIB}/lib \
-L/devel/dist/${ARCH}/${PROXY_LIBINTL}/lib -Wl,--exclude-libs=libintl.a \
-Wl,--enable-auto-image-base" \
LIBS=-lintl \
LIBPNG=`pkg-config --libs libpng` \
CFLAGS=-O2 \
./configure \
--with-gdktarget=win32 \
--enable-gdiplus \
--with-included-loaders \
--with-included-immodules \
--without-libjasper \
--enable-debug=yes \
--enable-explicit-deps=no \
--disable-gtk-doc \
--disable-static \
--prefix=$TARGET &&

rm gtk/gtk.def &&

PATH="$PWD/gdk-pixbuf/.libs:/devel/target/$HEX/bin:$PATH" make -j3 install &&

PATH="/devel/target/$HEX/bin:$PATH" gdk-pixbuf-query-loaders >/devel/target/$HEX/etc/gtk-2.0/gdk-pixbuf.loaders &&

(echo '# Note: After adding a new separate gdk-pixbuf loader (for instance the svg one)' &&
    echo '# run gdk-pixbuf-query-loaders.exe redirecting its output into this file.' &&
    echo &&
    echo '# Note that the LoaderDir folder below does not name a folder that is' &&
    echo '# expected to exist. It was just a temporary directory used at build time.' &&
    echo &&
    cat $TARGET/etc/gtk-2.0/gdk-pixbuf.loaders ) >$TARGET/etc/gtk-2.0/gdk-pixbuf.loaders.temp &&
    mv $TARGET/etc/gtk-2.0/gdk-pixbuf.loaders.temp $TARGET/etc/gtk-2.0/gdk-pixbuf.loaders &&

grep -v -E 'Automatically generated|Created by' <$TARGET/etc/gtk-2.0/gtk.immodules >$TARGET/etc/gtk-2.0/gtk.immodules.temp &&
    mv $TARGET/etc/gtk-2.0/gtk.immodules.temp $TARGET/etc/gtk-2.0/gtk.immodules &&

./gtk-zip.sh &&

# Package also the gtk-update-icon-cache.exe.manifest
(cd $TARGET && zip /tmp/${MOD}-dev-${VER}.zip bin/gtk-update-icon-cache.exe.manifest) &&

mv /tmp/${MOD}-${VER}.zip /tmp/$RUNZIP &&
mv /tmp/${MOD}-dev-${VER}.zip /tmp/$DEVZIP

) 2>&1 | tee /devel/src/tml/packaging/$THIS.log

(cd /devel && zip /tmp/$DEVZIP src/tml/packaging/$THIS.{sh,log}) &&
manifestify /tmp/$RUNZIP /tmp/$DEVZIP
