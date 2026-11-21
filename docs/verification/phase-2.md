# Ma trận kiểm chứng Phase 2

Trạng thái trên branch `khoa-verification`, sau khi tích hợp `origin/main` tại `d66c50d`.

| AC | Kiểm chứng / bằng chứng | Trạng thái | Chặn bởi |
|---|---|---|---|
| AC-P2-01 | Contract v1.1, dữ liệu chuẩn, 8 đàn, N5/N6, 6 món; regression hộp đen | đạt | — |
| AC-P2-02 | Số đàn/nút, yield cá kèo, cá bơi, tăng tuổi và sinh theo lịch có regression | đạt | — |
| AC-P2-03 | Chưa có `monsters.py` hoặc kiểm chứng Cá Sấu | chưa làm | Chuẩn #2 |
| AC-P2-04 | Cấu hình 2 bếp/4 bàn/6 món có test; chưa có kiểm chứng hành vi đồng thời đa bếp/bàn và lọc menu trong ngày | một phần | Quân #3 |
| AC-P2-05 | Mua nâng cấp, sai giá/thiếu tiền/cấp tối đa, `shop_done` và tự đóng Shop có test | đạt | — (Shop do Vĩnh #4 tích hợp) |
| AC-P2-06 | Thứ tự pha, kế hoạch D1–D5, kết thúc ngày và giới hạn tick có test; smoke 1 ngày và 5 ngày đạt | đạt | — |
| AC-P2-07 | Pause/resume và timer dừng có test trong gather, quán và Shop của day mode | đạt | — |
| AC-P2-08 | `live.py` hỗ trợ day, nhưng chưa kiểm chứng các màn hình, HUD v1.1 và menu pause trên UI | chưa làm | Lâm #5 |
| AC-P2-09 | Regression 92/92; smoke bàn giao kho và smoke ngày đạt. Chưa phải smoke gameplay đầy đủ hoặc kết quả gắn tag cuối | một phần | #2, #3, #5 và tag tích hợp |

## Kết quả đã chạy

- Windows PowerShell: `$env:PYTHONPATH="tests;."`
- `python3 -m unittest discover -s tests -v`: **92/92 OK** sau khi tích hợp `origin/main` tại `d66c50d`.
- Smoke gather → quan: [`integration.md`](../proof/phase-2/integration.md). Dùng giỏ fixture tại bến nên chỉ xác nhận luồng bàn giao kho.
- Smoke vòng ngày: [`day-smoke.md`](../proof/phase-2/day-smoke.md). Xác nhận chuyển pha/kế hoạch/kết thúc D1 và D1–D5; không có input gameplay.

## Việc còn chặn

- Hiếu #1: đã tích hợp cá bơi, tăng tuổi và sinh định kỳ tại `d66c50d`; regression có trong `tests/test_gather_fish.py`.
- Chuẩn #2: chưa có module/thực thể Cá Sấu và test tương ứng.
- Quân #3: cần kiểm tra hành vi 2 bếp/4 bàn và lọc menu theo kế hoạch ngày. Shop đã có implementation và test từ #4, không còn chặn vòng ngày.
- Lâm #5: còn thiếu kiểm chứng UI cho các màn hình ngày, HUD v1.1 và menu pause.
- Khoa #6: regression và smoke chuyển pha đã chạy; cần chạy smoke gameplay sau khi #2–#3 hoàn tất.
