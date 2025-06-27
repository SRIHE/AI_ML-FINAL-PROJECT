from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import pandas as pd

class MentalHealthChatBot:
    def __init__(self):
        # Load DialoGPT model
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
        self.chat_history_ids = None  # Keeps conversation memory

        # Load offensive words
        try:
            df = pd.read_csv("offensive_words.csv")
            self.offensive_words = df["offensive_term"].str.lower().tolist()
        except Exception:
            self.offensive_words = []

        # Load keyword-based responses
        try:
            df = pd.read_csv("keyword_responses.csv")
            df = df.dropna(subset=["keyword", "response", "helpline"])
            df["keyword"] = df["keyword"].str.lower().str.strip()
            df = df.drop_duplicates(subset="keyword")
            self.responses = {
                row["keyword"]: {
                    "response": row["response"],
                    "helpline": row["helpline"]
                }
                for _, row in df.iterrows()
            }
        except Exception:
            self.responses = {}

        # Emotion detection model
        self.emotion_classifier = pipeline(
            "text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion"
        )

    def get_response(self, text):
        text = text.lower()
        for keyword, info in self.responses.items():
            if keyword in text:
                return f"{info['response']}\n\n📞 Helpline: {info['helpline']}"
        return None

    def generate_response(self, user_input):
        # Check if a keyword match exists
        custom_reply = self.get_response(user_input)
        if custom_reply:
            return custom_reply

        # Encode new user input
        new_input_ids = self.tokenizer.encode(user_input + self.tokenizer.eos_token, return_tensors="pt")

        # Maintain chat memory
        if self.chat_history_ids is not None:
            bot_input_ids = torch.cat([self.chat_history_ids, new_input_ids], dim=-1)
        else:
            bot_input_ids = new_input_ids

        # Generate response using history + new input
        self.chat_history_ids = self.model.generate(
            bot_input_ids,
            max_length=1000,
            pad_token_id=self.tokenizer.eos_token_id,
            no_repeat_ngram_size=3,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.9
        )

        response = self.tokenizer.decode(
            self.chat_history_ids[:, bot_input_ids.shape[-1]:][0],
            skip_special_tokens=True
        )
        return response

    def reset_conversation(self):
        self.chat_history_ids = None
