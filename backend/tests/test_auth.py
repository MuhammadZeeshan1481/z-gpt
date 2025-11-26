def test_signup_and_login_flow(client):
    payload = {"email": "newuser@example.com", "password": "Password123", "full_name": "New User"}
    signup = client.post("/auth/signup", json=payload)
    assert signup.status_code == 201
    body = signup.json()
    assert body["access_token"]
    assert body["refresh_token"]

    login = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert login.status_code == 200
    tokens = login.json()
    assert tokens["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == payload["email"].lower()


def test_refresh_token(client):
    payload = {"email": "refresh@example.com", "password": "Password123"}
    signup = client.post("/auth/signup", json=payload)
    assert signup.status_code in (200, 201)
    refresh_token = signup.json()["refresh_token"]

    refreshed = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]
