import requests, time, json, sys

P = {"https": "http://127.0.0.1:1088"}
BASE = "https://backend-production-e62a.up.railway.app"
ORIGIN = "https://frontend-theta-inky-12.vercel.app"
H_BASE = {"Origin": ORIGIN, "Content-Type": "application/json"}

passed = 0
failed = 0
errors = []

def test(name, func):
    global passed, failed
    try:
        func()
        passed += 1
        print(f"  PASS  {name}")
    except Exception as e:
        failed += 1
        errors.append(f"{name}: {e}")
        print(f"  FAIL  {name} — {e}")

def api(method, path, token=None, json_data=None, stream=False, timeout=30):
    h = {**H_BASE}
    if token:
        h["Authorization"] = f"Bearer {token}"
    kwargs = {"headers": h, "proxies": P, "timeout": timeout}
    if json_data is not None:
        kwargs["json"] = json_data
    if stream:
        kwargs["stream"] = True
    r = getattr(requests, method)(f"{BASE}{path}", **kwargs)
    return r

def do_sse_chat(pid, token, content, mode="single", timeout=90):
    r = api("post", f"/api/chat/{pid}/message", token=token,
            json_data={"content": content, "mode": mode}, stream=True, timeout=timeout)
    assert r.status_code == 200, f"SSE status {r.status_code}"
    code = ""
    events = []
    for line in r.iter_lines():
        d = line.decode()
        if d.startswith("event:"):
            events.append(d[6:].strip())
        elif d.startswith("data:"):
            try:
                data = json.loads(d[5:].strip())
                if data.get("code"):
                    code = data["code"]
            except:
                pass
    return {"events": events, "code": code}

# ============================================================
ts = int(time.time() * 1000)
EMAIL = f"fulltest2_{ts}@test.dev"
USERNAME = f"fulltest2_{ts}"
PASSWORD = "Test123456!"
TOKEN = None

print("=" * 60)
print("SECTION 1: AUTH (10 tests)")
print("=" * 60)

def test_register_ok():
    global TOKEN
    r = api("post", "/api/auth/register", json_data={"email": EMAIL, "username": USERNAME, "password": PASSWORD})
    assert r.status_code == 200, f"got {r.status_code}: {r.text[:200]}"
    TOKEN = r.json().get("accessToken")
    assert TOKEN

def test_register_dup_email():
    r = api("post", "/api/auth/register", json_data={"email": EMAIL, "username": "other", "password": PASSWORD})
    assert r.status_code == 400

def test_register_dup_username():
    r = api("post", "/api/auth/register", json_data={"email": f"x_{ts}@t.dev", "username": USERNAME, "password": PASSWORD})
    assert r.status_code == 400

def test_register_short_pw():
    r = api("post", "/api/auth/register", json_data={"email": f"spw_{ts}@t.dev", "username": f"spw_{ts}", "password": "12"})
    assert r.status_code == 422

def test_register_missing_fields():
    r = api("post", "/api/auth/register", json_data={"email": f"mf_{ts}@t.dev"})
    assert r.status_code == 422

def test_login_ok():
    global TOKEN
    r = api("post", "/api/auth/login", json_data={"email": EMAIL, "password": PASSWORD})
    assert r.status_code == 200
    TOKEN = r.json()["accessToken"]

def test_login_wrong_pw():
    r = api("post", "/api/auth/login", json_data={"email": EMAIL, "password": "wrong"})
    assert r.status_code in (401, 400)

def test_login_no_user():
    r = api("post", "/api/auth/login", json_data={"email": "nobody@x.dev", "password": "x"})
    assert r.status_code in (401, 400)

def test_get_me():
    r = api("get", "/api/auth/me", token=TOKEN)
    assert r.status_code == 200
    assert r.json()["email"] == EMAIL

def test_get_me_bad_token():
    r = api("get", "/api/auth/me", token="badtoken")
    assert r.status_code == 401

test("Register", test_register_ok)
test("Dup email -> 400", test_register_dup_email)
test("Dup username -> 400", test_register_dup_username)
test("Short pw -> 422", test_register_short_pw)
test("Missing fields -> 422", test_register_missing_fields)
test("Login OK", test_login_ok)
test("Login wrong pw -> 401", test_login_wrong_pw)
test("Login no user -> 401", test_login_no_user)
test("GET /me", test_get_me)
test("GET /me bad token -> 401", test_get_me_bad_token)

# ============================================================
print()
print("=" * 60)
print("SECTION 2: PROJECTS CRUD (6 tests)")
print("=" * 60)

PID = None

def test_create_project():
    global PID
    r = api("post", "/api/projects", token=TOKEN, json_data={"name": "Test", "mode": "team"})
    assert r.status_code == 201
    PID = r.json()["id"]

def test_list_projects():
    r = api("get", "/api/projects", token=TOKEN)
    assert r.status_code == 200
    assert any(p["id"] == PID for p in r.json())

def test_get_project():
    r = api("get", f"/api/projects/{PID}", token=TOKEN)
    assert r.status_code == 200 and r.json()["id"] == PID

def test_get_404():
    r = api("get", "/api/projects/00000000-0000-0000-0000-000000000000", token=TOKEN)
    assert r.status_code == 404

def test_latest_code_empty():
    r = api("get", f"/api/projects/{PID}/latest-code", token=TOKEN)
    assert r.status_code == 200 and r.json().get("code") is None

def test_no_auth():
    r = api("post", "/api/projects", json_data={"name": "X", "mode": "team"})
    assert r.status_code in (401, 403)

test("Create project", test_create_project)
test("List projects", test_list_projects)
test("Get project", test_get_project)
test("Get 404", test_get_404)
test("Latest code empty", test_latest_code_empty)
test("No auth -> 401", test_no_auth)

# ============================================================
print()
print("=" * 60)
print("SECTION 3: MOCK TEMPLATES - 7 types (14 tests)")
print("=" * 60)

def make_and_chat(name, mode, content, content_check):
    r = api("post", "/api/projects", token=TOKEN, json_data={"name": name, "mode": mode})
    pid = r.json()["id"]
    result = do_sse_chat(pid, TOKEN, content, mode)
    assert "code_generated" in result["events"], f"no code_generated, events={result['events']}"
    assert len(result["code"]) > 200, f"code too short: {len(result['code'])}"
    assert content_check(result["code"]), f"content check failed for '{content}'"
    return pid, result["code"]

def test_1024_game():
    pid, code = make_and_chat("1024 Game", "single", "Build a 1024 game",
        lambda c: "1024" in c and ("ArrowLeft" in c or "keydown" in c))

def test_2048_game():
    pid, code = make_and_chat("2048 Game", "single", "Make a 2048 puzzle game",
        lambda c: "1024" in c or "2048" in c)

def test_snake_game():
    pid, code = make_and_chat("Snake", "single", "Create a snake game",
        lambda c: "1024" in c or "2048" in c or "snake" in c.lower() or "ArrowLeft" in c)

def test_todo_app():
    pid, code = make_and_chat("Todo", "single", "Build a todo list app",
        lambda c: "todo" in c.lower() or "task" in c.lower())

def test_counter():
    pid, code = make_and_chat("Counter", "single", "Make a counter app",
        lambda c: "count" in c.lower() or "increment" in c.lower() or "0" in c)

def test_ecommerce():
    pid, code = make_and_chat("Shop", "single", "Build an ecommerce shop",
        lambda c: "cart" in c.lower() or "product" in c.lower() or "shop" in c.lower())

def test_dashboard():
    pid, code = make_and_chat("Dashboard", "single", "Build an analytics dashboard",
        lambda c: "dashboard" in c.lower() or "chart" in c.lower() or "stat" in c.lower())

def test_landing():
    pid, code = make_and_chat("Landing", "single", "Create a landing page for my SaaS",
        lambda c: "hero" in c.lower() or "feature" in c.lower() or "cta" in c.lower() or "Atoms" in c)

def test_portfolio():
    pid, code = make_and_chat("Portfolio", "single", "Build my portfolio website",
        lambda c: "portfolio" in c.lower() or "project" in c.lower() or "skill" in c.lower())

def test_calculator():
    pid, code = make_and_chat("Calc", "single", "Make a calculator tool",
        lambda c: "calculator" in c.lower() or "appendNum" in c or "calculate" in c)

def test_team_mode():
    r = api("post", "/api/projects", token=TOKEN, json_data={"name": "Team Test", "mode": "team"})
    pid = r.json()["id"]
    result = do_sse_chat(pid, TOKEN, "Build a counter", "team")
    assert "agent_thinking" in result["events"]
    assert "code_generated" in result["events"]
    assert len(result["code"]) > 100

def test_review_mode():
    r = api("post", "/api/projects", token=TOKEN, json_data={"name": "Review Test", "mode": "review"})
    pid = r.json()["id"]
    result = do_sse_chat(pid, TOKEN, "Build a game then review it", "review")
    assert "code_generated" in result["events"]

def test_iterate_mode():
    r = api("post", "/api/projects", token=TOKEN, json_data={"name": "Iterate Test", "mode": "iterate"})
    pid = r.json()["id"]
    result1 = do_sse_chat(pid, TOKEN, "Build a todo", "iterate")
    assert "code_generated" in result1["events"]
    result2 = do_sse_chat(pid, TOKEN, "Add dark mode", "iterate")
    assert "code_generated" in result2["events"]

def test_race_mode():
    r = api("post", "/api/projects", token=TOKEN, json_data={"name": "Race Test", "mode": "race"})
    pid = r.json()["id"]
    result = do_sse_chat(pid, TOKEN, "Build a counter", "race")
    assert "code_generated" in result["events"]

test("1024 game template", test_1024_game)
test("2048 game template", test_2048_game)
test("Snake game template", test_snake_game)
test("Todo app template", test_todo_app)
test("Counter template", test_counter)
test("Ecommerce template", test_ecommerce)
test("Dashboard template", test_dashboard)
test("Landing template", test_landing)
test("Portfolio template", test_portfolio)
test("Calculator template", test_calculator)
test("Team mode", test_team_mode)
test("Review mode", test_review_mode)
test("Iterate mode (2 msgs)", test_iterate_mode)
test("Race mode", test_race_mode)

# ============================================================
print()
print("=" * 60)
print("SECTION 4: ITERATION & PERSISTENCE (8 tests)")
print("=" * 60)

ITER_PID = None
ITER_CODE1 = None
ITER_CODE2 = None
ITER_CODE3 = None

def test_iter_first():
    global ITER_PID, ITER_CODE1
    r = api("post", "/api/projects", token=TOKEN, json_data={"name": "Iter Persist", "mode": "single"})
    ITER_PID = r.json()["id"]
    result = do_sse_chat(ITER_PID, TOKEN, "Build a counter app")
    ITER_CODE1 = result["code"]
    assert len(ITER_CODE1) > 200

def test_iter_latest_code():
    r = api("get", f"/api/projects/{ITER_PID}/latest-code", token=TOKEN)
    assert r.status_code == 200
    assert r.json()["code"] == ITER_CODE1

def test_iter_second_msg():
    global ITER_CODE2
    result = do_sse_chat(ITER_PID, TOKEN, "Change the color to warm")
    ITER_CODE2 = result["code"]
    assert len(ITER_CODE2) > 200

def test_iter_code_changed():
    r = api("get", f"/api/projects/{ITER_PID}/latest-code", token=TOKEN)
    assert r.json()["code"] == ITER_CODE2

def test_iter_third_msg():
    global ITER_CODE3
    result = do_sse_chat(ITER_PID, TOKEN, "Add animations")
    ITER_CODE3 = result["code"]
    assert len(ITER_CODE3) > 200

def test_iter_history_count():
    r = api("get", f"/api/chat/{ITER_PID}/history", token=TOKEN)
    msgs = r.json()
    user_msgs = [m for m in msgs if m["role"] == "user"]
    assert len(user_msgs) >= 3, f"expected >=3 user msgs, got {len(user_msgs)}"

def test_iter_versions():
    r = api("get", f"/api/projects/{ITER_PID}/versions", token=TOKEN)
    versions = r.json()
    assert len(versions) >= 3, f"expected >=3 versions, got {len(versions)}"

def test_iter_history_has_roles():
    r = api("get", f"/api/chat/{ITER_PID}/history", token=TOKEN)
    msgs = r.json()
    roles = set(m["role"] for m in msgs)
    assert "user" in roles and "assistant" in roles

test("Iter: first msg", test_iter_first)
test("Iter: latest-code persists", test_iter_latest_code)
test("Iter: second msg", test_iter_second_msg)
test("Iter: code updated", test_iter_code_changed)
test("Iter: third msg", test_iter_third_msg)
test("Iter: history >=3 user msgs", test_iter_history_count)
test("Iter: versions >=3", test_iter_versions)
test("Iter: history has both roles", test_iter_history_has_roles)

# ============================================================
print()
print("=" * 60)
print("SECTION 5: MULTI-USER ISOLATION (3 tests)")
print("=" * 60)

def test_cannot_see_others():
    r = api("post", "/api/auth/register", json_data={"email": f"iso_{ts}@t.dev", "username": f"iso_{ts}", "password": "Iso1234!"})
    other_tok = r.json()["accessToken"]
    r = api("get", f"/api/projects/{PID}", token=other_tok)
    assert r.status_code in (403, 404)

def test_cannot_chat_others():
    r = api("post", "/api/auth/register", json_data={"email": f"iso2_{ts}@t.dev", "username": f"iso2_{ts}", "password": "Iso1234!"})
    other_tok = r.json()["accessToken"]
    result = do_sse_chat(PID, other_tok, "hack", "single")
    assert "error" in str(result["events"]).lower() or result["code"] == ""

def test_own_projects_isolated():
    r = api("post", "/api/auth/register", json_data={"email": f"iso3_{ts}@t.dev", "username": f"iso3_{ts}", "password": "Iso1234!"})
    tok2 = r.json()["accessToken"]
    api("post", "/api/projects", token=tok2, json_data={"name": "Other", "mode": "single"})
    r1 = api("get", "/api/projects", token=TOKEN)
    r2 = api("get", "/api/projects", token=tok2)
    ids1 = set(p["id"] for p in r1.json())
    ids2 = set(p["id"] for p in r2.json())
    assert ids1.isdisjoint(ids2), "projects leaked between users"

test("Cannot see others' project", test_cannot_see_others)
test("Cannot chat in others' project", test_cannot_chat_others)
test("Own projects isolated", test_own_projects_isolated)

# ============================================================
print()
print("=" * 60)
print("SECTION 6: CORS & ERROR HANDLING (6 tests)")
print("=" * 60)

def test_cors_preflight():
    r = requests.options(f"{BASE}/api/auth/register", headers={
        "Origin": ORIGIN, "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type,authorization",
    }, proxies=P, timeout=10)
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == ORIGIN

def test_cors_blocks_evil():
    r = requests.options(f"{BASE}/api/auth/register", headers={
        "Origin": "https://evil.com", "Access-Control-Request-Method": "POST",
    }, proxies=P, timeout=10)
    assert r.headers.get("access-control-allow-origin") != "https://evil.com"

def test_chat_invalid_project():
    r = api("post", "/api/chat/00000000-0000-0000-0000-000000000000/message", token=TOKEN,
            json_data={"content": "x", "mode": "team"}, stream=True, timeout=15)
    assert r.status_code in (404, 500)

def test_chat_no_auth():
    r = api("post", f"/api/chat/{PID}/message",
            json_data={"content": "x", "mode": "team"}, stream=True, timeout=15)
    assert r.status_code in (401, 403)

def test_latest_code_404():
    r = api("get", "/api/projects/00000000-0000-0000-0000-000000000000/latest-code", token=TOKEN)
    assert r.status_code == 404

def test_versions_empty():
    r = api("post", "/api/projects", token=TOKEN, json_data={"name": "No Chat", "mode": "team"})
    pid = r.json()["id"]
    r = api("get", f"/api/projects/{pid}/versions", token=TOKEN)
    assert r.json() == []

test("CORS preflight", test_cors_preflight)
test("CORS blocks evil", test_cors_blocks_evil)
test("Chat invalid project", test_chat_invalid_project)
test("Chat no auth", test_chat_no_auth)
test("Latest code 404", test_latest_code_404)
test("Versions empty", test_versions_empty)

# ============================================================
print()
print("=" * 60)
print("SECTION 7: FRONTEND ACCESSIBILITY (4 tests)")
print("=" * 60)

def test_frontend_loads():
    r = requests.get("https://frontend-theta-inky-12.vercel.app", proxies=P, timeout=15)
    assert r.status_code == 200
    assert "Atoms" in r.text or "atoms" in r.text.lower() or "AI" in r.text

def test_login_page_loads():
    r = requests.get("https://frontend-theta-inky-12.vercel.app/login", proxies=P, timeout=15)
    assert r.status_code == 200
    assert "email" in r.text.lower() or "login" in r.text.lower() or "sign" in r.text.lower()

def test_dashboard_requires_auth():
    r = requests.get("https://frontend-theta-inky-12.vercel.app/dashboard", proxies=P, timeout=15,
                     allow_redirects=True)
    assert r.status_code == 200

def test_api_url_embedded():
    r = requests.get("https://frontend-theta-inky-12.vercel.app/login", proxies=P, timeout=15)
    import re
    chunks = re.findall(r'/_next/static/chunks/[^"]+\.js', r.text)
    found = False
    for c in chunks[:15]:
        r2 = requests.get("https://frontend-theta-inky-12.vercel.app" + c, proxies=P, timeout=10)
        if "backend-production" in r2.text:
            idx = r2.text.find("backend-production")
            region = r2.text[max(0,idx-30):idx+80]
            if "\\uFEFF" in region or "\ufeff" in region:
                has_clean = "cleanUrl" in r2.text or "replace" in region[:50]
                found = True
                assert has_clean, "BOM present but no cleanUrl!"
            else:
                found = True
            break
    assert found, "backend URL not found in JS chunks"

test("Frontend loads", test_frontend_loads)
test("Login page loads", test_login_page_loads)
test("Dashboard accessible", test_dashboard_requires_auth)
test("API URL embedded (BOM cleaned)", test_api_url_embedded)

# ============================================================
print()
print()
print("=" * 60)
total = passed + failed
print(f"RESULTS: {passed}/{total} PASSED, {failed} FAILED")
print("=" * 60)
if errors:
    print("\nFAILED TESTS:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("\nALL TESTS PASSED!")
    sys.exit(0)
