"""Phase 2 #3 (HoangQuan23112004): 2 bếp / 4 bàn / 6 món, lọc menu theo kế hoạch Ngày, và Shop.

AC-P2-04: 2 bếp B1–B2, 4 bàn T1–T4, 6 món (gồm canh_chua_ca_loc, ca_keo_nuong, lau_mam),
          trong day lọc menu theo day_plan trước khi lọc nguyên liệu khả dụng và báo mã 2 nếu
          khách/bếp/tay trong scenario gọi món ngoài kế hoạch.
AC-P2-05: Shop mua oxygen/hp đúng giá (đủ đúng giá vẫn mua), trừ money giữ earned,
          buy_failed (funds / max_level / unknown), buy trước shop_done kể cả bước cuối,
          đóng bằng shop_done -> shop_end(done), tự đóng 600 tick -> shop_end(time).

Chạy: PYTHONPATH=tests:. python3 -m unittest tests.test_p2_quan_shop -v
"""

import unittest

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.quan import QuanSim
from chonoi.sim.shop import ShopSim

from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json


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


class MultiStoveTableAndSixDishes(unittest.TestCase):
    def test_two_stoves_cook_in_order_and_four_tables_fill_by_id(self):
        """B1 lấy đơn cũ nhất (T2 order_tick=5); hòa order_tick=10 thì B2 lấy bàn id nhỏ hơn (T1 trước T3)."""
        with Workdir() as w:
            block = {
                "player": {"pos": [2, 8]},  # B1 ở [2, 8], B2 ở [5, 8]
                "stock": {"ca_loc": 2, "bong_dien_dien": 2, "ca_keo": 3, "ca_linh": 2, "keo_neo": 1},
                "customers": [
                    {"id": "C1", "table_id": "T1", "dish_id": "canh_chua_ca_loc", "order_tick": 10},
                    {"id": "C2", "table_id": "T2", "dish_id": "ca_keo_nuong", "order_tick": 5},
                    {"id": "C3", "table_id": "T3", "dish_id": "lau_mam", "order_tick": 10},
                ],
            }
            rows = run_quan(w, block, 1, [{"tick": 0, "interact": True}])
            cs = events(rows, "cook_started")
            self.assertEqual(len(cs), 1)
            self.assertEqual(cs[0]["data"], {
                "stove_id": "B1", "order_id": "C2", "dish_id": "ca_keo_nuong",
                "items": ["ca_keo", "ca_keo"], "base_price": 70,
            })
            s1 = snap_at(rows, 1)
            self.assertEqual([st["id"] for st in s1["stoves"]], ["B1", "B2"])
            self.assertEqual([tb["id"] for tb in s1["tables"]], ["T1", "T2", "T3", "T4"])
            self.assertEqual(s1["stoves"][0]["state"], "cooking")
            self.assertEqual(s1["stoves"][0]["cook_ticks_left"], 6 * 60)
            self.assertEqual(s1["stoves"][1]["state"], "idle")

        with Workdir() as w:
            block = {
                "player": {"pos": [5, 8]},  # đứng tại B2
                "stock": {"ca_loc": 1, "bong_dien_dien": 2, "ca_keo": 1, "ca_linh": 2, "keo_neo": 1},
                "customers": [
                    {"id": "C3", "table_id": "T3", "dish_id": "lau_mam", "order_tick": 10},
                    {"id": "C1", "table_id": "T1", "dish_id": "canh_chua_ca_loc", "order_tick": 10},
                ],
            }
            rows = run_quan(w, block, 1, [{"tick": 0, "interact": True}])
            cs = events(rows, "cook_started")
            self.assertEqual(cs[0]["data"], {
                "stove_id": "B2", "order_id": "C1", "dish_id": "canh_chua_ca_loc",
                "items": ["bong_dien_dien", "ca_loc"], "base_price": 90,
            })

    def test_lau_mam_full_recipe_and_price(self):
        """Món mới lau_mam: ca_linh×2 + ca_keo×1 + keo_neo×1 + bong_dien_dien×1, nấu 12 s, giá 200."""
        with Workdir() as w:
            block = {
                "player": {"pos": [2, 8]},
                "stock": {"ca_linh": 2, "ca_keo": 1, "keo_neo": 1, "bong_dien_dien": 1},
                "customers": [{"id": "C1", "table_id": "T4", "dish_id": "lau_mam"}],
            }
            rows = run_quan(w, block, 1, [{"tick": 0, "interact": True}])
            cs = events(rows, "cook_started")[0]["data"]
            self.assertEqual(cs["items"], ["bong_dien_dien", "ca_keo", "ca_linh", "ca_linh", "keo_neo"])
            self.assertEqual(cs["base_price"], 200)
            s1 = snap_at(rows, 1)
            self.assertEqual(s1["stock"], {})
            self.assertEqual(s1["stoves"][0]["cook_ticks_left"], 12 * 60)

    def test_four_tables_auto_spawn_order(self):
        """Khách tự sinh lần lượt lấp T1, T2, T3, T4 theo id bàn nhỏ nhất; đủ 4 bàn thì bỏ lượt."""
        with Workdir() as w:
            block = {
                "random_customers": True,
                "stock": {"ca_loc": 10},
            }
            # first_customer_tick=120, interval=900 -> 4 lượt đầu: 120, 1020, 1920, 2820
            rows = run_quan(w, block, 2825)
            arrived = events(rows, "customer_arrived")
            self.assertEqual([e["data"]["table_id"] for e in arrived], ["T1", "T2", "T3", "T4"])
            self.assertEqual([e["tick"] for e in arrived], [120, 1020, 1920, 2820])

        # Cả 4 bàn đã có khách ở tick 120 -> bỏ lượt, không phát customer_arrived hay no_dish
        with Workdir() as w:
            block = {
                "random_customers": True,
                "stock": {"ca_loc": 10},
                "customers": [
                    {"id": f"C{i}", "table_id": f"T{i}", "dish_id": "ca_loc_nuong_trui"}
                    for i in range(1, 5)
                ],
            }
            rows = run_quan(w, block, 125)
            self.assertEqual(events(rows, "customer_arrived") + events(rows, "no_dish"), [])

    def test_menu_filter_limits_dishes_in_day_mode_and_rejects_out_of_plan_fixture(self):
        """Trong day, lọc menu theo kế hoạch Ngày trước khi lọc nguyên liệu; khách ngoài kế hoạch -> BadInput (mã 2)."""
        tuning = load_contract()["tuning"]
        tuning["quan"]["first_customer_tick"] = 1
        tuning["quan"]["customer_interval_s"] = 1 / 60
        d1_dishes = tuning["day_plan"][0]["dishes"]
        sim = QuanSim(tuning, {"stock": {"ca_keo": 4}}, Streams(1), IdAllocator(), menu_filter=d1_dishes)
        self.assertEqual(sim.step(InputState((0.0, 0.0), {}, set())), [("no_dish", {})])

        sim2 = QuanSim(tuning, {"stock": {"ca_loc": 2, "ca_keo": 4}}, Streams(1), IdAllocator(), menu_filter=d1_dishes)
        ev2 = sim2.step(InputState((0.0, 0.0), {}, set()))
        self.assertEqual(ev2[0][0], "customer_arrived")
        self.assertEqual(ev2[0][1]["dish_id"], "ca_loc_nuong_trui")

        # Scenario khách gọi món ngoài kế hoạch -> BadInput (mã 2)
        with self.assertRaises(BadInput):
            QuanSim(
                tuning,
                {"stock": {"ca_keo": 2}, "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_keo_nuong"}]},
                Streams(1), IdAllocator(), menu_filter=d1_dishes,
            )


class ShopRules(unittest.TestCase):
    def setUp(self):
        self.tuning = load_contract()["tuning"]

    def test_buy_oxygen_and_hp_exact_price_keeps_earned_and_hits_max_level(self):
        """Mua oxygen 1->2 (200, 400), hp 1 (250), vượt cấp -> max_level, thiếu tiền -> funds, lạ -> unknown."""
        shop = ShopSim(self.tuning, money=850, earned=1000, reputation=3.5, purchased={}, stock={"ca_loc": 2})
        self.assertEqual(shop.snapshot(), {"stock": {"ca_loc": 2}})
        self.assertEqual(shop.time_left_ticks, 600)

        ev = shop.step(InputState((0.0, 0.0), {}, set(), buy="oxygen"))
        self.assertEqual(ev, [("bought", {"upgrade": "oxygen", "level": 1, "price": 200, "money": 650})])
        self.assertEqual(shop.purchased, {"oxygen": 1})
        self.assertEqual((shop.money, shop.earned), (650, 1000))

        ev = shop.step(InputState((0.0, 0.0), {}, set(), buy="oxygen"))
        self.assertEqual(ev, [("bought", {"upgrade": "oxygen", "level": 2, "price": 400, "money": 250})])
        self.assertEqual(shop.purchased, {"oxygen": 2})

        ev = shop.step(InputState((0.0, 0.0), {}, set(), buy="oxygen"))
        self.assertEqual(ev, [("buy_failed", {"action": "oxygen", "reason": "max_level"})])
        self.assertEqual((shop.money, shop.purchased["oxygen"]), (250, 2))

        ev = shop.step(InputState((0.0, 0.0), {}, set(), buy="hp"))
        self.assertEqual(ev, [("bought", {"upgrade": "hp", "level": 1, "price": 250, "money": 0})])
        self.assertEqual(shop.purchased, {"oxygen": 2, "hp": 1})

        ev = shop.step(InputState((0.0, 0.0), {}, set(), buy="hp"))
        self.assertEqual(ev, [("buy_failed", {"action": "hp", "reason": "funds"})])
        self.assertEqual(shop.purchased["hp"], 1)

        ev = shop.step(InputState((0.0, 0.0), {}, set(), buy="weapon"))
        self.assertEqual(ev, [("buy_failed", {"action": "weapon", "reason": "unknown"})])
        self.assertEqual(shop.earned, 1000)

    def test_buy_processed_before_shop_done_even_on_last_tick(self):
        """Mục 4.5: xử lý buy trước shop_done kể cả bước cuối; đóng bằng nút ở bước cuối phát shop_end(done)."""
        shop = ShopSim(self.tuning, money=200, earned=200, reputation=3.0, purchased={}, stock={})
        for _ in range(599):
            self.assertEqual(shop.step(InputState((0.0, 0.0), {}, set())), [])
            self.assertFalse(shop.done)
        self.assertEqual(shop.time_left_ticks, 1)

        ev = shop.step(InputState((0.0, 0.0), {"shop_done": True}, {"shop_done"}, buy="oxygen"))
        self.assertEqual(ev, [
            ("bought", {"upgrade": "oxygen", "level": 1, "price": 200, "money": 0}),
            ("shop_end", {"reason": "done"}),
        ])
        self.assertTrue(shop.done)
        self.assertEqual(shop.reason, "done")

    def test_auto_close_after_600_ticks_with_time_reason(self):
        """Không nhấn shop_done -> tự đóng đúng tick 600 với shop_end(time)."""
        shop = ShopSim(self.tuning, money=0, earned=0, reputation=3.0, purchased={}, stock={})
        for i in range(599):
            self.assertEqual(shop.step(InputState((0.0, 0.0), {}, set())), [], i)
            self.assertFalse(shop.done)
        ev = shop.step(InputState((0.0, 0.0), {}, set()))
        self.assertEqual(ev, [("shop_end", {"reason": "time"})])
        self.assertTrue(shop.done)
        self.assertEqual(shop.reason, "time")


if __name__ == "__main__":
    unittest.main()
