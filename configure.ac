AC_INIT([daisyproducer], [1.0])
AM_INIT_AUTOMAKE([foreign])

# AM_PATH_PYTHON

# emacs and rsync are needed to create and deploy the web pages
AC_CHECK_PROG([EMACS], [emacs], [emacs])
AM_CONDITIONAL([HAVE_EMACS], [test x$EMACS = xemacs])

AC_CHECK_PROG([RSYNC], [rsync], [rsync])
AM_CONDITIONAL([HAVE_RSYNC], [test x$RSYNC = xrsync])

# Deployment
AC_ARG_ENABLE(deploy, AC_HELP_STRING([--enable-deploy], [enable web site deployment]),
		       enable_deploy=$enableval, enable_deploy=no)
AM_CONDITIONAL(DEPLOY, test "$enable_deploy" != "no")
if test "$enable_deploy" != "no"; then
   DEPLOYMENT_URL=$enable_deploy
   AC_SUBST(DEPLOYMENT_URL)
fi
AC_MSG_CHECKING([if web site deployment should be enabled])
AC_MSG_RESULT($enable_deploy)

# autodoc generation
AC_CHECK_PROG([POSTGRESQL_AUTODOC], [postgresql_autodoc], [postgresql_autodoc])
AM_CONDITIONAL([HAVE_POSTGRESQL_AUTODOC], [test x$POSTGRESQL_AUTODOC = xpostgresql_autodoc])

AC_CHECK_PROG([DOT], [dot], [dot])
AM_CONDITIONAL([HAVE_DOT], [test x$DOT = xdot])

AC_CONFIG_FILES([
	Makefile
	doc/Makefile
	web/Makefile
])

AC_OUTPUT
