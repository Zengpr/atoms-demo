import re


def extract_html(text: str) -> str:
    fence_match = re.search(r"```html\s*\n(.*?)```", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    fence_match = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
    if fence_match:
        content = fence_match.group(1).strip()
        if content.lower().startswith("<!doctype") or content.lower().startswith("<html"):
            return content
    if text.strip().lower().startswith("<!doctype") or text.strip().lower().startswith("<html"):
        return text.strip()
    for marker in ["<!DOCTYPE", "<!doctype", "<html", "<HTML"]:
        idx = text.find(marker)
        if idx != -1:
            return text[idx:].strip()
    return ""
