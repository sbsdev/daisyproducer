#!/bin/bash

# to build pipeline:
#    ant -q -e -f build-core.xml buildReleaseZip
# to build dtbook2sbsform:
#    ant dist
# to build dtbook_hyphenator
#    ant dist
# to build braille tables
#    make dist
# to build hyphenation tables
#    debuild -us -uc

CURDIR=$(cd $(dirname "$0") && pwd)

source $CURDIR/deploy.cfg || exit 1
source $CURDIR/deploy-utils.sh

DP2_PACKAGE=`ls -rt $DP2_PACKAGE_ROOT/daisy-pipeline2-[0-9].[0-9]-SNAPSHOT.deb|tail -1`
ODT_PACKAGE=`ls -rt $ODT_PACKAGE_ROOT/dtbook-to-odt-[0-9].[0-9].[0-9]-SNAPSHOT.deb|tail -1`
HYPHENATION_TABLES_PACKAGE=`ls -rt $HYPHENATION_TABLES_ROOT/../sbs-hyphenation-tables_*.deb|tail -1`

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
    local PACKAGE=$DTBOOK2SBSFORM_ROOT/dtbook2sbsform.zip
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
    local PACKAGE=$DTBOOK_HYPHENATOR_ROOT/dtbook_hyphenator.zip
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
    local PACKAGE=`ls -rt $BRAILLE_TABLES_ROOT/sbs-braille-tables-*.tar.gz|tail -1`
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
    local PACKAGE=`ls -rt $PIPELINE_ROOT/dist/pipeline-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].zip|tail -1`
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

function deb_is_newer_locally() {
    local DEB=$1
    local PACKAGE=`dpkg-deb -f $DEB Package`
    local HOST=$2
    local VERSION=`dpkg-deb -f $DEB version`
    local REMOTE_VERSION=$(ssh $HOST "dpkg-query -W -f='\${Version}' $PACKAGE 2>/dev/null")
    if [ -z "$REMOTE_VERSION" ]; then
	REMOTE_VERSION=0
    fi
    ssh $HOST "dpkg --compare-versions $REMOTE_VERSION lt $VERSION"
}

function deploy_deb() {
    local PACKAGE=$1
    local HOST=$2
    local DEST=$3
    if deb_is_newer_locally $PACKAGE $HOST; then
	echo "`basename $PACKAGE` is newer locally. Deploying it..."
	scp $PACKAGE $HOST:$DEST
	ssh -t $HOST "
cd $DEST
rm -rf `basename $PACKAGE .deb`
sudo dpkg -i `basename $PACKAGE`"
    else
	echo "`basename $PACKAGE` has already been deployed. Skipping it..."
    fi
}

function deploy_deb2() {
    local GA=$1             # group:artifact
    local VERSION=$2        # new version
    local HOST=$3           # host machine
    local PACKAGE=$4        # debian package name (must correspond to $GA)
    local LOCAL_TMP=$5      # tmp directory on this machine
    local REMOTE_TMP=$6     # tmp directory on remote machine
    local INSTALLED_DEB_VERSION FILENAME
    INSTALLED_DEB_VERSION="$( deb_get_installed_version $HOST $PACKAGE )"
    if [ -z "$INSTALLED_DEB_VERSION" ] || is_newer_deb $VERSION $INSTALLED_DEB_VERSION $GA:deb: ; then
        FILENAME="$( echo $GA | tr ':' '.' )-$VERSION.deb"
        mvn_download_artifact $GA:deb::$VERSION "$LOCAL_TMP/$FILENAME" || return 1
        scp "$LOCAL_TMP/$FILENAME" "$HOST:$REMOTE_TMP/$FILENAME"
        ssh -t $HOST "sudo dpkg -i $REMOTE_TMP/$FILENAME"
    else
        echo "$PACKAGE $VERSION has already been deployed. Skipping it..."
    fi
}

case "$1" in

    foo)
        deploy_deb2 org.daisy.pipeline:assembly 1.6.0 localhost daisy-pipeline2 ~/Desktop ~/Desktop
        deploy_deb2 ch.sbs.pipeline.modules:dtbook-to-odt 1.0.0-SNAPSHOT localhost dtbook-to-odt ~/Desktop ~/Desktop
        ;;

    prod)
	deploy_pipeline xmlp /opt
	deploy_deb $DP2_PACKAGE xmlp ~/src
	deploy_deb $ODT_PACKAGE xmlp ~/src
	deploy_dtbook2sbsform xmlp /opt
	deploy_dtbook_hyphenator xmlp /opt
	deploy_deb $HYPHENATION_TABLES_PACKAGE xmlp ~/src
	deploy_braille_tables xmlp ~/src
	restart_apache xmlp;;

    test)
	deploy_pipeline xmlp-test /opt
	deploy_deb $DP2_PACKAGE xmlp-test ~/src
	deploy_deb $ODT_PACKAGE xmlp-test ~/src
	deploy_dtbook2sbsform xmlp-test /opt
	deploy_dtbook_hyphenator xmlp-test /opt
	deploy_deb $HYPHENATION_TABLES_PACKAGE xmlp-test ~/src
	deploy_braille_tables xmlp-test ~/src
	restart_apache xmlp-test;;

    dev|*)
	deploy_pipeline localhost ~/tmp
	deploy_deb $DP2_PACKAGE localhost /tmp
	deploy_deb $ODT_PACKAGE localhost /tmp
	deploy_dtbook2sbsform localhost ~/tmp
	deploy_dtbook_hyphenator localhost ~/tmp
	deploy_deb $HYPHENATION_TABLES_PACKAGE localhost /tmp
	deploy_braille_tables localhost ~/tmp;;

esac

