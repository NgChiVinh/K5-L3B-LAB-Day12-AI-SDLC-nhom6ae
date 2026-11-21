# Kiểm giao diện nhà bè Má Tư

| Phép thử | Kết quả |
|---|---|
| `python3 -m unittest discover -s tests -v` với `PYTHONPATH=tests;.` trên Windows | 133/133 test đạt trong 16,362 giây |
| `python3 tools/hud_check.py --phase phase-4` | 67/67 mục đạt ở 1280, 900, 700 và 480 px. [Chi tiết HUD](hud.md) |
| Chrome headless với máy chủ live ở cả ba chế độ | Mở hướng dẫn và thực đơn từ bến, vào chơi, bật tương phản, mở sổ, tạm dừng, tiếp tục và về bến thành công |
| Bộ lọc công thức | Kho thử có một cá lóc tươi hiện đúng một món đủ nguyên liệu. Giỏ rỗng hiện thông báo khi lọc. Bộ lọc món trong ngày hiện đủ số món theo kế hoạch của lượt chơi |
| Chế độ ngày với ca quán rút ngắn bằng scenario | Cập bến, qua ca quán, mua bình oxy ở shop, thấy cấp oxy tăng và đóng shop đến màn tổng kết |
| Chrome mô phỏng cảm ứng ở 390 × 844 | Giữ nút sang phải làm vị trí Út Sen thay đổi. Thả tay giải phóng nút di chuyển |
| Tầng sâu trên máy chủ live | Trong scenario có đàn cá kèo ở 39,5 m, thao tác bắt từ 39 m đưa 2 cá kèo vào giỏ. Giữ phím bơi xuống đưa Út Sen tới giới hạn 45 m |
| Phục vụ trên Chrome | Với 2 cá kèo và 3 cá linh đã được hai khách giữ, nấu cá kèo kho tộ tại B1, bưng món đến T1 và thấy khách chuyển sang trạng thái đang ăn |
| Hai món mới qua vòng ngày | `test_live_specials_from_catch_to_payment` chạy riêng cho từng món, từ thao tác bắt cá, chuyển pha và nấu đến giao món và nhận tiền |

[Ảnh màn mở đầu chụp từ Chrome ở 1280 × 720](man-mo-dau.jpg)

[Lặn ở 39 m](lan-sau.jpg) · [Bưng cá kèo kho tộ ra bàn T1](phuc-vu.jpg)
