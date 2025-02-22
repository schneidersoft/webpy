"""
WSGI Utilities
(from web.py)
"""

import os
import sys

from . import webapi as web
from .utils import listget, intget
from .net import validaddr
from . import httpserver

def runfcgi(func, addr=('localhost', 8000)):
    """Runs a WSGI function as a FastCGI server."""
    import flup.server.fcgi as flups
    return flups.WSGIServer(func, multiplexed=True, bindAddress=addr, debug=False).run()

def runscgi(func, addr=('localhost', 4000)):
    """Runs a WSGI function as an SCGI server."""
    import flup.server.scgi as flups
    return flups.WSGIServer(func, bindAddress=addr, debug=False).run()

def runwsgi(func):
    """
    Runs a WSGI-compatible `func` using FCGI, SCGI, or a simple web server,
    as appropriate based on context and `sys.argv`.
    """

    if 'SERVER_SOFTWARE' in os.environ:  # cgi
        os.environ['FCGI_FORCE_CGI'] = 'Y'

    # PHP_FCGI_CHILDREN is used by lighttpd fastcgi
    if ('PHP_FCGI_CHILDREN' in os.environ or 'SERVER_SOFTWARE' in os.environ):
        return runfcgi(func, None)

    if 'fcgi' in sys.argv or 'fastcgi' in sys.argv:
        args = sys.argv[1:]
        if 'fastcgi' in args:
            args.remove('fastcgi')
        elif 'fcgi' in args:
            args.remove('fcgi')

        if args:
            return runfcgi(func, validaddr(args[0]))
        else:
            return runfcgi(func, None)

    if 'scgi' in sys.argv:
        args = sys.argv[1:]
        args.remove('scgi')
        if args:
            return runscgi(func, validaddr(args[0]))
        else:
            return runscgi(func)

    server_addr = validaddr(listget(sys.argv, 1, ''))
    if 'PORT' in os.environ:  # e.g. Heroku
        server_addr = ('0.0.0.0', intget(os.environ['PORT']))

    return httpserver.runsimple(func, server_addr)

def _is_dev_mode():
    # Some embedded python interpreters won't have sys.arv
    # For details, see https://github.com/webpy/webpy/issues/87
    argv = getattr(sys, "argv", [])

    # quick hack to check if the program is running in dev mode.
    if 'SERVER_SOFTWARE' in os.environ \
       or 'PHP_FCGI_CHILDREN' in os.environ \
       or 'fcgi' in argv or 'fastcgi' in argv \
       or 'mod_wsgi' in argv:
        return False
    return True

# When running the builtin-server, enable debug mode if not already set.
web.config.setdefault('debug', _is_dev_mode())
