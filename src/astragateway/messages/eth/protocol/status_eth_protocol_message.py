import blxr_rlp as rlp

from astragateway.messages.eth.protocol.eth_protocol_message import EthProtocolMessage
from astragateway.messages.eth.protocol.eth_protocol_message_type import EthProtocolMessageType


class StatusEthProtocolMessage(EthProtocolMessage):
    msg_type = EthProtocolMessageType.STATUS

    fields = [("eth_version", rlp.sedes.big_endian_int),
              ("network_id", rlp.sedes.big_endian_int),
              ("chain_difficulty", rlp.sedes.big_endian_int),
              ("chain_head_hash", rlp.sedes.binary),
              ("genesis_hash", rlp.sedes.binary),
              ("fork_id", rlp.sedes.List([rlp.sedes.binary, rlp.sedes.big_endian_int], strict=False))]

    def get_eth_version(self):
        return self.get_field_value("eth_version")

    def get_network_id(self):
        return self.get_field_value("network_id")

    def get_chain_difficulty(self):
        return self.get_field_value("chain_difficulty")

    def get_chain_head_hash(self):
        return self.get_field_value("chain_head_hash")

    def get_genesis_hash(self):
        return self.get_field_value("genesis_hash")

    def get_fork_id(self):
        return self.get_field_value("fork_id")
