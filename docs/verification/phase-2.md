# Ma trận kiểm chứng Phase 2

Trạng thái trên branch `qa/khoa-phase1-verification`, base `ac0bdd8`.

| AC | Kiểm chứng / bằng chứng | Trạng thái | Chặn bởi |
|---|---|---|---|
| AC-P2-01 | Contract v1.1 và số chuẩn; baseline/full suite | đạt khung | — |
| AC-P2-02 | 8 đàn, N5/N6, cá kèo yield 2 có test; cá bơi và sinh theo lịch chưa có | đang chờ phần hành vi | Hiếu #1 |
| AC-P2-03 | Chưa có `monsters.py`/test Cá Sấu | chưa làm | Chuẩn #2 |
| AC-P2-04 | Snapshot có B1/B2, T1–T4; menu có 6 món. Hành vi đa bếp/bàn và lọc món theo day chưa kiểm | một phần | Quân #3 |
| AC-P2-05 | Chưa có `shop.py`/test mua và đóng Shop | chưa làm | Quân #3 |
| AC-P2-06 | Chưa có runner vòng ngày và test `day --days` | chưa làm | Vĩnh #4; cần Shop của Quân #3 |
| AC-P2-07 | Chưa có kiểm pause xuyên các pha | chưa làm | Vĩnh #4 |
| AC-P2-08 | Chưa kiểm chơi trọn vòng ngày/HUD v1.1 | chưa làm | Vĩnh #4 và Lâm #5 |
| AC-P2-09 | Regression hiện có 74/74 pass; smoke kho tick 0 đạt. Smoke ngày và regression hành vi các lát mới còn chờ | một phần | #1–#4; smoke ngày cần #3 và #4 |

## Kết quả đã chạy

- Windows PowerShell: `$env:PYTHONPATH="tests;."`
- `python3 -m unittest discover -s tests -v`: **74/74 OK**.
- Smoke gather → quan: [`integration.md`](../proof/phase-2/integration.md).
- Smoke này dùng giỏ fixture tại bến, nên **không** chứng minh cá mới đã bơi/sinh hay được bắt trong gameplay.
