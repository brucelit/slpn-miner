import logging

from slpn_miner.slpn_opt_uemsc_discovery import optimize_with_uemsc
from slpn_miner.slpn_opt_entropic_relevance_discovery import optimize_with_er

logging.getLogger().setLevel(logging.INFO)

__all__ = ['optimize_with_uemsc', 'optimize_with_er']
