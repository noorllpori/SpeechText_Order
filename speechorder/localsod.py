import os
from .ft import *
import sys
import asyncio
import numpy as np
import queue
import threading
import json
import hashlib
try:
    import sounddevice as sd
    import websockets
except ImportError:
    print()
    print("  pip install sounddevice")
    print("  pip install websockets")
    print()
    sys.exit(-1)

class tokeN:
    def __init__(self,token:str,stime:float,sentid:int):
        self.token:str = token
        self.start_time:float = stime
        self.SentId:int = sentid
        text = f"{self.token}{str(self.start_time)}{str(self.sentid)}"
        tid = hashlib.sha256(text.encode()).hexdigest()
        self.Tid:str = f"tid{tid}"
        self._end = False
        self.ys_prob = 0

class t:
    def __init__(self) -> None:
        self.asrm:asr_mode = asr_mode()
        self.main_que:queue.Queue
        self.asr_thread:threading.Thread

        # 所有token列表
        self.tokenList:list[tokeN] = []

        # 开启torch bert模型匹配
        self.bert_step = False
        self.modelPath = ""

    def Bert_ModelLoad( self, model_path ):
        self.modelPath = model_path
        self.bert_step = True
        pass

    def SetASR( self, asr:asr_mode):
        self.asrm = asr
        if asr.id == "sherpa":
            # asyncio.run(self.sherpa_main())
            self.asr_thread = threading.Thread(target=self.run_async, daemon=True)
            self.asr_thread.start()

    def sherpa_decode_serverGet(self, msg:dict):
        """
        解码Sherpa获取的文本数据
        {
            'text': '喂喂', 
            'tokens': ['喂', '喂'], 
            'timestamps': [2.32, 2.44], 
            'ys_probs': [-0.141697, -0.511112], 
            'segment': 27, 
            'start_time': 6977.6, 
            'is_final': False}
        """
        # print( msg )
        msg_count = len(msg['tokens'])
        start_time:float = msg['start_time']
        sent_id:int = msg['segment']
        if_end:bool = msg['is_final']
        _i = 0
        for _t in msg['tokens']:
            tk = msg['tokens'][_i]
            tstamp = msg['timestamps'][_i]
            _ys = msg['ys_probs'][_i]
            _i += 1
            
        tok = tokeN( token="", stime=0.0, sentid=0 )
        # 字符列表上限为100
        while self.tokenList.count() >= 100: self.tokenList.remove(0)
        self.tokenList.append( tok )

    async def receive_results(self, socket: websockets.WebSocketServerProtocol):
        last_message = ""
        async for message in socket:
            if message != "Done!":
                if last_message != message:
                    last_message = message

                    if last_message:
                        try:
                            msg_dict:dict = json.loads(last_message)
                            if len(msg_dict['text']) > 0:
                                self.sherpa_decode_serverGet( msg_dict )
                        except:
                            pass

            else:
                return last_message
            
        
    async def inputstream_generator(self, channels=1):
        """Generator that yields blocks of input data as NumPy arrays.

        See https://python-sounddevice.readthedocs.io/en/0.4.6/examples.html#creating-an-asyncio-generator-for-audio-blocks
        """
        q_in = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def callback(indata, frame_count, time_info, status):
            loop.call_soon_threadsafe(q_in.put_nowait, (indata.copy(), status))

        devices = sd.query_devices()
        print(devices)
        default_input_device_idx = sd.default.device[0]
        print(f'Use default device: {devices[default_input_device_idx]["name"]}')
        print()
        print("Started! Please speak")

        stream = sd.InputStream(
            callback=callback,
            channels=channels,
            dtype="float32",
            samplerate=16000,
            blocksize=int(0.05 * 16000),  # 0.05 seconds
        )
        with stream:
            while True:
                indata, status = await q_in.get()
                yield indata, status

    async def shp_run(
        self,
        server_addr: str,
        server_port: int,
    ):
        print( f"ws://{server_addr}:{server_port}" ) 
        async with websockets.connect(
            f"ws://{server_addr}:{server_port}"
        ) as websocket:  # noqa
            receive_task = asyncio.create_task(self.receive_results(websocket))
            print("Started! Please Speak")

            async for indata, status in self.inputstream_generator():
                if status:
                    print(status)
                indata = indata.reshape(-1)
                indata = np.ascontiguousarray(indata)
                await websocket.send(indata.tobytes())

            decoding_results = await receive_task
            print(f"\nFinal result is:\n{decoding_results}")
            
    async def inputstream_generator(self, channels=1):
        """Generator that yields blocks of input data as NumPy arrays.

        See https://python-sounddevice.readthedocs.io/en/0.4.6/examples.html#creating-an-asyncio-generator-for-audio-blocks
        """
        q_in = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def callback(indata, frame_count, time_info, status):
            loop.call_soon_threadsafe(q_in.put_nowait, (indata.copy(), status))

        devices = sd.query_devices()
        print(devices)
        default_input_device_idx = sd.default.device[0]
        print(f'Use default device: {devices[default_input_device_idx]["name"]}')
        print()
        print("Started! Please speak")

        stream = sd.InputStream(
            callback=callback,
            channels=channels,
            dtype="float32",
            samplerate=16000,
            blocksize=int(0.05 * 16000),  # 0.05 seconds
        )
        with stream:
            while True:
                indata, status = await q_in.get()
                yield indata, status

    async def sherpa_main(self):

        server_addr = self.asrm.address
        server_port = self.asrm.port

        print( f">> server_addr {server_addr}" )
        print( f">> server_port {server_port}" )

        await self.shp_run(
            server_addr=server_addr,
            server_port=server_port,
        )

    def run_async(self):
        # 在新线程中运行异步事件循环
        asyncio.run(self.sherpa_main())