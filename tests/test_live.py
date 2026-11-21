"""Test cửa sổ chơi trực tiếp (chonoi.live). Chỉ dành cho starter Python: nhóm đổi ngôn ngữ thì xóa file này."""

import json
import time
import unittest
import urllib.error
import urllib.request

from chonoi.contract import load_contract
from chonoi.live import LiveGame, LiveServer, load_live_tuning


def _get(url):
    with urllib.request.urlopen(url, timeout=5) as r:
        return r.status, r.read()


def _post(url, obj):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except urllib.error.HTTPError as e:
        e.close()
        return e.code


class LiveServerTest(unittest.TestCase):
    def test_live_specials_from_catch_to_payment(self):
        tuning = load_live_tuning()
        core = load_contract()["tuning"]
        self.assertLess(core["gather"]["bounds"]["d"][1], tuning["gather"]["bounds"]["d"][1])
        for dish, kind in (("ca_keo_kho_to", "ca_keo"), ("ca_linh_chien_gion", "ca_linh")):
            with self.subTest(dish=dish):
                self.assertNotIn(dish, core["menu"])
                depth = max(tuning["gather"]["fish_spawn_depths"][kind])
                self.assertTrue(any(dish in p["dishes"] for p in tuning["day_plan"]))
                scenario = {
                    "day": {"day_plan": [{"day": 1, "dishes": {dish: 1}}]},
                    "gather": {"time_left_ticks": 2, "player": {"pos": [15, depth]},
                               "fish": [{"id": "F1", "kind": kind, "pos": [15, depth]}],
                               "random_fish": False},
                    "quan": {"player": {"pos": [2, 8]}, "tables": [{"id": "T1", "pos": [4, 8]}],
                             "customers": [{"id": "C1", "dish_id": dish, "table_id": "T1"}],
                             "random_customers": False},
                }
                game = LiveGame("day", tuning, scenario, 1)
                game.set_input({"catch": True})
                game._tick_once()
                game._tick_once()
                state = json.loads(game.state_json())
                self.assertEqual(state["phase"], "quan")
                self.assertEqual([i["kind"] for i in state["stock"]], [kind] * tuning["menu"][dish]["recipe"][kind])
                game.set_input({"interact": True})
                game._tick_once()
                game.set_input({"interact": False})
                for _ in range(tuning["menu"][dish]["cook_s"] * 60):
                    game._tick_once()
                game.set_input({"interact": True})
                game._tick_once()
                self.assertEqual(json.loads(game.state_json())["hand"]["dish_id"], dish)
                game.set_input({"interact": False, "move": [1, 0]})
                for _ in range(32):
                    game._tick_once()
                game.set_input({"interact": True, "move": [0, 0]})
                game._tick_once()
                for _ in range(tuning["quan"]["eat_s"] * 60):
                    game._tick_once()
                self.assertGreater(json.loads(game.state_json())["money"], 0)

    def test_state_input_and_clean_stop(self):
        tuning = load_contract()["tuning"]
        server = LiveServer(LiveGame("gather", tuning, {}, 1), port=0)  # cổng ngẫu nhiên
        server.start()
        try:
            base = f"http://127.0.0.1:{server.port}"
            code, body = _get(base + "/state")
            self.assertEqual(code, 200)
            st = json.loads(body)
            self.assertIn("tick", st)
            self.assertEqual(st["mode"], "gather")
            self.assertEqual(st["player"]["pos"], [2, 0])
            self.assertEqual(_post(base + "/input", {"move": [1, 0], "interact": False, "catch": False}), 200)
            self.assertEqual(_post(base + "/input", {"move": [5, 0]}), 400)
            code, html = _get(base + "/")
            self.assertEqual(code, 200)
            self.assertIn(b"<canvas", html)
            deadline = time.time() + 3
            while time.time() < deadline:
                st2 = json.loads(_get(base + "/state")[1])
                if st2["tick"] > st["tick"] + 3 and st2["player"]["pos"][0] > st["player"]["pos"][0]:
                    break
                time.sleep(0.05)
            self.assertGreater(st2["tick"], st["tick"], "mô phỏng phải chạy nền")
            self.assertGreater(st2["player"]["pos"][0], st["player"]["pos"][0], "input phải tác động tới sim")
        finally:
            server.stop()
        self.assertFalse(server.game._thread.is_alive())
        self.assertFalse(server._thread.is_alive())


if __name__ == "__main__":
    unittest.main()
