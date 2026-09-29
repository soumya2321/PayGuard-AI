"""
test_api_endpoints.py - Comprehensive verification of all PayGuard FastAPI endpoints.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_endpoints():
    print("Testing root...")
    res = client.get("/")
    assert res.status_code == 200, res.text
    print("Root OK:", res.json()["system"])

    print("\nTesting POST /transactions (Valid transaction - Safe)...")
    res = client.post("/transactions", json={
        "userId": 1,
        "amount": 450.0,
        "location": "Bengaluru, Karnataka",
        "deviceType": "Samsung Galaxy S23, Android App",
        "paymentMethod": "UPI",
        "receiverAddress": "fresh.mart@paytm"
    })
    assert res.status_code == 200, res.text
    data = res.json()
    print("Created TX ID:", data["transactionId"])
    print("Risk Score:", data["prediction"]["riskScore"], "Level:", data["prediction"]["riskLevel"])
    assert data["prediction"]["riskLevel"] == "SAFE"

    print("\nTesting POST /transactions (High Risk Fraud Anomaly)...")
    res = client.post("/transactions", json={
        "userId": 2,
        "amount": 45000.0,
        "location": "Kolkata, West Bengal",
        "deviceType": "Unknown Linux Browser",
        "paymentMethod": "COLLECT_REQUEST",
        "receiverAddress": "lottery.cashout@fakeupi"
    })
    assert res.status_code == 200, res.text
    data = res.json()
    print("High Risk TX ID:", data["transactionId"])
    print("Risk Score:", data["prediction"]["riskScore"], "Level:", data["prediction"]["riskLevel"])
    assert data["prediction"]["riskLevel"] == "HIGH RISK"
    assert data["alert"] is not None
    print("Alert generated:", data["alert"])

    print("\nTesting GET /transactions...")
    res = client.get("/transactions?limit=5")
    assert res.status_code == 200, res.text
    tx_list = res.json()
    print(f"Total transactions: {tx_list['total']}, Returned items: {len(tx_list['items'])}")

    print("\nTesting GET /transactions/{id}...")
    sample_id = tx_list["items"][0]["transactionId"]
    res = client.get(f"/transactions/{sample_id}")
    assert res.status_code == 200, res.text
    detail = res.json()
    print(f"Detail for TX #{sample_id}: User={detail['userName']}, Risk={detail['prediction']['riskScore']}")

    print("\nTesting GET /alerts...")
    res = client.get("/alerts")
    assert res.status_code == 200, res.text
    alerts = res.json()
    print(f"Total alerts: {len(alerts)}")
    if alerts:
        alert_id = alerts[0]["alertId"]
        print(f"Testing PATCH /alerts/{alert_id}...")
        res = client.patch(f"/alerts/{alert_id}", json={"status": "REVIEWED"})
        assert res.status_code == 200, res.text
        print("Alert updated:", res.json())

    print("\nTesting GET /dashboard/stats...")
    res = client.get("/dashboard/stats")
    assert res.status_code == 200, res.text
    stats = res.json()
    print(f"Dashboard Stats: Total TX={stats['totalTransactions']}, Fraud Rate={stats['fraudRatePercentage']}%, Alerts Today={stats['alertsToday']}")

    print("\nTesting GET /analytics/trends...")
    res = client.get("/analytics/trends")
    assert res.status_code == 200, res.text
    trends = res.json()
    print(f"Trends received: Days={len(trends['volumeOverTime'])}, Bins={len(trends['riskScoreDistribution'])}")

    print("\nTesting GET /users/1/profile...")
    res = client.get("/users/1/profile")
    assert res.status_code == 200, res.text
    prof = res.json()
    print(f"User profile for {prof['name']}: Avg Amount=INR {prof['avgTransactionAmount']}, Total TXs={prof['totalUserTransactions']}")

    print("\nALL BACKEND API TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_endpoints()
