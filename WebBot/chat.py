import os
from dotenv import load_dotenv
import json
from openai import OpenAI
from summarizer import text_summarizer

load_dotenv()
client = OpenAI(api_key=(os.getenv("OPENAI_API_KEY")))

class ChatGPTMini:
    def __init__(self, transcript):
        self.transcript = [transcript]

    def gpt(self):
        for transcript in self.transcript:
            try:
                text = (" ".join(entry['text'] for entry in transcript))
                
                prompt = (
                    "Summarize the following YouTube video transcripts. This means give the main idea of the video in 3 sentences(beginning, middle, end) or less."
                    "If a video mentions jargon like free_floating intake explain it."
                    "If video is not related to Vex Robotics Compeitions, return 'Null' in summary:"
                    "Assign one of these Discord tags: @general, @strategy, @mechanical, @electrical, @programming, @informational, @tutorial. \n\n"
                    "\"summary\":\"...\", \"tag\": \"@...\"}\n\n"
                    f"Transcript:\n{text_summarizer(text, num_sentences=8)}")

                response = client.chat.completions.create(
                    model='gpt-4o',
                    messages = [
                        {"role": "system", "content": "You're a helpful scout assistant who found a really good video and want to share it with the team. Summarize the video concisely."},
                        {"role": "user", "content": f"{prompt}\nRespond only in JSON."}],
                    temperature=0.5,
                    max_tokens=500,
                    response_format={'type': 'json_object'})

                raw_content = response.choices[0].message.content.strip()

                if raw_content.startswith("```json"):
                    raw_content = raw_content[len("```json"):].strip()
                if raw_content.endswith("```"):
                    raw_content = raw_content[:-3].strip()

                parsed = json.loads(raw_content)
                summary = parsed.get("summary")
                tag = parsed.get("tag")

            except json.JSONDecodeError:
                return None

        return summary, tag

            


            
        
        

