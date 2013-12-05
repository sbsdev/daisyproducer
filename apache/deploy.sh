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

source `dirname $0`/deploy.cfg
if [[ $? != 0 ]] ; then
    exit 1
fi

DP2_PACKAGE=`ls -rt $DP2_PACKAGE_ROOT/daisy-pipeline2_*_all.deb|tail -1`
ODT_PACKAGE=`ls -rt $ODT_PACKAGE_ROOT/dtbook-to-odt_*_all.deb|tail -1`
HYPHENATION_TABLES_PACKAGE=`ls -rt $HYPHENATION_TABLES_ROOT/target/sbs-hyphenation-tables_*_all.deb|tail -1`
TCOLORBOX_PACKAGE=`ls -rt $DEBIAN_PACKAGES_ROOT/tcolorbox_*_all.deb|tail -1`

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

case "$1" in
    prod)
	deploy_deb $TCOLORBOX_PACKAGE xmlp ~/src
	deploy_pipeline xmlp /opt
	deploy_deb $DP2_PACKAGE xmlp ~/src
	deploy_deb $ODT_PACKAGE xmlp ~/src
	deploy_dtbook2sbsform xmlp /opt
	deploy_dtbook_hyphenator xmlp /opt
	deploy_deb $HYPHENATION_TABLES_PACKAGE xmlp ~/src
	deploy_braille_tables xmlp ~/src
	restart_apache xmlp;;

    test)
	deploy_deb $TCOLORBOX_PACKAGE xmlp-test ~/src
	deploy_pipeline xmlp-test /opt
	deploy_deb $DP2_PACKAGE xmlp-test ~/src
	deploy_deb $ODT_PACKAGE xmlp-test ~/src
	deploy_dtbook2sbsform xmlp-test /opt
	deploy_dtbook_hyphenator xmlp-test /opt
	deploy_deb $HYPHENATION_TABLES_PACKAGE xmlp-test ~/src
	deploy_braille_tables xmlp-test ~/src
	restart_apache xmlp-test;;

    dev|*)
	deploy_deb $TCOLORBOX_PACKAGE localhost /tmp
	deploy_pipeline localhost ~/tmp
	deploy_deb $DP2_PACKAGE localhost /tmp
	deploy_deb $ODT_PACKAGE localhost /tmp
	deploy_dtbook2sbsform localhost ~/tmp
	deploy_dtbook_hyphenator localhost ~/tmp
	deploy_deb $HYPHENATION_TABLES_PACKAGE localhost /tmp
	deploy_braille_tables localhost ~/tmp;;

esac

