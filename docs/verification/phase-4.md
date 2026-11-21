# Ma trận kiểm chứng Phase 4 — QA

Kiểm chứng ngày 2026-11-21 trên code ở `main` `80c8ff4` (sau PR #15) và QA branch `7d9b946`. Đây chưa phải commit bàn giao cuối Phase 4; nếu code thay đổi trước khi phát hành, chạy lại bench, soak, regression và smoke trên commit tích hợp.

| Hạng mục | Lệnh / bằng chứng | Kết quả |
|---|---|---|
| Bench, cảnh render 1280×720, seed 42, làm nóng 3 s và đo 30 s | `python3 -m chonoi.bench --seed 42 --duration 30 --out docs\proof\phase-4\bench.json`; [bench.json](../proof/phase-4/bench.json) | Đạt: 257.13 avg FPS, 132.41 FPS 1% low, 7,715 frames / 30.004 s, load 84 ms; các mốc ≥60 / ≥30 / ≤10,000 ms đều đạt. |
| Hợp đồng bench và render | `tests.test_bench` trong regression bên dưới | Đạt: kiểm tra đủ 5 trường, quan hệ frames/measured_s và header framebuffer 1280×720. |
| Soak 10 ngày | `python3 -m chonoi.soak --seed 7 --days 10 --out docs\proof\phase-4\soak.json`; [soak.json](../proof/phase-4/soak.json), [soak-check.md](../proof/phase-4/soak-check.md) | Đạt: 10/10 ngày, 0 crash; lượt lặp cùng seed cho kết quả gameplay giống nhau khi bỏ `duration_s`. |
| Regression P1–P3 | `$env:PYTHONPATH='tests;.'; $env:PYTHONIOENCODING='utf-8'; python -m unittest discover -s tests -v`; [regression.txt](../proof/phase-4/regression.txt) | Đạt: 127/127 test. |
| Smoke gather → quan hai tiến trình | `$env:PYTHONIOENCODING='utf-8'; python3 tools\smoke_proof.py --phase phase-4`; [smoke.md](../proof/phase-4/smoke.md) | Đạt: 7/7 kiểm tra, gồm kho giao nhận, độ tươi và tính tất định. |

## Phạm vi còn chờ

Đây là kết quả QA của lát bench/soak/regression/smoke; chưa xác nhận DoD toàn Phase 4. Các thay đổi cảnh báo/tương phản, đóng gói và mở rộng cần được kiểm tra trên commit bàn giao trước khi gắn tag hoặc phát hành.
