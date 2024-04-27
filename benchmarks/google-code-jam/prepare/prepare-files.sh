#!/usr/bin/env bash

MAIN_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
cd "${MAIN_DIR}"

# extract each archive's contents into the same directory where the archive file is located
echo "extracting solutions.sqlar archives"
find ../ -name "solutions.sqlar" -execdir ../../prepare/sqlite3 '{}' ".ar x" \;

echo "sorting java files"
./separate_tasks.py --directory ../input/ --min-files 5 # --all-sub-tasks 

# remove unnecessary, leftover files
rm -rf ../input/static/
rm -rf ../input/index*.html
rm -rf ../input/*/problems/
rm -rf ../input/*/solutions/
rm -rf ../input/*/index*.html
rm -rf ../input/*/raw_data.sqlar
rm -rf ../input/*/solutions.sqlar

# delete all empty directories in the input directory.
# <year>wf directories are sometimes empty, 
# since no or too few .java submissions are in it (see --min-files argument from separate_tasks.py)
find ../input/ -type d -empty -delete