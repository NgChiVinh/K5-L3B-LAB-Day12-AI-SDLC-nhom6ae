# TEAM

**Tên nhóm:** nhom6ae  **Số người:** 6  (khớp `team_size` trong `game.contract.json`)

| Thành viên | GitHub handle | Module chính | Vai quy trình | Người dự phòng cho |
|---|---|---|---|---|
| Ngô Chí Vĩnh (2A202603724) | NgChiVinh | `sim/gather` lát 1: bơi, oxy, ngạt, Máu, giỏ · `docs/contracts/` · AGENTS.md + skills | Integrator (chốt hợp đồng kho/sự kiện, tích hợp, gắn tag) | TrungHieuPh |
| Phan Trung Hiếu (2A202603763) | TrungHieuPh | `sim/gather` lát 2: hái, bắt cá, cập bến, ghi file kho | PO (hỏi Anh Năm hàng xóm, giữ `docs/clarify.md`) | NgChiVinh |
| Lê Đức Trúc Lâm (2A202603787) | truclamld | `client/ui`: HUD hai buổi (`chonoi/web/`, `live.py`) · README (chạy, điều khiển, điểm) | Scrum/Release (theo dõi mốc, standup) | 22520160 (từ phút 20) |
| Lê Viết Khoa (2A202603737) | khoa-asta | `qa`: test hộp đen theo AC, smoke hai tiến trình, `docs/verification/` + `docs/proof/` | QA lead | truclamld |
| Hoàng Dương Anh Quân (2A202603735) | HoangQuan23112004 | `sim/quan` lát 3: khách, giữ chỗ, kiên nhẫn, rời bàn · kiểm scenario quán (`scenario.py`) | — | 22520160 |
| Phạm Lê Chuẩn (2A202603784) | 22520160 | `sim/quan` lát 4: bếp, bưng, phục vụ, tiền, boa, uy tín, đóng ca | — | HoangQuan23112004 |

**Vai quy trình:** PO (đầu mối hỏi giảng viên, giữ `docs/clarify.md`) · Integrator (giữ `docs/contracts/`, gắn tag) · QA lead · Scrum/Release. Có thể kiêm.

## Thỏa thuận làm việc nhóm (điền trong 15 phút kickoff, ≤ 10 dòng)

- Kênh liên lạc: nhóm chat của nhóm + nói trực tiếp tại lab.
- Khi bất đồng về thiết kế: mỗi bên nói 2 phút, không xong thì Integrator quyết và ghi lý do vào `docs/clarify.md` hoặc ADR.
- Khi ai đó trễ hoặc vướng quá 10 phút: báo ngay trong kênh, người dự phòng (cột cuối) vào giúp hoặc nhận việc.
- Giờ standup giữa phase: giữa mỗi phase, mỗi người 1 dòng trong `docs/standup.md`.
- Cách đọc code của nhau: mỗi người đọc lát của người dự phòng mình trước khi gộp; QA lead chạy test hộp đen.
- Cách làm việc với Git: nhánh ngắn theo lát rồi gộp vào `main` (pull --rebase, chạy test trước khi push); chỉ Integrator gắn tag `phase-n`.
