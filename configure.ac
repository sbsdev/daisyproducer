AC_INIT([daisyproducer], [1.0])
AM_INIT_AUTOMAKE([foreign])

# AM_PATH_PYTHON

# autodoc generation
AC_CHECK_PROG([POSTGRESQL_AUTODOC], [postgresql_autodoc], [postgresql_autodoc])
AM_CONDITIONAL([HAVE_POSTGRESQL_AUTODOC], [test x$POSTGRESQL_AUTODOC = xpostgresql_autodoc])

AC_CHECK_PROG([DOT], [dot], [dot])
AM_CONDITIONAL([HAVE_DOT], [test x$DOT = xdot])

AC_CONFIG_FILES([
	Makefile
	doc/Makefile
])

AC_OUTPUT
