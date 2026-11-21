# truclamld — phản tư cá nhân (≤ 200 từ)

- Tôi đã làm (kèm link commit): Thiết kế giao diện của trò chơi, cụ thể là phần HUD hiển thị thông tin như HP, Oxy còn lại, số nguyên liệu đã thu thập, và hệ thống cảnh báo. Hầu hết được thực hiện trên file `index.html` và một ít trong `hud_check.py`. 
  - Commit: HUD hai buổi (e5700a3, PR #2); menu chính, pause, HUD động P2 (9e8a0a1, PR #7); thanh độ tươi P3 (7cd9485, PR #10); 3 cảnh báo + chế độ tương phản cao P4 (494dabb, PR #16).
- Tôi đã review (kèm link): Chạy thử trò chơi và kiểm tra lỗi trong gameplay, ví dụ như lỗi khi thu thập nguyên liệu hay giỏ bị trống khi sang phần chơi Quán.
- AI sai ở đâu và tôi phát hiện thế nào: Giao diện cảnh báo người chơi bị lệch chữ ra khỏi text box, được phát hiện khi chạy thử trò chơi và cố tình kích hoạt cảnh báo.
- Điều tôi học được: AI thiết kế giao diện tốt nhưng đôi lúc không tuân theo tiêu chuẩn về usability. Việc thiết kế giao diện cần con người hỗ trợ để thân thiện với người dùng hơn
