# 🎨 AIIE - AI Image Enhancement Platform

Nền tảng xử lý và tạo ảnh AI với các tính năng:
- 🤖 AI Agent Chat với khả năng tạo và chỉnh sửa ảnh
- 🎨 Text-to-Image (Stable Diffusion)
- 🖼️ Image-to-Image transformation
- ✏️ Inpainting (chỉnh sửa vùng ảnh)
- 📐 Image Expansion
- 🔍 Image Segmentation
- ⬆️ Super Resolution (SRGAN)

## 📋 Yêu cầu hệ thống

- ✅ Node.js v18+
- ✅ Python 3.13+
- ✅ Docker Desktop
- ✅ 8GB+ RAM (16GB khuyến nghị)
- ✅ 10GB+ dung lượng ổ cứng trống

## 🚀 Cài đặt nhanh

### 1. Clone và cài đặt dependencies

```powershell
# Đã cài đặt xong! Bỏ qua bước này nếu đã chạy lệnh cài đặt
```

### 2. Cấu hình OpenAI API Key

Mở file `aiie-agent-api\.env` và thay thế:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

Lấy API key tại: https://platform.openai.com/api-keys

### 3. Khởi động tất cả services

```powershell
# Chạy script tự động
.\start-all.ps1
```

**Hoặc chạy thủ công từng service:**

#### Terminal 1: PostgreSQL & MinIO (Docker)
```powershell
# PostgreSQL
docker run -d --name aiie-postgres -e POSTGRES_DB=aiie_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15

# MinIO
docker run -d --name aiie-minio -p 9000:9000 -p 9001:9001 -e MINIO_ROOT_USER=minioadmin -e MINIO_ROOT_PASSWORD=minioadmin minio/minio server /data --console-address ":9001"
```

#### Terminal 2: Agent API
```powershell
cd aiie-agent-api
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

#### Terminal 3: Stable Diffusion API
```powershell
cd aiie-sd-api
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8001
```

#### Terminal 4: SRGAN API
```powershell
cd aiie-srgan-api
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8002
```

#### Terminal 5: Frontend
```powershell
cd aiie-ui
npm run dev
```

### 4. Cấu hình MinIO (Chỉ lần đầu)

1. Truy cập: http://localhost:9001
2. Đăng nhập với:
   - Username: `minioadmin`
   - Password: `minioadmin`
3. Tạo bucket mới tên: `aiie-storage`
4. Set bucket policy là **Public** (để có thể truy cập ảnh)

### 5. Truy cập ứng dụng

- **🌐 Frontend**: http://localhost:5173
- **📚 Agent API Docs**: http://localhost:8000/docs
- **🎨 SD API Docs**: http://localhost:8001/docs
- **⬆️ SRGAN API Docs**: http://localhost:8002/docs
- **💾 MinIO Console**: http://localhost:9001

## 🛑 Dừng tất cả services

```powershell
.\stop-all.ps1
```

## 📁 Cấu trúc dự án

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
├── start-all.ps1           # Script khởi động
├── stop-all.ps1            # Script dừng
└── README.md               # File này
```

## ⚙️ Cấu hình nâng cao

### Thay đổi model Stable Diffusion

Mở `aiie-sd-api\.env` và thay đổi:
```env
DEFAULT_MODEL=runwayml/stable-diffusion-v1-5
```

Các model khác có thể dùng:
- `stabilityai/stable-diffusion-2-1`
- `stabilityai/stable-diffusion-xl-base-1.0`

### Sử dụng GPU

Nếu có NVIDIA GPU với CUDA:
1. Cài đặt CUDA Toolkit
2. Cài đặt PyTorch với CUDA support
3. Services sẽ tự động detect và sử dụng GPU

## 🐛 Troubleshooting

### Lỗi: "Connection refused" khi gọi API

**Nguyên nhân**: Service chưa khởi động hoặc port bị chiếm
**Giải pháp**: 
- Kiểm tra service đang chạy
- Kiểm tra port không bị chiếm: `netstat -ano | findstr :8000`

### Lỗi: "Database connection failed"

**Nguyên nhân**: PostgreSQL chưa chạy
**Giải pháp**:
```powershell
docker start aiie-postgres
# Hoặc
docker ps -a  # Kiểm tra container
```

### Lỗi: "MinIO bucket not found"

**Nguyên nhân**: Chưa tạo bucket
**Giải pháp**: Truy cập http://localhost:9001 và tạo bucket `aiie-storage`

### Lỗi: "Out of memory" khi chạy SD API

**Nguyên nhân**: Không đủ RAM/VRAM
**Giải pháp**:
- Đóng các ứng dụng khác
- Sử dụng model nhỏ hơn
- Giảm batch size trong code

### Lần đầu chạy SD API rất lâu

**Bình thường!** Lần đầu tiên SD API sẽ tải model từ Hugging Face (~4GB), có thể mất 10-30 phút tùy tốc độ mạng.

## 📝 Ghi chú

- **Lần đầu chạy**: Agent API sẽ tự động tạo các bảng trong database
- **Model caching**: Các model AI sẽ được cache sau lần đầu tải
- **Development mode**: Tất cả services đang chạy ở chế độ development với auto-reload

## 🔒 Bảo mật

**⚠️ QUAN TRỌNG**: Đây là cấu hình development. Trước khi deploy production:

1. Thay đổi tất cả passwords trong `.env`
2. Thay đổi `SECRET_KEY` trong `aiie-agent-api\.env`
3. Cấu hình CORS đúng cách (không dùng `allow_origins=["*"]`)
4. Sử dụng HTTPS
5. Cấu hình firewall và security groups

## 📚 Tài liệu API

Sau khi khởi động services, truy cập:
- http://localhost:8000/docs - Agent API (Swagger UI)
- http://localhost:8001/docs - SD API
- http://localhost:8002/docs - SRGAN API

## 🤝 Đóng góp

Dự án này đang trong giai đoạn phát triển. Mọi đóng góp đều được hoan nghênh!

## 📄 License

[Thêm license của bạn ở đây]

---

**Chúc bạn sử dụng vui vẻ! 🎉**
