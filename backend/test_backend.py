import time
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("=" * 60)
    print("Testing ResearchFinder Backend Endpoints")
    print("=" * 60)

    # 1. Health
    print("[1] Testing /health...")
    r = requests.get(f"{BASE_URL}/health")
    print(f"Health Status: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 200

    # 2. Search
    print("\n[2] Testing POST /api/v1/search (Hybrid mode)...")
    payload = {
        "query": "transformer attention models in deep learning",
        "mode": "hybrid",
        "page": 1,
        "page_size": 5
    }
    t0 = time.time()
    r = requests.post(f"{BASE_URL}/api/v1/search", json=payload)
    elapsed = round((time.time() - t0) * 1000, 2)
    print(f"Search Status: {r.status_code} ({elapsed}ms)")
    assert r.status_code == 200
    res = r.json()
    print(f"Total Results: {res['total_results']:,}, Retrieved: {len(res['results'])}")
    if res['results']:
        top_paper = res['results'][0]
        print(f"Top Result: '{top_paper['title']}' (Score: {top_paper['explanation']['relevance_percentage']}%)")
        print(f"Signals: {top_paper['explanation']['signals']}")
        print(f"Reasons: {top_paper['explanation']['reasons'][:2]}")

    # 3. Autocomplete
    print("\n[3] Testing GET /api/v1/search/autocomplete?q=trans...")
    r = requests.get(f"{BASE_URL}/api/v1/search/autocomplete?q=trans&limit=5")
    print(f"Autocomplete Status: {r.status_code}, Suggestions: {r.json()}")
    assert r.status_code == 200

    # 4. Paper Recommendations
    if res['results']:
        top_id = res['results'][0]['paper_id']
        print(f"\n[4] Testing GET /api/v1/papers/{top_id}/recommendations...")
        r = requests.get(f"{BASE_URL}/api/v1/papers/{top_id}/recommendations?top_k=3")
        print(f"Recommendations Status: {r.status_code}")
        assert r.status_code == 200
        recs = r.json()
        print(f"Returned {len(recs)} recommendations for {top_id}:")
        for rec in recs:
            print(f" - [{rec['similarity_percentage']}%] {rec['title']} ({rec['primary_category']})")

    # 5. Analytics
    print("\n[5] Testing GET /api/v1/analytics/overview & /topics & /trends...")
    r_ov = requests.get(f"{BASE_URL}/api/v1/analytics/overview")
    r_top = requests.get(f"{BASE_URL}/api/v1/analytics/topics")
    r_tr = requests.get(f"{BASE_URL}/api/v1/analytics/trends")
    print(f"Overview Status: {r_ov.status_code}, Total Papers: {r_ov.json()['total_papers']:,}")
    print(f"Topics Status: {r_top.status_code}, Clusters: {len(r_top.json())}")
    print(f"Trends Status: {r_tr.status_code}, Trajectories: {len(r_tr.json())}")
    assert r_ov.status_code == 200 and r_top.status_code == 200 and r_tr.status_code == 200

    # 6. Evaluation Benchmark
    print("\n[6] Testing GET /api/v1/evaluation/benchmark...")
    t0 = time.time()
    r = requests.get(f"{BASE_URL}/api/v1/evaluation/benchmark")
    elapsed = round((time.time() - t0) * 1000, 2)
    print(f"Benchmark Status: {r.status_code} ({elapsed}ms)")
    assert r.status_code == 200
    bench = r.json()
    print(f"Benchmark evaluated on {bench['num_queries']} queries. Best: {bench['best_overall_method']}")
    for m in bench['methods']:
        print(f" - {m['method_name']}: MAP={m['map_score']}, MRR={m['mrr_score']}, NDCG@10={m['ndcg_at_10']}, Latency={m['avg_latency_ms']}ms")

    # 7. System Diagnostics
    print("\n[7] Testing GET /api/v1/system/stats...")
    r = requests.get(f"{BASE_URL}/api/v1/system/stats")
    print(f"System Stats: {r.status_code}, Memory: {r.json()['memory_usage_mb']}MB, Status: {r.json()['system_status']}")
    assert r.status_code == 200

    print("\n" + "=" * 60)
    print("ALL BACKEND ENDPOINTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
