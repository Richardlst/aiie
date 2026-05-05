import { useState, useRef } from "react";
import {
  Form,
  Input,
  Button,
  Card,
  Row,
  Col,
  Upload,
  Image as AntImage,
  message,
  Typography,
  Slider,
  Progress,
  Checkbox,
} from "antd";
import { FormOutlined, PictureOutlined } from "@ant-design/icons";
import { Palette, Sparkles, Download } from "lucide-react";
import type { UploadFile } from "antd/es/upload/interface";
import { saveImage } from "../services/apis";
import { getBase64, handlePreviewCallback } from "../utils";
import UploadButton from "../components/UploadButton";
import DisplayImage from "../components/DisplayImage";

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;

// Use local API instead of HF Space
const API_URL = "http://localhost:8000";

interface ColorizationRequest {
  image_url: string;
  prompt?: string;
  color_intensity?: number;
  fast_mode?: boolean;
}

const initialValues = {
  prompt: "A natural and vibrant colorization of the black and white image, realistic colors, high quality, detailed, authentic color palette, no watermarks, clean result",
  color_intensity: 0.8,
  fast_mode: false,
};

// ──────────────────────────────────────────────
// Call local Agent API for colorization
// ──────────────────────────────────────────────

async function colorizeWithLocalAPI(
  imageFile: File,
  prompt: string,
  fastMode: boolean = false,
  onProgress?: (msg: string) => void
): Promise<string> {
  onProgress?.(`Đang tải ảnh lên máy chủ${fastMode ? " (fast mode)" : ""}...`);
  
  // Step 1: Upload image to local API
  const uploadFormData = new FormData();
  uploadFormData.append("file", imageFile);

  const uploadRes = await fetch(`${API_URL}/upload`, {
    method: "POST",
    body: uploadFormData,
  });

  if (!uploadRes.ok) {
    throw new Error(`Upload failed: ${uploadRes.statusText}`);
  }

  const uploadData = await uploadRes.json();
  const imageUrl = uploadData.data?.url; // API returns { data: { url: "..." } }

  if (!imageUrl) {
    throw new Error("Upload returned no image URL");
  }

  onProgress?.("Đang xử lý ảnh (vui lòng chờ)...");

  // Step 2: Call colorization endpoint
  const colorizeRes = await fetch(`${API_URL}/image/colorization`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      image_url: imageUrl,
      prompt: prompt,
      color_intensity: 0.8,
      num_inference_steps: fastMode ? 4 : 4,  // Both use 4 steps (SDXL-Lightning default)
      guidance_scale: fastMode ? 5.0 : 7.5,   // Lower guidance = faster
    }),
  });

  if (!colorizeRes.ok) {
    const error = await colorizeRes.text();
    throw new Error(`Colorization failed (HTTP ${colorizeRes.status}): ${error}`);
  }

  const colorizeData = await colorizeRes.json();
  const resultUrl = colorizeData.image_url;

  if (!resultUrl) {
    throw new Error("No result URL returned from API");
  }

  return resultUrl;
}

// Convert UploadFile (antd) to File
function getFileFromUploadFile(uploadFile: UploadFile): File {
  const file = uploadFile.originFileObj as File;
  if (!file) throw new Error("No file object");
  return file;
}

// ──────────────────────────────────────────────
const Colorization = () => {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState<number>(0);
  const [statusText, setStatusText] = useState<string>("");
  const [imageFileList, setImageFileList] = useState<UploadFile[]>([]);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewImage, setPreviewImage] = useState("");
  const [processedImages, setProcessedImages] = useState<{
    original: string;
    processed: string;
    processedBlob?: string;
  } | null>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage();

  const handlePreview = handlePreviewCallback(setPreviewImage, setPreviewOpen);

  const handleUpload = async (file: File) => {
    const isLt10M = file.size / 1024 / 1024 < 10;
    if (!isLt10M) {
      messageApi.error("File size must be smaller than 10MB!");
      return Upload.LIST_IGNORE;
    }
    return false;
  };

  const handleGenerate = async (values: Omit<ColorizationRequest, "image_url">) => {
    if (imageFileList.length === 0) {
      messageApi.error("Vui lòng tải lên một ảnh");
      return;
    }

    setLoading(true);
    setProgress(20);
    setStatusText("Chuẩn bị file ảnh...");

    try {
      // Step 1: Get file and local preview URL
      const file = getFileFromUploadFile(imageFileList[0]);
      const objectUrl = URL.createObjectURL(file);

      // Step 2: Call local API with retry logic
      const prompt = values.prompt || initialValues.prompt;
      const fastMode = values.fast_mode || false;
      setProgress(50);
      
      const colorizedUrl = await colorizeWithLocalAPI(file, prompt, fastMode, (msg) => {
         setStatusText(msg);
      });

      setProgress(90);
      setStatusText("Đang tải kết quả về...");

      setProcessedImages({
        original: objectUrl,
        processed: colorizedUrl,
      });

      setProgress(100);
      setStatusText("Hoàn tất!");
      messageApi.success("Colorization completed successfully!");

      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: "smooth" });
        setProgress(0);
        setStatusText("");
      }, 800);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Không thể tô màu ảnh";
      console.error("Error colorizing image:", error);
      messageApi.error(`Lỗi: ${errorMessage}`);
      setProgress(0);
      setStatusText("");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!processedImages?.processed) return;
    try {
      const res = await fetch(processedImages.processed);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "colorized_image.png";
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      messageApi.error("Không thể tải ảnh về");
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {contextHolder}

      {/* Header Section */}
      <div
        className="rounded-2xl mb-12 p-10 bg-gradient-to-r from-purple-400 to-blue-400 text-white shadow-card"
        style={{ boxShadow: "0 8px 24px rgba(147, 112, 219, 0.25)" }}
      >
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm mb-4">
            <Palette size={32} className="text-white" />
          </div>
          <Title style={{ color: "white" }} level={1} className="mb-6">
            Image Colorization
          </Title>
          <Paragraph className="text-lg mt-4 mb-2 max-w-3xl mx-auto text-white/90">
            Breathe life into your black-and-white photography with advanced AI colorization. Transform historical archives, vintage portraits, or grayscale images into vibrant, photorealistic masterpieces with natural color palettes.
          </Paragraph>
          <Text className="text-white/70 text-sm">
            Powered by custom <strong>Realistic Vision & ControlNet Recolor</strong> · Local API
          </Text>
        </div>  
      </div>

      {/* Main Content */}
      <Row gutter={[24, 24]} className="mb-8">
        {/* Upload Section */}
        <Col xs={24} md={12}>
          <Card className="shadow-card border-gray-100 h-full">
            <Title level={4} className="mb-4">
              <PictureOutlined className="mr-2" />
              Upload Image
            </Title>
            <Paragraph className="text-gray-600 mb-6">
              Upload a black and white or grayscale image to colorize
            </Paragraph>
            <Upload
              listType="picture-card"
              fileList={imageFileList}
              beforeUpload={handleUpload}
              onPreview={handlePreview}
              onChange={({ fileList: newFileList }) =>
                setImageFileList(newFileList.slice(-1))
              }
              maxCount={1}
            >
              {imageFileList.length === 0 && <UploadButton />}
            </Upload>
          </Card>
        </Col>

        {/* How It Works */}
        <Col xs={24} md={12}>
          <Card className="shadow-card border-gray-100 h-full">
            <Title level={4} className="mb-4">
              How It Works
            </Title>
            <div className="space-y-4">
              {[
                { n: 1, title: "Upload Your Image", desc: "Choose a black and white or grayscale image" },
                { n: 2, title: "Describe Colors (optional)", desc: "Guide the AI with a color prompt" },
                { n: 3, title: "AI Colorizes Locally", desc: "Realistic Vision & ControlNet Recolor  processes your image" },
                { n: 4, title: "Download Result", desc: "Save your colorized masterpiece" },
              ].map(({ n, title, desc }) => (
                <div key={n} className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-purple-400 to-blue-400 flex items-center justify-center text-white font-semibold">
                    {n}
                  </div>
                  <div>
                    <div className="font-semibold mb-1">{title}</div>
                    <div className="text-gray-600 text-sm">{desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </Col>
      </Row>

      {/* Settings Form */}
      <Card className="shadow-card border-gray-100 mb-8">
        <Title level={4} className="mb-6">
          <FormOutlined className="mr-2" />
          Colorization Settings
        </Title>
        <Form
          form={form}
          layout="vertical"
          initialValues={initialValues}
          onFinish={handleGenerate}
        >
          <Row gutter={24}>
            <Col xs={24}>
              <Form.Item
                label="Prompt (Optional)"
                name="prompt"
                tooltip="Describe the desired color scheme or style"
              >
                <TextArea
                  rows={3}
                  placeholder="e.g., Warm and vibrant colors, realistic skin tones..."
                />
              </Form.Item>
            </Col>

            <Col xs={24} md={12}>
              <Form.Item
                label="Color Intensity"
                name="color_intensity"
                tooltip="Controls how vibrant the colors will be (informational only)"
              >
                <Slider
                  min={0.1}
                  max={1}
                  step={0.1}
                  marks={{
                    0.1: "Subtle",
                    0.5: "Medium",
                    1: "Vibrant",
                  }}
                />
              </Form.Item>
            </Col>

          </Row>

          {/* Progress bar */}
          {loading && (
            <div className="mb-4">
              <Progress percent={progress} status="active" />
              <div className="text-gray-500 text-sm mt-1">{statusText}</div>
            </div>
          )}

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              size="large"
              className="w-full bg-gradient-to-r from-purple-500 to-blue-500 border-0 hover:opacity-90"
              style={{ height: "48px" }}
              icon={<Sparkles className="w-5 h-5" />}
            >
              {loading ? "Colorizing..." : "Colorize Image"}
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {/* Results Section */}
      {processedImages && (
        <div ref={resultsRef}>
          <Card className="shadow-card border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <Title level={4} className="mb-0">
                <Sparkles className="inline mr-2" />
                Results
              </Title>

            </div>
            <Row gutter={[24, 24]}>
              <Col xs={24} md={12}>
                <div className="text-center mb-2 font-semibold text-gray-600">Original</div>
                <div className="flex justify-center">
                  <img
                    src={processedImages.original}
                    alt="Original"
                    style={{ maxWidth: "100%", maxHeight: 400, borderRadius: 8, objectFit: "contain" }}
                  />
                </div>
              </Col>
              <Col xs={24} md={12}>
                <div className="text-center mb-2 font-semibold text-purple-600">Colorized</div>
                <div className="flex justify-center">
                  <img
                    src={processedImages.processed}
                    alt="Colorized"
                    style={{ maxWidth: "100%", maxHeight: 400, borderRadius: 8, objectFit: "contain" }}
                    crossOrigin="anonymous"
                  />
                </div>
              </Col>
            </Row>
          </Card>
        </div>
      )}

      {previewImage && (
        <AntImage
          wrapperStyle={{ display: "none" }}
          preview={{
            visible: previewOpen,
            onVisibleChange: (visible) => setPreviewOpen(visible),
            afterOpenChange: (visible) => !visible && setPreviewImage(""),
          }}
          src={previewImage}
        />
      )}
    </div>
  );
};

export default Colorization;