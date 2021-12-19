#!/usr/bin/bash
log_file=/home/brad/.local/share/cura/4.11/cura.log
cura_command=cura

# Delete the log file
rm ${log_file}

# Launch cura
${cura_command}&
