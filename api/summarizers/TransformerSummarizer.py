from transformers import BartTokenizer, TFBartForConditionalGeneration


class TransformerSummarizer:
	def __init__(self) -> None:
		self.tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn', cache_dir='../models/')
		self.model = TFBartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn', cache_dir='../models/')
  
	def summarize(self, text: str, length: int) -> str:
		inputs = self.tokenizer.encode("summarize: " + text, return_tensors="tf", max_length=1024, truncation=True)
		summary_ids = self.model.generate(inputs, max_length=length, length_penalty=2.0, num_beams=4, early_stopping=True)
		summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
		return summary