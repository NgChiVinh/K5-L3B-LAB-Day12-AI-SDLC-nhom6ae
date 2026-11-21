# Ma trận truy vết Phase 1

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/phase-1/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|
| AC-P1-01 | Smoke hợp đồng kho và schema | `tests/test_smoke_p1.py::Integration`, `docs/proof/phase-1/qa-baseline.txt` | đạt |
| AC-P1-02 | Event oxy rỗng, ngạt/choke dưới nước | `tests/test_qa_phase1.py::GatherContract`, `tests/test_gather_lat1.py` | đạt |
| AC-P1-03 | Hái nút và hold_full | `tests/test_qa_phase1.py::GatherContract`, `tests/test_gather_lat2.py` | đạt |
| AC-P1-04 | Smoke gather ghi kho, quan đọc kho tick 0; smoke hai tiến trình trên `main` (`python3 tools/smoke_proof.py --phase phase-1`, 7 mục kiểm) | `tests/test_smoke_p1.py::Integration.test_inv_01_gather_writes_inventory_quan_reads_it`, [`docs/proof/phase-1/smoke.md`](../proof/phase-1/smoke.md) (commit `454b2eb`, 7/7) | đạt |
| AC-P1-05 | Khách đến theo lịch và giữ chỗ | `tests/test_qa_phase1.py::QuanContract.test_ac_p1_05_customer_arrives_and_reserves_inventory`, `tests/test_quan_lat3.py` | đạt |
| AC-P1-06 | Nấu, bưng, phục vụ, trả tiền | `tests/test_qa_phase1.py::QuanContract.test_ac_p1_06_cook_pick_serve_and_paid`, `tests/test_quan_lat4.py` | đạt |
| AC-P1-07 | HUD đọc snapshot | Cần xác minh bằng thử trình duyệt/UI | chưa kiểm |
| AC-P1-08 | Test bằng một lệnh; clone chạy trong ≤ 3 lệnh | `README.md`, lệnh unittest trong `AGENTS.md` | đạt test; chưa kiểm clone sạch |

## Đánh giá ngắn
- Yêu cầu đã kiểm đạt: AC-P1-01 đến AC-P1-06; full suite 70/70 pass.
- Chưa xác minh: AC-P1-07 bằng thử trình duyệt/UI; clone sạch cho AC-P1-08.
- Điều cần chỉnh: hoàn tất kiểm HUD và quy trình clone sạch trước khi chốt toàn bộ DoD.
