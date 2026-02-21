from pathlib import Path
import time
import torch
from PIL import Image
from transformers import DonutProcessor, VisionEncoderDecoderModel


MODEL_NAME = "naver-clova-ix/donut-base-finetuned-cord-v2"

PROMPT = "<s_cord-v2>"

class DonutOCR:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.processor = DonutProcessor.from_pretrained(MODEL_NAME)
        self.model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME)
        self.model.to(self.device)

    @torch.no_grad()
    def run(self, image_path):
        image = Image.open(image_path).convert("RGB")

        pixel_values = self.processor(image, return_tensors="pt").pixel_values.to(self.device)

        decoder_input_ids = self.processor.tokenizer(
            PROMPT,
            add_special_tokens=False,
            return_tensors="pt"
        ).input_ids.to(self.device)

        start = time.time()

        outputs = self.model.generate(
            pixel_values,
            decoder_input_ids=decoder_input_ids,
            max_length=768,
        )

        elapsed = time.time() - start

        seq = self.processor.batch_decode(outputs)[0]
        parsed = self.processor.token2json(seq)

        return {
            "time": elapsed,
            "parsed": parsed,
        }
