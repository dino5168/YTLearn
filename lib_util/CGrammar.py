# grammar.py
import language_tool_python


class GrammarChecker:
    def __init__(self, language="en-US"):
        self.tool = language_tool_python.LanguageTool(language)

    def check(self, text: str):
        matches = self.tool.check(text)
        corrected_text = language_tool_python.utils.correct(text, matches)

        errors = []
        for match in matches:
            errors.append(
                {
                    "message": match.message,
                    "suggestions": match.replacements,
                    "error_text": text[match.offset : match.offset + match.errorLength],
                    "start": match.offset,
                    "end": match.offset + match.errorLength,
                }
            )

        return {"original": text, "corrected": corrected_text, "errors": errors}
