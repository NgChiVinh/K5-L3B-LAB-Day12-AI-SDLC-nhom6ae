# Ma trận kiểm chứng Phase 2

Cập nhật trên `main` tại commit `fe3930f` (bản tích hợp cuối, ngay trước commit gắn tag `phase-2`; code giống hệt —
commit gắn tag chỉ thêm bằng chứng và file này). Bản trước (khoa-asta) chạy ở `d66c50d`, trước khi có Cá Sấu và PR #5.

| AC | Kiểm chứng / bằng chứng | Trạng thái |
|---|---|---|
| AC-P2-01 | Contract v1.1, số chuẩn, 6 nguyên liệu, 6 món, `day_plan`, `shop`: `chonoi/contract.py` kiểm khi load; `tests/test_qa_phase2.py`, `tests/test_smoke_p1.py` | đạt |
| AC-P2-02 | Cá bơi (1.5 m/s, đổi hướng mỗi 120 bước, phản xạ mép), sinh mỗi 360 tick, trần 12, 8 đàn đầu ca: `tests/test_gather_fish.py`, `tests/test_qa_phase2.py` | đạt |
| AC-P2-03 | Cá Sấu patrol/chase/recoil, `monster_hit` (−1 Máu, rơi floor(n/2) LIFO, bất tử 90), ngất do quái, M2 từ Ngày 3: `tests/test_gather_monsters.py`, `tests/test_monsters_edges.py`; [day-multi.md](../proof/phase-2/day-multi.md) (M1 Ngày 1–2, M1+M2 Ngày 3) | đạt (cách hiểu bất tử t+90 chờ xác nhận — `docs/clarify.md` #12) |
| AC-P2-04 | 2 bếp / 4 bàn / 6 món, lọc menu theo kế hoạch trong day: `tests/test_p2_quan_shop.py` | đạt |
| AC-P2-05 | Shop: đúng giá, `buy_failed` funds/max_level/unknown, buy trước `shop_done`, tự đóng 600 tick: `tests/test_day_p2.py`, `tests/test_p2_quan_shop.py`; [day-multi.md](../proof/phase-2/day-multi.md) mục B | đạt |
| AC-P2-06 | `--mode day`: thứ tự pha, kế hoạch D1–D5, chốt Ngày khi Shop đóng, cấp oxygen/hp áp từ Ngày kế, ≤ 20 s/Ngày: `tests/test_day_p2.py`; [day-smoke.md](../proof/phase-2/day-smoke.md), [day-multi.md](../proof/phase-2/day-multi.md) (5 Ngày 1.9 s; Ngày 2 oxy 2700, Máu 4) | đạt |
| AC-P2-07 | Pause/resume dừng mọi timer ở gather, quán, Shop: `tests/test_day_p2.py::Pause` | đạt |
| AC-P2-08 | Menu chính, pause, màn hình ngày, HUD v1.1 (PR #7): [hud.md](../proof/phase-2/hud.md) — 56/57 (480 px: "Độ sâu" đè Máu). **Còn thiếu:** chữ ≥ 18 px ở 1280×720, "Thủy quái!" + viền tím, "Hết hơi!", nút "Thoát" ở menu chính. Chưa kiểm chơi tay trọn vòng ngày trên trình duyệt | **một phần** |
| AC-P2-09 | Regression P1 + P2 với số chuẩn: [regression.txt](../proof/phase-2/regression.txt) **108/108 OK**; smoke tích hợp gather → quan: [integration.md](../proof/phase-2/integration.md) (khoa-asta), [smoke.md](../proof/phase-2/smoke.md) (7/7); test đổi do luật v1.1 đều ghi lý do trong commit (`ac0bdd8`, `2542a39`, `57ef9b3`) | đạt |

## Đánh giá ngắn
- Đạt: AC-P2-01 → 07, 09. Một phần: AC-P2-08 (HUD v1.1 thiếu 4 mục, chưa chơi tay trọn vòng).
- Chưa xong theo DoD: retro nhanh Phase 2 (`docs/retro.md` trống); nhật ký AI Phase 2 của 22520160, HoangQuan23112004, truclamld; chưa có mục mở rộng nào (`extensions: []`, nhóm 6 người cần ≥ 2 trong cả lab).
- Điều cần chỉnh cho Phase 3: chạy verification trên commit gắn tag (bảng trước đó cũ 2 lần tích hợp); hoàn tất HUD v1.1; làm 2 mở rộng (gợi ý `burn`, `snake`).
