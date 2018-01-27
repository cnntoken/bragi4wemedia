#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bragi.settings")

    from django.core.management import execute_from_command_line
    from corelib.store import init_connection
    init_connection()

    execute_from_command_line(sys.argv)
