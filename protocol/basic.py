import json
import socket

class BasicProtocol(object):
    """ Basic protocol based on sending 
    """

    def __init__(self, header_size=20, encoding='utf-8', debug=False):
        self.header_size = header_size
        self.encoding = encoding
        self.debug = debug

    def get_formated_message(self, msg: str):
        msg_len = str(len(msg))
        if self.debug:
            print("Encoding message | length:{} data:{}".format(msg_len, msg))
        if len(msg_len) > self.header_size:
            print("Message too long | Message: {}".format(msg))
            return ""

        header = msg_len.ljust(self.header_size)
        return msg, header

    def encode(self, msg):
        return bytes(msg, self.encoding)

    def get_messages_to_send(self, msg):
        if not isinstance(msg, str):
            msg = json.dumps(msg)

        data, header = self.get_formated_message(msg)
        return [self.encode(header), self.encode(data)]

    def decode(self, msg_bytes):
        msg = msg_bytes.decode(self.encoding).strip()
        if msg[0] == "{" or msg[0] == "[":
            msg = json.loads(msg)
        
        return msg

    def receive_packet(self, receive_fn, buff_size):
        result = receive_fn(buff_size)

        address = None
        if isinstance(result, tuple):
            msg, address = result
        else:
            msg = result
        
        return msg, address

    def receive_from_socket(self, receive_fn):
        """receive message using the given function by the client/server
        
        Raises:
            Exception: Receiving
        
        Returns:
            (data, address)
        """

        # get header
        msg_header, address = self.receive_packet(receive_fn, self.header_size)
        if not len(msg_header):
            raise Exception("Error receiving the header")
            return
        
        msg_len = int(self.decode(msg_header))
        msg_data, address = self.receive_packet(receive_fn, msg_len)
        data = self.decode(msg_data)
        return data, address
