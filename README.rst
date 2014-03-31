``pprint++``: a drop-in replacement for ``pprint`` that's actually pretty
=========================================================================

Installation
------------

::

    $ pip install pprintpp

The ``pprint++`` source distribution also contains a package called ``pp``, a
convinient alias for ``pprintpp``. The ``pp`` package is optional, but must be
installed separately::

    $ pip install pp-ez
    $ python
    ...
    >>> import pp
    >>> pp(["Hello", "world"])
    ["Hello", "world"]

For more, see https://pypi.python.org/pypi/pp-ez

Usage
-----

``pprint++`` can be used in three ways:

1. As a regular module::

   >>> import pprintpp
   >>> pprintpp.pprint(...)

2. As a command-line program, which will read Python literals from standard in
   and pretty-print them::

    $ echo "{'hello': 'world'}" | pypprint
    {'hello': 'world'}

3. To monkeypatch ``pprint``::

    >>> import pprintpp
    >>> pprintpp.monkeypatch()
    >>> import pprint
    >>> pprint.pprint(...)

   Note: the original ``pprint`` will be available with ``import
   pprint_original``.

4. Through the separate ``pp`` module::

    $ pip insatll pp
    $ python
    ...
    >>> import pp
    >>> pp(["Hello", "world"])
    ["Hello", "world"]

   For more, see https://pypi.python.org/pypi/pp-ez

Why is it prettier?
-------------------

Unlike ``pprint``, ``pprint++`` strives to emit a readable, largely
PEP8-complient, representation of its input.

It also has explicit support for: the ``collections`` module (``defaultdict``
and ``Counter``) and ``numpy`` arrays.

**Note**: ``pprint++`` is still under development, so the format *will* change
and improve over time.

Example
~~~~~~~

With ``printpp``::

    >>> import pprintpp
    >>> pprintpp.pprint(["Hello", np.array([[1,2],[3,4]])])
    [
        'Hello',
        array([[1, 2],
               [3, 4]]),
    ]
    >>> pprintpp.pprint(tweet)
    {
        'coordinates': None,
        'created_at': 'Mon Jun 27 19:32:19 +0000 2011',
        'entities': {
            'hashtags': [],
            'urls': [
                {
                    'display_url': 'tumblr.com/xnr37hf0yz',
                    'expanded_url': 'http://tumblr.com/xnr37hf0yz',
                    'indices': [107, 126],
                    'url': 'http://t.co/cCIWIwg',
                },
            ],
            'user_mentions': [],
        },
        'place': None,
        'source': '<a href="http://www.tumblr.com/" rel="nofollow">Tumblr</a>',
        'truncated': False,
        'user': {
            'contributors_enabled': True,
            'default_profile': False,
            'entities': {'hashtags': [], 'urls': [], 'user_mentions': []},
            'favourites_count': 20,
            'id_str': '6253282',
            'profile_link_color': '0094C2',
        },
    }

Without ``printpp``::

    >>> import pprint
    >>> import numpy as np
    >>> pprint.pprint(["Hello", np.array([[1,2],[3,4]])])
    ['Hello', array([[1, 2],
           [3, 4]])]
    >>> tweet = {'coordinates': None, 'created_at': 'Mon Jun 27 19:32:19 +0000 2011', 'entities': {'hashtags': [], 'urls': [{'display_url': 'tumblr.com/xnr37hf0yz', 'expanded_url': 'http://tumblr.com/xnr37hf0yz', 'indices': [107, 126], 'url': 'http://t.co/cCIWIwg'}], 'user_mentions': []}, 'place': None, 'source': '<a href="http://www.tumblr.com/" rel="nofollow">Tumblr</a>', 'truncated': False, 'user': {'contributors_enabled': True, 'default_profile': False, 'entities': {'hashtags': [], 'urls': [], 'user_mentions': []}, 'favourites_count': 20, 'id_str': '6253282', 'profile_link_color': '0094C2'}} 
    >>> pprint.pprint(tweet)
    {'coordinates': None,
     'created_at': 'Mon Jun 27 19:32:19 +0000 2011',
     'entities': {'hashtags': [],
                  'urls': [{'display_url': 'tumblr.com/xnr37hf0yz',
                            'expanded_url': 'http://tumblr.com/xnr37hf0yz',
                            'indices': [107, 126],
                            'url': 'http://t.co/cCIWIwg'}],
                  'user_mentions': []},
     'place': None,
     'source': '<a href="http://www.tumblr.com/" rel="nofollow">Tumblr</a>',
     'truncated': False,
     'user': {'contributors_enabled': True,
              'default_profile': False,
              'entities': {'hashtags': [], 'urls': [], 'user_mentions': []},
              'favourites_count': 20,
              'id_str': '6253282',
              'profile_link_color': '0094C2'}}
