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

function deploy_hyphenation_tables() {
    local PACKAGE=`ls -rt $HYPHENATION_TABLES_ROOT/../sbs-hyphenation-tables_*.deb|tail -1`
    if is_newer_locally $PACKAGE $1 $2; then
	echo "`basename $PACKAGE` is newer locally. Deploying it..."
	scp $PACKAGE $1:$2
	ssh -t $1 "
cd $2
rm -rf `basename $PACKAGE .deb`
sudo dpkg -i `basename $PACKAGE`"
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

function deploy_dp2() {
    local PACKAGE=`ls -rt $DP2_ROOT/target/pipeline2-[0-9].[0-9].zip|tail -1`
    if is_newer_locally $PACKAGE $1 $2; then
	echo "`basename $PACKAGE` is newer locally. Deploying it..."
	scp $PACKAGE $1:$2
	ssh $1 "
cd $2
unzip -o -q `basename $PACKAGE`"
    else
	echo "`basename $PACKAGE` has already been deployed. Skipping it..."
    fi
}

M2_REPO=${HOME}/.m2/repository

function deploy_dp2_module() {
    local MODULE=($(echo $1 | tr ":" " "))
    local GROUP_ID=${MODULE[0]}
    local ARTIFACT_ID=${MODULE[1]}
    local PACKAGING=${MODULE[2]}
    local VERSION CLASSIFIER
    if [ -n "${MODULE[4]}" ]; then
        CLASSIFIER=-${MODULE[3]}
        VERSION=${MODULE[4]}
    else
        VERSION=${MODULE[3]}
    fi
    local PACKAGE=${M2_REPO}/$(echo $GROUP_ID | tr "." "/")/${ARTIFACT_ID}/${VERSION}/${ARTIFACT_ID}-${VERSION}${CLASSIFIER}.${PACKAGING}
    if is_newer_locally $PACKAGE $2 $3; then
	echo "`basename $PACKAGE` is newer locally. Deploying it..."
	# remove old module
	ssh $2 "
cd $3
rm -rf ${ARTIFACT_ID}-*${CLASSIFIER}.${PACKAGING}"
	scp $PACKAGE $2:$3
    else
	echo "`basename $PACKAGE` has already been deployed. Skipping it..."
    fi
}

case "$1" in
    prod)
	deploy_pipeline xmlp /opt
	deploy_dp2 xmlp /opt
	deploy_dp2_module ch.sbs.pipeline.modules:dtbook-to-odt:jar::1.0.0-SNAPSHOT xmlp /opt/daisy-pipeline/modules
	deploy_dp2_module org.daisy.pipeline.modules:odt-utils:jar::1.0.0-SNAPSHOT xmlp /opt/daisy-pipeline/modules
	deploy_dp2_module org.daisy.libs:libreoffice-uno:jar::4.0.2-SNAPSHOT xmlp /opt/daisy-pipeline/modules
	deploy_dp2_module org.daisy.libs:jodconverter-core:jar::3.0-beta-4-SNAPSHOT xmlp /opt/daisy-pipeline/modules
	deploy_dp2_module org.daisy.pipeline.modules:asciimathml:jar::1.0.0-SNAPSHOT xmlp /opt/daisy-pipeline/modules
	deploy_dp2_module org.daisy.pipeline.modules:image-utils:jar::1.0.0-SNAPSHOT xmlp /opt/daisy-pipeline/modules
	deploy_dtbook2sbsform xmlp /opt
	deploy_dtbook_hyphenator xmlp /opt
	deploy_hyphenation_tables xmlp ~/src
	deploy_braille_tables xmlp ~/src
	restart_apache xmlp;;

    test)
	deploy_pipeline xmlp-test /opt
	deploy_dp2 xmlp-test /opt
	deploy_dp2_module ch.sbs.pipeline.modules:dtbook-to-odt:jar::1.0.0-SNAPSHOT xmlp-test /opt/daisy-pipeline/modules
	deploy_dp2_module org.daisy.pipeline.modules:odt-utils:jar::1.0.0-SNAPSHOT xmlp-test /opt/daisy-pipeline/modules
	deploy_dp2_module org.daisy.libs:libreoffice-uno:jar::4.0.2-SNAPSHOT xmlp-test /opt/daisy-pipeline/modules
	deploy_dp2_module org.daisy.libs:jodconverter-core:jar::3.0-beta-4-SNAPSHOT xmlp-test /opt/daisy-pipeline/modules
	deploy_dp2_module org.daisy.pipeline.modules:asciimathml:jar::1.0.0-SNAPSHOT xmlp-test /opt/daisy-pipeline/modules
	deploy_dp2_module org.daisy.pipeline.modules:image-utils:jar::1.0.0-SNAPSHOT xmlp-test /opt/daisy-pipeline/modules
	deploy_dtbook2sbsform xmlp-test /opt
	deploy_dtbook_hyphenator xmlp-test /opt
	deploy_hyphenation_tables xmlp-test ~/src
	deploy_braille_tables xmlp-test ~/src
	restart_apache xmlp-test;;

    dev|*)
	deploy_pipeline localhost ~/tmp
	deploy_dp2 localhost ~/tmp
	deploy_dp2_module ch.sbs.pipeline.modules:dtbook-to-odt:jar::1.0.0-SNAPSHOT localhost ~/tmp/daisy-pipeline/modules
	deploy_dp2_module org.daisy.pipeline.modules:odt-utils:jar::1.0.0-SNAPSHOT localhost ~/tmp/daisy-pipeline/modules
	deploy_dp2_module org.daisy.libs:libreoffice-uno:jar::4.0.2-SNAPSHOT localhost ~/tmp/daisy-pipeline/modules
	deploy_dp2_module org.daisy.libs:jodconverter-core:jar::3.0-beta-4-SNAPSHOT localhost ~/tmp/daisy-pipeline/modules
	deploy_dp2_module org.daisy.pipeline.modules:asciimathml:jar::1.0.0-SNAPSHOT localhost ~/tmp/daisy-pipeline/modules
	deploy_dp2_module org.daisy.pipeline.modules:image-utils:jar::1.0.0-SNAPSHOT localhost ~/tmp/daisy-pipeline/modules
	deploy_dtbook2sbsform localhost ~/tmp
	deploy_dtbook_hyphenator localhost ~/tmp
	deploy_hyphenation_tables localhost ~/tmp;;

esac

