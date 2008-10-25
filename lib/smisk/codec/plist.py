# encoding: utf-8
'''Apple/NeXT Property Lists.
'''
import base64
from smisk.codec.xmlbase import *
from smisk.util import DateTime
from datetime import datetime
from types import *

__all__ = [
  'PlistEncodingError',
  'PlistDecodingError',
  'XMLPlistCodec']

class PlistEncodingError(Exception):
  pass

class PlistDecodingError(Exception):
  pass

class XMLPlistCodec(XMLBaseCodec):
  '''XML Property List codec
  '''
  name = 'XML Property List'
  extensions = ('plist',)
  media_types = ('application/plist+xml',)
  charset = 'utf-8'
  
  xml_root_name = 'plist'
  xml_root_attrs = {'version': '1.0'}
  xml_doctype = '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '\
    '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
  
  # Reading
  
  @classmethod
  def parse_object(cls, elem):
    try:
      return cls._HANDLERS[elem.tag](elem)
    except KeyError:
      raise PlistDecodingError('%s not supported' % elem.tag)
  
  @classmethod
  def parse_plist_array(cls, elem):
    return [cls.parse_object(child) for child in elem.getchildren()]
  
  @classmethod
  def parse_plist_data(cls, elem):
    return  base64.b64decode(elem.text)
  
  @classmethod
  def parse_plist_date(cls, elem):
    return DateTime(DateTime.strptime(elem.text, '%Y-%m-%dT%H:%M:%SZ'))
  
  @classmethod
  def parse_plist_dict(cls, elem):
    children = elem.getchildren()
    
    if len(children) % 2 != 0:
      raise PlistDecodingError('dict must have even childrens')
    
    dic = dict()
    for i in xrange(len(children) / 2):
      key = children[i * 2]
      value = children[i * 2 + 1]
  
      if key.tag != 'key':
        raise PlistDecodingError('key element not found')
      dic[key.text] = cls.parse_object(value)
    
    return dic
  
  @classmethod
  def parse_plist_real(cls, elem):
    return float(elem.text)
  
  @classmethod
  def parse_plist_integer(cls, elem):
    return int(elem.text)
  
  @classmethod
  def parse_plist_string(cls, elem):
    return elem.text
  
  @classmethod
  def parse_plist_true(cls, elem):
    return True
  
  @classmethod
  def parse_plist_false(cls, elem):
    return False
  
  # Writing
  
  @classmethod
  def build_object(cls, obj):
    if obj is True:
      return Element('true')
    elif obj is False:
      return Element('false')
    elif isinstance(obj, list):
      return cls.build_array(obj)
    elif isinstance(obj, data): # must be tested before basestr
      return cls.xml_mktext('data', base64.b64encode(obj))
    elif isinstance(obj, datetime):
      return cls.xml_mktext('date', obj.strftime('%Y-%m-%dT%H:%M:%SZ'))
    elif isinstance(obj, dict):
      return cls.build_dict(obj)
    elif isinstance(obj, float):
      return cls.xml_mktext('real', obj.__str__())
    elif isinstance(obj, int):
      return cls.xml_mktext('integer', obj.__str__())
    elif isinstance(obj, basestring):
      return cls.xml_mktext('string', obj)
    else:
      raise PlistEncodingError('Unsupported type: %s' % type(obj).__name__)
  
  @classmethod
  def build_array(cls, obj):
    e = Element('array')
    for o in obj:
      e.append(cls.build_object(o))
    return e
  
  @classmethod
  def build_dict(cls, obj):
    e = Element('dict')
    for key, value in obj.iteritems():
      e.append(cls.xml_mktext('key', key))
      e.append(cls.build_object(value))
    return e
  
  # Setup
  
  @classmethod
  def did_register(cls, registry):
    # setup parse handlers
    cls._HANDLERS = dict((name, getattr(cls, 'parse_plist_' + name))
      for name in 'array data date dict real integer string true false'.split())
  

# Only register if xml.etree is available
if ElementTree is not None:
  codecs.register(XMLPlistCodec)

if __name__ == '__main__':
  charset, xmlstr = XMLPlistCodec.encode({
    'message': 'Hello worlds',
    'internets': [
      'interesting',
      'lolz',
      42.0,
      {
        'tubes': [1,3,16,18,24],
        'persons': True
      }
    ],
    'today': datetime.now()
  }, charset='utf-8')
  print xmlstr
  from StringIO import StringIO
  print repr(XMLPlistCodec.decode(StringIO(xmlstr)))
