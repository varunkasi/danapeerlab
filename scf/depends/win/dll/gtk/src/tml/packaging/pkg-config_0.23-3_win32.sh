# This is a shell script that calls functions and scripts from
# tml@iki.fi's personal work environment. It is not expected to be
# usable unmodified by others, and is included only for reference.

MOD=pkg-config
VER=0.23
REV=3
ARCH=win32

THIS=${MOD}_${VER}-${REV}_${ARCH}

RUNZIP=${MOD}_${VER}-${REV}_${ARCH}.zip
DEVZIP=${MOD}-dev_${VER}-${REV}_${ARCH}.zip

HEX=`echo $THIS | md5sum | cut -d' ' -f1`
TARGET=c:/devel/target/$HEX

usedev

(

set -x

GLIB=`latest --arch=${ARCH} glib`
PROXY_LIBINTL=`latest --arch=${ARCH} proxy-libintl`

sed -e 's/need_relink=yes/need_relink=no # no way --tml/' <ltmain.sh >ltmain.temp && mv ltmain.temp ltmain.sh &&

sed -e 's/-lglib-2.0 -liconv -lintl/-lglib-2.0/' <configure >configure.temp && mv configure.temp configure &&

PKG_CONFIG_PATH=/devel/dist/$ARCH/$GLIB/lib/pkgconfig

patch -p0 <<'EOF'
diff -ru ../orig-0.23/ChangeLog ./ChangeLog
--- ../orig-0.23/ChangeLog	2008-01-17 00:49:33.000000000 +0200
+++ ./ChangeLog	2009-06-12 14:56:02.093008900 +0300
@@ -1,3 +1,31 @@
+2009-06-12  Tor Lillqvist  <tml@iki.fi>
+
+	* parse.c: If the value of a a variable other than the "prefix"
+	one starts with the non-overridden value of "prefix", then replace
+	that prefix, too, with the run-time one.
+
+	* pkg-config.1: Corresponding update.
+
+2008-02-19  Tor Lillqvist  <tml@novell.com>
+
+	* main.c: Remove the possibility to have a default PKG_CONFIG_PATH
+	in the Registry. It is much more flexible to just use environment
+	variables. In general the Registry is not used in the ports of
+	GTK+ or GNOME libraries and software to Windows.
+
+	* parse.c (parse_line): On Windows, handle also .pc files found in
+	a share/pkgconfig folder when automatically redefining a prefix
+	variable for the package.
+
+	* pkg-config.1: Corresponding changes.
+
+2008-02-18  Tor Lillqvist  <tml@novell.com>
+
+	* main.c: Fix some bitrot: On Windows, don't use the compile-time
+	PKG_CONFIG_PC_PATH, but deduce a default one at run-time based on
+	the location of the executable. This was originally what
+	pkg-config did on Windows, but it had bit-rotted.
+
 2008-01-16  Tollef Fog Heen  <tfheen@err.no>
 
 	* NEWS, configure.in: Release 0.23
diff -ru ../orig-0.23/main.c ./main.c
--- ../orig-0.23/main.c	2008-01-17 00:06:48.000000000 +0200
+++ ./main.c	2009-06-12 13:28:26.671133900 +0300
@@ -38,9 +38,13 @@
 
 #ifdef G_OS_WIN32
 /* No hardcoded paths in the binary, thanks */
-#undef PKGLIBDIR
-/* It's OK to leak this, as PKGLIBDIR is invoked only once */
-#define PKG_CONFIG_PATH g_strconcat (g_win32_get_package_installation_directory (PACKAGE, NULL), "\\lib\\pkgconfig", NULL)
+/* It's OK to leak this */
+#undef PKG_CONFIG_PC_PATH
+#define PKG_CONFIG_PC_PATH \
+  g_strconcat (g_win32_get_package_installation_subdirectory (NULL, NULL, "lib/pkgconfig"), \
+	       ";", \
+	       g_win32_get_package_installation_subdirectory (NULL, NULL, "share/pkgconfig"), \
+	       NULL)
 #endif
 
 static int want_debug_spew = 0;
@@ -296,57 +300,6 @@
       add_search_dirs(PKG_CONFIG_PC_PATH, G_SEARCHPATH_SEPARATOR_S);
     }
 
-#ifdef G_OS_WIN32
-  {
-    /* Add search directories from the Registry */
-
-    HKEY roots[] = { HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE };
-    gchar *root_names[] = { "HKEY_CURRENT_USER", "HKEY_LOCAL_MACHINE" };
-    HKEY key;
-    int i;
-    gulong max_value_name_len, max_value_len;
-
-    for (i = 0; i < G_N_ELEMENTS (roots); i++)
-      {
-	key = NULL;
-	if (RegOpenKeyEx (roots[i], "Software\\" PACKAGE "\\PKG_CONFIG_PATH", 0,
-			  KEY_QUERY_VALUE, &key) == ERROR_SUCCESS &&
-	    RegQueryInfoKey (key, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
-			     &max_value_name_len, &max_value_len,
-			     NULL, NULL) == ERROR_SUCCESS)
-	  {
-	    int index = 0;
-	    gchar *value_name = g_malloc (max_value_name_len + 1);
-	    gchar *value = g_malloc (max_value_len + 1);
-
-	    while (TRUE)
-	      {
-		gulong type;
-		gulong value_name_len = max_value_name_len + 1;
-		gulong value_len = max_value_len + 1;
-
-		if (RegEnumValue (key, index++, value_name, &value_name_len,
-				  NULL, &type,
-				  value, &value_len) != ERROR_SUCCESS)
-		  break;
-
-		if (type != REG_SZ)
-		  continue;
-
-		value_name[value_name_len] = '\0';
-		value[value_len] = '\0';
-		debug_spew ("Adding directory '%s' from %s\\Software\\"
-			    PACKAGE "\\PKG_CONFIG_PATH\\%s\n",
-			    value, root_names[i], value_name);
-		add_search_dir (value);
-	      }
-	  }
-	if (key != NULL)
-	  RegCloseKey (key);
-      }
-  }
-#endif
-
   pcsysrootdir = getenv ("PKG_CONFIG_SYSROOT_DIR");
   if (pcsysrootdir)
     {
diff -ru ../orig-0.23/parse.c ./parse.c
--- ../orig-0.23/parse.c	2008-01-16 22:42:49.000000000 +0200
+++ ./parse.c	2009-06-12 14:52:58.296133900 +0300
@@ -897,6 +897,8 @@
 }
 
 #ifdef G_OS_WIN32
+static char *orig_prefix = NULL;
+
 static int
 pathnamecmp (const char *a,
 	     const char *b)
@@ -1011,29 +1013,38 @@
 	  gchar *prefix = pkg->pcfiledir;
 	  const int prefix_len = strlen (prefix);
 	  const char *const lib_pkgconfig = "\\lib\\pkgconfig";
+	  const char *const share_pkgconfig = "\\share\\pkgconfig";
 	  const int lib_pkgconfig_len = strlen (lib_pkgconfig);
+	  const int share_pkgconfig_len = strlen (share_pkgconfig);
 
-	  if (strlen (prefix) > lib_pkgconfig_len &&
-	      pathnamecmp (prefix + prefix_len - lib_pkgconfig_len,
-			   lib_pkgconfig) == 0)
+	  if ((strlen (prefix) > lib_pkgconfig_len &&
+	       pathnamecmp (prefix + prefix_len - lib_pkgconfig_len, lib_pkgconfig) == 0) ||
+	      (strlen (prefix) > share_pkgconfig_len &&
+	       pathnamecmp (prefix + prefix_len - share_pkgconfig_len, share_pkgconfig) == 0))
 	    {
-	      /* It ends in lib\pkgconfig. Good. */
+	      /* It ends in lib\pkgconfig or share\pkgconfig. Good. */
 	      
-	      gchar *p;
+	      gchar *q;
 	      
+	      orig_prefix = g_strdup (p);
+
 	      prefix = g_strdup (prefix);
-	      prefix[prefix_len - lib_pkgconfig_len] = '\0';
+	      if (strlen (prefix) > lib_pkgconfig_len &&
+		  pathnamecmp (prefix + prefix_len - lib_pkgconfig_len, lib_pkgconfig) == 0)
+		prefix[prefix_len - lib_pkgconfig_len] = '\0';
+	      else
+		prefix[prefix_len - share_pkgconfig_len] = '\0';
 	      
 	      /* Turn backslashes into slashes or
 	       * poptParseArgvString() will eat them when ${prefix}
 	       * has been expanded in parse_libs().
 	       */
-	      p = prefix;
-	      while (*p)
+	      q = prefix;
+	      while (*q)
 		{
-		  if (*p == '\\')
-		    *p = '/';
-		  p++;
+		  if (*q == '\\')
+		    *q = '/';
+		  q++;
 		}
 	      varname = g_strdup (tag);
 	      debug_spew (" Variable declaration, '%s' overridden with '%s'\n",
@@ -1042,6 +1053,16 @@
 	      goto cleanup;
 	    }
 	}
+      else if (!dont_define_prefix &&
+	       orig_prefix != NULL &&
+	       strncmp (p, orig_prefix, strlen (orig_prefix)) == 0 &&
+	       G_IS_DIR_SEPARATOR (p[strlen (orig_prefix)]))
+	{
+	  char *oldstr = str;
+
+	  p = str = g_strconcat (g_hash_table_lookup (pkg->vars, prefix_variable), p + strlen (orig_prefix), NULL);
+	  g_free (oldstr);
+	}
 #endif
 
       if (g_hash_table_lookup (pkg->vars, tag))
diff -ru ../orig-0.23/pkg-config.1 ./pkg-config.1
--- ../orig-0.23/pkg-config.1	2008-01-16 23:26:50.000000000 +0200
+++ ./pkg-config.1	2009-06-12 13:40:20.249258900 +0300
@@ -274,20 +274,14 @@
 
 .SH WINDOWS SPECIALITIES
 If a .pc file is found in a directory that matches the usual
-conventions (i.e., ends with \\lib\\pkgconfig), the prefix for that
-package is assumed to be the grandparent of the directory where the
-file was found, and the \fIprefix\fP variable is overridden for that
-file accordingly.
-
-In addition to the \fIPKG_CONFIG_PATH\fP environment variable, the
-Registry keys
-.DW
-\fIHKEY_CURRENT_USER\\Software\\pkgconfig\\PKG_CONFIG_PATH\fP and
-.EW
-\fIHKEY_LOCAL_MACHINE\\Software\\pkgconfig\\PKG_CONFIG_PATH\fP can be
-used to specify directories to search for .pc files. Each (string)
-value in these keys is treated as a directory where to look for .pc
-files.
+conventions (i.e., ends with \\lib\\pkgconfig or \\share\\pkgconfig),
+the prefix for that package is assumed to be the grandparent of the
+directory where the file was found, and the \fIprefix\fP variable is
+overridden for that file accordingly.
+
+If the value of a variable in a .pc file begins with the original,
+non-overridden, value of the \fIprefix\fP variable, then the overridden
+value of \fIprefix\fP is used instead.
 
 .SH AUTOCONF MACROS
 
EOF

CC='gcc -mtune=pentium3 -mthreads' \
CPPFLAGS="`$PKG_CONFIG --cflags glib-2.0` \
-I/devel/dist/${ARCH}/${PROXY_LIBINTL}/include" \
LDFLAGS="`$PKG_CONFIG --libs glib-2.0` \
-L/devel/dist/${ARCH}/${PROXY_LIBINTL}/lib -Wl,--exclude-libs=libintl.a" \
CFLAGS=-O2 \
./configure --disable-static --prefix=c:/devel/target/$HEX &&
make -j3 install &&

rm -f /tmp/$RUNZIP /tmp/$DEVZIP

cd /devel/target/$HEX && 
zip /tmp/$RUNZIP bin/pkg-config.exe &&
zip /tmp/$DEVZIP man/man1/pkg-config.1 share/aclocal/pkg.m4

) 2>&1 | tee /devel/src/tml/packaging/$THIS.log

(cd /devel && zip /tmp/$DEVZIP src/tml/packaging/$THIS.{sh,log}) &&
manifestify /tmp/$RUNZIP /tmp/$DEVZIP
