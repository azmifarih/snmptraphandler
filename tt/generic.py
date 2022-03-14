#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import sys,os
import urllib

class GenericType(object):
    (OK, WARN, CRIT, UNKNOWN) = range(4)

    def __init__(self, oid, host, *args):
        self._attr_ = {
            'status' : GenericType.UNKNOWN,
            'host' : host,
            'oid' : oid,
            'summary' : None,
            'description' : None,
            'nagios_service' : 'UNKNOWN',
            'default_handlers' : [],
        }

    def __getattr__(self, item):
        return self._attr_[item]

    def _set_summary(self):
        if self.summary is None:
            self.summary = self.description[:40]

    def nagios_handler(self):
        cmd = "/usr/local/nagios/libexec/eventhandlers/submit_check_result %s %s %s %s" 
	cmd = cmd % (self.host, self.nagios_service, self.status, self.description)
        os.system(cmd)
    
    def run(self, *args):
        if len(args[0]) == 0:
            handlers = self.default_handlers
        else:
            handlers = args[0]
        for handler in handlers:
            meth = "%s_handler" % handler
            if hasattr(self.__class__, meth) and callable(getattr(self.__class__, meth)):
                getattr(self.__class__, meth)(self)
