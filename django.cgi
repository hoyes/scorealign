#!/usr/bin/env python
import sys, os
import wsgiref.handlers

mypath = os.path.dirname(__file__)  # the path to this file on the server

sys.path += [mypath]    # python is a folder containing the django installation and other python modules
sys.path += ["/home/pah58/python/music21-1.5.0-py2.7.egg"] 
sys.path += [mypath + "/scorealign"] # your django app containing the settings.py


os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' # settings of your django page module

if __name__ == '__main__':
    import django.core.handlers.wsgi
    # Create a Django application for WSGI.
    application = django.core.handlers.wsgi.WSGIHandler()
    #print os.environ['LD_LIBRARY_PATH']
    wsgiref.handlers.CGIHandler().run(application)
