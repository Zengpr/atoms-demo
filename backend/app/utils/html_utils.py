import re


def extract_html(text: str) -> str:
    fence_match = re.search(r"```html\s*\n(.*?)```", text, re.DOTALL)
    if fence_match:
        return _ensure_complete(fence_match.group(1).strip())
    fence_match = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
    if fence_match:
        content = fence_match.group(1).strip()
        if content.lower().startswith("<!doctype") or content.lower().startswith("<html"):
            return _ensure_complete(content)
    if text.strip().lower().startswith("<!doctype") or text.strip().lower().startswith("<html"):
        return _ensure_complete(text.strip())
    for marker in ["<!DOCTYPE", "<!doctype", "<html", "<HTML"]:
        idx = text.find(marker)
        if idx != -1:
            return _ensure_complete(text[idx:].strip())
    return ""


def _ensure_complete(code: str) -> str:
    if not code:
        return code
    if "</html>" not in code.lower():
        if "</body>" not in code.lower():
            code += "\n</body>"
        code += "\n</html>"
    if "</script>" not in code.lower() and "<script" in code.lower():
        last_script = code.lower().rfind("<script")
        if code.lower().find("</script>", last_script) == -1:
            code += "\n</script>"
            if "</body>" not in code.lower():
                code += "\n</body>"
            if "</html>" not in code.lower():
                code += "\n</html>"
    return code
