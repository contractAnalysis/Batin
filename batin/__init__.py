# We use RsT document formatting in docstring. For example :param to mark parameters.
# See PEP 287
__docformat__ = "restructuredtext"
import logging

# Accept batin.VERSION to get batin's current version number
from .__version__ import __version__ as VERSION  # NOQA
# from batin.plugin.loader import MythrilPluginLoader

log = logging.getLogger(__name__)
