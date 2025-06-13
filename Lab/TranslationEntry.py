class TranslationEntry:
    def __init__(self):
        self.translations = []  # 儲存所有 en/zh 對應組

    def add_entry(self, lang: str, text: str):
        # 每個 en 開頭代表新的一筆資料開始
        if lang == "en":
            self.translations.append({"en": text, "zh": None})
        elif lang == "zh":
            if self.translations:
                # 將 zh 填入最近一筆 en
                if self.translations[-1]["zh"] is None:
                    self.translations[-1]["zh"] = text
                else:
                    # 如果 zh 已存在，視為新對應
                    self.translations.append({"en": None, "zh": text})

    def __str__(self):
        return "\n".join(
            [f"EN: {entry['en']} → ZH: {entry['zh']}" for entry in self.translations]
        )
