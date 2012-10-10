#!/usr/bin/env python
"""
unload.py - Jenni Module Unloader
Copyright @2012 Kenneth K. Sham
Licensed under the Eiffel Forum License 2.
"""

def f_unload (jenni, input):
    """ Unloads a module. For use by admins only. """
    if not input.admin:
        return

    nick = input.nick
    if nick not in jenni.config.admins and nick != jenni.config.owner:
        return

    module = input.group(2)
    if jenni.variables.has_key(module):
        jenni.unregister(module)
        jenni.bind_commands()
        jenni.reply('%s unloaded.' % (module))

f_unload.name = 'unload'
f_unload.rule = ('$nick', ['unload'], r'(\S+)?')
f_unload.priority = 'high'
f_unload.thread = False

if __name__ == '__main__':
    print __doc__.strip()
