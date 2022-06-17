'''Enodia: a small utility to search Kubernetes log output.'''

from collections import defaultdict
import yaml
import argparse
from kubernetes import client, config
from pprint import pprint
from copy import deepcopy

class FixedSizedList:
    """A special type of list that never gets to more than N elements, if N is specified"""
    def __init__(self, size):
        self.data = []
        try:
            int(size)
        except TypeError:
            self.size = 0
        else:
            self.size = int(size)

    def append(self, entry):
        if self.size <= 0:
            return
            # can't store any data
        if len(self.data) == self.size:
            self.data.pop(0)
            # remove first entry before appending new data
        self.data.append(entry)
    
    def get_data(self):
        return self.data

    def empty(self):
        self.data = []


class Enodia:
    def __init__(self) -> None:
        config.load_kube_config()
        self.client = client.CoreV1Api()

    def get_pod_names(self, namespace):
        pod_list = self.client.list_namespaced_pod(namespace=namespace).to_dict()['items']
        toReturn = []
        for entry in pod_list:
            toReturn.append(entry['metadata']['name'])
        return toReturn

    def get_logs(self, podname, namespace, container=None):
        logs = defaultdict()
        podNames = self.get_pod_names(namespace)
        for entry in podNames:
            if podname in entry:
                if not container:
                    logs[podname] = self.client.read_namespaced_pod_log(entry, namespace=namespace, async_req=True)
                else:
                    logs[podname] = self.client.read_namespaced_pod_log(entry, namespace=namespace, container=container, async_req=True)
        for entry in logs.keys():
            # currently there's a thread; get it's results and put it in the dict instead
            logs[entry] = logs[entry].get()
        return logs

    def search_logs(self, logs, searchTerms, exclude=[], before=0, after=0):
        try:
            after = int(after)
        except TypeError:
            after = 0
        beforeBuffer = FixedSizedList(before)
        searchArea = deepcopy(logs)
        results = defaultdict(list)
        for key in searchArea.keys():
            searchArea[key] = searchArea[key].split('\n') # turn the big text blob to lines
            for term in searchTerms:
                for line in searchArea[key]:
                    if term not in line and not before:
                        continue
                        # required term missing, skip
                    if term not in line and before:
                        beforeBuffer.append(line)
                        # save this entry for future use
                        continue
                        # required term missing, skip
                    skipExclude = False
                    for exclusion in exclude:
                        if exclusion in line:
                            skipExclude = True  # an excluded term is present, skip
                    if skipExclude:
                        continue
                    if before:  # the term is here, and they want the before buffer
                        results[key].extend(beforeBuffer.get_data())
                        beforeBuffer.empty() # flush items we already added
                    results[key].append(line)
        if after:
            for key in results.keys():
                cur_index = list(searchArea.keys()).index(key)
                for index in range(1, after):
                    try:
                        # go to the entry in search area for the current key,
                        # then grab the list entry N entries away from the start
                        results[key].append(searchArea[key][cur_index + index])
                    except IndexError:
                        # we hit the end, no reason to look for more
                        break
        return results



def process(arguments):
    enodia = Enodia()
    # parse_args creates a namespace that contains a list of lists. So 
    # arguments.exclude = [[text1, text2]]
    # grab the actual values out of the 0th element for lists, [0][0] for strings
    after = 0
    before = 0
    container = None
    namespace = 'default'
    pod = arguments.pod[0][0]  # pod is required
    search = arguments.search[0]  # search is required, might be a list
    exclude = []
    out = None
    if arguments.container:
        container = arguments.container[0][0]
    if arguments.exclude:
        exclude = arguments.exclude[0]  # might be a list
    if arguments.after:
        after = arguments.after[0][0]
    if arguments.before:
        before = arguments.before[0][0]
    if arguments.namespace:
        namespace = arguments.namespace[0][0]
    logs = enodia.get_logs(pod, namespace, container=container)
    results = enodia.search_logs(logs, search, exclude=exclude, before=before, after=after)
    if arguments.out:
        out = arguments.out[0][0]
    if out:
        with open(arguments.out[0][0], 'a') as outFile:
            pprint(results, stream=outFile)
        return 'Output written to %s' % arguments.out[0][0]
    else:
        pprint(results)

if __name__ == "__main__":
    '''
    Just do some parsinng here, then hand off the parsed arguments to the
    process method to do the actual work.'''
    parser = argparse.ArgumentParser(
        description='A utility to search kubernetes log files')
    parser.add_argument('-a', '--after', action='append', nargs='+',
                        help='lines after the search result to include')
    parser.add_argument('-b', '--before', action='append', nargs='+',
                        help='lines after the search result to include')
    parser.add_argument('-c', '--container', action='append', nargs='+',
                        help='container to search in')
    parser.add_argument('-p', '--pod', action='append', nargs=1,
                        required=True,
                        help='pod name to limit search results')
    parser.add_argument('-x', '--exclude', action='append', nargs='+',
                        help='a comma separated list of strings to exclude')
    parser.add_argument('-s', '--search', action='append', nargs='+',
                        required=True,
                        help='a comma separated list of strings to search for.')
    parser.add_argument('-o', '--out', action='append', nargs='+',
                        help='a filename to store results')
    parser.add_argument('-n', '--namespace', action='append', nargs='+',
                        help='Namespace to search in')
    arguments = parser.parse_args()
    pprint(process(arguments))
