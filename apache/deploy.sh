#!/bin/bash

# to build pipeline:
#   ant -q -e -f build-core.xml buildReleaseZip
# to build braille tables
#    make dist 

source deploy.cfg
if [[ $? != 0 ]] ; then
    exit 1
fi

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
    local PACKAGE=$SRC_ROOT/dtbook2sbsform/dtbook2sbsform.zip
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

function deploy_dtbook_hyphenator() {
    local PACKAGE=$SRC_ROOT/dtbook_hyphenator/dtbook_hyphenator.zip
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
    local PACKAGE=`ls -rt $SRC_ROOT/sbs-braille-tables/sbs-braille-tables-*.tar.gz|tail -1`
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

function deploy_pipeline() {
    local PACKAGE=`ls -rt $SRC_ROOT/dmfc/dist/pipeline-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].zip|tail -1`
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
	deploy_dtbook_hyphenator xmlp /opt
	deploy_braille_tables xmlp ~/src
	restart_apache xmlp;;

    test) 
	deploy_pipeline xmlp-test /opt
	deploy_dtbook2sbsform xmlp-test /opt
	deploy_dtbook_hyphenator xmlp-test /opt
	deploy_braille_tables xmlp-test ~/src
	restart_apache xmlp-test;;
    
    dev|*) 
	deploy_pipeline localhost ~/tmp
	deploy_dtbook2sbsform localhost ~/tmp
	deploy_dtbook_hyphenator localhost ~/tmp;;

esac

