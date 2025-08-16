from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import datetime
from isodate import parse_duration
# import logging
from message import WebHookMessage
import time
import random
from transcript_api import TranscriptFetcher
import asyncio


# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
published_after = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
processed_id = set()
#   Handles search and video details
class YouTubeSearch:

#   This block loads the requirements into the class.
    def __init__(self, query="vex robotics", max_results=20, days_back=30):
        load_dotenv()
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        self.youtube = build ('youtube', 'v3', developerKey=self.api_key)
        self.query = query
        self.max_results = max_results
        self.days_back = days_back
   
    def search_videos(self, min_duration=120, max_duration=3600):
        try:
            request = self.youtube.search().list(
                q=self.query,
                part='snippet',
                type='video',
                order='date',
                publishedAfter=published_after,
                maxResults=self.max_results,
                safeSearch='strict'
            ).execute()
            
            video_ids = [item["id"]["videoId"] for item in request['items']]

            if not video_ids:
                return
            
            request_details = self.youtube.videos().list(
                part='statistics,contentDetails',
                id=",".join(video_ids) 
            ).execute() 
            
            details = {
                item['id']: {
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'duration': parse_duration(item['contentDetails'].get('duration')).total_seconds()
                } for item in request_details.get('items', [])}
            
            videos = []
            for i, item in enumerate(request['items'], start=1):
                    videos.append({
                        'title': item['snippet']['title'],
                        'video_id': item['id']['videoId'],
                        'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                        'channelTitle': item['snippet']['channelTitle'],
                        'index': i,
                        **details[item['id']['videoId']]
                })
                    
            short_videos = [vid for vid in videos if vid['duration'] < min_duration]
            long_videos = [vid for vid in videos if min_duration <= vid['duration'] <= max_duration]
            streaming_videos = [vid for vid in videos if vid['duration'] > max_duration]

           
            return {
            'short_videos': short_videos,
            'long_videos': long_videos,
            'streaming_videos': streaming_videos
        }

        
        except Exception as e:
            # logging.error(f"Error fetching videos: {e}")
            return []
        
async def short_videos_task(short_videos):
    for videos in short_videos:
        WebHookMessage(videos=videos).short_videos()
        # logging.info(f"\nSuccessfully proccessed, {videos['title']}")
        await asyncio.sleep(500)

async def long_videos_task(long_videos):
    for videos in long_videos:
        # n = len(long_videos)
        # s = round(random.uniform(1,50), 2)
        # sleep = (86000 / n) + s
        # TranscriptFetcher(video=videos).long_video_processor()
        WebHookMessage(videos=videos).long_videos()
        # logging.info(f"\nSuccessfully Proccessed, {videos['title']}")
        
        await asyncio.sleep(600)

async def stream_videos_task(stream_videos):
    for videos in stream_videos:
        WebHookMessage(videos=videos).stream_videos()
        # logging.info(f"\nSuccessfully proccessed, {videos['video_id']}")
        await asyncio.sleep(700)
        

async def main():
        global processed_id

        yt = YouTubeSearch()
        print(published_after)
        vid = yt.search_videos()
        if not vid:
            return
        short_videos = [v for v in vid.get('short_videos', []) if v['video_id'] not in processed_id]
        long_videos = [v for v in vid.get('long_videos', []) if v['video_id'] not in processed_id]
        stream_videos = [v for v in vid.get('streaming_videos', []) if v['video_id'] not in processed_id]
        if not short_videos and not long_videos and not stream_videos:
            return
        for v in short_videos + long_videos + stream_videos:
            processed_id.add(v['video_id'])
        # logging.info(f"\n Video List {vid}")

        await asyncio.gather(
            short_videos_task(short_videos=short_videos),
            long_videos_task(long_videos=long_videos),
            stream_videos_task(stream_videos=stream_videos)
        )   
        


if __name__ == "__main__":
    while True:
        asyncio.run(main())
        # logging.info(f"\nFinishe Executing. Sleeping for 30 minutes.")
        time.sleep(1800)





