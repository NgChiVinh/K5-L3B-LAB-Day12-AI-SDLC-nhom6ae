"""Buổi tối — Mở Quán. KHUNG: đi lại, chặn biên, đồng hồ, kho nạp từ file/scenario.

Nhóm viết tiếp (PRD-0 mục F, Quán):
  TODO(nhóm, lát 3): khách đến theo lịch, chọn món nấu được, giữ chỗ nguyên liệu, kiên nhẫn,
                     bỏ đi (customer_left), no_dish, vòng đời khách.
  TODO(nhóm, lát 4): interact tại bếp/bàn (cook_started, dish_ready, dish_picked, served),
                     ăn xong trả tiền (paid), boa, uy tín, hết ca (quan_end).
"""

from ..ids import sort_by_id
from ..errors import BadInput
from .ramp import ramp_velocity

TICK = 60.0


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None):
        t = tuning["quan"]
        self.t = t
        self.menu = tuning["menu"]
        self.rng = streams
        self.ids = ids
        p = scenario.get("player", {})
        self.pos = list(p.get("pos", t["start_pos"]))
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        # kho: --inventory HOẶC scenario.stock (cả hai -> cli đã báo mã 2)
        self.stock = dict(inventory if inventory is not None else scenario.get("stock", {}))
        self.hand = scenario.get("hand")
        self.time_left_ticks = scenario.get("time_left_ticks", int(round(t["duration_s"] * 60)))
        self.phase_tick = 0
        self.random_customers = scenario.get("random_customers", True)
        self.reputation = scenario.get("reputation", t["reputation_initial"])
        self.stoves = [dict(s, state=s.get("state", "idle"), dish=s.get("dish"),
                            cook_ticks_left=s.get("cook_ticks_left", 0), ready_ticks=s.get("ready_ticks", 0))
                       for s in self._merge(t["stoves"], scenario.get("stoves", []))]
        self.tables = self._merge(t["tables"], scenario.get("tables", []))
        patience = int(round(t["patience_s"] * TICK))
        self.customers = []
        for source in scenario.get("customers", []):
            c = dict(source)
            c.setdefault("order_tick", 0)
            c.setdefault("state", "waiting")
            c.setdefault("patience_ticks_left", patience)
            c.setdefault("eat_ticks_left", 0)
            c.setdefault("order_status", "reserved")
            c.setdefault("reserved", dict(self.menu[c["dish_id"]]["recipe"])
                         if c["order_status"] == "reserved" else {})
            c.setdefault("base_price", None)
            c.setdefault("tip", None)
            self.customers.append(c)
        for e in self.customers:
            ids.reserve(e["id"])
        reserved = {}
        for c in self.customers:
            for kind, quantity in c.get("reserved", {}).items():
                reserved[kind] = reserved.get(kind, 0) + quantity
        if any(quantity > self.stock.get(kind, 0) for kind, quantity in reserved.items()):
            raise BadInput("khách giữ chỗ vượt tồn kho")
        self.money = 0
        self.earned = 0
        self.shift_earned = 0
        self.done = False
        self.reason = None

    @staticmethod
    def _merge(defaults, updates):
        by_id = {d["id"]: dict(d) for d in defaults}
        for u in updates:
            if u["id"] not in by_id:
                from ..errors import BadInput
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            by_id[u["id"]].update(u)
        return sort_by_id(list(by_id.values()))

    def snapshot(self) -> dict:
        occupied = {c["table_id"]: c["id"] for c in self.customers}
        return {
            "player": {"pos": self.pos},
            "stock": {k: self.stock[k] for k in sorted(self.stock) if self.stock[k] > 0},
            "hand": self.hand,
            "stoves": [{k: s.get(k) for k in ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks")}
                       for s in self.stoves],
            "tables": [{"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])} for tb in self.tables],
            "customers": sort_by_id(self.customers),
        }

    def step(self, inp):
        events = []
        self.phase_tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        # F.1: chỉ khách đang chờ mất kiên nhẫn; khách đang ăn dùng timer của lát 4.
        for c in self.customers:
            if c["state"] == "waiting":
                c["patience_ticks_left"] = max(0, c["patience_ticks_left"] - 1)
        self._move(inp)
        # Lát 4 đặt xử lý interact trước lời gọi này (F.3); deadline patience được xử lý ở F.4.
        if self.time_left_ticks > 0:
            for c in list(sort_by_id(self.customers)):
                if c["state"] == "waiting" and c["patience_ticks_left"] == 0:
                    self.reputation = self._clamp_reputation(
                        self.reputation + self.t["left_reputation_delta"])
                    events.append(("customer_left", {"order_id": c["id"], "table_id": c["table_id"],
                                                       "reason": "patience", "reputation": self.reputation}))
                    self._remove_customer(c)
        # F.5: lịch tính bằng phase_tick sau tăng; khách sinh cuối bước chỉ tham gia từ bước sau.
        if self.time_left_ticks > 0 and self._customer_due() and self.random_customers:
            free_tables = [tb for tb in self.tables
                           if not any(c["table_id"] == tb["id"] for c in self.customers)]
            if free_tables:
                table = sort_by_id(free_tables)[0]
                available = self._available()
                dishes = [dish_id for dish_id, dish in sorted(self.menu.items())
                          if all(available.get(kind, 0) >= qty for kind, qty in dish["recipe"].items())]
                if not dishes:
                    events.append(("no_dish", {}))
                else:
                    dish_id = self.rng.get("customer_dish").choice(dishes)
                    dish = self.menu[dish_id]
                    customer_id = self.ids.new("C")
                    c = {"id": customer_id, "table_id": table["id"], "dish_id": dish_id,
                         "order_tick": self.phase_tick, "state": "waiting",
                         "patience_ticks_left": int(round(self.t["patience_s"] * TICK)),
                         "eat_ticks_left": 0, "order_status": "reserved",
                         "reserved": dict(dish["recipe"]), "base_price": None, "tip": None}
                    self.customers.append(c)
                    events.append(("customer_arrived", {"order_id": customer_id, "table_id": table["id"],
                                                          "dish_id": dish_id}))
        if self.time_left_ticks <= 0:
            self.done = True
            self.reason = "time"
            events.append(("quan_end", {"reason": "time", "money": self.money, "earned": self.earned,
                                        "shift_earned": self.shift_earned, "reputation": self.reputation}))
        return events

    def _customer_due(self):
        first = int(self.t["first_customer_tick"])
        interval = int(round(self.t["customer_interval_s"] * TICK))
        return self.phase_tick >= first and (self.phase_tick - first) % interval == 0

    def _available(self):
        """Kho còn có thể dùng cho đơn mới: tồn vật lý trừ mọi phần đang giữ."""
        available = dict(self.stock)
        for c in self.customers:
            for kind, quantity in c.get("reserved", {}).items():
                available[kind] = available.get(kind, 0) - quantity
        return {kind: max(0, quantity) for kind, quantity in available.items()}

    def _remove_customer(self, c):
        """Nhả giữ chỗ và dọn món còn thuộc đơn; nguyên liệu đã tiêu thụ không được hoàn."""
        for stove in self.stoves:
            payload = stove.get("dish")
            if payload and payload.get("order_id") == c["id"]:
                stove.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)
        if self.hand and self.hand.get("order_id") == c["id"]:
            self.hand = None
        if c in self.customers:
            self.customers.remove(c)

    def _clamp_reputation(self, value):
        return min(self.t["reputation_max"], max(self.t["reputation_min"], value))

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
