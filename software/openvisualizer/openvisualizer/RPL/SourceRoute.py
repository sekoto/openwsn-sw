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
log = logging.getLogger('SourceRoute')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import threading

import openvisualizer.openvisualizer_utils as u
from openvisualizer.eventBus import eventBusClient

class SourceRoute(eventBusClient.eventBusClient):
       
    def __init__(self):
        
        # local variables
        self.dataLock        = threading.Lock()
        self.parents         = {}
        
        # initialize parent class
        eventBusClient.eventBusClient.__init__(
            self,
            name             = 'SourceRoute',
            registrations =  []
        )
    
    #======================== public ==========================================
    
    def getSourceRoute(self,destAddr):
        '''
        Retrieve the source route to a given mote.
        
        :param destAddr: [in] The EUI64 address of the final destination.
        
        :returns: The source route, a list of EUI64 address, ordered from
            destination to source.
        '''
        
        sourceRoute = []
        with self.dataLock:
            try:
                parents=self._dispatchAndGetResult(signal='getParents',data=None)
                self._getSourceRoute_internal(destAddr,sourceRoute,parents)
            except Exception as err:
                log.error(err)
                raise
        
        return sourceRoute
    
    #======================== private =========================================
    
    def _getSourceRoute_internal(self,destAddr,sourceRoute,parents):

        print 'getSourceRoute_internal--Datination Address  . {0}'.format(u.formatAddr(destAddr))
        
        if not destAddr:
            print '[Python] not destAddr -- No more Parents'
            # no more parents
            return
        
        if not parents.get(tuple(destAddr)):
            print '[Python] not parents.get -- No Parents'
            # this node does not have a list of parents
            return
        
        # first time add destination address
        if destAddr not in sourceRoute:
            print '[Python] destAddr not in sourceRoute -- Adding Destination Address'
            sourceRoute     += [destAddr]
        
        # pick a parent
        #parent               = parents.get(tuple(destAddr))[0]
        parent = parents[tuple(destAddr)]['parents'][0]['address']
        
        # avoid loops
        if parent not in sourceRoute:
            print '[Python] parent not in sourceRoute -- Adding Parent'
            print '   . {0}'.format(u.formatAddr(parent))
            
            sourceRoute     += [parent]
            
            #add non empty parents recursively
            nextparent       = self._getSourceRoute_internal(parent,sourceRoute,parents)
            
            if nextparent:
                print '[Python] nextparent'
                sourceRoute += [nextparent]
    
    #======================== helpers =========================================
    