import re


class EntityExtractor:

    def extract(self, text):

        entities = {}

        # tooth number detection
        tooth_match = re.findall(r"#?\d{1,2}", text)
        if tooth_match:
            entities["tooth_numbers"] = tooth_match

        # symptoms
        if "pain" in text.lower():
            entities["symptom"] = "pain"
        
        

        return entities