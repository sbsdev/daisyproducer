#! /bin/sh

# Copyright (C) 2009, 2010, 2011 by Swiss Library for the Blind, Visually Impaired and Print Disabled

# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.

case "$1" in
production) DEPLOY_ENV=demo;;
test|*) DEPLOY_ENV=test;;
esac

INSTALL_DIR=/srv/$DEPLOY_ENV.xmlp.sbszh.ch/daisyproducer

cd $INSTALL_DIR
git pull
make locale/de/LC_MESSAGES/django.mo
sudo /etc/init.d/apache2 restart
