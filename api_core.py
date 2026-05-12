import json
import os
from simple_ocr import SimpleOCR
from numeric_pinyin_ai import NumericPinyinAI
from lite_marker import LiteMarker

class ApiCore:
    def __init__(self):
        self.ocr = SimpleOCR()
        self.ai = NumericPinyinAI()
        self.marker = LiteMarker()
        self.logs = []

    def log_action(self, action, data):
        entry = {"action": action, "data": str(data)[:100]}
        self.logs.append(entry)
        return entry

    def health_check(self):
        return {"status": "ok", "components": ["OCR", "AI", "Marker"]}

    def ocr_process(self, data):
        self.log_action("ocr_process", data)
        return self.ocr.process(data)

    def ai_learn(self, input_text, output_pattern):
        self.log_action("ai_learn", {"in": input_text, "out": output_pattern})
        return {"success": self.ai.learn(input_text, output_pattern)}

    def ai_recognize(self, input_text):
        self.log_action("ai_recognize", input_text)
        result = self.ai.recognize(input_text)
        return {"result": result}

    def ai_add_memory(self, concept, details):
        self.log_action("ai_add_memory", concept)
        self.ai.add_memory(concept, details)
        return {"success": True}

    def marker_process(self, content):
        self.log_action("marker_process", type(content))
        return {"markdown": self.marker.process_document(content)}

    def export_data(self):
        return {
            "logs": self.logs[-50:],
            "ai_memory": self.ai.memory
        }
