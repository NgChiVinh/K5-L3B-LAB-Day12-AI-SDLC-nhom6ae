# Day 12 — AI SDLC: Quán Ăn Chợ Nổi

## Nhóm nhom6ae — chạy game (macOS / Linux, Python 3, không cần cài thêm)

```bash
git clone https://github.com/NgChiVinh/K5-L3B-LAB-Day12-AI-SDLC-nhom6ae.git && cd K5-L3B-LAB-Day12-AI-SDLC-nhom6ae
python3 -m chonoi.live --mode gather --inventory-out /tmp/kho.json     # buổi sáng: mở http://127.0.0.1:8000/
python3 -m chonoi.live --mode quan --inventory /tmp/kho.json           # buổi tối (sau khi về bến): nạp kho buổi sáng
```

- **Điều khiển:** WASD / phím mũi tên = bơi / đi · **E** = cập bến, hái (buổi sáng) · nấu, bưng, phục vụ (buổi tối) · **Space** = bắt cá · **R** = chơi lại.
- **Buổi sáng:** lặn bắt cá (Space, dưới nước), nổi lên hái bông súng / điên điển (E, mặt nước); oxy giảm khi lặn, hết oxy thì ngạt mất Máu, hết Máu thì ngất và mất cả giỏ. Về bến bấm E (hoặc hết giờ) để mang giỏ về kho.
- **Buổi tối:** khách gọi món nấu được từ kho và giữ chỗ nguyên liệu. Ra bếp B1 bấm E để nấu → chín thì E để bưng → mang tới bàn T1 bấm E để phục vụ trước khi khách hết kiên nhẫn. Khách ăn xong trả tiền; phục vụ khi còn ≥ 50% kiên nhẫn thì có boa (+uy tín); khách bỏ đi thì −0.5 uy tín.
- **Điểm:** `earned + 100 × floor(reputation)` (tiền thu cả lượt, nghìn đồng, cộng 100 cho mỗi điểm uy tín nguyên).
- **Test (1 lệnh):** `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`
- **Headless (Test Contract):** `python3 -m chonoi.headless --mode gather|quan --seed 1 --ticks 600 --out out.jsonl`
- Windows: dùng `python`, đặt `PYTHONIOENCODING=utf-8`, test dùng `PYTHONPATH="tests;."` (xem `AGENTS.md`).
- Nhóm, vai, thỏa thuận: [`TEAM.md`](TEAM.md) · đề: [`docs/prd/`](docs/prd/) · bằng chứng: [`docs/verification/`](docs/verification/), [`docs/proof/`](docs/proof/).

### Sáng tạo của nhóm
- Phase 1: chưa thêm phần sáng tạo — làm lõi đúng trước (HUD có tên món tiếng Việt và kho khả dụng là phần hiển thị bắt buộc, không đổi luật).

---

> **Làm theo nhóm 4–6 người** · Dùng AI để xây game 2D qua **4 phase** trong **3 giờ**: Út Sen lặn bắt cá, hái rau trên mặt nước rồi tối mở quán phục vụ khách.
> **Yêu cầu từng phase mở đúng mốc giờ tại lab board:** **[Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg)** (cần đăng nhập claude.ai; có trợ giảng AI cho từng phase).

## Bắt buộc (chỉ có thế)

Cách làm việc kỹ thuật là **tự do** (push thẳng, nhánh + PR, pair, có hay không CI…). Cái bắt buộc:

1. **Một repo chung:** trưởng nhóm **fork** repo này, đặt tên `K5-L3B-LAB-Day12-AI-SDLC-<ten-nhom>`, thêm mọi thành viên làm collaborator (*Settings → Collaborators*, quyền Write) và để repo **public** (giảng viên xem được, không cần mời).
2. **Cả nhóm cùng commit** bằng tài khoản GitHub của mình, mỗi người **≥ 3 commit có nội dung** (làm cặp thì ghi `Co-authored-by:`).
3. **Điền [`TEAM.md`](TEAM.md):** danh sách thành viên + thỏa thuận làm việc nhóm; sửa `team_size` trong [`game.contract.json`](game.contract.json). Commit của người không có trong `TEAM.md` không được tính.
4. **Gắn tag** `phase-1` … `phase-4` đúng hạn; chạy được tại từng tag.
5. **Ghi chép tối thiểu:** `docs/verification/phase-n.md`, `docs/clarify.md`, `docs/ai-usage-log.md`, `docs/retro.md`, `docs/members/<handle>.md`.

## Bắt đầu nhanh

```bash
git clone <fork-của-nhóm> && cd <fork-của-nhóm>
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v        # smoke test
python3 -m chonoi.live --mode gather                                # chơi thử trên trình duyệt (tùy chọn)
```

Game cần chế độ **headless** theo Test Contract (`python3 -m chonoi.headless --mode gather|quan …`) để được chạy và chấm tự động. **Công nghệ không ràng buộc**: khung Python trong `chonoi/` chỉ là gợi ý, chi tiết ở [`docs/STARTER.md`](docs/STARTER.md).

## Tự do sáng tạo

Ngoài phần đề yêu cầu, nhóm được **thêm** nhân vật, loài cá/cây, sinh vật, món, bản đồ, cơ chế, câu chuyện, đồ họa, âm nhạc… với ba điều kiện: **không phá phần cố định** (tắt ở headless), ghi mục **"Sáng tạo của nhóm"** trong README của nhóm, và **làm lõi đúng trước**.

## Lịch 3 giờ

| Mốc | Phase | Hạn tag |
|---|---|---|
| 0:00 | Phase 1 (PRD-0) | `phase-1` trước 1:00 |
| 1:00 | Phase 2 | `phase-2` trước 1:55 |
| 1:55 | Phase 3 | `phase-3` trước 2:30 |
| 2:30 | Phase 4 | `phase-4` + Release `v1.0.0` trước 3:00 |

Hết giờ mỗi phase thì gắn tag rồi đi tiếp; chỗ chưa xong ghi trung thực trong bằng chứng.

## Đánh giá (100 điểm)

| Hạng mục | Điểm |
|---|---|
| Test tự động ẩn (headless, gồm kiểm tra lại phase trước) | 25 |
| Làm việc nhóm (một repo chung, chia việc, tích hợp, đổi yêu cầu) | 25 |
| Kiểm chứng & bằng chứng | 15 |
| Harness AI (AGENTS.md, skill, nhật ký dùng AI) | 10 |
| Đánh giá & retro | 10 |
| Chất lượng sản phẩm (đúng yêu cầu, mở rộng/sáng tạo) | 10 |
| Demo | 5 |

## Quy định

- Dùng AI thoải mái; **không sao chép repo của nhóm khác**; bằng chứng phải thật.
- Nhân vật, bối cảnh là bản gốc của lab; asset ngoài chỉ dùng CC0/CC-BY/MIT hoặc tự tạo, ghi nguồn trong `CREDITS.md`. Không commit API key, token, `.env`.
