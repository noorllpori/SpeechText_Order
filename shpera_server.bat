cd sherpa_onnx\win\bin

sherpa-onnx-online-websocket-server.exe ^
    --port=30500 ^
    --num-work-threads=3 ^
    --num-io-threads=3 ^
    --tokens=../../streaming-small-zh-en/tokens.txt ^
    --encoder=../../streaming-small-zh-en/encoder-epoch-99-avg-1.onnx ^
    --decoder=../../streaming-small-zh-en/decoder-epoch-99-avg-1.onnx ^
    --joiner=../../streaming-small-zh-en/joiner-epoch-99-avg-1.onnx ^
    --log-file=../../log.txt ^
    --max-batch-size=5 ^
    --loop-interval-ms=11