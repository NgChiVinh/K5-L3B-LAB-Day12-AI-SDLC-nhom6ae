# Changelog

## Unreleased

## Contract v1.2 — "Mùa Nước Nổi" (Phase 3, TICKET-03) — BREAKING CHANGE

Quyết định, bảng tác động và thứ tự tích hợp: [`docs/adr/0001-kho-ca-the-do-tuoi.md`](docs/adr/0001-kho-ca-the-do-tuoi.md).

### Breaking change
- **File kho đổi schema** từ kho đếm sang **kho cá thể**:
  ```json
  // v1.0 / v1.1 (cũ) — từ v1.2 bị từ chối, mã 2
  {"items": {"bong_sung": 2, "ca_loc": 1}}
  // v1.2 (mới) — mảng cá thể, sắp theo id; kho rỗng là {"items": []}
  {"items": [{"id": "I1", "kind": "ca_loc", "fresh": 99.99166666666666},
             {"id": "I2", "kind": "bong_sung", "fresh": 100}]}
  ```
  Mã 2 khi: kho đếm, sai schema, `kind` lạ, `id` trùng/rỗng, `fresh` ngoài [0, 100] hoặc không hữu hạn.
  File ghi float đầy đủ (không làm tròn) để đọc lại giữ đúng nhánh ở ngưỡng 30.
- **Scenario:** `gather.hold` và `quan.stock` là **mảng cá thể** `{id, kind, fresh}`; `customers[].reserved` là
  **mảng id cá thể** (trỏ tới cá thể chưa ươn trong kho, đủ công thức, không dùng chung giữa các đơn).
- **JSONL:** snapshot `hold` (thứ tự vào giỏ), `stock` (quán và Shop, sắp id), `customers[].reserved` (mảng id),
  `gather_end.data.inventory` theo schema mới; `cook_started.data.items` là mảng cá thể sắp `kind` rồi `id`;
  `lost` trong `monster_hit` / `faint` là mảng cá thể theo thứ tự bỏ LIFO.
- **Giá:** `base_price = floor(giá niêm yết × trung bình fresh của các cá thể dùng / 100)`, chốt khi bắt đầu nấu
  (trước: giá niêm yết). Boa tính trên giá đã chốt.
- `contract_version: "1.2"`, thêm `tuning.freshness {initial: 100, gather_decay_per_s: 0.5, quan_decay_per_s: 0.25,
  spoiled_below: 30}`.

### Thêm
- Độ tươi: hàng mới `fresh 100` (hao từ bước sau); giỏ −0.5/s, kho quán −0.25/s (kể cả hàng đang giữ); pause
  dừng hao; món chín và hàng ở Shop không hao.
- Event `spoiled {item_id, kind, location: hold|stock}` đúng một lần khi đi từ ≥ 30 xuống < 30, theo id.
- Giữ chỗ theo id (tươi nhất, hòa theo id); phần giữ có cá thể vừa ươn → nhả và thử giữ lại một lần, thiếu →
  `unfulfillable`.
- Id cá thể `I1, I2, …` theo thứ tự vào giỏ, tăng xuyên pha và Ngày; trong `--mode day`, Ngày 2+ cấp id mới cho
  mẫu `gather.hold`.
- `chonoi/items.py` (adapter dùng chung); độ tươi lưu bằng `fractions.Fraction`.

### Cách cập nhật fixture / test cũ
- Viết fixture mới bằng `items("ca_loc", "bong_sung", fresh=100)` trong `tests/helpers.py`
  → `[{"id":"I1","kind":"ca_loc","fresh":100}, {"id":"I2","kind":"bong_sung","fresh":100}]`.
- Fixture P1–P2 còn dạng cũ được `write_json` tự đổi sang v1.2 (fresh 100, id I1, I2…; `reserved` đếm → id lấy từ
  `stock`) — chỉ khi fixture hợp lệ; fixture cố ý sai giữ nguyên để vẫn kiểm mã 2.
- So kết quả theo loại bằng `kinds_of(snapshot["hold"])` hoặc `counts(file_kho)`; kỳ vọng giá dùng công thức mới
  (ví dụ cá lóc 60 với fresh 99.99… → `base_price` 59).
- Test đổi vì luật mới phải ghi lý do trong commit (AGENTS.md).

## Contract v1.1 — "Một ngày ở chợ nổi" (Phase 2, TICKET-02) — tag `phase-2`
- Số liệu chuẩn; 6 nguyên liệu (thêm `ca_keo`, `keo_neo`), 6 món, nút N5/N6; 8 đàn cá bơi/sinh theo seed.
- Cá Sấu Năm Chèo (patrol/chase/recoil, `monster_hit`, ngất do quái); 2 bếp / 4 bàn.
- `--mode day` (`--days 1..5`), Shop nâng cấp oxygen/hp, pause ở cả 3 mode; HUD v1.1, menu, màn hình ngày.
- Nút `attack`/`photo` hợp lệ (bỏ qua khi chưa bật mở rộng) — không còn mã 2.

## Contract v1.0 — PRD-0 (Phase 1) — tag `phase-1`
- Lặn & hái (`gather`), mở quán (`quan`), bàn giao file kho đếm, headless theo Test Contract v1.0.
