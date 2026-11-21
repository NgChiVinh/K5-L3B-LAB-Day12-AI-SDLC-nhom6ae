# NgChiVinh — phản tư cá nhân (≤ 200 từ)

- Tôi đã làm (kèm link commit): kickoff — `TEAM.md`, kế hoạch, chép PRD, hợp đồng tích hợp (69cd936, eca9eaa); lát 1 gather theo TDD — oxy, ngạt, Máu, ngất (5f22e69); harness — skill `run-tests`, `smoke-proof`, `tools/smoke_proof.py` (1743992); sửa HUD (3a03e30, PR #2) và công cụ kiểm HUD `tools/hud_check.py` (10db256); tích hợp lát 3 + lát 4 (816fb57, PR #3); bằng chứng smoke + HUD, README.
- Tôi đã review (kèm link): PR #1 (lát 2, Hiếu), PR #2 (HUD, Lâm), nhánh `chuan` (phát hiện merge làm mất lát 4) → PR #3, nhánh QA của Khoa.
- AI sai ở đâu và tôi phát hiện thế nào: `git merge-tree` báo nhánh `chuan` không conflict nhưng chạy test trên đúng code nhánh thì 14 test hỏng; script smoke báo nhầm "có thay đổi chưa commit" và bằng chứng từng trỏ tới hash mất sau rebase — phát hiện khi đọc lại file bằng chứng.
- Điều tôi học được: luôn chạy cả bộ test trên kết quả merge, không tin "không conflict"; bằng chứng phải trỏ tới commit đã nằm trên `main`.
