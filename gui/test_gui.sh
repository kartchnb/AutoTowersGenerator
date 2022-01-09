#!/usr/bin/bash

# Locate the temporary Cura directory
cura_dir=`ls -a /tmp | grep .mount_cura | sed 1q`

# Display an error if a Cura directory was not found
if [ -z "${cura_dir}" ]; then
    echo "Could not find a Cura directory - make sure Cura is running"
    exit 1
fi

# Determine the UM include directory
um_dir="/tmp/${cura_dir}/usr/bin/lib/UM/Qt/qml"

# If a qml file was specified, use it, otherwise, use the first one found in the directory
qml_file=$1
if [ -z "${qml_file}" ]; then
    qml_file=`ls . | grep .qml | sed 1q`
fi

echo Displaying ${qml_file}

# Test the GUI
qmlscene -I ${um_dir} ${qml_file}
