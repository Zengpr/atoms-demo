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
    script_start = code.lower().find("<script")
    after = code[script_start:]
    script_close_pos = after.lower().find("</script>")
    if script_close_pos < 0:
        return True
    script_body = after[:script_close_pos]
    before_script = code[:script_start]
    all_text = before_script + script_body
    open_b = all_text.count("{")
    close_b = all_text.count("}")
    open_br = all_text.count("[")
    close_br = all_text.count("]")
    open_p = all_text.count("(")
    close_p = all_text.count(")")
    imbalance = (open_b - close_b) + (open_br - close_br) + (open_p - close_p)
    if imbalance > 3:
        return True
    last_meaningful = script_body.rstrip()
    if last_meaningful and not last_meaningful.endswith(("}", "]", ")", ";", "'", '"', "`", "//", "*/")):
        return True
    return False
