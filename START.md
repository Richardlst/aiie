# Hướng dẫn chạy dự án AIIE

## Yêu cầu hệ thống
- ✅ Node.js v18+ (Đã cài: v18.20.8)
- ✅ Python 3.13+ (Đã cài: 3.13.2)
- ✅ Docker (Đã cài: 27.5.1)
- PostgreSQL
- MinIO (Object Storage)

## Cấu trúc dự án
```
aiie/
├── aiie-agent-api/     # Backend chính (FastAPI + LangChain)
├── aiie-sd-api/        # Stable Diffusion API
├── aiie-srgan-api/     # Super Resolution API
└── aiie-ui/            # Frontend (React + TypeScript)
```

## Bước 1: Cài đặt PostgreSQL

### Cách 1: Dùng Docker (Khuyến nghị)
```powershell
docker run -d `
  --name aiie-postgres `
  -e POSTGRES_DB=aiie_db `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=postgres `
  -p 5432:5432 `
  postgres:15
```

### Cách 2: Cài đặt trực tiếp
Tải và cài đặt từ: https://www.postgresql.org/download/windows/

## Bước 2: Cài đặt MinIO

### Dùng Docker (Khuyến nghị)
```powershell
docker run -d `
  --name aiie-minio `
  -p 9000:9000 `
  -p 9001:9001 `
  -e MINIO_ROOT_USER=minioadmin `
  -e MINIO_ROOT_PASSWORD=minioadmin `
  minio/minio server /data --console-address ":9001"
```

Sau đó truy cập http://localhost:9001 để tạo bucket:
- Username: minioadmin
- Password: minioadmin
- Tạo bucket tên: `aiie-storage`

## Bước 3: Cấu hình OpenAI API Key

Mở file `aiie-agent-api\.env` và thêm OpenAI API key của bạn:
```
OPENAI_API_KEY=sk-your-api-key-here
```

## Bước 4: Chạy các services

### Terminal 1: Chạy Agent API (Backend chính)
```powershell
cd aiie-agent-api
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Chạy Stable Diffusion API
```powershell
cd aiie-sd-api
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8001
```

### Terminal 3: Chạy SRGAN API
```powershell
cd aiie-srgan-api
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8002
```

### Terminal 4: Chạy Frontend
```powershell
cd aiie-ui
npm run dev
```

## Bước 5: Truy cập ứng dụng

- **Frontend**: http://localhost:5173 (hoặc port mà Vite hiển thị)
- **Agent API**: http://localhost:8000/docs
- **SD API**: http://localhost:8001/docs
- **SRGAN API**: http://localhost:8002/docs
- **MinIO Console**: http://localhost:9001

## Lưu ý quan trọng

1. **Lần đầu chạy Agent API** sẽ tự động tạo các bảng trong database
2. **Stable Diffusion API** sẽ tải model lần đầu (khoảng 4GB), có thể mất 10-30 phút
3. **SRGAN API** cũng cần tải model lần đầu
4. Đảm bảo tất cả các services đang chạy trước khi sử dụng frontend

## Troubleshooting

### Lỗi kết nối Database
- Kiểm tra PostgreSQL đang chạy: `docker ps` hoặc kiểm tra service
- Kiểm tra thông tin kết nối trong `aiie-agent-api\.env`

### Lỗi kết nối MinIO
- Kiểm tra MinIO đang chạy: `docker ps`
- Đảm bảo đã tạo bucket `aiie-storage`

### Lỗi OpenAI API
- Kiểm tra API key trong `aiie-agent-api\.env`
- Đảm bảo tài khoản OpenAI có credits

### Lỗi CUDA/GPU
- Nếu không có GPU, các model sẽ chạy trên CPU (chậm hơn)
- Stable Diffusion và SRGAN sẽ tự động detect và sử dụng CPU
