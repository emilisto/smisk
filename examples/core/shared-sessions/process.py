#!/usr/local/bin/python2.5
# encoding: utf-8
from smisk.core import Application
import sys, os, socket
from datetime import datetime
from time import sleep

class MyApp(Application):
  def __init__(self, *args, **kwargs):

    self.sessions.ttl = 10

  def service(self):

    #if self.request.session is False:
    if self.request.session == None:
      self.request.session = os.getpid()

    self.response.headers = ["Content-Type: text/plain"]
    self.response(
      "This comes from a separately running process.\n\n",
      "Host:          %s\n" % socket.getfqdn(),
      "Process id:    %d\n" % os.getpid(),
      "Process owner: %s\n" % os.getenv('USER'),
      "self.request.url: %r\n" % self.request.url,
      "self.request.env: %r\n" % self.request.env,
      "self.request.session: %r\n" % self.request.session,
      "self.request.session_id: %r\n" % self.request.session_id
    )


    try:
      self.response("active: %r\n" % self.request.is_active)
      #self.response("session: %r\n" % self.request.session)
    except:
      print "Unexpected error:", sys.exc_info()[0]
      pass

    sleep(0.5)

try:
  MyApp().run()
except KeyboardInterrupt:
  pass
