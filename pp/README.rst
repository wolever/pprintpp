``pp``: an alias for pprint++
=============================

``pp`` can be installed with Python 2 or Python 3 using ``pip`` or
``easy_install``::

    $ pip install pprintpp pp-ez
    - OR -
    $ easy_install pprintpp pp-ez

The ``pp`` package is just an alias for the ``pprintpp`` package (and falls back
to the ``pprint`` package if ``pprintpp`` isn't available), plus a bit of magic
so it can be called directly::

    >>> import pp
    >>> pp(["Hello", "world"])
    ["Hello", "world"]
    >>> pp.fmt([1, 2, 3])
    '[1, 2, 3]'
    >>> pp.pprint([1, 2, 3])
    [1, 2, 3]
    >>> pp.pformat([1, 2, 3])
    '[1, 2, 3]'

By default, ``pp`` tries to use the ``pprintpp`` package, but if that is not
available it will fall back to using ``pprint``::

    >>> import pp
    >>> pp
    <module 'pp' (pp_magic_module with pprint_mod='pprint')>
    >>> pp.pprint_mod
    <module 'pprint' from '.../lib/python2.7/pprint.pyc'>


See also: ``pprint++``: https://pypi.python.org/pypi/pprintpp
