#!/usr/bin/env python

import bjoern # for local testing
from wsgi import application

bjoern.run(application, 'localhost', 8080) # for local testing
