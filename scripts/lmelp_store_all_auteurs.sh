#!/bin/bash 
# check arguments, valid ones are -v or --verbose, -d or --date, -h or --help and they are optional
while [ "$1" != "" ]; do
    case $1 in
        -v | --verbose )        shift
                                verbose=1
                                ;;
        -d | --date )           shift
                                date=$1
                                ;;
        -h | --help )           echo "Usage: lmelp_store_all_auteurs.sh [-v | --verbose] [-d | --date dd/mm/yyyy]"
                                exit
                                ;;
        * )                     echo "Usage: lmelp_store_all_auteurs.sh [-v | --verbose] [-d | --date dd/mm/yyyy]"
                                exit 1
    esac
    shift
done
export GPG_TTY=$(tty)
source ~/miniforge3/etc/profile.d/conda.sh
source ~/miniforge3/etc/profile.d/mamba.sh
mamba activate whisper
pushd ~/git/lmelp/scripts
python store_all_auteurs_from_all_episodes.py  "$@"
popd
