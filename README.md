# Cloreco: Clone Recognizer Comparator platform - A tool for the evaluation of clone detectors
This web platform can be used to execute one or multiple code clone detector tools on one or multiple clone benchmarks. 
Their configurations can be set directly in the web interface.  
Containers are used to run the clone detector tools in an isolated environment while ensuring reproducibility of execution.

Features:
 - execute one or multiple code clone detector tools
 - use one or multiple clone benchmarks
 - configure the options of benchmarks and clone detector tools
 - access and download the execution/evaluation results, used settings, recognised clones, etc.
 - recall display in interactive charts
 - display the current execution progress
 - add new clone detection tools via image or git repository
 - add new benchmarks (manually, without web interface)

The execution artefacts (settings, recognised clones, evaluation results, etc.) can be downloaded via the platform.

The platform includes various code clone detection tools and clone benchmarks. You can extend your instance with more of these tools and benchmarks. Code clone detection tools can be added directly through the web interface.

Further information can be found in the [Wiki](https://github.com/Glopix/cloreco/wiki), including information on how to set it up.

## Setup 
[Setup instructions](https://github.com/Glopix/cloreco/wiki/Setup)

## Images
The images of the already containerized code clone detector tools and clone benchmark frameworks are available in [this repository](https://github.com/Glopix/cloreco-images).

  
  <br><br><br><br><br><br><br><br>
  
  
Copyright (C) 2024  Franz Burock (Glopix)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
