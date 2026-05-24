# AIIE - AI Image Enhancement Platform

AIIE là nền tảng xử lý và tạo ảnh AI với AI Agent Chat. Các tính năng chính:

- AI Agent Chat tích hợp LangChain và LangGraph
- Text-to-Image (Stable Diffusion)
- Image-to-Image transformation
- Image Inpainting (chỉnh sửa vùng ảnh)
- Image Expansion
- Image Colorization
- Image Segmentation
- Face Refinement
- Super Resolution (SRGAN)

## Yêu cầu hệ thống

- Node.js v18 hoặc cao hơn
- Python 3.13 hoặc cao hơn
- Docker Desktop
- 8 GB RAM tối thiểu (16 GB khuyến nghị)
- OpenAI API key

## Cài đặt và khởi động nhanh

### Bước 1: Cấu hình biến môi trường

Sao chép file `aiie-agent-api\.env.example` thành `aiie-agent-api\.env` và cập nhật:

```env
# Database
DB_NAME=aiie_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5433

# OpenAI (bắt buộc)
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-mini

# Services
SD_API_URL=http://localhost:8001
SRGAN_API_URL=http://localhost:8002

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_RETURN_ENDPOINT=http://localhost:9000
MINIO_SECURE=false

# LangChain (tuỳ chọn)
LANGCHAIN_TRACING_V2=false
```

Lấy OpenAI API key tại: https://platform.openai.com/api-keys

### Bước 2: Khởi động tất cả services

Chạy script tự động:

```powershell
.\start-all.ps1
```

Script này sẽ:
- Kiểm tra Docker
- Khởi động PostgreSQL (port 5433)
- Khởi động MinIO (port 9000/9001)
- Khởi động Agent API (port 8000)
- Khởi động Stable Diffusion API (port 8001)
- Khởi động SRGAN API (port 8002)
- Khởi động Frontend (port 5173)

### Bước 3: Tạo bucket MinIO (lần đầu)

1. Truy cập http://localhost:9001
2. Đăng nhập: minioadmin / minioadmin
3. Tạo bucket tên: aiie-storage
4. Chọn Access Policy: Public

### Bước 4: Truy cập ứng dụng

- Frontend: http://localhost:5173
- Agent API: http://localhost:8000/docs
- SD API: http://localhost:8001/docs
- SRGAN API: http://localhost:8002/docs
- MinIO: http://localhost:9001

### Dừng tất cả services

```powershell
.\stop-all.ps1
```

## Khởi động thủ công (tùy chọn)

Nếu muốn khởi động từng service riêng lẻ:

PostgreSQL:

```powershell
docker run -d --name aiie-postgres `
  -e POSTGRES_DB=aiie_db `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=postgres `
  -p 5433:5432 `
  postgres:15
```

MinIO:

```powershell
docker run -d --name aiie-minio `
  -p 9000:9000 `
  -p 9001:9001 `
  -e MINIO_ROOT_USER=minioadmin `
  -e MINIO_ROOT_PASSWORD=minioadmin `
  minio/minio server /data --console-address ":9001"
```

Agent API:

```powershell
cd aiie-agent-api
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

Stable Diffusion API:

```powershell
cd aiie-sd-api
.\venv\Scripts\activate
$env:PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True'
uvicorn app.main:app --reload --port 8001
```

SRGAN API:

```powershell
cd aiie-srgan-api
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8002
```

Frontend:

```powershell
cd aiie-ui
npm run dev
```

## Cấu hình nâng cao

### Thay đổi model Stable Diffusion

Cập nhật biến `DEFAULT_MODEL` trong `aiie-sd-api\.env`:

```env
DEFAULT_MODEL=stabilityai/stable-diffusion-xl-base-1.0
```

Các model khác:
- stabilityai/stable-diffusion-2-1
- runwayml/stable-diffusion-v1-5

### Sử dụng GPU

Để sử dụng NVIDIA GPU:

1. Cài đặt CUDA Toolkit
2. Cài đặt PyTorch CUDA version
3. Thiết lập: `$env:PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True'`
4. Services sẽ tự động sử dụng GPU

## Kiến trúc dự án

Dự án gồm 4 service chính:

**aiie-agent-api** (FastAPI + LangChain + LangGraph)
- AI Agent chat backend
- Quản lý database (PostgreSQL)
- API REST để gọi các services khác
- Authentication và authorization
- Dependencies: FastAPI, LangChain, SQLModel, MinIO client

**aiie-sd-api** (FastAPI + Diffusers)
- Stable Diffusion pipelines
- Text-to-Image, Image-to-Image, Inpainting, Expansion
- Model caching và optimization

**aiie-srgan-api** (FastAPI + TensorFlow)
- Super Resolution sử dụng SRGAN
- Image upscaling

**aiie-ui** (React + TypeScript + Vite)
- Frontend chat interface
- Image generation và editing UI
- Ant Design components

## Xử lý sự cố

### Docker not running

Khởi động Docker Desktop trước khi chạy start-all.ps1.

### Connection refused khi gọi API

Kiểm tra service đang chạy:

```powershell
netstat -ano | findstr :8000
```

### Database connection failed

Kiểm tra PostgreSQL container:

```powershell
docker ps
docker logs aiie-postgres
```

### MinIO bucket not found

Tạo bucket tại http://localhost:9001 với tên aiie-storage.

### SD API khởi động lâu

Lần đầu chạy sẽ tải model (~4 GB) từ Hugging Face. Có thể mất 10-30 phút.

## Ghi chú

- Agent API tự động tạo database schema khi khởi động
- Tất cả services chạy ở development mode với auto-reload
- PostgreSQL chạy trên port 5433 (không 5432)
- Lần đầu chạy SD API sẽ tải model từ Hugging Face

