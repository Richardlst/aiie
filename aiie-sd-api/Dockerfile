# Sử dụng image cơ sở phù hợp với CUDA 12.1
FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu22.04

# Thiết lập biến môi trường để tránh tương tác với người dùng
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Cài đặt các gói cần thiết trong một layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3.10-distutils \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Thiết lập thư mục làm việc
WORKDIR /code

# Cài đặt các dependencies Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tạo các thư mục cần thiết
RUN mkdir -p /code/models

# Copy source code
COPY ./app /code/app/

# Thiết lập volumes
VOLUME ["/code/models", "/root/.cache/huggingface"]

# Expose port
EXPOSE 8002

# Khởi chạy ứng dụng
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
