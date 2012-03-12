======================
Daisy Producer INSTALL
======================

Requirements
============

Basic requirements
------------------

- Python_ (tested with Python 2.5)
- Django_ 
- lxml_
- pyPDF_ (used for large print volume size calculation)
- `Daisy Pipeline`_ (use the Pipeline Core Packages)
- XeTex_ (to generate Large Print from LaTeX)
- texlive_ (should contain the extbook and titlesec class which is
  needed for Large Print) 
- `Tiresias LP font`_ (a font designed for Large Print publications)
- `Java Runtime`_ (`Daisy Pipeline`_ needs at least Java 5)
- liblouis_ You need to install both liblouis, liblouixml and the
  python bindings.
- A database for example PostgreSQL_ or MySQL_.
- A Python database interface like psycopg2_ or mysqldb_ for example.
- docutils_ to render the help page (which is written in
  reStructuredText Markup).
- south_ to handle changes in the database schema

.. _Python: http://www.python.org
.. _Django: http://www.djangoproject.com
.. _lxml: http://codespeak.net/lxml/index.html
.. _Daisy Pipeline: http://www.daisy.org/projects/pipeline/
.. _pyPDF: http://pybrary.net/pyPdf/
.. _XeTex: http://www.tug.org/xetex/
.. _texlive: http://www.tug.org/texlive/
.. _`Tiresias LP font`: http://www.tiresias.org/fonts/lpfont/about_lp.htm
.. _`Java Runtime`: http://www.java.com/en/download/manual.jsp
.. _liblouis: http://code.google.com/p/liblouis/
.. _PostgreSQL: http://www.postgresql.org/
.. _MySQL: http://www.mysql.com/
.. _psycopg2: http://www.initd.org/
.. _mysqldb: http://sourceforge.net/projects/mysql-python
.. _docutils: http://docutils.sourceforge.net
.. _south: http://south.aeracode.org/

Required packages
~~~~~~~~~~~~~~~~~

Basics
------

In terms of (Debian/Ubuntu) packages this translates to

- python
- python-django
- python-lxml
- python-docutils
- python-libxml2
- python-libxslt1
- python-pypdf
- sun-java6-jre
- texlive-xetex
- texlive-latex-extra
- texlive-lang-german
- ttf-tiresias
- xsltproc

Install the basic packages::

  sudo aptitude install python python-django python-django-south	\
  python-lxml python-docutils python-libxml2 python-libxslt1            \
  python-pypdf sun-java6-jre texlive-xetex texlive-latex-extra		\
  texlive-latex-recommended texlive-lang-german ttf-tiresias lmodern 	\
  xsltproc unzip

Database
--------

For PostgreSQL

- postgresql
- postgresql-client
- python-psycopg2

Install PostgreSQL::

  sudo aptitude install postgresql postgresql-client python-psycopg2

Set up a database, a user and a database::

  sudo -u postgres sh
  createuser -DRSP daisyproducer
  # enter the password "sekret" at the prompt
  createdb -O daisyproducer daisyproducer_prod
  # adapt pg_hba so that the user daisyproducer can log in with a password

For MySQL

- mysql-server
- mysql-client
- python-mysqldb

IN case you prefer MySQL::

  sudo aptitude install mysql-server mysql-client python-mysqldb

Again, set up a database, a user and a database::

  mysql --user=root
  CREATE DATABASE daisyproducer_prod;
  CREATE USER 'daisyproducer'@'localhost' IDENTIFIED BY 'sekret';
  GRANT ALL ON daisyproducer_prod.* TO 'daisyproducer'@'localhost';

Liblouis
--------

There is a `Debian package for liblouis`_ which can be used. If you
want the newest liblouis I would recommend to install it from source
as follows::

  # install liblouis dependencies
  sudo aptitude install pkg-config libxml2-dev
  # first install liblouis
  wget http://liblouis.googlecode.com/files/liblouis-2.1.1.tar.gz
  tar xzf liblouis-2.1.1.tar.gz
  cd liblouis-2.1.1
  ./configure --enable-ucs4
  make
  sudo make install
  # also install the python bindings
  cd python
  sudo python setup.py install
  # now install liblouisxml
  cd
  wget http://liblouisxml.googlecode.com/files/liblouisxml-2.1.0.tar.gz
  tar xzf liblouisxml-2.1.0.tar.gz
  cd liblouisxml-2.1.0
  ./configure
  make
  sudo make install
  sudo ldconfig

.. _Debian package for liblouis: http://packages.debian.org/search?keywords=liblouis&searchon=names&suite=all&section=all

Daisy Pipeline
--------------
The Daisy Pipeline has not been packaged so far and will have to be
installed somewhere::

  cd /opt
  sudo wget http://downloads.sourceforge.net/project/daisymfc/pipeline/pipeline-20110317-RC/pipeline-20110317-RC.zip
  sudo unzip pipeline-20110317-RC.zip
  sudo chmod a+x pipeline-20110317/pipeline.sh

The Daisy Pipeline has some dependencies as well, namely lame and
espeak::

  sudo aptitude install espeak espeak-data
  # on Debian you might have to enable the http://debian-multimedia.org/ repository
  sudo aptitude install lame

Then configure the path to lame in
/opt/pipeline-20090410/pipeline.user.properties and set it to /usr/bin/lame

Deployment requirements
-----------------------
- Apache_ (apache2)
- `Python WSGI adapter module for Apache`_ (libapache2-mod-wsgi)

.. _Apache: http://www.apache.org
.. _Python WSGI adapter module for Apache: http://code.google.com/p/modwsgi/

Install Apache and WSGI::

  sudo aptitude install apache2 libapache2-mod-wsgi

Enable wsgi for Apache by using a config file in
/etc/apache2/sites-available along the lines of the one given in the
apache subdirectory (see also `Apache config file example`_)

.. _Apache config file example: http://github.com/egli/daisy-producer/blob/master/apache/demo.xmlp.sbszh.ch

Optional requirements
---------------------
- autodoc_ (package postgresql-autodoc) if you want to generate the ER
  diagrams. Note however that autodoc only works if you are sing
  PostgreSQL as a database.

- python-yaml_ When running the tests (make check), fixtures will be
  loaded using yaml.

- sqlite_ To run the tests you need to have SQLite installed.

  sudo aptitude install python-yaml postgresql-autodoc python-pysqlite2 sqlite3

.. _python-yaml: http://pyyaml.org/
.. _autodoc: http://www.rbt.ca/autodoc/
.. _sqlite: http://www.sqlite.org/

Installation
============

There is currently no released version of Daisy Producer, so you can
get it directly from the source code repository::

  sudo mkdir /srv/demo.daisyproducer.org
  sudo chown dpadmin:dpadmin /srv/demo.daisyproducer.org/
  cd /srv/demo.daisyproducer.org
  sudo aptitude install git-core autoconf automake
  git clone git://github.com/egli/daisy-producer.git daisyproducer
  cd daisyproducer
  autoreconf -vfi
  ./configure

Configuration
=============

You need to adapt the settings to your environment::

  cd /srv/demo.daisyproducer.org/daisyproducer
  emacs settings.py
  
The following settings have to be adapted for your site:

- DATABASE_ENGINE

  - Needs to be either 'postgresql_psycopg2' or 'mysql'

- DATABASE_NAME

  - set to 'daisyproducer_prod'

- DATABASE_USER

  - set to 'daisyproducer'

- DATABASE_PASSWORD

  - set to 'sekret'

- DAISY_DEFAULT_PUBLISHER

  - set to the name of your organization

- DAISY_PIPELINE_PATH

  - set to os.path.join('/', 'path', 'to', 'pipeline-20100125')

- DTBOOK2SBSFORM_PATH 

  - set to os.path.join('/', 'path', 'to', 'dtbook2sbsform')

- SECRET_KEY
- TIME_ZONE
- SERVE_STATIC_FILES

  - set to 'False'

For the archive create a directory named archive under the
daisyproducer directory and give www-data write access to it::

  mkdir archive
  sudo chown www-data archive

Set ip the initial database tables::

  python manage syncdb

Upgrading from an older installation
====================================

You will have to install south and migrate the database::

  ./manage.py syncdb
  ./manage.py migrate documents 0001 --fake


Application setup
=================

Once the application is installed you will need to configure the
workflow, the users and the groups. Daisy Producer comes with a
default workflow, default groups and a demo user (password "demo")
that you can use to get started. You are of course free to define your
own workflow, users and groups. 

Once you are familiar with the concepts you can use the `admin
interface`_ to define states and transitions between them.

After you've defined the states and the transitions you will have to
create groups and define which group is responsible for which state.
Only members of a group that is responsible for a state will see
pending jobs in that particular state.

Lastly you will have to assign your users to particular groups to make
sure they see the pending jobs that they are responsible for.

You will also to have to give permission to add documents to some
users. This will allow these dedicated users to create new documents
that will have to worked on. Use the admin interface to either assign
the permission directly to the user or create a specific group (say
"Managers") which has the permission to add documents and assign users
to this group. The demo user has permission to add documents.

 .. _admin interface: http://127.0.0.1:8000/admin/
