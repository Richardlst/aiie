import { useState, useRef } from "react";
import {
  Form,
  Input,
  Button,
  Card,
  Row,
  Col,
  InputNumber,
  Upload,
  Image as AntImage,
  message,
  Typography,
  Slider,
} from "antd";
import { FormOutlined, PictureOutlined } from "@ant-design/icons";
import { Palette, Wand2, Sparkles } from "lucide-react";
import type { UploadFile } from "antd/es/upload/interface";
import { saveImage, colorizationApi } from "../services/apis";
import { getBase64, handlePreviewCallback } from "../utils";
import UploadButton from "../components/UploadButton";
import DisplayImage from "../components/DisplayImage";

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

interface ColorizationRequest {
  image_url: string;
  prompt?: string;
  color_intensity?: number;
  num_inference_steps?: number;
  guidance_scale?: number;
}

const initialValues = {
  prompt: "A natural and vibrant colorization of the black and white image, realistic colors, high quality, detailed",
  color_intensity: 0.8,
  num_inference_steps: 4,
  guidance_scale: 7.5,
};

const Colorization = () => {
  const [loading, setLoading] = useState(false);
  const [imageFileList, setImageFileList] = useState<UploadFile[]>([]);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewImage, setPreviewImage] = useState("");
  const [processedImages, setProcessedImages] = useState<{
    original: string;
    processed: string;
  } | null>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage();

  const handlePreview = handlePreviewCallback(setPreviewImage, setPreviewOpen);

  const handleUpload = async (file: File) => {
    const base64 = await getBase64(file);
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
    try {
      const saveResponseData = await saveImage(imageFileList[0]);
      const imageUrl = saveResponseData.data.url;

      const requestData = {
        ...values,
        image_url: imageUrl,
      };
      const responseData = await colorizationApi(requestData);
      
      setProcessedImages({
        original: imageUrl,
        processed: responseData.image_url,
      });

      messageApi.success("Colorization completed successfully!");

      // Scroll to results after images are set
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (error) {
      console.error("Error generating image:", error);
      messageApi.error("Lỗi khi tạo ảnh");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {contextHolder}

      {/* Header Section */}
      <div
        className="rounded-2xl mb-12 p-10 bg-gradient-to-r from-purple-400 to-blue-400 text-white shadow-card"
        style={{
          boxShadow: "0 8px 24px rgba(147, 112, 219, 0.25)",
        }}
      >
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm mb-4">
            <Palette size={32} className="text-white" />
          </div>
          <Title style={{ color: "white" }} level={1} className="mb-6">
            Image Colorization
          </Title>
          <Paragraph className="text-lg mt-4 mb-8 max-w-3xl mx-auto text-white/90">
            Bring your black and white photos to life with AI-powered colorization. 
            Transform historic photos, vintage images, or grayscale pictures into vibrant, 
            naturally colored masterpieces.
          </Paragraph>
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
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-purple-400 to-blue-400 flex items-center justify-center text-white font-semibold">
                  1
                </div>
                <div>
                  <div className="font-semibold mb-1">Upload Your Image</div>
                  <div className="text-gray-600 text-sm">
                    Choose a black and white or grayscale image
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-purple-400 to-blue-400 flex items-center justify-center text-white font-semibold">
                  2
                </div>
                <div>
                  <div className="font-semibold mb-1">Customize Settings</div>
                  <div className="text-gray-600 text-sm">
                    Adjust color intensity and other parameters (optional)
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-purple-400 to-blue-400 flex items-center justify-center text-white font-semibold">
                  3
                </div>
                <div>
                  <div className="font-semibold mb-1">Generate Colors</div>
                  <div className="text-gray-600 text-sm">
                    Our AI analyzes and adds natural colors to your image
                  </div>
                </div>
              </div>
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

            <Col xs={24} md={8}>
              <Form.Item
                label="Color Intensity"
                name="color_intensity"
                tooltip="Controls how vibrant the colors will be"
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

            <Col xs={24} md={8}>
              <Form.Item
                label="Inference Steps"
                name="num_inference_steps"
                tooltip="SDXL-Lightning 4-step model: dùng đúng 4 steps cho kết quả tốt nhất"
              >
                <InputNumber min={1} max={8} className="w-full" />
              </Form.Item>
            </Col>

            <Col xs={24} md={8}>
              <Form.Item
                label="Guidance Scale"
                name="guidance_scale"
                tooltip="How closely to follow the prompt"
              >
                <InputNumber
                  min={1}
                  max={20}
                  step={0.5}
                  className="w-full"
                />
              </Form.Item>
            </Col>
          </Row>

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
            <Title level={4} className="mb-6">
              <Sparkles className="inline mr-2" />
              Results
            </Title>
            <Row gutter={[24, 24]}>
              <Col xs={24} md={12}>
                <div className="text-center mb-2 font-semibold text-gray-600">Original</div>
                <div className="flex justify-center">
                  <DisplayImage imageUrl={processedImages.original} imageWidth="auto" style={{ width: "auto" }} />
                </div>
              </Col>
              <Col xs={24} md={12}>
                <div className="text-center mb-2 font-semibold text-purple-600">Colorized</div>
                <div className="flex justify-center">
                  <DisplayImage imageUrl={processedImages.processed} imageWidth="auto" style={{ width: "auto" }} />
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
