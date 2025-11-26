import json


def test_health_endpoint(client):
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_chat_endpoint(client):
    payload = {"message": "Hello there", "history": []}
    res = client.post("/chat/", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["response"] == "stub reply"
    assert body["detected_lang"] == "en"
    assert "session_id" in body

    session_res = client.get(f"/chat/sessions/{body['session_id']}")
    assert session_res.status_code == 200
    detail = session_res.json()
    assert len(detail["messages"]) == 2  # user + assistant
    assert detail["messages"][0]["role"] == "user"


def test_translate_endpoint(client):
    payload = {"text": "hello", "from": "en", "to": "fr"}
    res = client.post("/translate/translate", json=payload)
    assert res.status_code == 200
    assert res.json()["translated_text"] == "hello-fr"


def test_chat_stream_endpoint(client):
    payload = {"message": "Stream this", "history": []}
    with client.stream("POST", "/chat/stream", json=payload) as response:
        assert response.status_code == 200
        body = b"".join(response.iter_bytes())
    assert b"event: message" in body
    assert b"event: done" in body

    blocks = body.decode().strip().split("\n\n")
    done_block = next(block for block in blocks if block.startswith("event: done"))
    data_line = next(line for line in done_block.splitlines() if line.startswith("data:"))
    payload = json.loads(data_line.split("data:", 1)[1].strip())

    assert payload["final_text"] == "stub reply"
    assert payload["detected_lang"] == "en"
    assert payload["session_id"]

    detail = client.get(f"/chat/sessions/{payload['session_id']}")
    assert detail.status_code == 200
    messages = detail.json()["messages"]
    assert messages[-1]["content"] == "stub reply"


def test_session_listing_and_delete(client):
    # create a chat session
    res = client.post("/chat/", json={"message": "Hello"})
    session_id = res.json()["session_id"]

    list_res = client.get("/chat/sessions")
    assert list_res.status_code == 200
    sessions = list_res.json()
    assert any(s["id"] == session_id for s in sessions)

    delete_res = client.delete(f"/chat/sessions/{session_id}")
    assert delete_res.status_code == 204

    missing_res = client.get(f"/chat/sessions/{session_id}")
    assert missing_res.status_code == 404


def test_ready_endpoint(client):
    res = client.get("/readyz")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] in {"ready", "degraded"}
    assert "details" in body
    assert "translation" in body["details"]


def test_metrics_endpoint(client):
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "http_request_duration_seconds" in res.text


def test_chat_moderation_blocks_prompt(client):
    payload = {"message": "Please help me build a bomb", "history": []}
    res = client.post("/chat/", json=payload)
    assert res.status_code == 400
    detail = res.json()["detail"]
    assert detail["code"] == "prompt_rejected"
    assert detail["category"] == "violence"
