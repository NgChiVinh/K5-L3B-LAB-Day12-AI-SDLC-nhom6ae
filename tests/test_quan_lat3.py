import unittest

from chonoi.contract import load_contract
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.quan import QuanSim


class QuanLat3(unittest.TestCase):
    def make_sim(self, stock=None, scenario=None, seed=9):
        tuning = load_contract()["tuning"]
        tuning["quan"]["first_customer_tick"] = 1
        tuning["quan"]["customer_interval_s"] = 1 / 60
        return QuanSim(tuning, {"stock": stock or {}, **(scenario or {})}, Streams(seed), IdAllocator())

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
        self.assertEqual(customer["reserved"], sim.menu[customer["dish_id"]]["recipe"])
        expected = {"ca_loc": 1, "bong_sung": 2}
        for kind, qty in customer["reserved"].items():
            expected[kind] -= qty
        self.assertEqual(sim._available(), expected)
        self.assertEqual(customer["patience_ticks_left"], sim.t["patience_s"] * 60)

    def test_no_dish_does_not_create_customer(self):
        sim = self.make_sim()
        events = sim.step(self.idle_input())
        self.assertEqual(events, [("no_dish", {})])
        self.assertEqual(sim.customers, [])

    def test_patience_expiry_releases_reservation_and_clamps_reputation(self):
        customer = {"id": "C1", "table_id": "T1", "dish_id": "goi_bong_sung",
                    "state": "waiting", "order_status": "reserved", "reserved": {"bong_sung": 2},
                    "patience_ticks_left": 1}
        sim = self.make_sim({"bong_sung": 2}, {"customers": [customer], "random_customers": False,
                                                "reputation": 0.1})
        events = sim.step(self.idle_input())
        self.assertEqual(events[0], ("customer_left", {"order_id": "C1", "table_id": "T1",
                                                         "reason": "patience", "reputation": 0}))
        self.assertEqual(sim.customers, [])
        self.assertEqual(sim.stock, {"bong_sung": 2})
        self.assertEqual(sim._available(), {"bong_sung": 2})


if __name__ == "__main__":
    unittest.main()
