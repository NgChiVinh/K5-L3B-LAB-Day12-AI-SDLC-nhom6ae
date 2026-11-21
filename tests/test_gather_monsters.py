"""Cá Sấu, chạm, bất tử và dữ liệu quái — TICKET-02 mục 1.2."""

import unittest

from helpers import Workdir, events, read_jsonl, run_headless, snapshots, write_json


def run_gather(w, block, ticks):
    scenario = write_json(w.path("scenario.json"), {"gather": {"random_fish": False, **block}})
    output = w.path("run.jsonl")
    code, err = run_headless("--mode", "gather", "--seed", "8", "--scenario", scenario,
                             "--ticks", str(ticks), "--snapshot-every", "1", "--out", output)
    assert code == 0, err
    return read_jsonl(output)


def crocodile(**updates):
    monster = {"id": "M9", "kind": "ca_sau", "pos": [20, 10],
               "waypoints": [[20, 10], [40, 10]], "state": "chase"}
    monster.update(updates)
    return monster


class CrocodileHit(unittest.TestCase):
    def test_hit_drops_half_lifo_and_starts_recoil(self):
        with Workdir() as w:
            rows = run_gather(w, {"player": {"pos": [20, 10]},
                                  "hold": ["ca_loc", "ca_linh", "bong_sung", "keo_neo"],
                                  "monsters": [crocodile()]}, 2)
            hit = events(rows, "monster_hit")
            self.assertEqual(len(hit), 1)
            self.assertEqual(hit[0]["data"], {"monster_id": "M9", "hp": 2,
                                                "lost": ["keo_neo", "bong_sung"], "pos": [20.0, 10.0]})
            s1, s2 = snapshots(rows)[1:]
            self.assertEqual(s1["hold"], ["ca_loc", "ca_linh"])
            self.assertEqual(s1["monsters"][0]["state"], "recoil")
            self.assertEqual(s1["monsters"][0]["state_ticks_left"], 60)
            self.assertAlmostEqual(s2["monsters"][0]["pos"][0], 20 + 2 / 60, places=3)
            self.assertEqual(s2["monsters"][0]["state_ticks_left"], 59)

    def test_invulnerability_blocks_hits_for_full_90_ticks(self):
        with Workdir() as w:
            rows = run_gather(w, {"player": {"pos": [20, 10], "invuln_ticks": 90},
                                  "monsters": [crocodile()]}, 90)
            self.assertEqual(events(rows, "monster_hit"), [])
            self.assertEqual(snapshots(rows)[-1]["player"]["invuln_ticks"], 0)

    def test_one_hit_uses_nearest_then_id_order(self):
        with Workdir() as w:
            farther = crocodile(id="M1", pos=[20, 12], waypoints=[[20, 12], [40, 12]])
            tied_later = crocodile(id="M10")
            tied_first = crocodile(id="M2")
            rows = run_gather(w, {"player": {"pos": [20, 10]},
                                  "monsters": [farther, tied_later, tied_first]}, 1)
            self.assertEqual([e["data"]["monster_id"] for e in events(rows, "monster_hit")], ["M2"])

    def test_monster_faint_drops_rest_of_bag_and_ends_gather(self):
        with Workdir() as w:
            rows = run_gather(w, {"player": {"pos": [20, 10], "hp": 1},
                                  "hold": ["ca_loc", "ca_linh", "bong_sung"],
                                  "monsters": [crocodile()]}, 4)
            self.assertEqual([e["name"] for e in events(rows)], ["monster_hit", "faint", "gather_end"])
            self.assertEqual(events(rows, "faint")[0]["data"], {
                "cause": "monster", "lost": ["ca_linh", "ca_loc"], "hp": 0,
            })
            self.assertEqual(rows[-1]["reason"], "fainted")
            self.assertEqual(snapshots(rows)[-1]["hold"], [])

    def test_default_gather_spawns_m1_but_not_day_three_m2(self):
        with Workdir() as w:
            rows = run_gather(w, {}, 0)
            self.assertEqual([m["id"] for m in snapshots(rows)[0]["monsters"]], ["M1"])


class MonsterScenario(unittest.TestCase):
    def test_invalid_monster_scenarios_return_exit_two(self):
        base = crocodile()
        invalid = (
            {**base, "target_idx": 2},
            {**base, "pos": [20, 9]},
            {**base, "state": "recoil", "recoil_dir": [1, 0]},
            {**base, "state": "recoil", "state_ticks_left": 2, "recoil_dir": [2, 0]},
            {**base, "kind": "unknown"},
        )
        with Workdir() as w:
            for monster in invalid:
                scenario = write_json(w.path("scenario.json"), {"gather": {"monsters": [monster]}})
                code, _ = run_headless("--mode", "gather", "--seed", "1", "--ticks", "0",
                                       "--scenario", scenario, "--out", w.path("out.jsonl"))
                self.assertEqual(code, 2, monster)


if __name__ == "__main__":
    unittest.main()
