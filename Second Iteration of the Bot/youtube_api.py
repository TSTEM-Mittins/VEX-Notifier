from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from isodate import parse_duration
import logging
from message import WebHookMessage
import time
import random
from transcript_api import TranscriptFetcher
import asyncio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
published_after = (datetime.utcnow() - timedelta(days=30)).isoformat("T") + "Z"
#   Handles search and video details
class YouTubeSearch:

#   This block loads the requirements into the class.
    def __init__(self, query="vex robotics", max_results=5, days_back=30):
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
            logging.error(f"Error fetching videos: {e}")
            return []
        
async def short_videos_task(short_videos):
    for videos in short_videos:
        WebHookMessage(videos=videos).short_videos()
        logging.info(f"\nSuccessfully proccessed, {videos['title']}")
        await asyncio.sleep(60)

async def long_videos_task(long_videos):
    for videos in long_videos:
        n = len(long_videos)
        s = round(random.uniform(1,50), 2)
        sleep = (86000 / n) + s
        TranscriptFetcher(video_batch=videos).long_video_processor()
        print(f"\nSuccessfully Proccessed, {videos['title']}")
        
        await asyncio.sleep(sleep)

async def stream_videos_task(stream_videos):
    for videos in stream_videos:
        WebHookMessage.stream_videos(videos)
        logging.info(f"\nSuccessfully proccessed, {'video_id'}")
        await asyncio.sleep(60)

async def main():
        yt = YouTubeSearch()
        vid = yt.search_videos()

        await asyncio.gather(
            short_videos_task(vid.get('short_videos', [])),
            long_videos_task(vid.get('long_videos', [])),
            stream_videos_task(vid.get('streaming_videos', []))
        )   

if __name__ == "__main__":
       
    asyncio.run(main())
    

