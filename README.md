# Enodia
A python wrapper around kubectl logs to make searches easier

In short, this is a version of git for Kubernetes logs. It will allow you to 
go through the logs for a specified container name for every pod that matches
a simple string search. It will then go through the log file and provide all
the lines that match your search terms, exclude any lines that have excluded
terms, and provide the requested number of lines before or after each instance
of the search term.

# Requirements
Hecate only requires the official Kubernetes Python library. You can run

pip install -r requirements.txt

To install it on most systems.

# Examples

python3 enodia.py -o output.txt -s mytext1 mytext2 -c container_name \
    -p partial_pod_name -n namespace_name -x exclude1 exclude2 \
    -a 10 -b 5

This will look at the logs for container container_name in every pod that has
partial_pod_name in it for the namespace namespace_name. Any lines that have
exclude1 or exclude2 will be removed from the search results. Five lines before
the result and ten lines after the result will be included in the output.

This is analagous to 

kubectl logs -c container_name -n namespace_name pod_name | grep -v exclude1 \
    | grep -v exclude2 | grep 'mytext1\|mytext2' -A10 -B10

The only difference is that it will search all pods with a match on the pod
name, rather than the one specific pod.


# Usage

A utility to search kubernetes log files

optional arguments:
  -h, --help            show this help message and exit
  -a AFTER [AFTER ...], --after AFTER [AFTER ...]
                        lines after the search result to include                                                                                                                                                  
  -b BEFORE [BEFORE ...], --before BEFORE [BEFORE ...]                                                                                                                                                            
                        lines after the search result to include                                                                                                                                                  
  -c CONTAINER [CONTAINER ...], --container CONTAINER [CONTAINER ...]                                                                                                                                             
                        container to search in                                                                                                                                                                    
  -p POD [POD ...], --pod POD [POD ...]                                                                                                                                                                           
                        pod name to limit search results                                                                                                                                                          
  -x EXCLUDE [EXCLUDE ...], --exclude EXCLUDE [EXCLUDE ...]
                        a comma separated list of strings to exclude
  -s SEARCH [SEARCH ...], --search SEARCH [SEARCH ...]
                        a comma separated list of strings to search for.
  -o OUT [OUT ...], --out OUT [OUT ...]
                        a filename to store results
  -n NAMESPACE [NAMESPACE ...], --namespace NAMESPACE [NAMESPACE ...]
                        Namespace to search in

LICENSE

Copyright 2022 Philip Eatherington

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
