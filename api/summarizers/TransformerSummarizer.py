from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, BartForConditionalGeneration
import re

class TransformerSummarizer:
	def __init__(self) -> None:
		self.tokenizer = AutoTokenizer.from_pretrained('./models/lexsum_model')
		self.model = AutoModelForSeq2SeqLM.from_pretrained('./models/lexsum_model')
  
  
	def summarize(self, text: str) -> str:
		text = self.clean_text(text)
		inputs = self.tokenizer.encode(text, return_tensors="pt", max_length=1024, truncation=True)
		summary_ids = self.model.generate(inputs, max_length=256, length_penalty=2.0, num_beams=4, early_stopping=True)
		summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
		return summary

	def clean_text(self, text: str) -> str:
		new_text = re.sub(r"\b(?:https?://)?(?:www\.)?\S+\.com\b", "", text)
		new_text = re.sub(r"[\n\t]", "", new_text)
		new_text = re.sub(r"[^a-zA-z0-9]", "", new_text)
		return new_text