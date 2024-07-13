#!/usr/bin/env python3

"""
This script is designed to automate the building and pushing of Docker images 
for various combinations of OS distributions and Java Development Kits (JDKs). 

It accepts several command-line arguments to customize the build process, including: 
- an access token 
- a version tag, 
- a single directory to execute the build process instead of all subdirectories,
- directories to exclude from the build process.
The script also prunes unused Docker resources after building to reduce the storage usage.
"""

import os
from pathlib import Path
import subprocess
from argparse import ArgumentParser

# Repository/Registry to which the created images are pushed
repo = 'ghcr.io/glopix/cloreco-images'
path = Path(__file__).parent

parser = ArgumentParser()
parser.add_argument("-a", "--access-token", 
                    help="(GitLab/GitHub) Access Token")
parser.add_argument("-v", "--version-tag", 
                    help="give each image a version tag  (e.g. 1.0)", default=None)
parser.add_argument("-d", "--directory", 
                    help="execute docker build for this directory only")
parser.add_argument("-e", "--excluded-directories", nargs="*",
                    help="exclude these directories from docker build")
args = parser.parse_args()

excluded_dirs = ['iclones']
print(args.excluded_directories)
if args.excluded_directories:
    excluded_dirs.extend(args.excluded_directories)

# combination of OS distributions and JDK versions, 
# used to build different detector-tool-base images (detector-tool-base:ubuntu:XX.04-jdkX)
dist_jdks = [
    {"distro" : 'ubuntu:22.04', "jdk" : 'openjdk-21-jdk'},
    {"distro" : 'ubuntu:22.04', "jdk" : 'openjdk-17-jdk'},
    {"distro" : 'ubuntu:22.04', "jdk" : 'openjdk-11-jdk'},
    {"distro" : 'ubuntu:22.04', "jdk" : 'openjdk-8-jdk'},
    {"distro" : 'ubuntu:18.04', "jdk" : 'openjdk-8-jdk'}
    ]

if args.access_token:
    build_arg_token = f"--build-arg GITLAB_ACCESS_TOKEN={args.access_token}"
else:
    build_arg_token = ""

def dockerBuild(dir: Path, version=None):
    os.chdir(dir)
    tag = "latest"
    image_name = f"{repo}/{dir.name.lstrip('_')}"

    # for detector-tool-base base image
    if dir.name == '_detector-tool-base':

        for combo in dist_jdks:
            jdk = combo['jdk']
            distro = combo['distro']
            jdk_tag = jdk.replace('open','').replace('-jdk','').replace('-','')  # remove 'open', '-jdk' and '-' from e.g. 'openjdk-17-jdk'
            tag = f"{distro.replace(':', '')}-{jdk_tag}"

            if version:
                version_tag = f" -t {image_name}:{tag}_v{version} "
            else:
                version_tag = ""

            print(f"\033[93m==============> building {image_name}:{tag} \033[00m")
            
            # build image
            # {image_name}:{tag} --> detector-tool-base:ubuntu:XX.04-jdkX
            subprocess.run(f""" docker build . -t {image_name}:{tag} {version_tag} --build-arg DISTRO={distro} --build-arg JDK_VERSION={jdk}""", shell=True, capture_output=False, check=True)


    if version:
        # set an additional version tag for this image
        version_tag = f" -t {image_name}:v{version} "
    else:
        version_tag = ""
    
    print(f"\033[93m==============> building {image_name}:{tag} \033[00m")
    
    # build image
    subprocess.run(f""" docker build . -t {image_name} {version_tag} {build_arg_token} """, shell=True, capture_output=False, check=True)
    
    # push all local versions of this image
    subprocess.run(f""" docker push {image_name} --all-tags """, shell=True, capture_output=False, check=True)

# execute for one directory only, if specified via argument
if args.directory:
    directory = path / args.directory
    if directory.is_dir():
        dockerBuild(directory, version=args.version_tag)
        exit()
    else:
        exit("no valid directory")



# execute for all directories
dirs = list(path.glob("*"))
dirs.sort()

# for every clone detection tool / directory in images/
for dir in dirs:
    if dir.is_dir() and dir.name not in excluded_dirs:
        dockerBuild(dir, version=args.version_tag)
    else:
        continue
    
subprocess.run(f"""docker system prune --force""", shell=True, capture_output=False, check=True)
exit()
