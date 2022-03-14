#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import sys,os
import datetime
import MySQLdb
import time
import re
from generic import GenericType

# Global Variables
db = MySQLdb.connect("localhost","","","nagios_traps")
c = db.cursor()
logging = open('/var/log/ggsn.log','a')

#VALUE 0 IS NOT VALID
alarm_types = ['UNKNOWND','CRITICAL','MAJOR','MINOR','WARNING','CLEAR']
CRITICAL=1
MAJOR=2
MINOR=3
WARNING=4
CLEAR=5
alarm_links=[]
		
class ggsn(GenericType):

    @classmethod
    def insert_db(self,trap_type,ip_value,str_text,alarm_level,oid,source):
	try:
	#Inserting new Trap
	    trap_time = datetime.datetime.now()
            t_trap = trap_time.strftime("%b %d %Y %H:%M:%S")
	    insert_string = "INSERT INTO ggsn VALUES(DEFAULT,\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',%s) " % (trap_time.strftime("%Y-%m-%d %H:%M:%S"),oid,ip_value,re.escape(source),trap_type,str_text,alarm_level)
	    logging.write(insert_string)
	    c.execute(insert_string)
	    logging.write("Insert of OID %s and trap id: %s" % (oid, trap_type))
	except MySQLdb.Error, e: 
	    logging.write("Exception: %s" % e)

    @classmethod
    def check_type(self,source,description,category):
        logging.write("\n Source: %s \n" % source)
	logging.write("Description : %s \n" % description)
	if 'networkContext' in source:
	    context = source.split('/')[1].split('[')[1][:-1]
	    interface = source.split('/')[2].split('[')[1][:-1].replace('\\','')
	    service = 'Interface_%s_%s' % (interface,category)
	elif 'diameter' in source:
	    context = source.split('[')[1].split(']')[0]
	    peer = source.split('[')[2][:-1]
	    service = '%s_%s' % (context,peer)
	elif 'cluster' in source:
	    service = description.split(' ')[0]
	    if source.split('/')[1] == 'cluster[100]':
		node = source.split('/')[2][-2]
	    service = service+'_node_'+node
	elif 'radius' in source:
	    context = source.split('[')[1].split(']')[0]
            peer = source.split('[')[2][:-1]
            service = '%s/%s' % (context,peer)
	else:
	    service = 'UNKNOWN'
	description = '%s : %s' % (service,description)
	return (service,description)
	
    def __init__(self, oid, host, *args):
        GenericType.__init__(self, oid, host, *args)
        self.status = GenericType.UNKNOWN
        #print(self.status)
        self.remote_cmd = '/mycommand'
        self.default_handlers = ['nagios']
	for i in range(len(args)):
	   now = datetime.datetime.now()
	   logging.write(now.strftime("%Y/%m/%d %H:%M"))
	   s = " - Args number %d : %s \n" %(i,args[i])
	   logging.write(s)
	#Parameteres
	#print args
	source = args[6]
        if (all(x.isupper() for x in args[8])):
            alarm_level = args[8]
	trap_type = args[7]
	if "Ospfv2" in trap_type:
	    category = "OSPFv2"
	elif "Ospfv3" in trap_type:
	    category = "OSPFv3"
	elif "Bgp" in trap_type:
	    category = "BGP"
	else:
	    category = "UNKNOWN"
	oid = args[4]
	ip_value= args[5]
	if 'xx.xx.xx.xx' in ip_value:
		self.host='xxx'
	self.nagios_service = trap_type
	self.description = ' '.join(args[7:len(args)-1])
	#print alarm_level
	if alarm_level == 'CLEARED' : 
		alarm_level = 5
		self.status = GenericType.OK
	elif alarm_level == 'CRITICAL':
		alarm_level = 4
		self.status = GenericType.CRIT
	elif alarm_level == 'MAJOR' : 
		alarm_level = 3
		self.status = GenericType.CRIT
	elif alarm_level == 'MINOR' : 
		alarm_level = 2
		self.status = GenericType.WARN
	elif alarm_level == 'INFORMATIONAL':
		alarm_level = 1
		self.status = GenericType.OK
	self.insert_db(trap_type,ip_value,' '.join(args[7:len(args)-1]),alarm_level,oid,source)
	(self.nagios_service,self.description) = self.check_type(source,self.description,category)
	logging.write("\n IP :" + self.host +"\n")
	self.description = "\" " + self.description + "\""
	logging.write("\n Nagios Service : " + self.nagios_service)
	logging.write("\n Service Description : " + self.description)
	#Close File
	logging.close()
