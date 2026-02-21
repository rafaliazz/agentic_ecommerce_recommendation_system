from pathlib import Path
import time
import torch
from PIL import Image
import easyocr
import cv2
import numpy as np


class EasyOCR:
    def __init__(self, languages=None):
        """
        languages: list of language codes
        Example: ['en'] or ['en', 'id']
        """
        if languages is None:
            languages = ["en"]

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        use_gpu = self.device == "cuda"

        self.reader = easyocr.Reader(
            languages,
            gpu=use_gpu
        )

    def run(self, image_path):
        """
        Full OCR run (no filtering)
        """
        image_path = Path(image_path)
        start = time.time()

        results = self.reader.readtext(str(image_path), detail=1)

        elapsed = time.time() - start

        lines = []
        raw_blocks = []

        for bbox, text, confidence in results:
            lines.append(text)
            raw_blocks.append({
                "text": text,
                "confidence": float(confidence),
                "bbox": bbox
            })

        return {
            "time": elapsed,
            "text": "\n".join(lines),
            "lines": lines,
            "blocks": raw_blocks
        }

    # ---------------------------------------------------------
    # DESKTOP (PC) FILTERING
    # ---------------------------------------------------------
    def get_relevant_boxes_pc(self, image_path, conf_threshold=0.5):
        """
        Filters relevant OCR blocks for desktop ecommerce layout.
        """

        image = cv2.imread(str(image_path))
        h, w, _ = image.shape

        results = self.reader.readtext(str(image_path), detail=1)

        relevant = []

        for bbox, text, conf in results:
            if conf < conf_threshold:
                continue

            (tl, tr, br, bl) = bbox
            x_center = (tl[0] + br[0]) / 2
            y_center = (tl[1] + br[1]) / 2
            box_height = abs(bl[1] - tl[1])

            # ---- PC FILTER RULES ----
            # Ignore left product image panel
            if x_center < w * 0.45:
                continue

            # Ignore navbar
            if y_center < h * 0.15:
                continue

            # Ignore tiny UI text
            if box_height < 15:
                continue

            relevant.append({
                "text": text,
                "confidence": float(conf),
                "bbox": bbox
            })

        return relevant

    # ---------------------------------------------------------
    # MOBILE FILTERING
    # ---------------------------------------------------------
    def get_relevant_boxes_mobile(self, image_path, conf_threshold=0.5):
        """
        Filters relevant OCR blocks for mobile ecommerce layout.
        """

        image = cv2.imread(str(image_path))
        h, w, _ = image.shape

        results = self.reader.readtext(str(image_path), detail=1)

        relevant = []

        for bbox, text, conf in results:
            if conf < conf_threshold:
                continue

            (tl, tr, br, bl) = bbox
            x_center = (tl[0] + br[0]) / 2
            y_center = (tl[1] + br[1]) / 2
            box_height = abs(bl[1] - tl[1])

            # ---- MOBILE FILTER RULES ----

            # Ignore status/store header
            if y_center < h * 0.18:
                continue

            # Ignore bottom navigation buttons
            if y_center > h * 0.92:
                continue

            # Ignore tiny text
            if box_height < 18:
                continue

            relevant.append({
                "text": text,
                "confidence": float(conf),
                "bbox": bbox
            })
        return relevant
