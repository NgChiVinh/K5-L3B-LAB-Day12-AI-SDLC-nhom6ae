"""Lát 4 (quan): bếp, bưng, phục vụ, tiền, boa, uy tín, đóng ca — PRD-0 mục F, Quán bước 1–4.

Test hộp đen qua headless_cmd. Chạy: PYTHONPATH=tests:. python3 -m unittest tests.test_quan_lat4 -v
"""

import math
import unittest

from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json

PATIENCE_MAX = 60 * 60  # patience_s × 60
EAT_MAX = 10 * 60       # eat_s × 60
STOVE_POS = [2, 8]      # B1 trong game.contract.json
TABLE_POS = [9, 2]      # T1 trong game.contract.json


def run_quan(w, block, ticks, inputs=None):
    b = dict(block)
    b.setdefault("random_customers", False)
    sc = write_json(w.path("sc.json"), {"quan": b})
    args = ["--mode", "quan", "--seed", "1", "--ticks", str(ticks), "--scenario", sc,
            "--snapshot-every", "1", "--out", w.path("o.jsonl")]
    if inputs is not None:
        args += ["--inputs", write_json(w.path("in.json"), frames(*inputs))]
    code, err = run_headless(*args)
    assert code == 0, err
    return read_jsonl(w.path("o.jsonl"))


def snap_at(rows, tick):
    return next(s for s in snapshots(rows) if s["tick"] == tick)


class StoveCookAndReady(unittest.TestCase):
    def test_cook_started_consumes_reserved_and_sorts_items(self):
        """Bếp idle lấy đơn reserved, trừ stock, xóa reserved, chốt giá, items sắp theo kind."""
        with Workdir() as w:
            block = {
                "player": {"pos": STOVE_POS},
                "stock": {"ca_linh": 3, "bong_dien_dien": 1, "ca_loc": 1},
                "customers": [{
                    "id": "C1", "table_id": "T1", "dish_id": "lau_ca_linh_dien_dien",
                    "order_tick": 10, "state": "waiting", "order_status": "reserved",
                    "reserved": {"ca_linh": 3, "bong_dien_dien": 1},
                }],
            }
            rows = run_quan(w, block, 1, [{"tick": 0, "interact": True}])
            ev = events(rows, "cook_started")
            self.assertEqual(len(ev), 1)
            self.assertEqual(ev[0]["tick"], 1)
            self.assertEqual(ev[0]["data"], {
                "stove_id": "B1", "order_id": "C1", "dish_id": "lau_ca_linh_dien_dien",
                "items": ["bong_dien_dien", "ca_linh", "ca_linh", "ca_linh"],
                "base_price": 120,
            })
            s1 = snap_at(rows, 1)
            self.assertEqual(s1["stock"], {"ca_loc": 1})
            c1 = s1["customers"][0]
            self.assertEqual(c1["order_status"], "assigned")
            self.assertEqual(c1["reserved"], {})
            self.assertEqual(c1["base_price"], 120)
            st = s1["stoves"][0]
            self.assertEqual(st["state"], "cooking")
            self.assertEqual(st["cook_ticks_left"], 10 * 60)
            self.assertEqual(st["ready_ticks"], 0)
            self.assertEqual(st["dish"], {
                "order_id": "C1", "dish_id": "lau_ca_linh_dien_dien", "base_price": 120,
            })

    def test_dish_ready_and_ready_ticks_increment(self):
        """Nấu xong ở tick 2 -> dish_ready với ready_ticks=0; tick 3 ready_ticks=1; không cháy."""
        with Workdir() as w:
            dish = {"order_id": "C1", "dish_id": "goi_bong_sung", "base_price": 40}
            block = {
                "stoves": [{"id": "B1", "state": "cooking", "dish": dish, "cook_ticks_left": 2}],
                "customers": [{
                    "id": "C1", "table_id": "T1", "dish_id": "goi_bong_sung",
                    "state": "waiting", "order_status": "assigned", "reserved": {}, "base_price": 40,
                }],
            }
            rows = run_quan(w, block, 4)
            ready_ev = events(rows, "dish_ready")
            self.assertEqual([(e["tick"], e["data"]) for e in ready_ev], [
                (2, {"stove_id": "B1", "order_id": "C1", "dish_id": "goi_bong_sung"}),
            ])
            self.assertEqual(snap_at(rows, 1)["stoves"][0]["state"], "cooking")
            self.assertEqual(snap_at(rows, 1)["stoves"][0]["cook_ticks_left"], 1)
            self.assertEqual(snap_at(rows, 2)["stoves"][0]["state"], "ready")
            self.assertEqual(snap_at(rows, 2)["stoves"][0]["ready_ticks"], 0)
            self.assertEqual(snap_at(rows, 3)["stoves"][0]["ready_ticks"], 1)
            self.assertEqual(snap_at(rows, 4)["stoves"][0]["ready_ticks"], 2)


class PickAndInteractPriority(unittest.TestCase):
    def test_dish_picked_when_hand_empty_and_blocked_when_full(self):
        """Bếp ready giao món cho tay trống và về idle; tay đang cầm món thì bỏ lượt."""
        dish = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 60}
        with Workdir() as w:
            block = {
                "player": {"pos": STOVE_POS},
                "stoves": [{"id": "B1", "state": "ready", "dish": dish, "ready_ticks": 5}],
                "customers": [{
                    "id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                    "state": "waiting", "order_status": "assigned", "reserved": {}, "base_price": 60,
                }],
            }
            rows = run_quan(w, block, 1, [{"tick": 0, "interact": True}])
            ev = events(rows, "dish_picked")
            self.assertEqual([(e["tick"], e["data"]) for e in ev], [
                (1, {"stove_id": "B1", "order_id": "C1", "dish_id": "ca_loc_nuong_trui"}),
            ])
            s1 = snap_at(rows, 1)
            self.assertEqual(s1["hand"], dish)
            self.assertEqual(s1["stoves"][0]["state"], "idle")
            self.assertIsNone(s1["stoves"][0]["dish"])
            self.assertEqual(s1["stoves"][0]["ready_ticks"], 0)

        # Tay cầm món của đơn C2 không có khách = "liên kết thiếu" (PRD mục D) -> fixture mâu thuẫn, mã 2.
        # Với 1 bàn chỉ có 1 khách nên "tay đầy + bếp ready" không dựng được bằng fixture hợp lệ ở P1.
        with Workdir() as w:
            other = {"order_id": "C2", "dish_id": "goi_bong_sung", "base_price": 40}
            block = {
                "random_customers": False,
                "player": {"pos": STOVE_POS},
                "hand": other,
                "stoves": [{"id": "B1", "state": "ready", "dish": dish, "ready_ticks": 5}],
                "customers": [{
                    "id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                    "state": "waiting", "order_status": "assigned", "reserved": {}, "base_price": 60,
                }],
            }
            sc = write_json(w.path("sc.json"), {"quan": block})
            code, _ = run_headless("--mode", "quan", "--seed", "1", "--ticks", "1", "--scenario", sc,
                                   "--out", w.path("o.jsonl"))
            self.assertEqual(code, 2)

    def test_interact_prefers_stove_over_table_on_equal_distance_and_skips_if_unusable(self):
        """Cùng khoảng cách: chọn bếp trước bàn. Nếu đối tượng gần nhất không tương tác được thì bỏ lượt."""
        dish = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 60}
        # Đặt bếp B1 ở [5, 5], bàn T1 ở [7, 5], người chơi ở [6, 5] (cùng cách 1.0 m <= 1.5 m).
        # Bếp idle nhưng không còn đơn reserved (C1 đã assigned) -> không tương tác được; bàn lại có thể
        # phục vụ -> phải chọn bếp và BỎ LƯỢT. (Trước dùng bếp cooking đơn C9 không có khách = fixture
        # mâu thuẫn theo PRD mục D, scenario.py trả mã 2.)
        with Workdir() as w:
            block = {
                "player": {"pos": [6, 5]},
                "hand": dish,
                "stoves": [{"id": "B1", "pos": [5, 5], "state": "idle"}],
                "tables": [{"id": "T1", "pos": [7, 5]}],
                "customers": [{
                    "id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                    "state": "waiting", "order_status": "assigned", "reserved": {}, "base_price": 60,
                }],
            }
            rows = run_quan(w, block, 1, [{"tick": 0, "interact": True}])
            self.assertEqual(events(rows, "served"), [])
            self.assertEqual(snap_at(rows, 1)["hand"], dish)


class ServeTipPayAndReputation(unittest.TestCase):
    def test_serve_with_tip_boundary_and_pay_reputation(self):
        """Kiên nhẫn còn 1800/3600 = 0.5 sau bước 1 -> có boa floor(60*0.2)=12, ăn xong +0.2 uy tín."""
        dish = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 60}
        with Workdir() as w:
            block = {
                "player": {"pos": TABLE_POS},
                "hand": dish,
                "reputation": 3.0,
                "customers": [{
                    "id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                    "state": "waiting", "order_status": "assigned", "reserved": {},
                    "base_price": 60, "patience_ticks_left": 1801,  # sau bước 1 còn đúng 1800
                }],
            }
            rows = run_quan(w, block, EAT_MAX + 2, [{"tick": 0, "interact": True}])
            sv = events(rows, "served")
            self.assertEqual(len(sv), 1)
            self.assertEqual(sv[0]["tick"], 1)
            self.assertEqual(sv[0]["data"], {
                "order_id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                "patience_ticks_left": 1800, "base_price": 60, "tip": 12,
            })
            s1 = snap_at(rows, 1)
            self.assertIsNone(s1["hand"])
            self.assertEqual(s1["customers"][0]["state"], "eating")
            self.assertEqual(s1["customers"][0]["order_status"], "served")
            self.assertEqual(s1["customers"][0]["eat_ticks_left"], EAT_MAX)

            paid = events(rows, "paid")
            self.assertEqual(len(paid), 1)
            self.assertEqual(paid[0]["tick"], 1 + EAT_MAX)
            self.assertEqual(paid[0]["data"], {
                "order_id": "C1", "table_id": "T1", "base_price": 60, "tip": 12,
                "amount": 72, "reason": "finished_eating",
            })
            sp = snap_at(rows, 1 + EAT_MAX)
            self.assertEqual(sp["customers"], [])
            self.assertIsNone(sp["tables"][0]["customer_id"])
            self.assertEqual((sp["money"], sp["earned"]), (72, 72))
            self.assertAlmostEqual(sp["reputation"], 3.2, places=3)
            self.assertEqual(sp["score"], 72 + 100 * math.floor(3.2))

    def test_serve_below_tip_threshold_and_at_zero_patience(self):
        """Kiên nhẫn 1799/3600 sau bước 1 -> boa 0; kiên nhẫn về đúng 0 vẫn phục vụ hợp lệ."""
        dish = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 60}
        for start_pat, want_pat in ((1800, 1799), (1, 0)):
            with Workdir() as w:
                block = {
                    "player": {"pos": TABLE_POS},
                    "hand": dish,
                    "reputation": 3.0,
                    "customers": [{
                        "id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                        "state": "waiting", "order_status": "assigned", "reserved": {},
                        "base_price": 60, "patience_ticks_left": start_pat,
                    }],
                }
                rows = run_quan(w, block, EAT_MAX + 2, [{"tick": 0, "interact": True}])
                sv = events(rows, "served")
                self.assertEqual(len(sv), 1)
                self.assertEqual(sv[0]["data"]["patience_ticks_left"], want_pat)
                self.assertEqual(sv[0]["data"]["tip"], 0)
                self.assertEqual(events(rows, "customer_left"), [])
                paid = events(rows, "paid")
                self.assertEqual(paid[0]["data"]["amount"], 60)
                self.assertAlmostEqual(snap_at(rows, 1 + EAT_MAX)["reputation"], 3.0, places=3)

    def test_reputation_clamped_at_max(self):
        """Uy tín cộng tip_reputation không vượt reputation_max (5.0)."""
        with Workdir() as w:
            block = {
                "reputation": 4.9,
                "customers": [{
                    "id": "C1", "table_id": "T1", "dish_id": "goi_bong_sung",
                    "state": "eating", "order_status": "served", "reserved": {},
                    "eat_ticks_left": 1, "base_price": 40, "tip": 8,
                }],
            }
            rows = run_quan(w, block, 2)
            self.assertAlmostEqual(snap_at(rows, 1)["reputation"], 5.0, places=3)


class ClosingShift(unittest.TestCase):
    def test_closing_pays_eating_customer_including_served_on_last_tick(self):
        """Phục vụ ở đúng tick cuối ca -> served, paid(closing), quan_end."""
        dish = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 60}
        with Workdir() as w:
            block = {
                "player": {"pos": TABLE_POS},
                "hand": dish,
                "time_left_ticks": 1,
                "reputation": 3.0,
                "customers": [{
                    "id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                    "state": "waiting", "order_status": "assigned", "reserved": {},
                    "base_price": 60, "patience_ticks_left": PATIENCE_MAX,
                }],
            }
            rows = run_quan(w, block, 10, [{"tick": 0, "interact": True}])
            names = [e["name"] for e in events(rows)]
            self.assertEqual(names, ["served", "paid", "quan_end"])
            self.assertEqual(events(rows, "paid")[0]["data"]["reason"], "closing")
            self.assertEqual(events(rows, "paid")[0]["data"]["amount"], 72)
            qend = events(rows, "quan_end")[0]["data"]
            self.assertEqual(qend, {
                "reason": "time", "money": 72, "earned": 72, "shift_earned": 72, "reputation": 3.2,
            })
            self.assertEqual(rows[-1]["reason"], "time")
            self.assertEqual(rows[-1]["score"], 72 + 300)

    def test_closing_waiting_customer_leaves_without_rep_loss_and_clears_stove(self):
        """Hết ca: khách chờ rời với closing, không trừ uy tín, bỏ món đang nấu trên bếp (không hoàn kho)."""
        dish = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 60}
        with Workdir() as w:
            block = {
                "time_left_ticks": 1,
                "reputation": 3.0,
                "stock": {},
                "stoves": [{"id": "B1", "state": "cooking", "dish": dish, "cook_ticks_left": 100}],
                "customers": [{
                    "id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                    "state": "waiting", "order_status": "assigned", "reserved": {},
                    "base_price": 60, "patience_ticks_left": 1,  # đúng tick hết ca cũng là closing, không trừ uy tín
                }],
            }
            rows = run_quan(w, block, 10)
            names = [e["name"] for e in events(rows)]
            self.assertEqual(names, ["customer_left", "quan_end"])
            left = events(rows, "customer_left")[0]["data"]
            self.assertEqual(left, {
                "order_id": "C1", "table_id": "T1", "reason": "closing", "reputation": 3.0,
            })
            last = snapshots(rows)[-1]
            self.assertEqual(last["customers"], [])
            self.assertEqual(last["stoves"][0]["state"], "idle")
            self.assertIsNone(last["stoves"][0]["dish"])
            self.assertEqual(last["stock"], {})


class FullCycleEndToEnd(unittest.TestCase):
    def test_full_cook_pick_serve_pay_close(self):
        """Vòng đầy đủ: nấu (B1) -> chín -> bưng -> đi tới T1 -> phục vụ -> ăn xong trả tiền -> hết ca."""
        with Workdir() as w:
            # goi_bong_sung: cook_s=4 (240 ticks), price=40, tip=8
            block = {
                "player": {"pos": STOVE_POS},
                "stock": {"bong_sung": 2},
                "time_left_ticks": 1200,
                "customers": [{
                    "id": "C1", "table_id": "T1", "dish_id": "goi_bong_sung",
                }],
            }
            # Tick 0: interact ở B1 -> cook_started (tick 1), cook_ticks_left=240
            # Tick 241: dish_ready (sau 240 tick nấu từ tick 1 -> tick 241)
            # Tick 241: interact ở B1 -> dish_picked (tick 242), rồi đi tới T1 [9,2] từ [2,8]
            # khoảng cách dx=7, dz=-6 -> dist=9.22m, walk_speed=4m/s -> ~2.3s (~145 tick)
            # Thay vào đó, đi từ [2,8] sang [9,2] bằng vector (1, -6/7) trong 160 tick -> tới [9,2]
            inp = [
                {"tick": 0, "interact": True},
                {"tick": 1, "interact": False},
                {"tick": 241, "interact": True},
                {"tick": 242, "interact": False, "move": [1, -0.857]},
                {"tick": 385, "move": [0, 0], "interact": True},
                {"tick": 386, "interact": False},
            ]
            rows = run_quan(w, block, 1300, inp)
            names = [e["name"] for e in events(rows)]
            self.assertEqual(names, ["cook_started", "dish_ready", "dish_picked", "served", "paid", "quan_end"])
            self.assertEqual(events(rows, "paid")[0]["data"]["amount"], 48)
            self.assertEqual(rows[-1]["earned"], 48)
            self.assertAlmostEqual(rows[-1]["reputation"], 3.2, places=3)
            self.assertEqual(rows[-1]["score"], 348)


if __name__ == "__main__":
    unittest.main()
