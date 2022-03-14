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
logging = open('/var/log/stp_hlr.log','a')
		
class stp_hlr(GenericType):

    @classmethod
    def insert_db(self,trap_type,ip_value,str_text,alarm_level,oid,source):
	try:
	#Inserting new Trap
	    trap_time = datetime.datetime.now()
            t_trap = trap_time.strftime("%b %d %Y %H:%M:%S")
	    insert_string = "INSERT INTO stp_hlr VALUES(DEFAULT,\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',%s) " % (trap_time.strftime("%Y-%m-%d %H:%M:%S"),oid,ip_value,re.escape(source),trap_type,str_text,alarm_level)
	    logging.write(insert_string)
	    c.execute(insert_string)
	    logging.write("Insert of OID %s and trap id: %s" % (oid, trap_type))
	except MySQLdb.Error, e: 
	    logging.write("Exception: %s" % e)

    @classmethod
    def check_type(self,source,description):
        logging.write("\n Source: %s \n" % source)
	logging.write("Description : %s \n" % description)
  	if 'ss7_itu_stp_link' in source:
	    link = description.split(' ')[2]
	    if 'Link' in link:
		service = source.split(' ')[1]
	    else:
		service = 'UNKNOWN'
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
	source = args[8]
        alarm_level = args[5]
	trap_type = args[6]
	oid = args[4]
	ip_value= args[2]
	if 'xx.xx.xx.xx' in ip_value:
	    self.host='xxx'
	elif 'xx.xx.xx.xx' in ip_value:
	    self.host='xxx'
	elif 'xx.xx.xx.xx' in ip_value:
            self.host='xxx'
	self.nagios_service = trap_type
	self.description = ' '.join(args[8:len(args)])
	if alarm_level == '1' : 
	    self.status = GenericType.OK
	elif alarm_level == '2':
	    self.status = GenericType.WARN
	elif alarm_level == '3' : 
	    self.status = GenericType.WARN
	elif alarm_level == '4' : 
	    self.status = GenericType.CRIT
	elif alarm_level == '5':
	    self.status = GenericType.CRIT
	elif alarm_level == '6':
  	    self.status = GenericType.UNKNOWN
	elif alarm_level == '7':
	    self.status = GenericType.UNKNOWN
	self.insert_db(trap_type,ip_value,self.description,alarm_level,oid,source)
	(self.nagios_service,self.description) = self.check_type(source,self.description)
	logging.write("\n IP :" + self.host +"\n")
	self.description = "\" " + self.description + "\""
	logging.write("\n Nagios Service : " + self.nagios_service)
	logging.write("\n Service Description : " + self.description)
	#Close File
	logging.close()
