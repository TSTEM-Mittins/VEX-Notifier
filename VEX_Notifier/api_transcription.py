from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import os
import json
import time

class TranscriptFetcher:
    def __init__(self):
        self.total_sleep_time = 86400
        # self.proxies = self._load_proxies()
    #     self.current_proxy = None

    # def _load_proxies(self):
    #     if os.path.exists('proxies.txt'):
    #         with open('proxies.txt') as f:
    #             return[line.strip() for line in f if line.strip()]
    #     return []

    # def _rotate_proxy(self):
    #     if self.proxies:
    #         self.current_proxy = random.choice(self.proxies)
    #         YouTubeTranscriptApi.set_proxy({
    #             'http': self.current_proxy,
    #             'https': self.current_proxy
    #         })
    #         print(f"Using proxy: {self.current_proxy}")

    def fetch_all_transcript(self, filtered_videos):
        if not filtered_videos:
            print("No videos found")
            return {}
        
        n = len(filtered_videos)
        if n == 0:
            print("No videos to process.")
            return {}
        sleep_interval = self.total_sleep_time / n
        results = {}

        os.makedirs("transcripts", exist_ok=True)
          
        for idx, video in enumerate(filtered_videos, 1):
            video_id = video['video_id']
            try:
                # if idx % 5 == 0 and self.proxies:

                #     self._rotate_proxy()

                print(f"\nProcessing {idx}/{n}: {video['title']}")
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id,
                    languages=['en'],
                    # proxies={'https': self.current_proxy} 
                    # if self.current_proxy else None
                )
                results[video_id] = {
                    'video_id': video_id,
                    'title': video['title'],
                    'url': video['url'],
                    'transcript': [
                        {
                            'text': entry['text'],
                            'start': entry['start'],
                            'duration': entry['duration']
                        } for entry in transcript
                    ]
                }

                print(f"Successfully fetched transcript for {video_id}")
                print(f"Defined transcript for {video_id}")

            except (TranscriptsDisabled, NoTranscriptFound) as e:
                print(f"Skipping {video_id}: {str(e)}")
                results[video_id] = None
            except Exception as e:
                print(f"Error on {video_id}: {str(e)}")
                if "429" in str(e):
                    self._rotate_proxy()
                results[video_id] = None

            if idx < n:
                print(f"Sleeping for {sleep_interval / 3600:.2f} hours")
                time.sleep(sleep_interval)

        return results

def fetch_and_transcribe():
    video = {
            'video_id': 'rOrr_1h2YfE',
            'title': 'VEX Smart Motor Cartridge Change',
            'url': 'https://www.youtube.com/watch?v=rOrr_1h2YfE'
        }
    
    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            video['video_id'], 
            languages=['en']
            )
        
        print("Raw Transcript:", transcript)

        if not transcript:
            raise ValueError("Empty Transcript returned")
        
        results = {
                'video_id': video['video_id'],
                'title': video['title'],
                'url': video['url'],
                'transcript': [
                    {
                        'text': entry['text'],
                        'start': entry['start'],
                        'duration': entry['duration']
                    }
                    for entry in transcript
                ]
            }
        print(f"Defined transcript for {video['video_id']}")
        return {video['video_id']: results}

    
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        print(f"Skipping {video['video_id']}: {e}")
        return {video['video_id']: None}
    except Exception as e:
        print(f"Error defining video {video['video_id']}: {e}")
        return {video['video_id']: None}

if __name__ == "__main__":
    transcript_result = fetch_and_transcribe()

    for video_id, data in transcript_result.items():
        if data:
            print(f"\nTranscript for {video_id}:")
            for line in data['transcript']:
                print(f"{line['start']:.2f}s: {line['text']}")
        else:
            print(f"No transcript found for video {video_id}")
