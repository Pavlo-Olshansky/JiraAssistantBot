#!/usr/bin/env python3

import os
from os import system

root_dir = '.'


def should_ignore(fn):
    if '/migrations/' in fn:
        return True
    if '/.jira_assistant/' in fn:
        return True
    return False


for directory, subdirectories, files in os.walk(root_dir):
    for file in files:
        fn = os.path.join(directory, file)
        if fn.endswith('.py') and not should_ignore(fn):
            system(f'flake8 {fn}')
