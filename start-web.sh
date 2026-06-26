#!/bin/bash
export NVM_DIR="/home/msi/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
cd /home/msi/project/degree-guidance
exec npm --prefix web run dev
