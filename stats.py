#!/usr/bin/env python2.7

import json
import argparse
import pprint

parser = argparse.ArgumentParser()
parser.add_argument("network", help="Network json file", type=argparse.FileType('r'))
parser.add_argument("-d", "--density", type=int, default=1, help="LEDs per unit length")

gargs = None

def main():
    network = json.load(gargs.network)
    pprint.pprint(network)
    output = {
#       "Synapse Length (displayed)":   (sum(network['synapses'][s_key]['nlights'] 
#                                           for s_key in (set(network['keyorder']) & set(network['synapses'].keys()))) 
#                                       / gargs.density),
        "Synapse Length (total)":       (sum((s_entry[0]['nlights'] 
                                            for s_entry in network['synapses'].values()))
                                        / gargs.density),
#       "Neuron Length (displayed)":    (sum(network['neurons'][n_key]['nlights'] 
#                                           for n_key in set(network['keyorder']) & set(network['neurons'].keys()))
#                                       / gargs.density),
        "Neuron Length (total)":        (sum((n_entry['nlights'] for n_entry in network['neurons'].values()))
                                        / gargs.density),
       "Total Length (total)":          ((sum((n_entry['nlights'] for n_entry in network['neurons'].values()))
                                         / gargs.density) + 
                                         (sum((s_entry[0]['nlights'] 
                                            for s_entry in network['synapses'].values()))
                                        / gargs.density))

           
    }
    pprint.pprint(output)

if __name__ == '__main__':
    gargs = parser.parse_args();
    main()
