# Dockerfile tối ưu cho ứng dụng Python FastAPI
# Sử dụng multi-stage build để giảm kích thước image cuối cùng

# Stage 1: Base image cho cả builder và final
FROM python:3.10-slim AS base

# Thiết lập biến môi trường để tối ưu hóa Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.6.1

# Stage 2: Builder - cài đặt dependencies
FROM base AS builder

# Cài đặt các package cần thiết để compile dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Sao chép requirements vào image
COPY requirements.txt .

# Cài đặt dependencies vào thư mục /app/venv
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Cài đặt dependencies trong build stage
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Final - chỉ chứa ứng dụng và runtime dependencies
FROM base AS final

# Cài đặt runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Sao chép virtual environment từ builder stage
COPY --from=builder /app/venv /app/venv

# Sao chép mã nguồn ứng dụng vào image
COPY . .

# Kích hoạt virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Mở port mà ứng dụng sẽ lắng nghe
EXPOSE 8000

# Khởi động ứng dụng với Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]