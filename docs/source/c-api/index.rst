.. _c-api:

Smisk C library
===========================================================

This is the C API for :mod:`smisk.core`.

Types
-------------------------------------------------

.. ctype:: byte
  
  8 bits of data.


Members
-------------------------------------------------

.. cvar:: PyObject* smisk_core_module
  
  The module itself.

  .. versionadded:: 1.1

.. cvar:: PyObject* Error
  
  General error

.. cvar:: PyObject* IOError
  
  Input/output error

.. cvar:: PyObject* InvalidSessionError
  
  Session-related error

.. cvar:: PyObject* kString_http
  
  The string ``"http"``

.. cvar:: PyObject* kString_https
  
  The string ``"https"``

.. cvar:: int smisk_listensock_fileno
  
  FastCGI connection *fileno*.


Functions
-------------------------------------------------

.. cfunction:: PyObject* smisk_bind(PyObject *self, PyObject *args)


.. cfunction:: PyObject* smisk_unbind(PyObject *self)

  .. versionadded:: 1.1


.. cfunction:: PyObject* smisk_listening(PyObject *self, PyObject *args)


.. cfunction:: PyObject* smisk_uid(PyObject *self, PyObject *args)

  .. versionadded:: 1.1


.. cfunction:: PyObject* smisk_pack(PyObject *self, PyObject *args)

  .. versionadded:: 1.1


.. cfunction:: PyObject* SMISK_PyObject_GET(PyObject *object, char *attrname)
  
  Macro for getting an arbitrary attribute from `object`.
  
  This is the only way to set/get Type/Class properties.
  Based on the python interal function ``PyObject **_PyObject_GetDictPtr(PyObject *)``
  
  :Returns: A `PyString` or NULL if an exception was raised.
  
  .. versionadded:: 1.1


.. cfunction:: int SMISK_PyObject_SET(PyObject *object, char *attrname, PyObject *value)
  
  Macro for setting an arbitrary attribute of `object`.
  
  This is the only way to set/get Type/Class properties.
  Based on the python interal function ``PyObject **_PyObject_GetDictPtr(PyObject *)``
  
  :Returns: -1 is an error occured or 0 on success.
  
  .. versionadded:: 1.1


.. cfunction:: void REPLACE_OBJ(destination, new_value, type)
  
  Macro for replacing a value somewhere, releasing a reference to any previous value and 
  retaining one reference to the new value.


.. cfunction:: void ENSURE_BY_GETTER(void *direct, cfunction *getter[, error_code...])

  Macro used to ensure a lazy instance variable is available.
  ``error_code`` is executed if ``getter`` returns ``NULL``.


.. cfunction:: int SMISK_PyString_Check(PyObject *object)

  Macro for testing if `object` is a kind of string (either `str` or `unicode`).
  Workaround for a nasty bug in ``PyString_Check()``.
  
  :Returns: 1 if `object` is a kind of string, otherwise 0.


Logging
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cfunction:: int log_error(char *fmt, ...)
  
  Log an error to *stderr*.
  
  The message actually being written has the following format::
    
    <MOD_IDENT> [<PID>] ERROR <FILE>:<LINE>: <fmt % ...><LF>
  
  :Returns: Number of characters printed (not including the trailing ``\0`` used to end
            output to strings) or a negative value if an output error occured.


.. cfunction:: int log_debug(char *fmt, ...)
  
  Log something to *stderr*.
  
  Enabled if :cmacro:`SMISK_DEBUG` evaluates to true, otherwise all instances of
  `log_debug` are removed a compile time.
  
  The message actually being written has the following format::
    
    <MOD_IDENT> [<PID>] DEBUG <FILE>:<LINE>: <fmt % ...><LF>
  
  :Returns: Number of characters printed (not including the trailing ``\0`` used to end
            output to strings) or a negative value if an output error occured.


.. cfunction:: int log_trace(char *fmt, ...)
  
  Log a trace message to *stderr*.
  
  Enabled if :cmacro:`SMISK_TRACE` evaluates to true, otherwise all instances of
  `log_trace` are removed a compile time.
  
  The message actually being written has the following format::
    
    <MOD_IDENT> [<PID>] TRACE <FILE>:<LINE> in <FUNCTION> <fmt % ...><LF>
  
  :Returns: Number of characters printed (not including the trailing ``\0`` used to end
            output to strings) or a negative value if an output error occured.


.. cfunction:: void assert_refcount(PyObject *object, count_test...)
  
  Macro to assert refcount on `object` matches `count_test`.
  
  Evaluated only if :cmacro:`SMISK_DEBUG` is true.
  
  Asserting *my_dict* has 3 or less references:
  
  .. code-block:: c
    
    assert_refcount(my_dict, <= 3)



Macros
-------------------------------------------------

.. cmacro:: XDIGIT_TO_NUM
  
  Convert an ASCII hex digit to the corresponding number in the range [0-16).


.. cmacro:: X2DIGITS_TO_NUM
  
  Convert two ASCII hex digits, representing one value, to the corresponding 
  number between 0-255.


.. cmacro:: XNUM_TO_DIGIT
  
  Convert a number in the [0, 16) range to the ASCII representation of the 
  corresponding hexadecimal digit in the set ``0-9A-F``.


.. cmacro:: XNUM_TO_digit
  
  Convert a number in the [0, 16) range to the ASCII representation of the 
  corresponding hexadecimal digit in the set ``0-9a-f``.


.. cmacro:: MOD_IDENT
  
  Module identifier used in logging. Might be redefined by submodules.


.. cmacro:: QUOTE
  
  Wrap the *value* of another macro in double quotes.
  
  Example:
  
  .. code-block:: c
    
    MY_VERSION_MAJOR 2
    puts("Program version " QUOTE(MY_VERSION_MAJOR))
    // Is equivalent to:
    puts("Program version 2")
  

.. cmacro:: PyErr_SET_FROM_ERRNO
  
  Expands to::
  
    PyErr_SetFromErrnoWithFilename(PyExc_IOError, __FILE__)


Debugging
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cmacro:: SMISK_DEBUG
  
  If defined and evaluates to true, enables Smisk debugging features, like 
  :func:`log_debug` and setting :cmacro:`SMISK_TRACE` to true (thus in turn 
  activating :func:`log_trace()`).
  
  Automatically enabled when passing ``--debug-smisk`` to *setup.py build*.


.. cmacro:: SMISK_TRACE
  
  Activates :func:`log_trace()` if defined and evaluates to true.
  Automatically defined as ``SMISK_TRACE 1`` if :cmacro:`SMISK_DEBUG` is enabled.


.. cmacro:: IFDEBUG(x)
  
  `x` is evaluated if :cmacro:`SMISK_DEBUG` is enabled.


.. cmacro:: DUMP_REFCOUNT(PyObject *object)
  
  Evaluates only if :cmacro:`SMISK_DEBUG` is true and expands to:
  
  .. code-block:: c
  
    log_debug(" *** %s: %ld", #o, (o) ? (Py_ssize_t)(o)->ob_refcnt : 0)


.. cmacro:: DUMP_REPR(PyObject *object)
  
  Like ``repr()`` in interpreted Python or ``PyObject_Repr`` in CPython, but takes
  care of *NULL* values and refcounting.
  
  Evaluates only if :cmacro:`SMISK_DEBUG` is true and expands to something like this:
  
  .. code-block:: c
  
    log_debug("repr(%s) = %s", #o, PyObject_Repr(object));
  

.. cmacro:: IFTRACE(x)
  
  `x` is evaluated if :cmacro:`SMISK_TRACE` is enabled.
  

Threading
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cmacro:: EXTERN_OP_START
  
  TODO


.. cmacro:: EXTERN_OP_END
  
  TODO


.. cmacro:: EXTERN_OP(section)
  
  TODO


.. cmacro:: EXTERN_OP2(section)
  
  TODO


.. cmacro:: EXTERN_OP3(state_var, section)
  
  TODO


String manipulation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cmacro:: STR_LTRIM_S
  
  TODO

.. cmacro:: STR_LTRIM_ST
  
  TODO

.. cmacro:: STR_LTRIM_STRN
  
  TODO


String comparison
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Inspired by Igor Sysoev.

These macros evaluate to true if *string* equals, or starts with, *abc...*.

Example:

.. code-block:: c
  
  char *string = "Help";
  if (smisk_str4cmp(string, 'H', 'e', 'l', 'p'))
    fprint("Yes, string == \"Help\"");
  // Output: Yes, string == "Help"


.. cmacro:: smisk_str3cmp(string, a,b,c)
.. cmacro:: smisk_str4cmp(string, a,b,c,d)
.. cmacro:: smisk_str5cmp(string, a,b,c,d,e)
.. cmacro:: smisk_str6cmp(string, a,b,c,d,e,f)
.. cmacro:: smisk_str7cmp(string, a,b,c,d,e,f,g)
.. cmacro:: smisk_str8cmp(string, a,b,c,d,e,f,g,h)
.. cmacro:: smisk_str9cmp(string, a,b,c,d,e,f,g,h,i)


Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Macros defined in *config.h*.


.. cmacro:: SMISK_STREAM_READ_CHUNKSIZE
  
  Chunk size for reading unknown length from a stream.


.. cmacro:: SMISK_STREAM_READLINE_LENGTH
  
  Default readline length for :meth:`smisk.Stream.readline()`.
  

.. cmacro:: SMISK_POST_SIZE_MEMORY_LIMIT
  
  How much post data can be stored in memory, instead of being written to disk.


.. cmacro:: SMISK_FILE_UPLOAD_DIR
  
  Where uploaded files are saved before taken care of. If ``TMPDIR`` is not 
  available in process ``env``, the value of this macro is used to construct 
  a temporary filename.


.. cmacro:: SMISK_FILE_UPLOAD_PREFIX
  
  Prefix for temporary uploaded files.


.. cmacro:: SMISK_SESSION_NBITS
  
  Session ID compactness.
  
  .. versionadded:: 1.1
