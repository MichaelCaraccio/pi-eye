#! /bin/bash

#set -e
#set -u

function launch
{
    local readonly PATH_TO_SCRIPT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    pushd $PATH_TO_SCRIPT &> /dev/null
    export PYTHONPATH=$PATH_TO_SCRIPT:$PYTHONPATH
    python3 use/main_camera_sensor.py
    popd &> /dev/null 
}

launch
