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

def api(method, path, token=None, json_data=None, stream=False, timeout=15):
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

# ============================================================
print("=" * 60)
print("SECTION 1: AUTH")
print("=" * 60)

ts = int(time.time() * 1000)
EMAIL = f"fulltest_{ts}@test.dev"
USERNAME = f"fulltest_{ts}"
PASSWORD = "Test123456!"
TOKEN = None
USER_ID = None

def test_register_ok():
    global TOKEN, USER_ID
    r = api("post", "/api/auth/register", json_data={
        "email": EMAIL, "username": USERNAME, "password": PASSWORD
    })
    assert r.status_code == 200, f"got {r.status_code}: {r.text[:200]}"
    data = r.json()
    TOKEN = data.get("accessToken")
    assert TOKEN, "no accessToken"
    assert r.headers.get("access-control-allow-origin") == ORIGIN, "CORS missing"

def test_register_duplicate_email():
    r = api("post", "/api/auth/register", json_data={
        "email": EMAIL, "username": "other", "password": PASSWORD
    })
    assert r.status_code == 400, f"expected 400, got {r.status_code}"
    assert "already" in r.json().get("detail", "").lower() or "exists" in r.json().get("detail", "").lower(), "wrong error msg"

def test_register_duplicate_username():
    r = api("post", "/api/auth/register", json_data={
        "email": f"other_{ts}@test.dev", "username": USERNAME, "password": PASSWORD
    })
    assert r.status_code == 400, f"expected 400, got {r.status_code}"

def test_register_short_password():
    r = api("post", "/api/auth/register", json_data={
        "email": f"shortpw_{ts}@test.dev", "username": f"shortpw_{ts}", "password": "12"
    })
    assert r.status_code in (400, 422), f"expected 400/422, got {r.status_code}"

def test_register_missing_fields():
    r = api("post", "/api/auth/register", json_data={"email": f"nofields_{ts}@test.dev"})
    assert r.status_code == 422, f"expected 422, got {r.status_code}"

def test_login_ok():
    global TOKEN
    r = api("post", "/api/auth/login", json_data={"email": EMAIL, "password": PASSWORD})
    assert r.status_code == 200, f"got {r.status_code}: {r.text[:200]}"
    TOKEN = r.json().get("accessToken")
    assert TOKEN, "no accessToken"

def test_login_wrong_password():
    r = api("post", "/api/auth/login", json_data={"email": EMAIL, "password": "wrongpassword"})
    assert r.status_code in (401, 400), f"expected 401/400, got {r.status_code}"

def test_login_nonexistent_user():
    r = api("post", "/api/auth/login", json_data={"email": "nobody@nowhere.dev", "password": "whatever"})
    assert r.status_code in (401, 400), f"expected 401/400, got {r.status_code}"

def test_get_me():
    global USER_ID
    r = api("get", "/api/auth/me", token=TOKEN)
    assert r.status_code == 200, f"got {r.status_code}: {r.text[:200]}"
    data = r.json()
    assert data["email"] == EMAIL
    assert data["username"] == USERNAME
    USER_ID = data["id"]

def test_get_me_invalid_token():
    r = api("get", "/api/auth/me", token="invalidtoken12345")
    assert r.status_code == 401, f"expected 401, got {r.status_code}"

test("Register new user", test_register_ok)
test("Register duplicate email -> 400", test_register_duplicate_email)
test("Register duplicate username -> 400", test_register_duplicate_username)
test("Register short password -> 400/422", test_register_short_password)
test("Register missing fields -> 422", test_register_missing_fields)
test("Login with correct credentials", test_login_ok)
test("Login with wrong password -> 401", test_login_wrong_password)
test("Login nonexistent user -> 401", test_login_nonexistent_user)
test("GET /me with valid token", test_get_me)
test("GET /me with invalid token -> 401", test_get_me_invalid_token)

# ============================================================
print()
print("=" * 60)
print("SECTION 2: PROJECTS CRUD")
print("=" * 60)

PROJECT_ID = None

def test_create_project():
    global PROJECT_ID
    r = api("post", "/api/projects", token=TOKEN, json_data={
        "name": "Test Project Alpha", "mode": "team"
    })
    assert r.status_code == 201, f"got {r.status_code}: {r.text[:200]}"
    data = r.json()
    PROJECT_ID = data["id"]
    assert data["name"] == "Test Project Alpha"
    assert data["mode"] == "team"

def test_create_project_no_auth():
    r = api("post", "/api/projects", json_data={"name": "No Auth", "mode": "single"})
    assert r.status_code in (401, 403), f"expected 401/403, got {r.status_code}"

def test_list_projects():
    r = api("get", "/api/projects", token=TOKEN)
    assert r.status_code == 200, f"got {r.status_code}"
    data = r.json()
    assert isinstance(data, list)
    assert any(p["id"] == PROJECT_ID for p in data), "project not in list"

def test_get_single_project():
    r = api("get", f"/api/projects/{PROJECT_ID}", token=TOKEN)
    assert r.status_code == 200, f"got {r.status_code}"
    assert r.json()["id"] == PROJECT_ID

def test_get_nonexistent_project():
    r = api("get", "/api/projects/00000000-0000-0000-0000-000000000000", token=TOKEN)
    assert r.status_code == 404, f"expected 404, got {r.status_code}"

def test_create_second_project():
    r = api("post", "/api/projects", token=TOKEN, json_data={
        "name": "Test Project Beta", "mode": "single"
    })
    assert r.status_code == 201, f"got {r.status_code}"
    r2 = api("get", "/api/projects", token=TOKEN)
    assert len(r2.json()) >= 2

def test_latest_code_empty():
    r = api("get", f"/api/projects/{PROJECT_ID}/latest-code", token=TOKEN)
    assert r.status_code == 200, f"got {r.status_code}"
    assert r.json().get("code") is None, "code should be None for new project"

def test_latest_code_nonexistent():
    r = api("get", "/api/projects/00000000-0000-0000-0000-000000000000/latest-code", token=TOKEN)
    assert r.status_code == 404, f"expected 404, got {r.status_code}"

test("Create project", test_create_project)
test("Create project without auth -> 401", test_create_project_no_auth)
test("List projects", test_list_projects)
test("Get single project", test_get_single_project)
test("Get nonexistent project -> 404", test_get_nonexistent_project)
test("Create second project", test_create_second_project)
test("Latest code (empty) -> null", test_latest_code_empty)
test("Latest code nonexistent project -> 404", test_latest_code_nonexistent)

# ============================================================
print()
print("=" * 60)
print("SECTION 3: CHAT / SSE")
print("=" * 60)

CHAT_PID = None

def test_sse_first_message():
    global CHAT_PID
    r = api("post", "/api/projects", token=TOKEN, json_data={
        "name": "Chat Test Project", "mode": "team"
    })
    CHAT_PID = r.json()["id"]

    r = api("post", f"/api/chat/{CHAT_PID}/message", token=TOKEN,
            json_data={"content": "Build a counter app", "mode": "team"}, stream=True, timeout=90)
    assert r.status_code == 200, f"got {r.status_code}"
    events = []
    has_thinking = False
    has_code = False
    has_complete = False
    for line in r.iter_lines():
        d = line.decode()
        if d.startswith("event:"):
            ev = d[6:].strip()
            events.append(ev)
            if ev == "agent_thinking":
                has_thinking = True
            if ev == "code_generated":
                has_code = True
            if ev == "message_complete":
                has_complete = True
    assert has_thinking, f"no agent_thinking event, events={events}"
    assert has_code, f"no code_generated event, events={events}"
    assert has_complete, f"no message_complete event, events={events}"

def test_latest_code_after_chat():
    r = api("get", f"/api/projects/{CHAT_PID}/latest-code", token=TOKEN)
    assert r.status_code == 200
    code = r.json().get("code", "")
    assert len(code) > 100, f"code too short: {len(code)} chars"

def test_chat_history_after_message():
    r = api("get", f"/api/chat/{CHAT_PID}/history", token=TOKEN)
    assert r.status_code == 200
    msgs = r.json()
    assert len(msgs) >= 2, f"expected >=2 messages, got {len(msgs)}"
    roles = [m["role"] for m in msgs]
    assert "user" in roles, "no user message in history"
    assert "assistant" in roles, "no assistant message in history"

def test_sse_iteration_second_message():
    r = api("post", f"/api/chat/{CHAT_PID}/message", token=TOKEN,
            json_data={"content": "Change the color to blue", "mode": "team"}, stream=True, timeout=90)
    assert r.status_code == 200
    has_code = False
    for line in r.iter_lines():
        d = line.decode()
        if "code_generated" in d:
            has_code = True
    assert has_code, "no code_generated on iteration"

def test_chat_history_after_two_messages():
    r = api("get", f"/api/chat/{CHAT_PID}/history", token=TOKEN)
    msgs = r.json()
    user_msgs = [m for m in msgs if m["role"] == "user"]
    assert len(user_msgs) == 2, f"expected 2 user msgs, got {len(user_msgs)}"

def test_sse_third_message_still_works():
    r = api("post", f"/api/chat/{CHAT_PID}/message", token=TOKEN,
            json_data={"content": "Add a reset button", "mode": "team"}, stream=True, timeout=90)
    assert r.status_code == 200
    has_complete = False
    for line in r.iter_lines():
        d = line.decode()
        if "message_complete" in d:
            has_complete = True
    assert has_complete, "no message_complete on 3rd message"

def test_chat_history_after_three_messages():
    r = api("get", f"/api/chat/{CHAT_PID}/history", token=TOKEN)
    user_msgs = [m for m in r.json() if m["role"] == "user"]
    assert len(user_msgs) == 3, f"expected 3 user msgs, got {len(user_msgs)}"

def test_latest_code_after_iteration():
    r = api("get", f"/api/projects/{CHAT_PID}/latest-code", token=TOKEN)
    assert len(r.json().get("code", "")) > 100

def test_sse_single_mode():
    r2 = api("post", "/api/projects", token=TOKEN, json_data={
        "name": "Single Mode Test", "mode": "single"
    })
    pid = r2.json()["id"]
    r = api("post", f"/api/chat/{pid}/message", token=TOKEN,
            json_data={"content": "Make a todo list", "mode": "single"}, stream=True, timeout=90)
    assert r.status_code == 200
    has_code = False
    for line in r.iter_lines():
        if "code_generated" in line.decode():
            has_code = True
    assert has_code, "single mode: no code_generated"

def test_sse_iterate_mode():
    r2 = api("post", "/api/projects", token=TOKEN, json_data={
        "name": "Iterate Mode Test", "mode": "iterate"
    })
    pid = r2.json()["id"]
    api("post", f"/api/chat/{pid}/message", token=TOKEN,
        json_data={"content": "Make a portfolio", "mode": "iterate"}, stream=True, timeout=90)
    r = api("post", f"/api/chat/{pid}/message", token=TOKEN,
            json_data={"content": "Add contact section", "mode": "iterate"}, stream=True, timeout=90)
    assert r.status_code == 200

def test_sse_review_mode():
    r2 = api("post", "/api/projects", token=TOKEN, json_data={
        "name": "Review Mode Test", "mode": "review"
    })
    pid = r2.json()["id"]
    api("post", f"/api/chat/{pid}/message", token=TOKEN,
        json_data={"content": "Review this landing page", "mode": "review"}, stream=True, timeout=90)
    r = api("get", f"/api/chat/{pid}/history", token=TOKEN)
    assert r.status_code == 200
    assert len(r.json()) >= 2

def test_chat_invalid_project():
    r = api("post", "/api/chat/00000000-0000-0000-0000-000000000000/message", token=TOKEN,
            json_data={"content": "test", "mode": "team"}, stream=True, timeout=15)
    assert r.status_code in (404, 500), f"expected error, got {r.status_code}"

def test_chat_no_auth():
    r = api("post", f"/api/chat/{CHAT_PID}/message",
            json_data={"content": "test", "mode": "team"}, stream=True, timeout=15)
    assert r.status_code in (401, 403), f"expected 401/403, got {r.status_code}"

test("SSE first message (team mode)", test_sse_first_message)
test("Latest code exists after chat", test_latest_code_after_chat)
test("Chat history after 1 message", test_chat_history_after_message)
test("SSE iteration (2nd message)", test_sse_iteration_second_message)
test("Chat history after 2 messages", test_chat_history_after_two_messages)
test("SSE 3rd message still works", test_sse_third_message_still_works)
test("Chat history after 3 messages", test_chat_history_after_three_messages)
test("Latest code after iteration", test_latest_code_after_iteration)
test("SSE single mode", test_sse_single_mode)
test("SSE iterate mode", test_sse_iterate_mode)
test("SSE review mode", test_sse_review_mode)
test("Chat invalid project -> error", test_chat_invalid_project)
test("Chat no auth -> 401", test_chat_no_auth)

# ============================================================
print()
print("=" * 60)
print("SECTION 4: CODE VERSIONS")
print("=" * 60)

def test_code_versions_list():
    r = api("get", f"/api/projects/{CHAT_PID}/versions", token=TOKEN)
    assert r.status_code == 200
    versions = r.json()
    assert len(versions) >= 2, f"expected >=2 versions, got {len(versions)}"
    for v in versions:
        assert "id" in v
        assert "createdAt" in v

def test_code_versions_empty_project():
    r2 = api("post", "/api/projects", token=TOKEN, json_data={
        "name": "No Chat Project", "mode": "team"
    })
    pid = r2.json()["id"]
    r = api("get", f"/api/projects/{pid}/versions", token=TOKEN)
    assert r.status_code == 200
    assert r.json() == [], f"expected empty, got {r.json()}"

test("Code versions list (>=2)", test_code_versions_list)
test("Code versions empty project", test_code_versions_empty_project)

# ============================================================
print()
print("=" * 60)
print("SECTION 5: MULTI-USER ISOLATION")
print("=" * 60)

def test_user_cannot_see_other_projects():
    r2 = api("post", "/api/auth/register", json_data={
        "email": f"other_{ts}@test.dev", "username": f"other_{ts}", "password": "Other1234!"
    })
    other_token = r2.json()["accessToken"]
    r = api("get", f"/api/projects/{PROJECT_ID}", token=other_token)
    assert r.status_code in (403, 404), f"should not see other user project, got {r.status_code}"
    r = api("get", "/api/projects", token=other_token)
    assert not any(p["id"] == PROJECT_ID for p in r.json()), "other user sees my projects"

def test_user_cannot_chat_other_project():
    r2 = api("post", "/api/auth/register", json_data={
        "email": f"other2_{ts}@test.dev", "username": f"other2_{ts}", "password": "Other1234!"
    })
    other_token = r2.json()["accessToken"]
    r = api("post", f"/api/chat/{CHAT_PID}/message", token=other_token,
            json_data={"content": "hack", "mode": "team"}, stream=True, timeout=15)
    assert r.status_code in (403, 404), f"should not chat in other project, got {r.status_code}"

test("User cannot see other user's project", test_user_cannot_see_other_projects)
test("User cannot chat in other user's project", test_user_cannot_chat_other_project)

# ============================================================
print()
print("=" * 60)
print("SECTION 6: CORS / PREFLIGHT")
print("=" * 60)

def test_cors_preflight():
    r = requests.options(f"{BASE}/api/auth/register", headers={
        "Origin": ORIGIN,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type,authorization",
    }, proxies=P, timeout=10)
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == ORIGIN
    assert "POST" in r.headers.get("access-control-allow-methods", "")

def test_cors_wrong_origin():
    r = requests.options(f"{BASE}/api/auth/register", headers={
        "Origin": "https://evil-site.com",
        "Access-Control-Request-Method": "POST",
    }, proxies=P, timeout=10)
    allow = r.headers.get("access-control-allow-origin")
    assert allow != "https://evil-site.com", f"CORS allows evil origin!"

test("CORS preflight OK", test_cors_preflight)
test("CORS blocks wrong origin", test_cors_wrong_origin)

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
