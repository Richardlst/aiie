# Sử dụng base image CUDA phù hợp với TensorFlow
FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu22.04

# Thiết lập biến môi trường để tránh tương tác trong quá trình cài đặt
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Ho_Chi_Minh

# Cài đặt Python và các gói cần thiết
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

# Copy requirements trước để tận dụng Docker cache
COPY requirements.txt .

# Cài đặt dependencies Python
RUN pip install --no-cache-dir -r requirements.txt

# Tạo thư mục cho models
RUN mkdir -p /code/models

# Copy source code
COPY . .

# Thiết lập volumes
VOLUME ["/code/models"]

# Thiết lập biến môi trường cho TensorFlow
ENV TF_FORCE_GPU_ALLOW_GROWTH=true
ENV TF_CPP_MIN_LOG_LEVEL=2

# Expose port
EXPOSE 8001

# Khởi chạy ứng dụng
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
