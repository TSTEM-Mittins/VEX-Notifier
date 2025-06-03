from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from isodate import parse_duration

#   Handles search and video details
class YouTubeSearch:

#   This block loads the requirements into the class.
    def __init__(self, query="vex robotics", max_results=50, days_back=30):
        load_dotenv()
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        self.youtube = build ('youtube', 'v3', developerKey=self.api_key)
        self.query = query
        self.max_results = max_results
        self.days_back = days_back

#   Filter requirements to only gather videos that are 7 days old
    def search_videos(self):
        published_after = (datetime.utcnow() - timedelta(days=self.days_back)).isoformat("T") + "Z"

#   Results cannot be below 1 search or exeed 50 searches
        if self.max_results < 1 or self.max_results > 50:
            raise ValueError
        
        try:
            request = self.youtube.search().list(
                q=self.query,
                part='snippet',
                type='video',
                order='date',
                publishedAfter=published_after,
                maxResults=self.max_results,
                safeSearch='strict'
            )
            response = request.execute()
        
            #   If search fails
        except Exception as e:
            print(f"Error fetching video details: {e}")
            return []

#   If search query is empty
        if not response.get('items'):
            print("No videos found.")
            return []

#   If video is found
        videos = []
        for item in response['items']:
            videos.append({
                'title': item['snippet']['title'],
                'video_id': item['id']['videoId'],
                'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                'channelTitle': item['snippet']['channelTitle']
            })

#   Return video data
        return videos
    
    def video_details(self, video_ids):
        detailed_videos = []

        try:
            request = self.youtube.videos().list(
                part='statistics,contentDetails',
                id=",".join(video_ids) 
            )
            response = request.execute()

            for item in response.get('items', []):
                view_count = item['statistics'].get('viewCount', 0)
                duration = parse_duration(item['contentDetails'].get('duration')).total_seconds()

                detailed_videos.append({
                    'video_id': item['id'],
                    'view_count': view_count,
                    'duration_seconds': duration
                })

        except Exception as e:
            print(f"Error fetching video details for videos {video_ids}: {e}")
            return []

        return detailed_videos

class YouTubeFilter: 
    def __init__(self, videos, details, min_duration = 120):
        self.videos = videos
        self.details = details
        self.min_duration = min_duration

    def apply_filters(self):
        filtered = []

        details_map = {d['video_id']: d for d in self.details}

        for video in self.videos:
            detail =  details_map.get(video['video_id'])
            if not detail:
                continue

            if detail['duration_seconds'] >= self.min_duration:
                filtered.append({**video, **detail})

        return filtered

def get_filtered_videos():
        youtube = YouTubeSearch(query="vex robotics", max_results=50, days_back=30)
        videos = youtube.search_videos()

        if not videos:
            return []
            
        video_ids = [v['video_id'] for v in videos]
        details = youtube.video_details(video_ids)

        if not details:
            return []
            
        filterer = YouTubeFilter(videos, details, min_duration=120)

        return filterer.apply_filters()