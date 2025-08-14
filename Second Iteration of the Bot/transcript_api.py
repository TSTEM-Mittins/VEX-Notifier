from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from message import WebHookMessage
from chat import ChatGPTMini
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TranscriptFetcher:
    def __init__(self, video):
        self.video=[video]
    def long_video_processor(self):
            for video in self.video:
                print(video['video_id'])
                fetched_transcript = YouTubeTranscriptApi().fetch(video_id=video['video_id'], languages=['en']).to_raw_data()
                summary, tag = ChatGPTMini(transcript=fetched_transcript).gpt()
                if summary == 'Null':
                    return []
                WebHookMessage(videos=video, tag=tag, summary=summary).long_videos()
                # if (TranscriptsDisabled, NoTranscriptFound):
                #     logging.info(f"\n For {video('title')} could not find transcript")
                #     return []
            # if Exception as e:
            #     if '429' in str(e):
            #         retries += 1
            #         if retries < 3:
            #             sleep_time = 2 * (2 ** (retries - 1))
            #             time.sleep(sleep_time)
                        
            #         else:
            #             return []
            #     elif '401' in str(e) or '403' in str(e):
            #         return []
