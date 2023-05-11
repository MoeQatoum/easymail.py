#!/bin/bash

#colors
W="\033[0;00m"
G="\033[0;92m"
R="\033[0;91m"
Y="\033[0;93m"

APP_FOLDER_EXISTS=false

SCRIPT_PATH=$(realpath "$(dirname "${BASH_SOURCE[0]}")")

SRC_PATH=$SCRIPT_PATH/src
BUILD_PATH=$SCRIPT_PATH/build
INSTALL_PATH=$SCRIPT_PATH/app
UPX_PATH=$SCRIPT_PATH/upx/upx-4.0.2_linux

printf "${G}-- SCRIPT_PATH: $SCRIPT_PATH${W}\n"
printf "${G}-- INSTALL_PATH: $INSTALL_PATH${W}\n"

if [ -d $BUILD_PATH ]; then
  rm -rf $BUILD_PATH
fi

if [ -d $INSTALL_PATH ]; then
  APP_FOLDER_EXISTS=true
fi

pyinstaller $SRC_PATH/main.py -n easymail --upx-dir=$UPX_PATH --workpath $BUILD_PATH --distpath $INSTALL_PATH --onefile --clean -c --log-level INFO
if [[ $? -eq 0 ]]; then
  if [ $APP_FOLDER_EXISTS = false ]; then
    printf "${G}-- copying fresh config files ...${W}\n"
    cp $SCRIPT_PATH/sample_config.json $INSTALL_PATH/config.json
    cp $SCRIPT_PATH/*.txt $INSTALL_PATH
    echo "[]" >$INSTALL_PATH/blacklist.json
    echo "{}" >$INSTALL_PATH/timestamp.json
  fi
  printf "${G}-- Build success${W}\n"
else
  printf "${R}-- Build failed${W}\n"
fi

rm -rf $BUILD_PATH
