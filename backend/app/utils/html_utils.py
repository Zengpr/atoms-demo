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
    html_start = text.find("<!DOCTYPE")
    if html_start == -1:
        html_start = text.find("<html")
    if html_start != -1:
        return text[html_start:].strip()
    return text.strip()
