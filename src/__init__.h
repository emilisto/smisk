/*
Copyright (c) 2007-2009 Rasmus Andersson

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
#ifndef SMISK_MODULE_H
#define SMISK_MODULE_H

// fcgi socket fd
extern int smisk_listensock_fileno;
extern PyObject *os_module; // private
extern PyThreadState *smisk_py_thstate; // private

// The smisk.core module
extern PyObject *smisk_core_module;

// static objects at module-level
extern PyObject *smisk_InvalidSessionError; // extends PyExc_ValueError

// String constants
extern PyObject *kString_http;
extern PyObject *kString_https;
extern PyObject *kString_utf_8;

// Functions
PyObject *smisk_bind (PyObject *self, PyObject *args);
PyObject *smisk_unbind (PyObject *self);
PyObject *smisk_listening (PyObject *self, PyObject *args);
PyObject *smisk_uid (PyObject *self, PyObject *args);
PyObject *smisk_pack (PyObject *self, PyObject *args);


#endif
