# Ma trận kiểm chứng Phase 4 — QA

Kiểm chứng trên commit đầu vào `1df38e5737f3f0f9ef346225ae41d3a35dfe6626` (`main` sau PR #14), ngày 2026-11-21. Đây chưa phải commit bàn giao cuối Phase 4; chạy lại bench, soak, regression và smoke trên commit tích hợp trước khi phát hành.

| Hạng mục | Lệnh / bằng chứng | Kết quả |
|---|---|---|
| Bench, cảnh render 1280×720, seed 42, làm nóng 3 s và đo 30 s | `python3 -m chonoi.bench --seed 42 --duration 30 --out docs\proof\phase-4\bench.json`; [bench.json](../proof/phase-4/bench.json) | Đạt: 221.85 avg FPS, 76.97 FPS 1% low, 6,656 frames / 30.0019 s, load 1,373 ms; các mốc ≥60 / ≥30 / ≤10,000 ms đều đạt. |
| Hợp đồng bench và render | `tests.test_bench` trong regression bên dưới | Đạt: kiểm tra đủ 5 trường, quan hệ frames/measured_s và header framebuffer 1280×720. |
| Soak 10 ngày | `python3 -m chonoi.soak --seed 7 --days 10 --out docs\proof\phase-4\soak.json` | Chưa đạt / bị chặn: commit đầu vào khai `soak_cmd` nhưng chưa có `chonoi.soak`; lệnh trả `No module named chonoi.soak`, không tạo `soak.json`. Cần chạy lại sau khi lát Soak được tích hợp. |
| Regression P1–P3 | `$env:PYTHONPATH='tests;.'; $env:PYTHONIOENCODING='utf-8'; python -m unittest discover -s tests -v`; [regression.txt](../proof/phase-4/regression.txt) | Đạt: 124/124 test. |
| Smoke gather → quan hai tiến trình | `$env:PYTHONIOENCODING='utf-8'; python3 tools\smoke_proof.py --phase phase-4`; [smoke.md](../proof/phase-4/smoke.md) | Đạt: 7/7 kiểm tra, gồm kho giao nhận, độ tươi và tính tất định. |

## Phạm vi còn chờ

Đây là kết quả QA trên commit `1df38e5`, không phải xác nhận DoD toàn Phase 4. Chưa thể xác minh soak cho đến khi `chonoi/soak.py` được tích hợp; các thay đổi cảnh báo/tương phản, đóng gói và mở rộng cũng cần kiểm tra trên commit bàn giao. Không dùng kết quả một phần này để gắn tag hoặc phát hành.
