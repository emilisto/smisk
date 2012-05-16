#!/usr/local/bin/python2.5
# encoding: utf-8
from smisk.core import Application
from smisk.config import config
import sys, os, socket
from datetime import datetime
from time import sleep
import tempfile
from smisk.util.main import daemonize, main

class MyApp(Application):
  def __init__(self, *args, **kwargs):

    self.sessions.ttl = 10
    self.sessions.memcached_config = "--SERVER=localhost:11211"

  def service(self):

    #if self.request.session is False:
    if self.request.session == None:
      # self.request.session = "coooolers: %d" % os.getpid()
      self.request.session = "apan ola spelar boll"

    val = config.get('smisk.memcached.configstring')
    memcached = self.sessions.memcached_config

    self.response.headers = ["Content-Type: text/plain"]
    self.response(
      "This comes from a separately running process.\n\n",
      "Host:          %s\n" % socket.getfqdn(),
      "Config val:          %s\n" % memcached,
      "Process id:    %d\n" % os.getpid(),
      "Process owner: %s\n" % os.getenv('USER'),
      "self.request.url: %r\n" % self.request.url,
      "self.request.env: %r\n" % self.request.env,
      "self.request.session: %r\n" % self.request.session,
      "self.request.session_id: %r\n" % self.request.session_id
    )

try:

  # config.load('shared-sessions.conf')
  # config('shared-sessions')

  MyApp().run()

except KeyboardInterrupt:
  pass
