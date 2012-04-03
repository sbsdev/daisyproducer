#!/bin/bash

# to build pipeline:
#   ant -q -e -f build-core.xml buildReleaseZip
# to build braille tables
#    make dist 

function is_newer_locally() {
    if ( cd `dirname $1` && md5sum `basename $1` ) | ssh $2 " ( cd $3 &&  md5sum --check --status ) "; then
	return 1
    else
	return 0
    fi
}

function restart_apache() {
    ssh -t $1 "sudo /etc/init.d/apache2 restart"
}

function deploy_dtbook2sbsform() {
    local PACKAGE=~/src/dtbook2sbsform/dtbook2sbsform.zip
    if is_newer_locally $PACKAGE $1 $2; then
	echo "`basename $PACKAGE` is newer locally. Deploying it..."
	scp $PACKAGE $1:$2
	ssh $1 "
cd $2
rm -rf `basename $PACKAGE .zip`
unzip -q `basename $PACKAGE`"
    else
	echo "`basename $PACKAGE` has already been deployed. Skipping it..."
    fi
}

function deploy_braille_tables() {
    local PACKAGE=`ls -rt ~/src/sbs-braille-tables/sbs-braille-tables-*.tar.gz|tail -1`
    if is_newer_locally $PACKAGE $1 $2; then
	echo "`basename $PACKAGE` is newer locally. Deploying it..."
	scp $PACKAGE $1:$2
	ssh -t $1 "
cd $2
tar xzf `basename $PACKAGE`
cd `basename $PACKAGE .tar.gz`
./configure
make
sudo make install"
    else
	echo "`basename $PACKAGE` has already been deployed. Skipping it..."
    fi
}

function deploy_hyphen_java_bindings() {
    local PACKAGE=`ls -rt ~/src/jhyphen/jhyphen-*.tar.gz|tail -1`
    if is_newer_locally $PACKAGE $1 $2; then
	echo "`basename $PACKAGE` is newer locally. Deploying it..."
	scp $PACKAGE $1:$2
	ssh -t $1 "
cd $2
# removing the old source seems to help with using user variables for make below
rm -rf `basename $PACKAGE .tar.gz` 
tar xzf `basename $PACKAGE`
cd `basename $PACKAGE .tar.gz`
./configure
make $3
sudo make install"
    else
	echo "`basename $PACKAGE` has already been deployed. Skipping it..."
    fi
}

function deploy_pipeline() {
    local PACKAGE=`ls -rt ~/src/dmfc/dist/pipeline-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].zip|tail -1`
    if is_newer_locally $PACKAGE $1 $2; then
	echo "`basename $PACKAGE` is newer locally. Deploying it..."
	scp $PACKAGE $1:$2
	ssh $1 "
cd $2
rm -rf `basename $PACKAGE .zip`
unzip -q `basename $PACKAGE`
rm pipeline
ln -s `basename $PACKAGE .zip` pipeline
cp pipeline/transformers/se_tpb_dtbook2latex/dtbook2latex_sbs.xsl pipeline/transformers/se_tpb_dtbook2latex/dtbook2latex.xsl"
    else
	echo "`basename $PACKAGE` has already been deployed. Skipping it..."
    fi
}

case "$1" in
    prod) 
	deploy_pipeline xmlp /opt
	deploy_dtbook2sbsform xmlp /opt
	deploy_braille_tables xmlp ~/src
	restart_apache xmlp;;
    test) 
	deploy_pipeline xmlp-test /opt
	deploy_dtbook2sbsform xmlp-test /opt
	deploy_braille_tables xmlp-test ~/src
	deploy_hyphen_java_bindings xmlp-test ~/src "CPPFLAGS='-I/usr/lib/jvm/java-6-sun-1.6.0.26/include -I/usr/lib/jvm/java-6-sun-1.6.0.26/include/linux'"
	restart_apache xmlp-test;;
    
    dev|*) 
	deploy_pipeline localhost ~/tmp
	deploy_dtbook2sbsform localhost ~/tmp;;

esac

