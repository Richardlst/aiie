import { UploadFile } from "antd/es/upload/interface";

export const getBase64 = (file: File | Blob): Promise<string> =>
    new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = (error) => reject(error);
    });

export const handlePreviewCallback = (setPreviewImage: (image: string) => void, setPreviewOpen: (open: boolean) => void) => {
    return async (file: UploadFile) => {
        if (!file.url && !file.preview) {
            file.preview = await getBase64(file.originFileObj as File);
        }
        setPreviewImage(file.url || (file.preview as string));
        setPreviewOpen(true);
    };
}

export const downloadImage = async (imageUrl: string) => {
    if (!imageUrl) {
        console.error("Image URL is not provided");
        return;
    }

    try {
        // Fetch ảnh dưới dạng blob
        const response = await fetch(imageUrl);

        // Kiểm tra nếu fetch thành công
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Chuyển đổi response thành blob
        const blob = await response.blob();

        // Tạo URL từ blob
        const blobUrl = window.URL.createObjectURL(blob);

        // Tạo thẻ a để tải xuống
        const a = document.createElement("a");
        a.href = blobUrl;
        a.download = "mask.png"; // Tên file khi tải xuống
        document.body.appendChild(a);
        a.click();

        // Dọn dẹp: xóa thẻ a và giải phóng URL
        document.body.removeChild(a);
        window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
        console.error("Failed to download image:", error);
    }
}
