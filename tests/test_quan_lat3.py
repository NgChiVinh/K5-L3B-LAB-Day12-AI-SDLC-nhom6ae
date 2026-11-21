import unittest

from chonoi.contract import load_contract
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.quan import QuanSim
from helpers import counts, items


def stock_items(stock):
    """v1.2 (TICKET-03): kho quán là mảng cá thể; đổi kho đếm của test cũ sang cá thể fresh 100, id I1, I2…"""
    return items(*[k for k in sorted(stock) for _ in range(stock[k])])


class QuanLat3(unittest.TestCase):
    def make_sim(self, stock=None, scenario=None, seed=9):
        tuning = load_contract()["tuning"]
        tuning["quan"]["first_customer_tick"] = 1
        tuning["quan"]["customer_interval_s"] = 1 / 60
        return QuanSim(tuning, {"stock": stock_items(stock or {}), **(scenario or {})}, Streams(seed), IdAllocator())

    @staticmethod
    def idle_input():
        return InputState((0.0, 0.0), {}, set())

    def test_arrival_reserves_recipe_and_uses_seeded_id(self):
        sim = self.make_sim({"ca_loc": 1, "bong_sung": 2})
        events = sim.step(self.idle_input())
        self.assertEqual(events[0][0], "customer_arrived")
        self.assertEqual(sim.customers[0]["id"], "C1")
        customer = sim.customers[0]
        self.assertEqual(customer["table_id"], "T1")
        # v1.2: reserved là mảng id cá thể — đúng công thức về số lượng theo loại
        by_id = {it["id"]: it for it in sim.stock}
        self.assertEqual(counts([by_id[x] for x in customer["reserved"]]), sim.menu[customer["dish_id"]]["recipe"])
        expected = {"ca_loc": 1, "bong_sung": 2}
        for kind, qty in sim.menu[customer["dish_id"]]["recipe"].items():
            expected[kind] -= qty
        # _available() (bản tích hợp với lát 4) bỏ khóa bằng 0; thiếu khóa nghĩa là 0.
        self.assertEqual(sim._available(), {k: v for k, v in expected.items() if v > 0})
        self.assertEqual(customer["patience_ticks_left"], sim.t["patience_s"] * 60)

    def test_no_dish_does_not_create_customer(self):
        sim = self.make_sim()
        events = sim.step(self.idle_input())
        self.assertEqual(events, [("no_dish", {})])
        self.assertEqual(sim.customers, [])

    def test_patience_expiry_releases_reservation_and_clamps_reputation(self):
        customer = {"id": "C1", "table_id": "T1", "dish_id": "goi_bong_sung",
                    "state": "waiting", "order_status": "reserved", "reserved": ["I1", "I2"],  # v1.2: id cá thể
                    "patience_ticks_left": 1}
        sim = self.make_sim({"bong_sung": 2}, {"customers": [customer], "random_customers": False,
                                                "reputation": 0.1})
        events = sim.step(self.idle_input())
        self.assertEqual(events[0], ("customer_left", {"order_id": "C1", "table_id": "T1",
                                                         "reason": "patience", "reputation": 0}))
        self.assertEqual(sim.customers, [])
        self.assertEqual(counts(sim.stock), {"bong_sung": 2})  # v1.2: nhả giữ chỗ, cá thể vẫn trong kho
        self.assertEqual(sim._available(), {"bong_sung": 2})


if __name__ == "__main__":
    unittest.main()
