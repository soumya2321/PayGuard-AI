"""
test_auth_endpoints.py - Verification script for PayGuard authentication flow:
- Valid login (customer, merchant, admin)
- Generic 401 on bad credentials (no info leak)
- JWT issuance and verification (/auth/me)
- Brute-force rate limiting (5 failed attempts -> 429 lock)
- Audit logging verification
"""

from fastapi.testclient import TestClient
from app.main import app
from app.core.logging import get_login_audit_trail

client = TestClient(app)

def test_auth_pipeline():
    print("--- 1. Testing Customer Login (Rahul Sharma) ---")
    res = client.post("/auth/login", json={
        "email": "rahul.sharma@oksbi",
        "password": "Customer#2026"
    })
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    token = data["token"]
    user = data["user"]
    print(f"Customer login OK! User: {user['name']} ({user['email']}), Role: {user['role']}")
    assert user["role"] == "customer"
    assert token and len(token) > 20

    print("\n--- 2. Testing /auth/me with Bearer Token ---")
    res_me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200, f"Expected 200, got {res_me.status_code}: {res_me.text}"
    assert res_me.json()["email"] == "rahul.sharma@oksbi"
    print("Profile query /auth/me OK!")

    print("\n--- 3. Testing Merchant Login (Fresh Mart) ---")
    res_m = client.post("/auth/login", json={
        "email": "fresh.mart@paytm",
        "password": "Merchant#2026"
    })
    assert res_m.status_code == 200, res_m.text
    print("Merchant login OK! Role:", res_m.json()["user"]["role"])
    assert res_m.json()["user"]["role"] == "merchant"

    print("\n--- 4. Testing Admin/Analyst Login ---")
    res_a = client.post("/auth/login", json={
        "email": "analyst@payguard.ai",
        "password": "Admin@Secure2026"
    })
    assert res_a.status_code == 200, res_a.text
    print("Admin login OK! Role:", res_a.json()["user"]["role"])
    assert res_a.json()["user"]["role"] == "admin"

    print("\n--- 5. Testing Generic 401 on Bad Password ---")
    res_bad_pw = client.post("/auth/login", json={
        "email": "rahul.sharma@oksbi",
        "password": "WrongPassword#999"
    })
    assert res_bad_pw.status_code == 401
    assert res_bad_pw.json()["detail"] == "Incorrect email or password."
    print("Generic 401 on bad password verified (no info leaked).")

    print("\n--- 6. Testing Generic 401 on Non-Existent User ---")
    res_no_user = client.post("/auth/login", json={
        "email": "unknown.ghost@fakebank",
        "password": "RandomPassword#999"
    })
    assert res_no_user.status_code == 401
    assert res_no_user.json()["detail"] == "Incorrect email or password."
    print("Generic 401 on unknown user verified (no email enumeration).")

    print("\n--- 7. Testing Brute-Force Rate Limiting (5 failed attempts) ---")
    target_email = "bruteforce.target@payguard.ai"
    for i in range(1, 6):
        res_fail = client.post("/auth/login", json={
            "email": target_email,
            "password": "WrongPassword#999"
        })
        print(f"  Attempt {i}: HTTP {res_fail.status_code}")

    # 6th attempt should be blocked with 429
    res_locked = client.post("/auth/login", json={
        "email": target_email,
        "password": "WrongPassword#999"
    })
    print(f"  Attempt 6: HTTP {res_locked.status_code} - {res_locked.json()['detail']}")
    assert res_locked.status_code == 429
    assert "locked" in res_locked.json()["detail"].lower()
    print("Rate-limiting 429 lockout verified!")

    print("\n--- 8. Testing Logout Endpoint ---")
    res_logout = client.post("/auth/logout")
    assert res_logout.status_code == 200
    print("Logout response:", res_logout.json())

    print("\n--- 9. Verifying Audit Trail ---")
    trail = get_login_audit_trail()
    print(f"Total audit events recorded: {len(trail)}")
    assert len(trail) > 0
    # Ensure no passwords in audit log
    for entry in trail:
        assert "password" not in entry, "SECURITY VIOLATION: Password found in audit log!"
    print("Audit log integrity verified (zero passwords stored).")

    print("\nALL AUTHENTICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_auth_pipeline()
