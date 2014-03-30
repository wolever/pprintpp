``pprintpp``: a drop-in replacement for ``pprint`` that's actually pretty
=========================================================================

Usage
-----

``pprintpp`` can be used in three ways:

1. As a regular module::

   >>> import pprintpp
   >>> pprintpp.pprint(...)

2. As a command-line program, which will read Python literals from standard in
   and pretty-print them::

    $ echo "{'hello': 'world'}" | pypprint
    {
        'hello': 'world',
    }

3. To monkeypatch ``pprint``::

    >>> import pprintpp
    >>> pprintpp.monkeypatch()
    >>> import pprint
    >>> pprint.pprint(...)

   Note: the original ``pprint`` will be available with ``import
   pprint_original``.

Why is it prettier?
-------------------

Unlike ``pprint``, ``pprintpp`` strives to emit a readable, largely
PEP8-complient, representation of its input.

**Note**: ``pprintpp`` is still under development, so the format *will* change
and improve over time.

Without ``printpp``::

    >>> import pprint
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


With ``printpp``::

    >>> import pprintpp
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
