# Retro nhóm

## Phase 2 (nhanh)
> Integrator (NgChiVinh) soạn từ lịch sử git, PR và bằng chứng của phase; cả nhóm sửa/bổ sung ý của mình.

- Điều tốt:
  - Khung v1.1 (contract số chuẩn, nút mới, `--days`) lên `main` sớm (`ac0bdd8`) nên 4 lát làm song song trên cùng nền.
  - `--mode day` + Shop + pause có trước (`2542a39`) → tích hợp sớm; cả 4 lát lõi (cá bơi/sinh, Cá Sấu, 2 bếp/4 bàn/6 món, vòng ngày) vào `main` trước tag, **108/108 test**, 1 Ngày ≈ 0.4 s.
  - Test bắt lỗi thật trước khi tới máy chấm: Shop chưa hiện cấp vừa mua; 2 lỗi lệch 1 tick của Cá Sấu (PR #6) — phát hiện nhờ đọc code theo PRD + dựng scenario, dù `merge-tree` và test cũ đều xanh.
  - QA có smoke tích hợp ở phút 20 (`docs/proof/phase-2/integration.*`) và regression; thêm bằng chứng nhiều Ngày + nâng cấp (`day-multi.md`).
  - Commit của Lâm, Quân, Khoa, Chuẩn đã gắn đúng tài khoản GitHub.
- Điều tệ:
  - Bảng `verification/phase-2.md` chạy ở commit cũ (`d66c50d`, trước Cá Sấu) — suýt gắn tag trên bằng chứng sai; phải chạy lại trên `fe3930f` ngay trước tag.
  - Shop không ai bắt đầu kịp → Integrator viết thay để vòng ngày không bị chặn; kế hoạch phải sửa giữa phase.
  - HUD v1.1 trễ và lỗi (chữ 10–13 px, phím Q/M/Enter không chạy, DayIntro… không hiện) → AC-P2-08 chỉ "một phần" lúc gắn tag.
  - Commit `d66c50d` (cá bơi) lại không gắn tài khoản GitHub (đổi email máy).
  - Một số nhánh tự merge vào `main` không qua kiểm của Integrator; may là test vẫn xanh.
  - Retro, nhật ký AI (thiếu 22520160, truclamld), phản tư cá nhân và 2 mục mở rộng (đang 0/2) dồn về cuối.
- 1 hành động cho Phase 3: **Trước mỗi lần gắn tag, Integrator chạy lại `run-tests`, `smoke-proof`, `hud_check` trên ĐÚNG commit sẽ gắn tag và cập nhật `docs/verification/phase-n.md` từ kết quả đó; mọi lát vào `main` qua PR để Integrator chạy cả bộ test trước khi merge.** — Người nhận: NgChiVinh (Integrator). Kèm theo: bắt đầu 2 mở rộng ngay đầu Phase 3 (`burn` — HoangQuan23112004, `snake` — 22520160).

## Phase 4 (cuối)
- Rà lại hành động Phase 2: đã làm chưa? vì sao?
- Điều tốt / điều tệ:
- Số liệu: số commit theo người, cách đọc code của nhau, token theo người:
- Một lần AI sai và cách nhóm phát hiện:
- Nếu làm lại, đổi gì:
