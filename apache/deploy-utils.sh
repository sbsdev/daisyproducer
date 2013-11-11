#!/bin/bash

# ==============================================================================

curl() {
    local URL=$1
    if ! /usr/bin/curl "$URL" --silent --head --fail >/dev/null ; then
        echo "curl failed to resolve $URL" 1>&2
        return 1
    fi
    /usr/bin/curl "$URL" "${@:2}"
}

xpath() {
    /usr/bin/xpath -e "$1" 2>&1 | sed "s/^Query didn't return a nodeset\. Value: //"
    return ${PIPESTATUS[0]}
}

sha() {
    local HOST=$1
    local FILE=$2
    ssh $HOST "shasum -a 1 $FILE | awk '{print \$1;}'"
}

compare_versions() {
    perl -e '($x,$y)=@ARGV; print $x cmp $y' $1 $2
}

filter_versions() {
    local PREDICATE=$1
    local VERSION
    while read VERSION ; do
        eval "$PREDICATE $VERSION ${@:2}" && echo $VERSION
    done
}

select_version() {
    local VERSIONS VERSION
    VERSIONS=( )
    while read VERSION; do
        VERSIONS+=( $VERSION )
    done
    VERSIONS+=( Skip )
    PS3='Please select a version: '
    select VERSION in ${VERSIONS[@]}; do
        [ $VERSION = 'Skip' ] && return 1
        [ -n "$VERSION" ] && break || echo -n "Wrong answer! "
    done
    RET=$VERSION
    return 0
}

# ==============================================================================
# DEBIAN
# ==============================================================================

deb_get_version() {
    local HOST=$1
    local FILE=$2
    ssh $HOST "dpkg-deb -f $FILE Version"
}

deb_get_installed_version() {
    local HOST=$1
    local PACKAGE=$2
    ssh $HOST "dpkg-query -W -f='\${Version}' $PACKAGE 2>/dev/null"
}

deb_compare_versions() {
    dpkg --compare-versions $1 gt $2
}

# ==============================================================================
# MAVEN
# ==============================================================================

NEXUS_URL=http://xmlp-test:8081/nexus
NEXUS_STORAGE_SERVER=xmlp-test
NEXUS_STORAGE_PATH=/srv/nexus/sonatype-work/nexus/storage

mvn_parse_artifact_identifier() {
    local GAPCV=$1
    local IFS FIELS LENGTH
    IFS=':'
    FIELDS=( $(echo "$GAPCV") )
    LENGTH=${#FIELDS[@]}
    [ $LENGTH -gt 0 ] && G=${FIELDS[0]} &&
    [ $LENGTH -gt 1 ] && A=${FIELDS[1]} &&
    [ $LENGTH -gt 2 ] && P=${FIELDS[2]} &&
    [ $LENGTH -gt 3 ] && C=${FIELDS[3]} &&
    [ $LENGTH -gt 4 ] && V=${FIELDS[4]}
}

mvn_is_snapshot() {
    local VERSION=$1
    [ ${VERSION%-SNAPSHOT} != $VERSION ]
}

mvn_get_artifact_sha() {
    local GAPCV=$1
    local G A P C V R
    mvn_parse_artifact_identifier $GAPCV
    R=public
    curl "$NEXUS_URL/service/local/artifact/maven/resolve?r=$R&g=$G&a=$A&p=$P&c=$C&v=$V" \
        --silent --show-error --location \
    | xpath 'string(//sha1)'
}

mvn_list_versions() {
    local GA=$1
    # TODO: GAPC
    local G A R VERSIONS
    mvn_parse_artifact_identifier $GA
    R=public
    VERSIONS=( $( \
        curl "$NEXUS_URL/content/repositories/$R/$(echo $G | tr '.' '/')/$A/maven-metadata.xml" \
            --silent --show-error --location \
        | xpath 'string(//versions)' ) )
    [ $? = 0 ] && printf '%s\n' "${VERSIONS[@]}" | sort -r
}

mvn_download_artifact() {
    local GAPCV=$1
    local FILE=$2
    local G A P C V R
    mvn_parse_artifact_identifier $GAPCV
    R=public
    mkdir -p $( dirname "$FILE" )
    rm -rf "$FILE"
    curl "${NEXUS_URL}/service/local/artifact/maven/redirect?r=$R&g=$G&a=$A&p=$P&c=$C&v=$V" \
        --silent --show-error --location --output $FILE
    [ -e $FILE ] || return 1 
}

mvn_get_deb_version() {
    local GAPCV=$1
    local G A P C V R REPOSITORY_PATH
    mvn_parse_artifact_identifier $GAPCV
    [ "$P" = deb ] || return 1
    R=public
    REPOSITORY_PATH=$( \
        curl "$NEXUS_URL/service/local/artifact/maven/resolve?r=$R&g=$G&a=$A&p=$P&c=$C&v=$V" \
            --silent --show-error --location \
        | xpath 'string(//repositoryPath)' ) || return 1
    R=$( mvn_is_snapshot $V && echo snapshots || echo releases )
    deb_get_version $NEXUS_STORAGE_SERVER $NEXUS_STORAGE_PATH/$R/$REPOSITORY_PATH
}

# ==============================================================================

is_newer_file() {
    local VERSION=$1
    local FILE_VERSION=$2
    local FILE_SHA=$3
    local GAPC=$4
    local ARTIFACT_SHA FILE_SHA
    case $( compare_versions $VERSION $FILE_VERSION ) in
        1) return 0 ;;
        0)
            mvn_is_snapshot $VERSION || return 1
            [ -e $FILE ] || return 0
            ARTIFACT_SHA=$( mvn_get_artifact_sha $GAPC:$VERSION ) || return 1
            [ $ARTIFACT_SHA != $FILE_SHA ] && return 0
            ;;
    esac
    return 1
}

is_newer_deb() {
    local VERSION=$1
    local DEB_VERSION=$2
    local GAPC=$3
    local ARTIFACT_DEB_VERSION
    ARTIFACT_DEB_VERSION=$( mvn_get_deb_version $GAPC:$VERSION ) || return 1
    deb_compare_versions $ARTIFACT_DEB_VERSION $DEB_VERSION
}
