# TEAM

**Tên nhóm:** nhom6ae  **Số người:** 6  (khớp `team_size` trong `game.contract.json`)

| Thành viên | GitHub handle | Module chính | Vai quy trình | Người dự phòng cho |
|---|---|---|---|---|
| Ngô Chí Vĩnh (2A202603724) | NgChiVinh | `sim/gather` lát 1: bơi, oxy, ngạt, Máu, giỏ · `docs/contracts/` · AGENTS.md + skills | Integrator (chốt hợp đồng kho/sự kiện, tích hợp, gắn tag) | TrungHieuPh |
| Phan Trung Hiếu (2A202603763) | TrungHieuPh | `sim/gather` lát 2: hái, bắt cá, cập bến, ghi file kho | PO (hỏi Anh Năm hàng xóm, giữ `docs/clarify.md`) | NgChiVinh |
| Lê Đức Trúc Lâm (2A202603787) | truclamld | `client/ui`: HUD hai buổi (`chonoi/web/`, `live.py`) · README (chạy, điều khiển, điểm) | Scrum/Release (theo dõi mốc, standup) | HoangQuan23112004 (từ phút 20) |
| Lê Viết Khoa (2A202603737) | khoa-asta | `qa`: test hộp đen theo AC, smoke hai tiến trình, `docs/verification/` + `docs/proof/` | QA lead | truclamld |
| Hoàng Dương Anh Quân (2A202603735) | HoangQuan23112004 | `sim/quan` lát 4: bếp, bưng, phục vụ, tiền, boa, uy tín, đóng ca | — | 22520160 |
| Phạm Lê Chuẩn (2A202603784) | 22520160 | `sim/quan` lát 3: khách, giữ chỗ, kiên nhẫn, rời bàn · kiểm scenario quán (`scenario.py`) | — | HoangQuan23112004 |

**Vai quy trình:** PO (đầu mối hỏi giảng viên, giữ `docs/clarify.md`) · Integrator (giữ `docs/contracts/`, gắn tag) · QA lead · Scrum/Release. Có thể kiêm.

## Thỏa thuận làm việc nhóm (điền trong 15 phút kickoff, ≤ 10 dòng)

- Kênh liên lạc: nhóm chat của nhóm + nói trực tiếp tại lab.
- Khi bất đồng về thiết kế: mỗi bên nói 2 phút, không xong thì Integrator quyết và ghi lý do vào `docs/clarify.md` hoặc ADR.
- Khi ai đó trễ hoặc vướng quá 10 phút: báo ngay trong kênh, người dự phòng (cột cuối) vào giúp hoặc nhận việc.
- Giờ standup giữa phase: giữa mỗi phase, mỗi người 1 dòng trong `docs/standup.md`.
- Cách đọc code của nhau: mỗi người đọc lát của người dự phòng mình trước khi gộp; QA lead chạy test hộp đen.
- Cách làm việc với Git: nhánh ngắn theo lát rồi gộp vào `main` (pull --rebase, chạy test trước khi push); chỉ Integrator gắn tag `phase-n`.

## Việc theo phase (chi tiết, phụ thuộc, AC: `docs/plan/phase-n.md`; đề: `docs/prd/phase-n.md`)

| Thành viên | Phase 1 ([plan](docs/plan/phase-1.md)) | Phase 2 ([plan](docs/plan/phase-2.md) · [đề](docs/prd/phase-2.md)) | Phase 3 ([ADR](docs/adr/0001-kho-ca-the-do-tuoi.md) · [đề](docs/prd/phase-3.md)) |
|---|---|---|---|
| NgChiVinh | Lát 1 gather, hợp đồng, harness, tích hợp | **#0 khung v1.1 (push trước)** + **#4 `--mode day` + pause**, tích hợp, tag | adapter v1.2 (`items.py`, `inventory.py`, contract, scenario) + day/Shop, tích hợp nhánh `v1.2`, tag |
| TrungHieuPh | Lát 2 gather, PO | **#1 số chuẩn gather + cá bơi/sinh**, PO (hỏi Anh Năm) | Lặn: giỏ cá thể, hao tươi, `spoiled` (hold), hái/bắt tạo cá thể, `gather_end.inventory` v1.2 |
| 22520160 | Lát 3 khách + kiểm scenario quán | **#2 Cá Sấu, `monster_hit`, ngất do quái** (`chonoi/sim/monsters.py`) | Quán: giữ chỗ theo id, ươn → nhả + giữ lại; `monster_hit.lost` cá thể; mở rộng `snake` nếu kịp |
| HoangQuan23112004 | Lát 4 bếp, phục vụ, tiền | **#3 2 bếp/4 bàn/6 món, lọc menu theo kế hoạch + Shop** (`chonoi/sim/shop.py`) | Quán: kho cá thể hao 0.25/s, nấu tiêu id, giá theo tươi, `cook_started.items`; mở rộng `burn` nếu kịp |
| truclamld | HUD, README, Scrum | **#5 menu, các màn hình ngày, pause, HUD v1.1**, retro nhanh | HUD độ tươi / nhãn ươn (giỏ, kho), `hud_check` |
| khoa-asta | QA, verification | **#6 regression P1 số chuẩn, smoke phút 20, smoke day, verification P2** | QA v1.2: test ngưỡng, giữ lại, giá, smoke file + day, regression, verification P3 |
