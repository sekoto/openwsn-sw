# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
'''
Module which receives DAO messages and calculates source routes.

.. moduleauthor:: Xavi Vilajosana <xvilajosana@eecs.berkeley.edu>
                  January 2013
.. moduleauthor:: Thomas Watteyne <watteyne@eecs.berkeley.edu>
                  April 2013
'''
import logging
log = logging.getLogger('topology')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import threading

import openvisualizer.openvisualizer_utils as u
from openvisualizer.eventBus import eventBusClient

import time, datetime

class topology(eventBusClient.eventBusClient):
    
    def __init__(self):
        
        # local variables
        self.dataLock        = threading.Lock()
        self.parents         = {}

        eventBusClient.eventBusClient.__init__(
            self,
            name                  = 'topology',
            registrations         =  [
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'updateParents',
                    'callback'    : self.updateParents,
                },
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'getParents',
                    'callback'    : self.getParents,
                },
            ]
        )
    
    #======================== public ==========================================

    def getstamp(self):
        ''' timestamp creator (seconds) '''
        ts = time.time()
        return ts
    
    def getParents(self,sender,signal,data):
        return self.parents
    
    def getDAG(self):
        states = []
        edges = []
        motes = []
        
        with self.dataLock:
            for src, dsts in self.parents.iteritems():
                dstslst = []
                for i in range(len(dsts)):
                    #print (dsts['parents'][i]['address'])
                    dstslst.append(dsts['parents'][i]['address'])
                     
                src_s = ''.join(['%02X' % x for x in src[-2:] ])
                motes.append(src_s)
                
                for dst in dstslst:
                    dst_s = ''.join(['%02X' % x for x in dst[-2:] ])
                    edges.append({ 'u':src_s, 'v':dst_s })
                    motes.append(dst_s)
            motes = list(set(motes))
            for mote in motes:
                d = { 'id': mote, 'value': { 'label': mote } } 
                states.append(d)
        
        return (states,edges)
        
    def updateParents(self,sender,signal,data):
        ''' inserts parent information into the parents dictionary '''
        with self.dataLock:
            #data[0] == source address, data[1] == list of parents
            #self.parents.update({data[0]:data[1]})
            try:
                value = self.parents[data[0]]
                #print ('Address exists, updating parents')
                if not self.parents[data[0]]['parents']:
                    self.parents[data[0]] = {'parents':data[1]}
                else:
                    for i in range(len(data[1])):
                        #print 'Current parent to add:', data[1][i]
                        controla=0
                        for j in range(len(self.parents[data[0]]['parents'])):
                            if (self.parents[data[0]]['parents'][j]['address'] == data[1][i]['address']):
                                #print ('Updating parent')
                                self.parents[data[0]]['parents'][j]['timestamp']=data[1][i]['timestamp']
                                controla=1
                                break
                        if (controla==0):
                            #print ('This parent isn't inside, adding parent')
                            self.parents[data[0]]['parents'] += data[1][i]   
            except KeyError:
                # Key is not present
                #print ('This Address doesn't exist, adding all')
                self.parents[data[0]] = {'parents':data[1]}

    def cleanParents(self):		
        ''' cleans the parents if are too old '''
        plifetime = 180 # Lifetime of a Parent in the Parent Table
        for element in self.parents:
            #print (element)
            listpop = []
            i=0
            for i in range(len(self.parents[element]['parents'])):
                actualtime=self.getstamp()
                #print (actualtime - self.parents[element]['parents'][i]['timestamp'])
                if (actualtime - self.parents[element]['parents'][i]['timestamp'])> plifetime:
                    listpop.append(self.parents[element]['parents'][i]['address'])
                    
            for pop in range(len(listpop)):
                for i in range(len(self.parents[element]['parents'])):
                    if (self.parents[element]['parents'][i]['address'] == listpop[pop]):
                        print ("Removing Parent {0} For innactivity".format(u.formatAddr(listpop[pop]))))
                        self.parents[element]['parents'].pop(pop)
                        break
                
    #======================== private =========================================
    

    
    #======================== helpers =========================================
