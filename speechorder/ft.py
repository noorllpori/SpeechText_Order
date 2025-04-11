
class asr_mode():
    def __init__(   self,
                    id='sherpa',
                    address="127.0.0.1",
                    port=5000,
        ) -> None:
        self.id = id
        self.address = address
        self.port = port

        self.tcp = False
        self.udp = False
        self.http = False

