# AIIE - AI Image Enhancement Platform

AIIE là nền tảng xử lý và tạo ảnh AI. Các tính năng chính bao gồm:

- AI Agent Chat với khả năng tạo và chỉnh sửa ảnh
- Text-to-Image (Stable Diffusion)
- Image-to-Image transformation
- Inpainting (chỉnh sửa vùng ảnh)
- Image Expansion
- Image Segmentation
- Super Resolution (SRGAN)

## Yêu cầu hệ thống

- Node.js v18 hoặc cao hơn
- Python 3.13 hoặc cao hơn
- Docker Desktop
- 8 GB RAM tối thiểu (16 GB khuyến nghị)
- 10 GB không gian ổ cứng trống

## Cài đặt và khởi động

### Bước 1: Cấu hình OpenAI API Key

Mở file `aiie-agent-api\.env` và thiết lập:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

Lấy API key tại: https://platform.openai.com/api-keys

### Bước 2: Khởi động tất cả services

Chạy script tự động:

```powershell
.\start-all.ps1
```

Hoặc khởi động từng service thủ công:

PostgreSQL và MinIO (chạy trong Docker):

```powershell
# PostgreSQL
docker run -d --name aiie-postgres -e POSTGRES_DB=aiie_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15

# MinIO
docker run -d --name aiie-minio -p 9000:9000 -p 9001:9001 -e MINIO_ROOT_USER=minioadmin -e MINIO_ROOT_PASSWORD=minioadmin minio/minio server /data --console-address ":9001"
```

Agent API (chạy trong terminal riêng):

```powershell
cd aiie-agent-api
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

Stable Diffusion API (chạy trong terminal riêng):

```powershell
cd aiie-sd-api
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8001
```

SRGAN API (chạy trong terminal riêng):

```powershell
cd aiie-srgan-api
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8002
```

Frontend (chạy trong terminal riêng):

```powershell
cd aiie-ui
npm run dev
```

### Bước 3: Cấu hình MinIO (lần đầu tiên)

1. Truy cập http://localhost:9001
2. Đăng nhập:
   - Username: minioadmin
   - Password: minioadmin
3. Tạo bucket mới với tên: aiie-storage
4. Đặt bucket policy thành Public

### Bước 4: Truy cập các dịch vụ

- Frontend: http://localhost:5173
- Agent API Docs: http://localhost:8000/docs
- SD API Docs: http://localhost:8001/docs
- SRGAN API Docs: http://localhost:8002/docs
- MinIO Console: http://localhost:9001

### Dừng tất cả services

```powershell
.\stop-all.ps1
```

## Cấu trúc dự án

```
aiie/
├── aiie-agent-api/          # Backend chính
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core config, DB
│   │   ├── models/         # Database models
│   │   └── main.py         # Entry point
│   ├── venv/               # Python virtual environment
│   └── .env                # Environment variables
│
├── aiie-sd-api/            # Stable Diffusion service
│   ├── app/
│   │   ├── services/       # SD pipelines
│   │   └── main.py
│   └── .env
│
├── aiie-srgan-api/         # Super Resolution service
│   ├── app/
│   │   └── main.py
│   └── .env
│
├── aiie-ui/                # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── App.tsx
│   └── .env
│
├──Cấu hình nâng cao

### Thay đổi model Stable Diffusion

Mở file `aiie-sd-api\.env` và cập nhật:

```env
DEFAULT_MODEL=runwayml/stable-diffusion-v1-5
```

Các model khác khả dụng:

- stabilityai/stable-diffusion-2-1
- stabilityai/stable-diffusion-xl-base-1.0

### Sử dụng GPU

Nếu có NVIDIA GPU với CUDA:

1. Cài đặt CUDA Toolkit
2. Cài đặt PyTorch với CUDA support
3. Services sẽ tự động phát hiện và sử dụng GPU

## Xử lý sự cố

### Connection refused khi gọi API

Nguyên nhân: Service chưa khởi động hoặc port bị chiếm.

Giải pháp:

- Kiểm tra service đang chạy
- Kiểm tra port không bị chiếm: `netstat -ano | findstr :8000`

### Database connection failed

Nguyên nhân: PostgreSQL chưa chạy.

Giải pháp:

```powershell
docker start aiie-postgres
docker ps -a
```

### MinIO bucket not found

Nguyên nhân: Chưa tạo bucket.

Giải pháp: Truy cập http://localhost:9001 và tạo bucket aiie-storage.

### Out of memory khi chạy SD API

Nguyên nhân: Không đủ RAM/VRAM.

Giải pháp:

- Đóng các ứng dụng khác
- Sử dụng model nhỏ hơn
- Giảm batch size trong code

### SD API khởi động lâu lần đầu

Khi chạy lần đầu, SD API sẽ tải model từ Hugging Face (khoảng 4 GB). Quá trình này có thể mất 10-30 phút tùy thuộc vào tốc độ kết nối.

## Ghi chú

- Agent API sẽ tự động tạo các bảng trong database khi chạy lần đầu
- Các model AI sẽ được cache sau lần đầu tải
- Tất cả services đang chạy ở chế độ development với auto-reload

## Bảo mật

CẢNH BÁO: Cấu hình này là cho môi trường development. Trước khi deploy production, cần thực hiện:

1. Thay đổi tất cả mật khẩu trong file .env
2. Thay đổi SECRET_KEY trong aiie-agent-api\.env
3. Cấu hình CORS đúng cách (không dùng allow_origins=["*"])
4. Sử dụng HTTPS
5. Cấu hình firewall và security groups

## Tài liệu API

Sau khi khởi động services, có thể truy cập:

- http://localhost:8000/docs - Agent API (Swagger UI)
- http://localhost:8001/docs - SD API (Swagger UI)
- http://localhost:8002/docs - SRGAN API (Swagger UI)

## License

Thêm license của dự án tại đây.
[Thêm license của bạn ở đây]

---

**Chúc bạn sử dụng vui vẻ! 🎉**
