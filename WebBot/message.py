import os
from dotenv import load_dotenv
import requests
load_dotenv()

  # This file is for the discord webhook messages.

class WebHookMessage:
    def __init__(self, videos=None, tag=None, hashtag=None, summary=None):
        self.videos = videos
        self.tag = tag
        self.hashtag = hashtag
        self.summary = summary

    def short_videos(self):
        message = (
            f"🎥 **New VEX Video Found!**\n"
            f"**Title**: {self.videos['title']}\n"
            f"📺 Watch it here: {self.videos['url']}\n"
            f"📡 from: {self.videos['channelTitle']}\n"
            f"⌛ Video Duration: {self.videos['duration']}\n"
            f"👀 Views: {self.videos['view_count']}\n"
            f"@Shorts\n" 
        )
        webhook_url = os.getenv("WEBHOOK_SHORTS")
        response = requests.post(webhook_url, json={"content": message})
        response.raise_for_status()
    
    def long_videos(self):
        message = (
            f"🎥 **New VEX Video Found!**\n"
            f"**Title**: {self.videos['title']}\n"
            f"📺 Watch it here: {self.videos['url']}\n"
            f"📡 from: {self.videos['channelTitle']}\n"
            f"⌛ Video Duration: {self.videos['duration']}\n"
            f"👀 Views: {self.videos['view_count']}\n"
            f"@Vex_General\n"
            # f"{self.tag}\n" 
            # f"📜 Summary: \n{self.summary}"
        )
        webhook_url = os.getenv("WEBHOOK_GENERAL")
        response = requests.post(webhook_url, json={"content": message})
        response.raise_for_status()
  
      # Going to use this code in a later update.
        # self.webhook_url = os.getenv(f"WEBHOOK_{self.tag.strip('@').upper()}")
        # response = requests.post(self.webhook_url, json={"content": message})
        # response.raise_for_status()
    
    def stream_videos(self):
        message = (
            f"🎥 **New VEX Video Found!**\n"
            f"**Title**: {self.videos['title']}\n"
            f"📺 Watch it here: {self.videos['url']}\n"
            f"📡 from: {self.videos['channelTitle']}\n"
            f"⌛ Video Duration: {self.videos['duration']}\n"
            f"👀 Views: {self.videos['view_count']}\n"
            f"@Stream\n" 
        )
        self.webhook_url = os.getenv("WEBHOOK_STREAM")
        response = requests.post(self.webhook_url, json={"content": message})
        response.raise_for_status()
    
    def tiktok_videos(self):
        message = (
            f"🎥 **New VEX Video Found!**\n"
            f"**Title**: {self.videos['title']}\n"
            f"📺 Watch it here: {self.videos['url']}\n"
            f"📡 from: {self.videos['channelTitle']}\n"
            f"@TikTok\n" 
        )
        self.webhook_url = os.getenv("STREAM_VIDEOS")
        response = requests.post(self.webhook_url, json={"content": message})
        response.raise_for_status()

