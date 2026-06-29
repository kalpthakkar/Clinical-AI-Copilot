import requests


class LLMSummarizer:

    def __init__(self, model="llama3.1:latest"):
        self.url = "http://localhost:11434/api/generate"
        self.model = model

    def summarize(self, text):

        prompt = f"""
        Summarize the following dental patient statement in clinical style:

        "{text}"

        Output concise professional summary.
        """

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"].strip()