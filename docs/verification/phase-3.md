# Ma trận kiểm chứng Phase 3

QA branch `v1.2`; kết quả dưới đây chưa phải verification cuối cho `main`.

| Check | Kiểm chứng / bằng chứng | Trạng thái |
|---|---|---|
| AC-P3-01 | File kho v1.1 và schema cá thể sai trả mã 2: `tests/test_smoke_p1.py::Integration.test_inv_bad_schema_exit_2` | đạt |
| AC-P3-02 | Fresh đúng 30 phát `spoiled` ở tick 1 đúng một lần: `tests/test_qa_phase3.py::Phase3FreshnessQA.test_gather_threshold_spoils_once_at_tick_one` | đạt |
| AC-P3-03 | Cá thể giữ chỗ vừa ươn được nhả và thử giữ lại bằng ID khác: `tests/test_qa_phase3.py::Phase3FreshnessQA.test_spoiled_reserved_item_releases_and_reholds_order_once` | đạt |
| AC-P3-04 | Giá món dùng floor trên độ tươi sau hao trong tick: `tests/test_qa_phase3.py::Phase3FreshnessQA.test_cook_price_floors_after_freshness_adjustment` | đạt |
| AC-P3-05 | Smoke `gather --inventory-out` → `quan --inventory`, giữ ID/kind/freshness: [qa-results.md](../proof/phase-3/qa-results.md), [gather JSONL](../proof/phase-3/integration.gather.jsonl), [inventory](../proof/phase-3/integration.inventory.json), [quan JSONL](../proof/phase-3/integration.quan.jsonl) | đạt |
| AC-P3-06 | Day chuyển gather → quan cùng tick, không hao thêm: `tests/test_qa_phase3.py::Phase3FreshnessQA.test_day_handoff_preserves_gather_freshness_in_same_tick`; [day JSONL](../proof/phase-3/day.jsonl) | đạt |
| AC-P3-07 | Regression thuộc Khoa: `test_smoke_p1`, `test_python_starter_units`, `test_qa_phase2`, `test_qa_phase3`; [regression output](../proof/phase-3/regression.txt) | 36/36 đạt |
| AC-P3-08 | Regression toàn nhóm: `python3 -m unittest discover -s tests -v`; [full regression result](../proof/phase-3/full-regression.txt) | **chặn** — 112 tests, 12 failures, 5 errors ở các test migration được liệt kê trong [qa-results.md](../proof/phase-3/qa-results.md) |
| AC-P3-09 | HUD freshness / dấu hiệu hàng ươn | chờ bằng chứng HUD của Lâm; không được tính là đã đạt trong QA này |

## Kết luận

Các kiểm thử và smoke thuộc phạm vi Khoa đã đạt. Chưa thể xác nhận DoD Phase 3, merge hoặc tag `main`: regression tích hợp còn lỗi ở test của Hiếu, Chuẩn và Quân, và HUD chưa có bằng chứng được xác nhận. Theo ADR-0001, giữ `main` ở v1.1 cho đến khi các lát tích hợp, file/day smoke, regression và HUD đều được kiểm lại trên cùng commit.
