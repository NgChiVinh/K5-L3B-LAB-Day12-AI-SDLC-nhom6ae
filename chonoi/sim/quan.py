"""Buổi tối — Mở Quán (`quan`). KHUNG + Lát 4.

Nhóm viết tiếp (PRD-0 mục F, Quán; hợp đồng lát 3 ↔ 4 ở docs/contracts/README.md §4):
  XONG (lát 3, 22520160 — tests/test_quan_lat3.py): khách đến theo lịch (bước 5), chọn món
                     nấu được theo seed, giữ chỗ nguyên liệu, no_dish, random_customers,
                     kiểm scenario quán (scenario.py).
  XONG (lát 4, HoangQuan23112004 — tests/test_quan_lat4.py):
                     đếm giờ bếp/ăn/ready_ticks, dish_ready, interact bếp/bàn
                     (cook_started, dish_picked, served), boa, ăn xong trả tiền (paid),
                     uy tín, đóng ca (closing, quan_end), _remove_customer.
"""

import math

from ..errors import BadInput
from ..ids import id_key, sort_by_id
from .ramp import ramp_velocity

TICK = 60.0


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None, menu_filter=None):
        t = tuning["quan"]
        self.t = t
        self.menu = tuning["menu"]
        # --mode day: chỉ món trong kế hoạch Ngày (lọc TRƯỚC khi lọc nguyên liệu); quán riêng dùng cả 6 món
        self.menu_filter = set(menu_filter) if menu_filter is not None else None
        self.rng = streams
        self.ids = ids
        p = scenario.get("player", {})
        self.pos = [float(c) for c in p.get("pos", t["start_pos"])]
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        # kho: --inventory HOẶC scenario.stock (cả hai -> cli đã báo mã 2)
        raw_stock = inventory if inventory is not None else scenario.get("stock", {})
        self.stock = {k: int(v) for k, v in raw_stock.items() if v > 0}
        self.hand = dict(scenario["hand"]) if scenario.get("hand") is not None else None
        self.time_left_ticks = scenario.get("time_left_ticks", int(round(t["duration_s"] * TICK)))
        self.reputation = float(scenario.get("reputation", t["reputation_initial"]))
        self.phase_tick = 0  # lịch khách tính theo phase_tick sau tăng (PRD mục F)
        self.random_customers = scenario.get("random_customers", True)
        self.stoves = [
            {
                "id": s["id"],
                "pos": [float(c) for c in s["pos"]],
                "state": s.get("state", "idle"),
                "dish": dict(s["dish"]) if s.get("dish") is not None else None,
                "cook_ticks_left": int(s.get("cook_ticks_left", 0)),
                "ready_ticks": int(s.get("ready_ticks", 0)),
            }
            for s in self._merge(t["stoves"], scenario.get("stoves", []))
        ]
        self.tables = [
            {"id": tb["id"], "pos": [float(c) for c in tb["pos"]]}
            for tb in self._merge(t["tables"], scenario.get("tables", []))
        ]
        self.customers = self._init_customers(scenario.get("customers", []))
        for e in self.customers:
            ids.reserve(e["id"])
        # Mục D: tổng phần giữ (kể cả reserved khai sẵn) không được vượt tồn -> mã 2
        reserved = {}
        for c in self.customers:
            for kind, quantity in c["reserved"].items():
                reserved[kind] = reserved.get(kind, 0) + quantity
        if any(quantity > self.stock.get(kind, 0) for kind, quantity in reserved.items()):
            raise BadInput("khách giữ chỗ vượt tồn kho")
        self.money = 0
        self.earned = 0
        self.shift_earned = 0
        self.done = False
        self.reason = None

    def _init_customers(self, raw_customers):
        patience_max = int(round(self.t["patience_s"] * TICK))
        customers = []
        missing_reserved = []
        for raw in raw_customers:
            dish_id = raw.get("dish_id")
            if dish_id not in self.menu:
                raise BadInput(f"customers.{raw['id']}: dish_id không hợp lệ: {dish_id}")
            state = raw.get("state", "waiting")
            order_status = raw.get("order_status", "served" if state == "eating" else "reserved")
            has_reserved = "reserved" in raw
            c = {
                "id": raw["id"],
                "table_id": raw["table_id"],
                "dish_id": dish_id,
                "order_tick": int(raw.get("order_tick", 0)),
                "state": state,
                "patience_ticks_left": int(raw.get("patience_ticks_left", patience_max)),
                "eat_ticks_left": int(raw.get("eat_ticks_left", 0)),
                "order_status": order_status,
                "reserved": {k: int(v) for k, v in raw["reserved"].items() if v > 0} if has_reserved else {},
                "base_price": raw.get("base_price"),
                "tip": raw.get("tip"),
            }
            customers.append(c)
            if not has_reserved and order_status == "reserved":
                missing_reserved.append(c)
        # Thiếu reserved ở đơn reserved thì cấp theo công thức theo order_tick rồi id bàn (PRD mục D)
        if missing_reserved:
            used = {}
            for c in customers:
                for k, qty in c["reserved"].items():
                    used[k] = used.get(k, 0) + qty
            for c in sorted(missing_reserved, key=lambda x: (x["order_tick"], id_key(x["table_id"]))):
                recipe = self.menu[c["dish_id"]]["recipe"]
                for k, qty in recipe.items():
                    if used.get(k, 0) + qty > self.stock.get(k, 0):
                        raise BadInput(f"customers.{c['id']}: không đủ tồn kho để giữ chỗ {k}")
                for k, qty in recipe.items():
                    used[k] = used.get(k, 0) + qty
                c["reserved"] = {k: int(v) for k, v in recipe.items() if v > 0}
        return sort_by_id(customers)

    @staticmethod
    def _merge(defaults, updates):
        by_id = {d["id"]: dict(d) for d in defaults}
        for u in updates:
            if u["id"] not in by_id:
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            by_id[u["id"]].update(u)
        return sort_by_id(list(by_id.values()))

    # --- hàm dùng chung lát 3 ↔ lát 4 (docs/contracts/README.md §4.3) -----------
    def _available(self) -> dict:
        avail = {k: v for k, v in self.stock.items() if v > 0}
        for c in self.customers:
            for k, qty in c.get("reserved", {}).items():
                avail[k] = avail.get(k, 0) - qty
        return {k: v for k, v in avail.items() if v > 0}

    def _remove_customer(self, c) -> None:
        order_id = c["id"]
        c["reserved"] = {}
        for s in self.stoves:
            if s["dish"] is not None and s["dish"]["order_id"] == order_id:
                s["state"] = "idle"
                s["dish"] = None
                s["cook_ticks_left"] = 0
                s["ready_ticks"] = 0
        if self.hand is not None and self.hand["order_id"] == order_id:
            self.hand = None
        self.customers = [x for x in self.customers if x["id"] != order_id]

    def _adjust_reputation(self, delta: float) -> None:
        lo = float(self.t["reputation_min"])
        hi = float(self.t["reputation_max"])
        self.reputation = round(max(lo, min(hi, self.reputation + float(delta))), 6)

    def snapshot(self) -> dict:
        occupied = {c["table_id"]: c["id"] for c in self.customers}
        return {
            "player": {"pos": self.pos, "vel": self.vel},
            "stock": {k: self.stock[k] for k in sorted(self.stock) if self.stock[k] > 0},
            "hand": dict(self.hand) if self.hand is not None else None,
            "stoves": [
                {
                    "id": s["id"],
                    "pos": s["pos"],
                    "state": s["state"],
                    "dish": dict(s["dish"]) if s["dish"] is not None else None,
                    "cook_ticks_left": s["cook_ticks_left"],
                    "ready_ticks": s["ready_ticks"],
                }
                for s in sort_by_id(self.stoves)
            ],
            "tables": [
                {"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])}
                for tb in sort_by_id(self.tables)
            ],
            "customers": [
                {
                    "id": c["id"],
                    "table_id": c["table_id"],
                    "dish_id": c["dish_id"],
                    "order_tick": c["order_tick"],
                    "state": c["state"],
                    "patience_ticks_left": c["patience_ticks_left"],
                    "eat_ticks_left": c["eat_ticks_left"],
                    "order_status": c["order_status"],
                    "reserved": {k: c["reserved"][k] for k in sorted(c["reserved"]) if c["reserved"][k] > 0},
                    "base_price": c["base_price"],
                    "tip": c["tip"],
                }
                for c in sort_by_id(self.customers)
            ],
        }

    # --- một bước (PRD-0 mục F, Quán) -------------------------------------------
    def step(self, inp):
        events = []
        self.phase_tick += 1
        # 1. Tăng đồng hồ, giảm timer ca, nấu, ăn và kiên nhẫn.
        #    Chỉ tăng ready_ticks cho món đã ready ở đầu bước.
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        for s in self.stoves:
            if s["state"] == "ready":
                s["ready_ticks"] += 1
            elif s["state"] == "cooking":
                s["cook_ticks_left"] = max(0, s["cook_ticks_left"] - 1)
        for c in self.customers:
            if c["state"] == "waiting":
                c["patience_ticks_left"] = max(0, c["patience_ticks_left"] - 1)
            elif c["state"] == "eating":
                c["eat_ticks_left"] = max(0, c["eat_ticks_left"] - 1)

        # 2. Xét bếp theo id. Món nấu xong chuyển ready với ready_ticks = 0 (burn_s: null).
        for s in sort_by_id(self.stoves):
            if s["state"] == "cooking" and s["cook_ticks_left"] == 0:
                s["state"] = "ready"
                s["ready_ticks"] = 0
                events.append((
                    "dish_ready",
                    {"stove_id": s["id"], "order_id": s["dish"]["order_id"], "dish_id": s["dish"]["dish_id"]},
                ))

        # 3. Di chuyển rồi xét tối đa một interact, chọn theo (khoảng cách, bếp trước bàn, id).
        self._move(inp)
        if inp.pressed("interact"):
            self._interact(events)

        # 4. Theo id bàn: ăn xong trả tiền, hết kiên nhẫn (khi còn giờ), đóng ca (closing) và quan_end.
        self._resolve_customers_and_close(events)

        # 5. (lát 3) Còn giờ: lịch khách theo phase_tick sau tăng; khách sinh cuối bước tham gia từ bước sau.
        if self.time_left_ticks > 0 and self.random_customers and self._customer_due():
            self._spawn_customer(events)
        return events

    def _customer_due(self) -> bool:
        first = int(self.t["first_customer_tick"])
        interval = int(round(self.t["customer_interval_s"] * TICK))
        return self.phase_tick >= first and (self.phase_tick - first) % interval == 0

    def _spawn_customer(self, events) -> None:
        occupied = {c["table_id"] for c in self.customers}
        free_tables = [tb for tb in self.tables if tb["id"] not in occupied]
        if not free_tables:
            return  # không còn bàn: bỏ lượt
        table = sort_by_id(free_tables)[0]
        available = self._available()
        dishes = [dish_id for dish_id, dish in sorted(self.menu.items())
                  if self.menu_filter is None or dish_id in self.menu_filter
                  if all(available.get(kind, 0) >= qty for kind, qty in dish["recipe"].items())]
        if not dishes:
            events.append(("no_dish", {}))
            return
        dish_id = self.rng.get("customer_dish").choice(dishes)
        customer_id = self.ids.new("C")
        self.customers.append({
            "id": customer_id, "table_id": table["id"], "dish_id": dish_id,
            "order_tick": self.phase_tick, "state": "waiting",
            "patience_ticks_left": int(round(self.t["patience_s"] * TICK)),
            "eat_ticks_left": 0, "order_status": "reserved",
            "reserved": dict(self.menu[dish_id]["recipe"]), "base_price": None, "tip": None,
        })
        events.append(("customer_arrived", {"order_id": customer_id, "table_id": table["id"],
                                            "dish_id": dish_id}))

    def _interact(self, events) -> None:
        radius = float(self.t["interact_radius"])
        candidates = []
        for s in self.stoves:
            d = math.dist(self.pos, s["pos"])
            if d <= radius:
                candidates.append((d, 0, id_key(s["id"]), "stove", s))
        for tb in self.tables:
            d = math.dist(self.pos, tb["pos"])
            if d <= radius:
                candidates.append((d, 1, id_key(tb["id"]), "table", tb))
        if not candidates:
            return
        _, _, _, kind, target = min(candidates, key=lambda x: (x[0], x[1], x[2]))
        if kind == "stove":
            self._interact_stove(target, events)
        else:
            self._interact_table(target, events)

    def _interact_stove(self, stove, events) -> None:
        if stove["state"] == "idle":
            reserved_orders = [
                c for c in self.customers
                if c["state"] == "waiting" and c["order_status"] == "reserved"
            ]
            if not reserved_orders:
                return
            c = min(reserved_orders, key=lambda x: (x["order_tick"], id_key(x["table_id"])))
            items = []
            for k in sorted(c["reserved"]):
                qty = c["reserved"][k]
                if qty > 0:
                    self.stock[k] = self.stock.get(k, 0) - qty
                    if self.stock[k] <= 0:
                        self.stock.pop(k, None)
                    items.extend([k] * qty)
            c["reserved"] = {}
            base_price = int(self.menu[c["dish_id"]]["price"])
            c["order_status"] = "assigned"
            c["base_price"] = base_price
            stove["state"] = "cooking"
            stove["dish"] = {"order_id": c["id"], "dish_id": c["dish_id"], "base_price": base_price}
            stove["cook_ticks_left"] = int(round(self.menu[c["dish_id"]]["cook_s"] * TICK))
            stove["ready_ticks"] = 0
            events.append((
                "cook_started",
                {
                    "stove_id": stove["id"],
                    "order_id": c["id"],
                    "dish_id": c["dish_id"],
                    "items": items,
                    "base_price": base_price,
                },
            ))
        elif stove["state"] == "ready":
            if self.hand is not None:
                return
            dish = dict(stove["dish"])
            self.hand = dish
            stove["state"] = "idle"
            stove["dish"] = None
            stove["cook_ticks_left"] = 0
            stove["ready_ticks"] = 0
            events.append((
                "dish_picked",
                {"stove_id": stove["id"], "order_id": dish["order_id"], "dish_id": dish["dish_id"]},
            ))

    def _interact_table(self, table, events) -> None:
        if self.hand is None:
            return
        c = next((x for x in self.customers if x["table_id"] == table["id"]), None)
        if c is None or c["state"] != "waiting" or c["id"] != self.hand["order_id"]:
            return
        patience_max = int(round(self.t["patience_s"] * TICK))
        ratio = c["patience_ticks_left"] / patience_max if patience_max > 0 else 0.0
        base_price = int(self.hand["base_price"])
        tip = math.floor(base_price * self.t["tip_rate"]) if ratio >= self.t["tip_min_patience_ratio"] else 0
        c["state"] = "eating"
        c["order_status"] = "served"
        c["eat_ticks_left"] = int(round(self.t["eat_s"] * TICK))
        c["base_price"] = base_price
        c["tip"] = tip
        self.hand = None
        events.append((
            "served",
            {
                "order_id": c["id"],
                "table_id": c["table_id"],
                "dish_id": c["dish_id"],
                "patience_ticks_left": c["patience_ticks_left"],
                "base_price": base_price,
                "tip": tip,
            },
        ))

    def _collect_payment(self, c, reason: str, events) -> None:
        base_price = int(c["base_price"])
        tip = int(c["tip"])
        amount = base_price + tip
        self.money += amount
        self.earned += amount
        self.shift_earned += amount
        if tip > 0:
            self._adjust_reputation(self.t["tip_reputation"])
        events.append((
            "paid",
            {
                "order_id": c["id"],
                "table_id": c["table_id"],
                "base_price": base_price,
                "tip": tip,
                "amount": amount,
                "reason": reason,
            },
        ))
        self._remove_customer(c)

    def _resolve_customers_and_close(self, events) -> None:
        by_table = {c["table_id"]: c for c in self.customers}
        closing = self.time_left_ticks == 0
        for tb in sort_by_id(self.tables):
            c = by_table.get(tb["id"])
            if c is None:
                continue
            if c["state"] == "eating" and c["eat_ticks_left"] == 0:
                self._collect_payment(c, "finished_eating", events)
            elif not closing:
                # Lát 3 / patience timeout khi ca còn giờ
                if c["state"] == "waiting" and c["patience_ticks_left"] == 0:
                    self._adjust_reputation(self.t["left_reputation_delta"])
                    events.append((
                        "customer_left",
                        {
                            "order_id": c["id"],
                            "table_id": c["table_id"],
                            "reason": "patience",
                            "reputation": self.reputation,
                        },
                    ))
                    self._remove_customer(c)
            else:
                if c["state"] == "eating":
                    self._collect_payment(c, "closing", events)
                else:
                    events.append((
                        "customer_left",
                        {
                            "order_id": c["id"],
                            "table_id": c["table_id"],
                            "reason": "closing",
                            "reputation": self.reputation,
                        },
                    ))
                    self._remove_customer(c)
        if closing:
            self.done = True
            self.reason = "time"
            events.append((
                "quan_end",
                {
                    "reason": "time",
                    "money": self.money,
                    "earned": self.earned,
                    "shift_earned": self.shift_earned,
                    "reputation": self.reputation,
                },
            ))

    def _move(self, inp):
        speed = self.t["walk_speed"]
        mx, mz = inp.move
        self.vel = ramp_velocity(self, (mx * speed, mz * speed), int(self.t.get("ramp_max_ticks", 6)))
        b = self.t["bounds"]
        for i, axis in enumerate(("x", "z")):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i], self.vel[i] = lo, max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i], self.vel[i] = hi, min(0.0, self.vel[i])
