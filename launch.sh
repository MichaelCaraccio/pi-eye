#! /bin/bash

#set -e
#set -u

function requirements 
{
    if [ $(dpkg-query -W -f='${Status}' gpac 2>/dev/null | grep -c "ok installed") -eq 0 ];
    then
        sudo apt-get update
	sudo apt-get -y install gpac
    fi
}

function launch
{
    requirements
    local readonly PATH_TO_SCRIPT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    pushd $PATH_TO_SCRIPT &> /dev/null
    export PYTHONPATH=$PATH_TO_SCRIPT:$PYTHONPATH
    python3 use/main_camera_sensor.py
    popd &> /dev/null 
}

launch
