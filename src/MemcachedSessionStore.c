/*
Copyright (c) 2012 Emil Stenqvist

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/
#include "__init__.h"
#include "utils.h"
#include "file.h"
#include "MemcachedSessionStore.h"

/*
 * DEVELOPER NOTES
 *
 * Memcached command reference:
 * http://code.google.com/p/memcached/wiki/NewCommands
 *
 */

#include <libmemcached/memcached.h>
#include <pythread.h>

#pragma mark Initialization & deallocation

int smisk_MemcachedSessionStore_init(smisk_MemcachedSessionStore *self, PyObject *args, PyObject *kwargs) {  
  log_trace("ENTER");
  return 0;
}


void smisk_MemcachedSessionStore_dealloc(smisk_MemcachedSessionStore *self) {
  log_trace("ENTER");
  ((smisk_SessionStore *)self)->ob_type->tp_base->tp_dealloc((PyObject *)self);

  log_debug("EXIT smisk_MemcachedSessionStore_dealloc");
}

#pragma mark -
#pragma mark Methods


PyDoc_STRVAR(smisk_MemcachedSessionStore_read_DOC,
  ":param  session_id: Session ID\n"
  ":type   session_id: string\n"
  ":raises smisk.core.InvalidSessionError: if there is no actual session associated with ``session_id``.\n"
  ":rtype: object");
PyObject *smisk_MemcachedSessionStore_read(smisk_MemcachedSessionStore *self, PyObject *session_id) {
  log_trace("ENTER");

  PyObject *data = NULL, *key;

  if ( !SMISK_STRING_CHECK(session_id) ) {
    PyErr_SetString(PyExc_TypeError, "session_id must be a string");
    return NULL;
  }

  // Find session
  // key = ...;
  if(NULL /* session was found */) {

    // Read session
    // Check ttl
    // Put session data in "data"

  } else {
    log_debug("No session data.");
    PyErr_SetString(smisk_InvalidSessionError, "no data");
  }

  return data;
}


PyDoc_STRVAR(smisk_MemcachedSessionStore_write_DOC,
  ":param  session_id: Session ID\n"
  ":type   session_id: string\n"
  ":param  data:       Data to be associated with ``session_id``\n"
  ":type   data:       object\n"
  ":rtype: None");
PyObject *smisk_MemcachedSessionStore_write(smisk_MemcachedSessionStore *self, PyObject *args) {
  log_trace("ENTER");

  PyObject *session_id, *data, *key;

  if ( PyTuple_GET_SIZE(args) != 2 )
    return PyErr_Format(PyExc_TypeError, "this method takes exactly 2 arguments");

  if ( (session_id = PyTuple_GET_ITEM(args, 0)) == NULL )
    return NULL;

  if ( (data = PyTuple_GET_ITEM(args, 1)) == NULL )
    return NULL;

  if(NULL /* check if locked */) {
    // We want to fail silently here, because another process go to the session before we did.
    // Sorry, nothing we can do about it.
    log_debug("smisk_file_lock failed - probably because another process has locked the session");
  } else {
    // Save session in memcached
    log_debug("Wrote s");
  }

  Py_RETURN_NONE;
}


PyDoc_STRVAR(smisk_MemcachedSessionStore_refresh_DOC,
  ":param  session_id: Session ID\n"
  ":type   session_id: string\n"
  ":rtype: None");
PyObject *smisk_MemcachedSessionStore_refresh(smisk_MemcachedSessionStore *self, PyObject *session_id) {
  log_trace("ENTER");

  PyObject *key;
  
  /* if ( (key = smisk_FileSessionStore_path(self, session_id)) == NULL )*/
    /* return NULL;*/

  PyErr_SetString(PyExc_NotImplementedError, "refresh");
  return NULL;
}


PyDoc_STRVAR(smisk_MemcachedSessionStore_destroy_DOC,
  ":param  session_id: Session ID\n"
  ":type   session_id: string\n"
  ":rtype: None");
PyObject *smisk_MemcachedSessionStore_destroy(smisk_MemcachedSessionStore *self, PyObject *session_id) {
  log_trace("ENTER");
  PyErr_SetString(PyExc_NotImplementedError, "destroy");
  return NULL;
}


#pragma mark -
#pragma mark Type construction

PyDoc_STRVAR(smisk_MemcachedSessionStore_DOC,
  "Basic session store type");

// Methods
static PyMethodDef smisk_MemcachedSessionStore_methods[] = {
  {"read", (PyCFunction)smisk_MemcachedSessionStore_read, METH_O, smisk_MemcachedSessionStore_read_DOC},
  {"write", (PyCFunction)smisk_MemcachedSessionStore_write, METH_VARARGS, smisk_MemcachedSessionStore_write_DOC},
  {"refresh", (PyCFunction)smisk_MemcachedSessionStore_refresh, METH_O, smisk_MemcachedSessionStore_refresh_DOC},
  {"destroy", (PyCFunction)smisk_MemcachedSessionStore_destroy, METH_O, smisk_MemcachedSessionStore_destroy_DOC},
  {NULL, NULL, 0, NULL}
};

// Class members
static struct PyMemberDef smisk_MemcachedSessionStore_members[] = {
  {NULL, 0, 0, 0, NULL}
};

// Type definition
PyTypeObject smisk_MemcachedSessionStoreType = {
  PyObject_HEAD_INIT(&PyType_Type)
  0,                         /*ob_size*/
  "smisk.core.SessionStore",  /*tp_name*/
  sizeof(smisk_MemcachedSessionStore), /*tp_basicsize*/
  0,                         /*tp_itemsize*/
  (destructor)smisk_MemcachedSessionStore_dealloc,        /* tp_dealloc */
  0,                         /*tp_print*/
  0,                         /*tp_getattr*/
  0,                         /*tp_setattr*/
  0,                         /*tp_compare*/
  0,                         /*tp_repr*/
  0,                         /*tp_as_number*/
  0,                         /*tp_as_sequence*/
  0,                         /*tp_as_mapping*/
  0,                         /*tp_hash */
  0,                         /*tp_call*/
  0,                         /*tp_str*/
  0,                         /*tp_getattro*/
  0,                         /*tp_setattro*/
  0,                         /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE, /*tp_flags*/
  smisk_MemcachedSessionStore_DOC,          /*tp_doc*/
  (traverseproc)0,           /* tp_traverse */
  0,                         /* tp_clear */
  0,                         /* tp_richcompare */
  0,                         /* tp_weaklistoffset */
  0,                         /* tp_iter */
  0,                         /* tp_iternext */
  smisk_MemcachedSessionStore_methods, /* tp_methods */
  smisk_MemcachedSessionStore_members, /* tp_members */
  0,                              /* tp_getset */
  0,                           /* tp_base */
  0,                           /* tp_dict */
  0,                           /* tp_descr_get */
  0,                           /* tp_descr_set */
  0,                           /* tp_dictoffset */
  (initproc)smisk_MemcachedSessionStore_init, /* tp_init */
  0,                           /* tp_alloc */
  0,                           /* tp_new */
  0                            /* tp_free */
};

int smisk_MemcachedSessionStore_register_types(PyObject *module) {
  log_trace("ENTER");
  smisk_MemcachedSessionStoreType.tp_base = &smisk_SessionStoreType;
  if (PyType_Ready(&smisk_MemcachedSessionStoreType) == 0)
    return PyModule_AddObject(module, "SessionStore", (PyObject *)&smisk_MemcachedSessionStoreType);
  return -1;
}
