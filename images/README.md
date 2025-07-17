# images
Each subdirectory contains the files needed to containerize a clone detector tool.
Typically, this includes:
- Dockerfiles
- Runner scripts
- Additional scripts, if needed

All container images can be built at once using the docker-build.py script, instead of manually running `docker build` in each subdirectory.
Use the following command:
`./docker-build.py`

