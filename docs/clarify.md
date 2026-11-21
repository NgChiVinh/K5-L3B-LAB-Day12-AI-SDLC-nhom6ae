# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| 1 | 2026-11-21, P1 | Fixture quán có món trên bếp / trên tay thuộc đơn không có khách (ví dụ `C9`) thì xử lý thế nào? | PRD mục D: "liên kết thiếu", "món không khớp đơn" → mã 2. Giữ kiểm trong `scenario.py` (lát 3); test lát 4 đổi sang fixture hợp lệ (PR #3). | Integrator (NgChiVinh), theo PRD |
| 2 | 2026-11-21, P1 | Với 1 bàn T1, trạng thái "tay đang cầm món + bếp có món ready" có dựng được không? | Không bằng fixture hợp lệ (1 bàn = tối đa 1 khách = 1 đơn; "bếp và tay giữ cùng đơn" → mã 2). Test kiểm mã 2 cho fixture đó. | Integrator (NgChiVinh), theo PRD |
| 3 | 2026-11-21, P1 | HUD buổi tối hiện "kho" là tồn vật lý hay kho khả dụng? | DoD ghi "kho khả dụng" → HUD hiện tồn − phần khách giữ chỗ (UI tự trừ để hiển thị, luật dùng `_available()`). | Integrator (NgChiVinh), theo DoD |
| 4 | 2026-11-21, P1 | Khách đang ăn thì HUD hiện gì ở ô gọi món? | Khách đang ăn không mất kiên nhẫn (mục F) → hiện thời gian ăn còn lại, không hiện kiên nhẫn đứng yên. | Integrator (NgChiVinh) — giả định nhóm |
| 5 | 2026-11-21, P1 | `_available()` trả khóa có lượng 0 hay bỏ đi? | Bỏ khóa 0 (thiếu khóa = 0), thống nhất giữa lát 3 và lát 4 khi tích hợp. Chỉ là biểu diễn nội bộ, không ra JSONL. | Integrator (NgChiVinh) — giả định nhóm |
| 6 | 2026-11-21, P1 | Danh sách "mục mở rộng" (nhóm 6 người ≥ 2 mục) ở đâu? | Bản PRD-0 nhóm chép không có danh sách; cần hỏi Anh Năm hàng xóm / giảng viên. | PO (TrungHieuPh) — còn mở |
| 7 | 2026-11-21, P2 | 8 đàn đầu ca chọn loài thế nào? PRD chỉ nói "8 đàn ở 8 điểm khác nhau". | Giả định: dùng đúng luật sinh theo lịch (trọng số loài 40/30/30 chuẩn hóa trên loài còn điểm, chọn đều điểm, cách mọi đàn > 1 m), lặp 8 lần, luồng RNG `fish_spawn`. Cần hỏi Anh Năm. | Integrator (NgChiVinh) — giả định, chờ PO hỏi |
| 8 | 2026-11-21, P2 | "Hướng ban đầu theo seed" là phân phối gì? | Giả định: góc đều trong [0°, 360°) qua `Streams`. Cần hỏi Anh Năm (có thể chỉ ±x). | Integrator (NgChiVinh) — giả định, chờ PO hỏi |
| 9 | 2026-11-21, P2 | Nút `attack`/`photo` khi chưa bật mở rộng: mã 2 hay bỏ qua? | Mục 4.2: "nút đúng kiểu nhưng mở rộng chưa bật thì bỏ qua" → nhận ở inputs, sim bỏ qua; nút lạ (`jump`) vẫn mã 2. Test P1 đổi theo. | Integrator (NgChiVinh), theo PRD |
