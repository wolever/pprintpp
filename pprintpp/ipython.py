"""
An ipython extension that monkey-patches it to use pprintpp.

This solution was adapted from an answer to this Stack Overflow question:
https://stackoverflow.com/questions/35375099
asked by:
https://stackoverflow.com/users/71522/david-wolever
and answered by:
https://stackoverflow.com/users/1530134/kupiakos
"""
import IPython
from traitlets.config import Configurable
from traitlets import Int

from . import pformat


original_representation = IPython.lib.pretty.RepresentationPrinter
DEFAULT_INDENTATION = 2


def load_ipython_extension(ipython):
    ipython.config.PPrintPP.indentation = DEFAULT_INDENTATION
    IPython.lib.pretty.RepresentationPrinter = PPrintPPRepresentation
    pprintpp = PPrintPP(parent=ipython, config=ipython.config)
    ipython.configurables.append(pprintpp)


def unload_ipython_extension(ipython):
    IPython.lib.pretty.RepresentationPrinter = original_representation
    try:
        pprintpp = [
            configurable for configurable in ipython.configurables
            if isinstance(configurable, PPrintPP)
        ][0]
    except IndexError:
        print('Could not unload {}'.format(__name__))
    else:
        ipython.configurables.remove(pprintpp)


class PPrintPPRepresentation(object):
    """
    A pretty printer that uses pprintpp
    """

    def __init__(self, stream, *args, **kwargs):
        self.stream = stream
        self.config = IPython.get_ipython().config

    def pretty(self, obj):
        indentation = self.config.PPrintPP.indentation
        self.stream.write(pformat(obj, indent=indentation))

    def flush(self):
        pass


class PPrintPP(Configurable):
    """
    PPrintPP configuration
    """
    indentation = Int(config=True)
