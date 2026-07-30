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


def is_js_truncated(code: str) -> bool:
    if not code or "<script" not in code.lower():
        return False
    lower = code.lower()
    last_script_open = lower.rfind("<script")
    if last_script_open < 0:
        return False
    after_last_open = code[last_script_open:]
    has_close = "</script>" in after_last_open.lower()
    if not has_close:
        return True
    all_script_texts = []
    pos = 0
    lower_code = code.lower()
    while True:
        open_idx = lower_code.find("<script", pos)
        if open_idx < 0:
            break
        src_check = code[open_idx:open_idx + 8]
        close_idx = lower_code.find("</script>", open_idx)
        if close_idx < 0:
            body = code[open_idx:]
            all_script_texts.append(body)
            break
        else:
            body = code[open_idx:close_idx]
            all_script_texts.append(body)
            pos = close_idx + 9
    combined = " ".join(all_script_texts)
    open_b = combined.count("{")
    close_b = combined.count("}")
    open_br = combined.count("[")
    close_br = combined.count("]")
    open_p = combined.count("(")
    close_p = combined.count(")")
    imbalance = (open_b - close_b) + (open_br - close_br) + (open_p - close_p)
    if imbalance > 3:
        return True
    if not code.rstrip().endswith(("</script>", "</html>", "</body>")):
        last_tag = code.rstrip()[-50:].lower().strip()
        if not last_tag.endswith(("</script>", "</html>", "</body>")):
            return True
    return False
