from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from message import WebHookMessage
from chat import ChatGPTMini
import time




class TranscriptFetcher:
    def __init__(self, video_batch):
        self.video_batch=[video_batch]
        # print(f"\n Processing this {video_batch}")
       
    def long_video_processor(self):

        # processed_count = 0
        for video in self.video_batch:
            # print(video['video_id'])


        # #     retries = 0
        # while retries < 3:
            # try:
                # id = self.video_batch['video_id']
                # print(id)
            fetched_transcript = YouTubeTranscriptApi().fetch(video['video_id'], languages=['en']).to_raw_data()
            # print(fetched_transcript)
            summary, tag = ChatGPTMini(transcript=fetched_transcript).gpt()
            # print(summary)
            if summary == 'Null':
                break
            WebHookMessage(videos=video, tag=tag, summary=summary).long_videos()
            #     processed_count += 1
            #     break
            # except (TranscriptsDisabled, NoTranscriptFound):
            #     continue []
            # except Exception as e:
            #     if '429' in str(e):
            #         retries += 1
            #         if retries < 3:
            #             sleep_time = 2 * (2 ** (retries - 1))
            #             time.sleep(sleep_time)
            #             continue
            #         else:
            #             break
            #     elif '401' in str(e) or '403' in str(e):
            #         break