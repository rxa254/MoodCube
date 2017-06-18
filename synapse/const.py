import os

SYNAPSE_PORTS = os.getenv('SYNAPSE_PORTS', '5555:5556').split(':')

MUX_SINK = 'tcp://127.0.0.1:{}'.format(SYNAPSE_PORTS[0])
MUX_SOURCE = 'tcp://127.0.0.1:{}'.format(SYNAPSE_PORTS[1])

AUDIO_CHANNEL = 1
#AUDIO_RATE = 44100
# for phoenix
AUDIO_RATE = 16000

OPC_ADDR = 'localhost:7890'
