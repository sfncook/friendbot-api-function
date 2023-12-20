import os
from typing import Any
import azure.cognitiveservices.speech as speechsdk
import base64

azureVisemeIdToModelCodes = {
    0: {"target":"viseme_sil", "value":1},
    1: {"target":"viseme_aa", "value":1},
    2: {"target":"viseme_aa", "value":1},
    3: {"target":"viseme_O", "value":1},
    4: {"target":"viseme_O", "value":0.7},
    5: {"target":"viseme_RR", "value":1},
    6: {"target":"viseme_I", "value":0.7},
    7: {"target":"viseme_U", "value":1},
    8: {"target":"viseme_aa", "value":0.8},
    9: {"target":"viseme_O", "value":1},
    10: {"target":"viseme_aa", "value":0.7},
    11: {"target":"viseme_aa", "value":1},
    12: {"target":"viseme_RR", "value":0.8},
    13: {"target":"viseme_O", "value":1},
    14: {"target":"viseme_O", "value":1},
    15: {"target":"viseme_SS", "value":1},
    16: {"target":"viseme_CH", "value":1},
    17: {"target":"viseme_TH", "value":1},
    18: {"target":"viseme_FF", "value":1},
    19: {"target":"viseme_DD", "value":1},
    20: {"target":"viseme_kk", "value":1},
    21: {"target":"viseme_PP", "value":1},
}


async def audio_file_to_base64(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
        return base64.b64encode(data).decode('utf-8')


async def azure_speech(text, file_name):
    try:
        print(f'fuck azure a.1 text:{text}')
        speech_key = os.environ.get("AZURE_SPEECH_KEY")
        speech_region = os.environ.get("AZURE_SPEECH_REGION")
        print(f"speech_key: {speech_key}")
        print(f"speech_region: {speech_region}")
        print('fuck azure a.2')
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

        print('fuck azure a.3')
        synthesizer.viseme_received.connect(on_viseme_received)
        print('fuck azure a.4')
        synthesizer.speak_text_async(text).get()
        print('fuck azure a.5')

        lipsync_data: dict[str, list[Any]] = {
            "mouthCues": [
                # example--> { "start": 0.00, "end": 0.01, "value": "X" },
            ]
        }
        prev_offset = 0

        print('fuck azure ')
        for azure_viseme in viseme_data:
            model_code = azureVisemeIdToModelCodes[azure_viseme["visemeId"]]
            lipsync_data["mouthCues"].append({
                "start": prev_offset,
                "end": azure_viseme["offset"],
                "target": model_code['target'],
                "value": model_code['value']
            })
            prev_offset = azure_viseme["offset"]

        return {
            "lipsync": lipsync_data,
            "audio": await audio_file_to_base64(file_name)
        }
    except Exception as inst:
        print("ERROR in azure_speech")
        print(type(inst))    # the exception type
        print(inst.args)     # arguments stored in .args
        print(inst)          # __str__ allows args to be printed directly,
        # but may be overridden in exception subclasses
        return {
            "lipsync": "",
            "audio": ""
        }
