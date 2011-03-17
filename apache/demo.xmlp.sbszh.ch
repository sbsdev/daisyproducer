#
# VirtualHost demo.xmlp.sbszh.ch
#
#
<VirtualHost *:80>
    ServerAdmin sysadmin@sbszh.ch
    ServerName demo.xmlp.sbszh.ch
    ServerAlias xmlp.sbszh.ch demo.xmlp xmlp

    DocumentRoot /srv/demo.xmlp.sbszh.ch/
    ErrorLog /var/log/apache2/demo.xmlp.sbszh.ch-error_log
    CustomLog /var/log/apache2/demo.xmlp.sbszh.ch-access_log combined

    HostnameLookups Off
    UseCanonicalName Off
    ServerSignature On

    Alias /media/ /usr/share/python-support/python-django/django/contrib/admin/media/

    <Directory /usr/share/python-support/python-django/django/contrib/admin/media>
        Order deny,allow
        Allow from all
    </Directory>

    Alias /stylesheets/ /srv/demo.xmlp.sbszh.ch/daisyproducer/public/stylesheets/
    Alias /javascripts/ /srv/demo.xmlp.sbszh.ch/daisyproducer/public/javascripts/
    Alias /images/      /srv/demo.xmlp.sbszh.ch/daisyproducer/public/images/

    <Directory /srv/demo.xmlp.sbszh.ch/daisyproducer>
        Order deny,allow
        Allow from all
    </Directory>

    Alias /archive/ /srv/demo.xmlp.sbszh.ch/daisyproducer/archive/
    Alias /schema/  /srv/demo.xmlp.sbszh.ch/daisyproducer/documents/schema/


    WSGIScriptAlias / /srv/demo.xmlp.sbszh.ch/daisyproducer/daisyproducer.wsgi
</VirtualHost>
