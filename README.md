# GitLab Dump Variables

Script Python dùng GitLab API để **sao lưu (dump) CI/CD Variables** từ một GitLab Group, các subgroup trực tiếp, và các project thuộc các group đó.

## Tính năng

- Lấy variables của **group cha** và **các subgroup cấp 1**
- Lấy variables của **tất cả project** trong mỗi group/subgroup
- Lưu toàn bộ variables vào file `all_vars.json`
- Với biến kiểu **file** (`variable_type == "file"`), ghi riêng thành file `FILE_<key>`
- Hỗ trợ GitLab.com hoặc GitLab self-hosted (tùy cấu hình `GITLAB_URL`)

## Yêu cầu

- Python 3.7+
- Thư viện `requests`

```bash
pip install requests
```

## Cấu hình

Mở `gl_fecther.py` và chỉnh các biến ở đầu file:

| Biến | Mô tả |
|------|--------|
| `GITLAB_URL` | URL GitLab, ví dụ: `https://gitlab.com` hoặc `https://gitlab.example.com` |
| `PARENT_GROUP_PATH` | Đường dẫn group cha, ví dụ: `my-org` hoặc `my-org/team-a` |
| `PRIVATE_TOKEN` | Personal Access Token hoặc Group Access Token có quyền đọc variables |
| `OUTPUT_DIR` | Thư mục lưu kết quả, mặc định: `./gitlab_dump_all` |

### Quyền token cần có

Token cần quyền đọc:

- Group CI/CD variables
- Project CI/CD variables
- Danh sách subgroup và project trong group

Với Personal Access Token trên GitLab.com, thường cần scope **`api`** hoặc **`read_api`**.

## Cách sử dụng

1. Cấu hình các biến ở trên
2. Chạy script:

```bash
python gl_fecther.py
```

3. Kết quả được lưu trong thư mục `OUTPUT_DIR`

## Cấu trúc thư mục đầu ra

```
gitlab_dump_all/
├── GROUP_my-org/
│   ├── all_vars.json
│   └── FILE_<ten_bien_file>    # nếu có biến kiểu file
├── GROUP_my-org_team-a/
│   └── all_vars.json
└── PROJECT_my-org_my-project/
    ├── all_vars.json
    └── FILE_<ten_bien_file>
```

- Tên thư mục: `/` trong path được thay bằng `_`
- Tiền tố `GROUP_` cho group/subgroup, `PROJECT_` cho project

## Ví dụ output console

```
--- Bắt đầu quét từ Group: my-org (ID: 12345) ---
    [OK] Đã lưu 5 biến.

[*] Xử lý Subgroup: my-org/team-a
    [OK] Đã lưu 3 biến.
  > Project: my-org/team-a/backend
    [OK] Đã lưu 8 biến.
```

## Lưu ý bảo mật

- **Không commit** token hoặc file dump chứa secrets lên Git
- `all_vars.json` có thể chứa giá trị biến nhạy cảm (password, API key, v.v.)
- Nên đặt `OUTPUT_DIR` ngoài repo và thêm vào `.gitignore`
- Xóa hoặc mã hóa file dump sau khi dùng xong

## Hạn chế hiện tại

- Chỉ lấy **subgroup cấp 1** của group cha (không đệ quy sâu hơn)
- Mỗi API gọi tối đa **100** bản ghi (`per_page: 100`), chưa xử lý phân trang
- Không dump variables của subgroup lồng nhau sâu hoặc project ngoài phạm vi group đã quét

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân có thể |
|-----|---------------------|
| `401 Unauthorized` | Token sai hoặc hết hạn |
| `403 Forbidden` | Token thiếu quyền |
| `404 Not Found` | Sai `PARENT_GROUP_PATH` hoặc không có quyền truy cập group |
| Thư mục rỗng | Group/project không có CI/CD variables |

## Cách hoạt động (tóm tắt)

1. Lấy thông tin group cha qua API `/api/v4/groups/{path}`
2. Dump variables của group cha
3. Lấy danh sách subgroup qua `/api/v4/groups/{id}/subgroups`
4. Với mỗi group/subgroup: dump variables và lấy danh sách project
5. Với mỗi project: dump variables qua `/api/v4/projects/{id}/variables`

## Giấy phép

Sử dụng tự do theo nhu cầu nội bộ. Kiểm tra chính sách bảo mật của tổ chức trước khi dump variables từ GitLab production.
