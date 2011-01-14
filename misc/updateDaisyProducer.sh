#! /bin/sh

#  Copyright (C) 2009, 2011 Christian Egli

# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.

INSTALL_DIR=/srv/demo.xmlp.sbszh.ch/daisyproducer

cd $INSTALL_DIR
git pull
sudo /etc/init.d/apache2 restart
