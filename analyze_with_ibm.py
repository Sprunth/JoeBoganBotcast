from typing import Dict, List

from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud.watson_service import DetailedResponse

from dataclasses import dataclass

import configparser
import json
import os.path

AUDIO_SOURCE_FILE = 'sample'
AUDIO_SOURCE_FILE_NAME = '%s.flac' % AUDIO_SOURCE_FILE
CACHE_FILE_NAME = 'ibm_response-%s.json' % AUDIO_SOURCE_FILE


@dataclass
class SpeechRecord(object):
    start: float
    end: float
    word: str
    speaker: int


config = configparser.ConfigParser()
config.read("config.ini")

speech_to_text = SpeechToTextV1(
    username=config.get('credentials', 'username'),
    password=config.get('credentials', 'password')
)


def get_raw_transcription_results() -> Dict:
    # ibm API is slow, so call it once and cache it
    if os.path.isfile(CACHE_FILE_NAME):
        with open(CACHE_FILE_NAME) as f:
            res = json.load(f)
            print('recognition result loaded from cache')
        return res

    with open(AUDIO_SOURCE_FILE_NAME, 'rb') as audio_file:
        speech_recognition_results: DetailedResponse = speech_to_text.recognize(
            audio=audio_file,
            content_type='audio/flac',
            timestamps=True,
            word_alternatives_threshold=0.9,
            keywords=['Conor'],
            keywords_threshold=0.2,
            speaker_labels=True,
            profanity_filter=False
        )
    print(speech_recognition_results.get_status_code())
    res = speech_recognition_results.get_result()
    print(json.dumps(res, indent=2))

    with open(CACHE_FILE_NAME, 'w') as outfile:
        outfile.write(json.dumps(res))
    return res


def process_raw_results(res):
    # post processing of result
    segment_count = 0
    segments: Dict[str, int] = {}
    transcription: Dict[int, SpeechRecord] = {}

    # index speakers
    for entry in res['speaker_labels']:
        f = entry['from']
        t = entry['to']
        s = entry['speaker']

        segments['%s-%s' % (f, t)] = segment_count
        transcription[segment_count] = SpeechRecord(f, t, '', s)
        segment_count += 1

    # index transcribed text

    # because it's broken up into multiple results for some reason
    for result in res['results']:
        # strange key value to use, but it's actually only the *best* alternative here
        # and again they use return a list so we iterate...
        for stamps in result['alternatives']:
            # finally the dict containing a list of timestamps, each as an array of [word, from, to]
            for ts in stamps['timestamps']:
                word = ts[0]
                f = ts[1]
                t = ts[2]
                transcription[segments['%s-%s' % (f, t)]].word = word
    # done
    print(transcription)

    # we know how many segments there are due to segment_count, so just go through them in order
    # collect words until we see a speaker change
    current_speaker = transcription[0].speaker  # initial speaker
    current_speech: List[str] = []
    for segment_number in range(segment_count):
        record = transcription[segment_number]
        if record.speaker != current_speaker:
            # speaker changed, so let's print and flush
            print('Speaker %s: %s' % (current_speaker, ' '.join(current_speech)))
            current_speaker = record.speaker
            current_speech.clear()
        current_speech.append(record.word)
    # need to make sure final words are printed
    print('Speaker %s: %s' % (current_speaker, ' '.join(current_speech)))


if __name__ == '__main__':
    res = get_raw_transcription_results()
    process_raw_results(res)
