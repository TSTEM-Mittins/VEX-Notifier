import os
import openai
from dotenv import load_dotenv
import requests
import json
from openai import OpenAI

load_dotenv()
client = OpenAI()
print("Using OpenAI client (key loaded from .env)")

class ChatGPTMini:
    def __init__(self, model='gpt-4o', temperature=0.5, max_tokens=1000):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def ask(self, video):

        try:
            transcript_text = "\n".join([
    f"{entry['start']:.2f}s: {entry['text']}" for entry in video['transcript']
])

            prompt = (
                "Summarize the following YouTube video transcripts. "
                "Assign one of these Discord tags: #general, #strategy, #mechanical, #electrical. \n\n"
                "Output format (JSON): {\"summary\":\"...\", \"tag\": \"#...\"}\n\n"
                f"Transcript:\n{transcript_text}"
            )

            print(f"[Prompt Preview for {video['video_id']}]: {prompt[:300]}...")

            response = client.chat.completions.create(
                model=self.model,
                messages = [
                    {"role": "system", "content": "You're a helpful scout assistant who found a really good video and want to share it with the team. Summarize the video concisely."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            raw_content = response.choices[0].message.content.strip()
            print(f"[GPT Output for {video['video_id']}]: {raw_content}")

            if raw_content.startswith("```json"):
                raw_content = raw_content[len("```json"):].strip()
            if raw_content.endswith("```"):
                raw_content = raw_content[:-3].strip()


            return json.loads(raw_content)
        
        except json.JSONDecodeError as je:
            print(f"[JSON Error for {video['video_id']}]: {je}")
            print("Raw response content:", raw_content)
            return None
        except Exception as e:
            print(f"[OpenAI Error for {video['video_id']}]: {e}")
            return None


class DiscordWebhook:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_message(self, message):
        try: 
            response = requests.post(self.webhook_url, json={"content": message})
            response.raise_for_status()
            print(f"Message sent to Discord")
        except requests.exceptions.RequestException as e:
            print(f"Discord did not receive: {e}")

def main():
    from api_transcription import fetch_and_transcribe

    results = fetch_and_transcribe()
    gpt = ChatGPTMini(model='gpt-4o')

    for video_id, video in results.items():
        if not video or 'transcript' not in video:
            print(f"Transcript not found or empty for video {video_id}... skipping")
            continue 

        if not video['transcript']:
            print(f"[Empty transcript for video {video_id}]")
            continue
            
        summary_info = gpt.ask(video)
        if not summary_info:
            print(f"ChatGPT Mini returned nothing for {video_id}... skipping")
            continue

        summary = summary_info.get("summary")
        tag = summary_info.get("tag")

        if not tag or not summary:
            print(f"No valid summary or tag returned for video {video_id}... skipping")
            continue

        env_var_key = f"WEBHOOK_{tag.strip('#').upper()}"
        webhook_url = os.getenv(env_var_key)

        if not webhook_url:
            print(f"NO webhook URL for tag {tag}... Skipping video {video_id}.")
            continue

        discord = DiscordWebhook(webhook_url)

        message = (
            f"🎥 **New VEX Video Found!**\n"
            f"**Title**: {video['title']}\n"
            f"📺 Watch it here: {video['url']}\n"
            # f"📡 from: {video['channelTitle']}\n"
            f"{tag}\n\n"
            f"📜 Summary: \n{summary}" 
        )
        discord.send_message(message)

if __name__ == "__main__":
    main()