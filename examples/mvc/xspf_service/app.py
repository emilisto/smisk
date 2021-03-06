#!/usr/bin/env python
# encoding: utf-8
from smisk.mvc import *

class root(Controller):
  def __call__(self):
    raise http.Found('/example')
  
  def echo(self, **params):
    return params
  
  def example(self):
    return {
      'title': 'Spellistan frum hell',
      'creator': 'rasmus',
      'trackList': [
        {
          'location': 'spotify:track:0yR57jH25o1jXGP4T6vNGR',
          'identifier': 'spotify:track:0yR57jH25o1jXGP4T6vNGR',
          'title': 'Go Crazy (feat. Majida)',
          'creator': 'Armand Van Helden',
          'album': 'Ghettoblaster',
          'trackNum': 1,
          'duration': 410000
        },
        {
          'location': 'spotify:track:0yR57jH25o1jXGP4T6vNGR',
          'identifier': 'spotify:track:0yR57jH25o1jXGP4T6vNGR',
          'title': 'Go Crazy2 (feat. Majida)',
          'creator': 'Armand Van Helden2',
          'album': 'Ghettoblaster2',
          'trackNum': 2,
          'duration': 410002
        },
        {
          'location': 'spotify:track:0yR57jH25o1jXGP4T6vNGR',
          'identifier': 'spotify:track:0yR57jH25o1jXGP4T6vNGR',
          'title': 'Go Crazy3 (feat. Majida)',
          'creator': 'Armand Van Helden3',
          'album': 'Ghettoblaster3',
          'trackNum': 3,
          'duration': 410007
        },
      ]
    }

if __name__ == '__main__':
  config.load('app.conf')
  main()
