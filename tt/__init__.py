#!/usr/bin/env python
import os
__all__ = []
path = os.path.dirname(os.path.abspath(__file__))
for module in os.listdir(path):
    if module[-3:] == '.py':
       __all__.append(module[:-3])
    else:
       continue
