import requests
import sys
import time
import json


BASE_URL = "https://h2iz7egg4l.execute-api.us-east-1.amazonaws.com/dev"




def _get(path):
    start = time.perf_counter()
    r = requests.get(f"{BASE_URL}{path}", timeout=10)
    duration_ms = (time.perf_counter() - start) * 1000
    r.raise_for_status()
    return r, duration_ms


def _post(path, payload):
    start = time.perf_counter()
    r = requests.post(
        f"{BASE_URL}{path}",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=10
    )
    duration_ms = (time.perf_counter() - start) * 1000
    r.raise_for_status()
    return r, duration_ms


def _delete(path):
    start = time.perf_counter()
    r = requests.delete(f"{BASE_URL}{path}", timeout=10)
    duration_ms = (time.perf_counter() - start) * 1000
    if r.status_code >= 400:
        r.raise_for_status()
    return r, duration_ms


# ------------ Existing endpoints ------------

def health():
    """
    Call the /Health endpoint and print the JSON response.
    """
    r, ms = _get("/Health")
    print(f"[health] OK in {ms:.1f} ms")
    print(r.json())


def version():
    """
    Call the /Verison endpoint and print the JSON response.
    """
    r, ms = _get("/Verison")
    print(f"[version] OK in {ms:.1f} ms")
    print(r.json())


# ------------ : full CRUD smoke test ------------

def smoke_test():
    """
    End-to-end smoke test:
    1) /Health
    2) /Verison
    3) POST /todos  (create test item)
    4) GET /todos   (list items)
    5) DELETE item  (best effort cleanup)
    """
    print(f"Running smoke test against {BASE_URL}\n")

    # 1) Health
    try:
        health_resp, health_ms = _get("/Health")
        print(f"1) /Health OK ({health_ms:.1f} ms)")
    except Exception as e:
        print("1) /Health FAILED:", e)
        print("\nSmoke test FAILED at step 1 (health).")
        return

    # 2) Version
    try:
        version_resp, version_ms = _get("/Verison")
        print(f"2) /Verison OK ({version_ms:.1f} ms)")
    except Exception as e:
        print("2) /Verison FAILED:", e)
        print("\nSmoke test FAILED at step 2 (version).")
        return

    # 3) Create test todo
    test_payload = {
        "title": "smoke-test-item",
        "source": "ops-cli",
        "done": False,
    }
    try:
        create_resp, create_ms = _post("/todos", test_payload)
        print(f"3) POST /todos OK ({create_ms:.1f} ms)")
    except Exception as e:
        print("3) POST /todos FAILED:", e)
        print("\nSmoke test FAILED at step 3 (create).")
        return

    created_body = {}
    try:
        created_body = create_resp.json()
    except Exception:
        pass

    # Try to detect an ID in common response shapes
    test_id = (
        created_body.get("id")
        or created_body.get("todoId")
        or created_body.get("Item", {}).get("id")
        or created_body.get("item", {}).get("id")
    )

    # 4) List todos
    try:
        list_resp, list_ms = _get("/todos")
        print(f"4) GET /todos OK ({list_ms:.1f} ms)")
    except Exception as e:
        print("4) GET /todos FAILED:", e)
        print("\nSmoke test FAILED at step 4 (list).")
        return

    # 5) Delete the test item (best effort)
    delete_msg = "skipped (no id returned from create)"
    delete_ms = 0.0

    if test_id:
        deleted = False

        # Pattern 1: DELETE /todos/{id}
        try:
            _, delete_ms = _delete(f"/todos/{test_id}")
            delete_msg = f"DELETE /todos/{test_id} OK"
            deleted = True
        except Exception:
            pass

        # Pattern 2: DELETE /{id}
        if not deleted:
            try:
                _, delete_ms = _delete(f"/{test_id}")
                delete_msg = f"DELETE /{test_id} OK"
                deleted = True
            except Exception:
                pass

        if not deleted:
            delete_msg = (
                "delete attempted but failed (route shape may be different); "
                "update smoke_test() to match your real DELETE path."
            )

    print(f"5) {delete_msg}" + (f" ({delete_ms:.1f} ms)" if delete_ms else ""))

    total_ms = health_ms + version_ms + create_ms + list_ms + delete_ms
    print(f"\nSmoke test COMPLETE. Total measured time: {total_ms:.1f} ms")


# ------------ CLI entrypoint ------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ops.py [health|version|smoke-test]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "health":
        health()
    elif cmd == "version":
        version()
    elif cmd in ("smoke-test", "smoketest"):
        smoke_test()
    else:
        print("Unknown command. Use health, version, or smoke-test.")
