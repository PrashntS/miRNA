#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
from functools import wraps


def mproperty(fget):
    """
    Return a property attribute for new-style classes that only calls its getter on the first
    access. The result is stored and on subsequent accesses is returned, preventing the need to
    call the getter any more.
    Example::
        >>> class C(object):
        ...     load_name_count = 0
        ...     @mproperty
        ...     def name(self):
        ...         "name's docstring"
        ...         self.load_name_count += 1
        ...         return "the name"
        >>> c = C()
        >>> c.load_name_count
        0
        >>> c.name
        "the name"
        >>> c.load_name_count
        1
        >>> c.name
        "the name"
        >>> c.load_name_count
        1
    """
    attr_name = '_{0}'.format(fget.__name__)

    @wraps(fget)
    def fget_memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fget(self))
        return getattr(self, attr_name)

    return property(fget_memoized)
