/*
Copyright (c) 2007-2008 Rasmus Andersson and contributors

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
#include "uid.h"
#include "Application.h"
#include "Request.h"
#include "Response.h"
#include "Stream.h"
#include "URL.h"
#include "SessionStore.h"
#include "FileSessionStore.h"
#include "xml/__init__.h"
#include "crash_dump.h"

#include <fastcgi.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/un.h>
#include <arpa/inet.h>
#include <signal.h>
#include <unistd.h>

#include <fcgiapp.h>
#include <fastcgi.h>

// Set default listensock
int smisk_listensock_fileno = FCGI_LISTENSOCK_FILENO;

// Objects at module-level
PyObject *smisk_Error, *smisk_IOError, *smisk_InvalidSessionError;
PyObject *os_module;

// Other static strings (only used in C API)
PyObject *kString_http;
PyObject *kString_https;

// Smisk main thread python global interp. lock thread state.
PyThreadState *smisk_py_thstate;

PyDoc_STRVAR(smisk_bind_DOC,
  "Bind to a specific unix socket or host (and/or port).\n"
  "\n"
  ":param path: The Unix domain socket (named pipe for WinNT), hostname, "
    "hostname and port or just a colon followed by a port number. e.g. "
    "\"/tmp/fastcgi/mysocket\", \"some.host:5000\", \":5000\", \"\\*:5000\".\n"
  ":type  path: string\n"
  ":param backlog: The listen queue depth used in the ''listen()'' call. "
    "Set to negative or zero to let the system decide (recommended).\n"
  ":type  backlog: int\n"
  ":raises smisk.IOError: On failure.\n"
  ":rtype: None");
PyObject *smisk_bind(PyObject *self, PyObject *args) {
  log_trace("ENTER");
  //int FCGX_OpenSocket(const char *path, int backlog)
  int fd, backlog;
  PyObject *path;
  
  // Set default backlog size (<=0 = let system implementation decide)
  backlog = 0;
  
  // Did we get enough arguments?
  if (!args || PyTuple_GET_SIZE(args) < 1) {
    PyErr_SetString(PyExc_TypeError, "bind takes at least 1 argument");
    return NULL;
  }
  
  // Save reference to first argument and type check it
  path = PyTuple_GET_ITEM(args, 0);
  if (path == NULL || !PyString_Check(path)) {
    PyErr_SetString(PyExc_TypeError, "first argument must be a string");
    return NULL;
  }
  
  // Did we get excplicit backlog size?
  if (PyTuple_GET_SIZE(args) > 1) {
    PyObject *arg1 = PyTuple_GET_ITEM(args, 1);
    if (arg1 != NULL) {
      if (!PyInt_Check(arg1)) {
        PyErr_SetString(PyExc_TypeError, "second argument must be an integer");
        return NULL;
      }
      backlog = (int)PyInt_AS_LONG(arg1);
    }
  }
  
  // Bind/listen
  fd = FCGX_OpenSocket(PyString_AS_STRING(path), backlog);
  if (fd < 0) {
    log_debug("ERROR: FCGX_OpenSocket(\"%s\", %d) returned %d. errno: %d", 
      PyString_AS_STRING(path), backlog, fd, errno);
    return PyErr_SET_FROM_ERRNO;
  }
  
  // Set the process global fileno
  smisk_listensock_fileno = fd;
  
  Py_RETURN_NONE;
}


PyDoc_STRVAR(smisk_listening_DOC,
  "Find out if this process is a \"remote\" process, bound to a socket "
  "by means of calling bind(). If it is listening, this function returns "
  "the address and port or the UNIX socket path. If not bound, this "
  "function returns None.\n"
  "\n"
  ":raises smisk.IOError: On failure.\n"
  ":rtype: string");
PyObject *smisk_listening(PyObject *self, PyObject *args) {
  log_trace("ENTER");
  PyObject *s = Py_None;
  socklen_t addrlen;
  struct sockaddr *addr;
  
  if (smisk_listensock_fileno == FCGI_LISTENSOCK_FILENO)
    Py_RETURN_NONE;
  
  addrlen = sizeof(struct sockaddr_in); // Assume INET
  addr = (struct sockaddr *)malloc(addrlen);
  if (getsockname(smisk_listensock_fileno, addr, &addrlen) != 0)
    return PyErr_SET_FROM_ERRNO;
  
  if (addr->sa_family == AF_INET || addr->sa_family == AF_INET6) {
    char *saddr = "*";
    if (((struct sockaddr_in *)addr)->sin_addr.s_addr != (in_addr_t)0) {
      saddr = (char *)inet_ntoa(((struct sockaddr_in *)addr)->sin_addr);
    }
    s = PyString_FromFormat("%s:%d",
      saddr, 
      htons(((struct sockaddr_in *)addr)->sin_port) );
  }
  else if (addr->sa_family == AF_UNIX) {
    // This may be a bit risky...
    s = PyString_FromString(((struct sockaddr_un *)addr)->sun_path);
  }
  
  if (s == Py_None)
    Py_INCREF(s);
  
  return s;
}


PyDoc_STRVAR(smisk_uid_DOC,
  "Generate a universal Unique Identifier.\n"
  "\n"
  "Note: This is not a UUID (ISO/IEC 11578:1996) implementation. However it "
    "uses an algorithm very similar to UUID v5 (RFC 4122).\n"
  "\n"
  "The UID is calculated like this:\n"
  "\n"
  ".. python::\n"
   "\n"
   "  sha1 ( time.secs, time.usecs, pid, random[, node] )\n"
  "\n"
  ":param node: Optional data to be used when creating the uid.\n"
  ":type  node: string\n"
  ":param nbits: Number of bits to pack into each byte when creating "
    "the string representation. A value in the range 4-6. Defaults to 5.\n"
  ":type  nbits: int\n"
  ":rtype: string");
PyObject *smisk_uid(PyObject *self, PyObject *args) {
  log_trace("ENTER");
  PyObject *node = NULL;
  int nbits = 5;
  smisk_uid_t uid;
  
  // node
  if (PyTuple_GET_SIZE(args) > 0) {
    node = PyTuple_GET_ITEM(args, 0);
    if (node == NULL || !PyString_Check(node)) {
      PyErr_SetString(PyExc_TypeError, "first argument must be a string");
      return NULL;
    }
  }
  
  // nbits
  if (PyTuple_GET_SIZE(args) > 1) {
    PyObject *arg = PyTuple_GET_ITEM(args, 1);
    if (arg != NULL) {
      if (!PyInt_Check(arg)) {
        PyErr_SetString(PyExc_TypeError, "second argument must be an integer");
        return NULL;
      }
      nbits = (int)PyInt_AS_LONG(arg);
    }
  }
  
  if ((node ? smisk_uid_create(&uid, PyString_AS_STRING(node), PyString_GET_SIZE(node))
            : smisk_uid_create(&uid, NULL, 0)) == -1) {
    PyErr_SetString(PyExc_SystemError, "smisk_uid_create() failed");
    return NULL;
  }
  
  return smisk_uid_format(&uid, nbits);
}


/* ------------------------------------------------------------------------- */

static PyMethodDef module_methods[] = {
  {"bind",      (PyCFunction)smisk_bind,       METH_VARARGS, smisk_bind_DOC},
  {"listening", (PyCFunction)smisk_listening,  METH_NOARGS,  smisk_listening_DOC},
  {"uid",       (PyCFunction)smisk_uid,        METH_VARARGS, smisk_uid_DOC},
  {NULL, NULL, 0, NULL}
};

PyDoc_STRVAR(smisk_module_DOC,
  "Smisk core library");

PyMODINIT_FUNC initcore(void) {
  log_trace("ENTER");
  
  // Without
  PyEval_InitThreads();
  
  // Initialize libfcgi
  if(FCGX_Init() != 0) {
		PyErr_SetString(PyExc_ImportError, "smisk.core: FCGX_Init() failed");
		return;
	}
  
  // Create module
  PyObject *module;
  module = Py_InitModule("smisk.core", module_methods);
  
  // Initialize crash dumper
  smisk_crash_dump_init();
  
  // Load os module
  PyObject *os_str = PyString_FromString("os");
  os_module = PyImport_Import(os_str);
  Py_DECREF(os_str);
  if (os_module == NULL)
    return;
  
  // Constants: Other static strings (only used in C API)
  kString_http = PyString_FromString("http");
  kString_https = PyString_FromString("https");
  
  // Constants: Special variables
  if (PyModule_AddStringConstant(module, "__build__", SMISK_BUILD_ID) != 0)
    return;
  if (PyModule_AddStringConstant(module, "__doc__", smisk_module_DOC) != 0)
    return;
  
  // Register types
  if (!module ||
    (smisk_Application_register_types(module) != 0) ||
    (smisk_Request_register_types(module) != 0) ||
    (smisk_Response_register_types(module) != 0) ||
    (smisk_Stream_register_types(module) != 0) ||
    (smisk_URL_register_types(module) != 0) ||
    (smisk_SessionStore_register_types(module) != 0) ||
    (smisk_FileSessionStore_register_types(module) != 0) ||
    (smisk_xml_register(module) == NULL)
    ) {
      return;
  }
  
  // Exceptions
  if (!(smisk_Error = PyErr_NewException("smisk.core.Error", PyExc_StandardError, NULL))) return;
  PyModule_AddObject(module, "Error", smisk_Error);
  if (!(smisk_IOError = PyErr_NewException("smisk.core.IOError", PyExc_IOError, NULL))) return;
  PyModule_AddObject(module, "IOError", smisk_IOError);
  if (!(smisk_InvalidSessionError = PyErr_NewException("smisk.core.InvalidSessionError", PyExc_ValueError, NULL))) return;
  PyModule_AddObject(module, "InvalidSessionError", smisk_InvalidSessionError);
}

