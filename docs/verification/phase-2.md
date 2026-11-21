# Ma trận kiểm chứng Phase 2

Trạng thái trên branch `khoa-verification`, sau khi tích hợp `origin/main` tại `fe3930f`.

| AC | Kiểm chứng / bằng chứng | Trạng thái | Chặn bởi |
|---|---|---|---|
| AC-P2-01 | Contract v1.1, dữ liệu chuẩn, 8 đàn, N5/N6, 6 món; regression hộp đen | đạt | — |
| AC-P2-02 | Số đàn/nút, yield cá kèo, cá bơi, tăng tuổi và sinh theo lịch có regression | đạt | — |
| AC-P2-03 | Cá Sấu, hit/faint, bất tử và các ca biên có regression | đạt | — |
| AC-P2-04 | 2 bếp/4 bàn hoạt động; sáu món và lọc menu theo kế hoạch ngày có regression | đạt | — |
| AC-P2-05 | Mua nâng cấp, sai giá/thiếu tiền/cấp tối đa, `shop_done` và tự đóng Shop có test | đạt | — |
| AC-P2-06 | Thứ tự pha, kế hoạch D1–D5, kết thúc ngày và giới hạn tick có test; smoke 1 ngày và 5 ngày đạt | đạt | — |
| AC-P2-07 | Pause/resume và timer dừng có test trong gather, quán và Shop của day mode | đạt | — |
| AC-P2-08 | HUD check đạt 56/57; còn một va chạm ở gather 480px | một phần | Lâm #5 |
| AC-P2-09 | Regression 108/108; smoke bàn giao kho và D1/D5 đạt; HUD check còn một lỗi | một phần | Lâm #5 và tag tích hợp |

## Kết quả đã chạy

- Windows PowerShell: `$env:PYTHONPATH="tests;."`
- `python3 -m unittest discover -s tests -v`: **108/108 OK** sau khi tích hợp `origin/main` tại `fe3930f`.
- Smoke gather → quan: [`integration.md`](../proof/phase-2/integration.md). Dùng giỏ fixture tại bến nên chỉ xác nhận luồng bàn giao kho.
- Smoke vòng ngày: [`day-smoke.md`](../proof/phase-2/day-smoke.md). Xác nhận chuyển pha/kế hoạch/kết thúc D1 và D1–D5; không có input gameplay.
- HUD: [`hud.md`](../proof/phase-2/hud.md) — **56/57**, lỗi duy nhất là `♥♥♥` va chạm với `Độ sâu 5.5 m` ở 480px.

## Việc còn chặn

- Các lát #1–#4 đã tích hợp vào `main` tại `fe3930f` và regression tương ứng đều đạt.
- Lâm #5: cần sửa va chạm HUD ở gather 480px; AC-P2-08 chưa đạt hoàn toàn.
- Khoa #6: regression 108/108, smoke bàn giao kho và D1/D5 đã chạy; còn ghi nhận và theo dõi lỗi HUD trong bằng chứng.
