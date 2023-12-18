import os
from typing import Any
import azure.cognitiveservices.speech as speechsdk
import base64

azureVisemeIdToRhubarb = {
    0: 'X',
    1: 'C',
    2: 'D',
    3: 'F',
    4: 'C',
    5: 'E',
    6: 'B',
    7: 'F',
    8: 'E',
    9: 'D',
    10: 'F',
    11: 'D',
    12: 'C',
    13: 'H',
    14: 'H',
    15: 'B',
    16: 'B',
    17: 'C',
    18: 'G',
    19: 'H',
    20: 'H',
    21: 'A',
}


async def audio_file_to_base64(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
        return base64.b64encode(data).decode('utf-8')


async def azure_speech(text, file_name):
    print('azure_speech')
    speech_key = os.environ.get("AZURE_SPEECH_KEY")
    speech_region = os.environ.get("AZURE_SPEECH_REGION")
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    audio_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    viseme_data = []

    def on_viseme_received(e):
        viseme_data.append({
            "offset": e.audio_offset / 10000000.0,
            "visemeId": e.viseme_id
        })

    synthesizer.viseme_received.connect(on_viseme_received)
    synthesizer.speak_text_async(text).get()

    lipsync_data: dict[str, list[Any]] = {
        "mouthCues": [
            # example--> { "start": 0.00, "end": 0.01, "value": "X" },
        ]
    }
    prev_offset = 0

    for azure_viseme in viseme_data:
        lipsync_data["mouthCues"].append({
            "start": prev_offset,
            "end": azure_viseme["offset"],
            "value": azureVisemeIdToRhubarb[azure_viseme["visemeId"]]
        })
        prev_offset = azure_viseme["offset"]

    return {
        "lipsync": lipsync_data,
        "audio": await audio_file_to_base64(file_name)
    }
