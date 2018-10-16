
def load():
    from . import \
         builtin, \
         stdio, \
         entity

    return locals()

# load() returns a dict of (name: module) items.
# Map each item into (name: module.exports)
libs = dict(map(lambda i: (i[0], i[1].exports), load().items()))
