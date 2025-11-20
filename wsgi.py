#!/usr/bin/env python3
"""
WSGI configuration file for PythonAnywhere deployment.

Instructions for PythonAnywhere:
1. Upload this file to: /home/yourusername/italian-trainer/wsgi.py
2. In the PythonAnywhere Web tab, edit the WSGI configuration file
3. Replace the entire contents with the code from this file
4. Update the path '/home/yourusername/italian-trainer' to match your actual path
"""

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/italian-trainer'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the Flask application
from vocab_web import application

# PythonAnywhere will use this 'application' object
# Note: Make sure all your files (vocab_core.py, vocab_db.py, etc.) are in the same directory
