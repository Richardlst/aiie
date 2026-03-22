import { useState, useRef } from "react";
import {
  Form,
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
  Switch,
} from "antd";
import { FormOutlined, PictureOutlined } from "@ant-design/icons";
import { Sparkles, UserCircle2 } from "lucide-react";
import type { UploadFile } from "antd/es/upload/interface";
import { saveImage, faceRefineApi } from "../services/apis";
import { handlePreviewCallback } from "../utils";
import UploadButton from "../components/UploadButton";
import DisplayImage from "../components/DisplayImage";

const { Title, Paragraph } = Typography;

interface FaceRefineFormValues {
  upscale: number;
  only_center_face: boolean;
  weight: number;
}

const initialValues: FaceRefineFormValues = {
  upscale: 2,
  only_center_face: false,
  weight: 0.5,
};

const FaceRefine = () => {
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
    const isLt10M = file.size / 1024 / 1024 < 10;
    if (!isLt10M) {
      messageApi.error("File size must be smaller than 10MB!");
      return Upload.LIST_IGNORE;
    }
    return false;
  };

  const handleGenerate = async (values: FaceRefineFormValues) => {
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
      const responseData = await faceRefineApi(requestData);
      
      setProcessedImages({
        original: imageUrl,
        processed: responseData.image_url,
      });

      messageApi.success("Face refinement completed successfully!");

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
        className="rounded-2xl mb-12 p-10 bg-gradient-to-r from-[#667eea] to-[#764ba2] text-white shadow-card"
        style={{
          boxShadow: "0 8px 24px rgba(102, 126, 234, 0.35)",
        }}
      >
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm mb-4">
            <UserCircle2 size={32} className="text-white" />
          </div>
          <Title style={{ color: "white" }} level={1} className="mb-6">
            Face Refinement
          </Title>
          <Paragraph className="text-lg mt-4 mb-8 max-w-3xl mx-auto text-white/90">
            Enhance facial features in your photos with AI-powered refinement. 
            Improve skin texture, enhance details, correct colors, and create 
            professional-quality portraits with natural results.
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
              Upload a portrait or photo with faces to enhance
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
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-[#667eea] to-[#764ba2] flex items-center justify-center text-white font-semibold">
                  1
                </div>
                <div>
                  <div className="font-semibold mb-1">Upload Portrait</div>
                  <div className="text-gray-600 text-sm">
                    Choose an image with one or more faces
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-[#667eea] to-[#764ba2] flex items-center justify-center text-white font-semibold">
                  2
                </div>
                <div>
                  <div className="font-semibold mb-1">Configure Settings</div>
                  <div className="text-gray-600 text-sm">
                    Adjust enhancement strength and features
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-[#667eea] to-[#764ba2] flex items-center justify-center text-white font-semibold">
                  3
                </div>
                <div>
                  <div className="font-semibold mb-1">AI Enhancement</div>
                  <div className="text-gray-600 text-sm">
                    Our AI refines facial features naturally and professionally
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
          Refinement Settings
        </Title>
        <Form
          form={form}
          layout="vertical"
          initialValues={initialValues}
          onFinish={handleGenerate}
        >
          <Row gutter={24}>
            <Col xs={24} md={8}>
              <Form.Item
                label="Upscale Factor"
                name="upscale"
                tooltip="Super-resolution upscale factor (1–4×)"
              >
                <InputNumber min={1} max={4} className="w-full" />
              </Form.Item>
            </Col>

            <Col xs={24} md={8}>
              <Form.Item
                label="Restoration Weight"
                name="weight"
                tooltip="1.0 = max detail restoration, 0.0 = preserve original identity"
              >
                <Slider
                  min={0}
                  max={1}
                  step={0.1}
                  marks={{
                    0: "Original",
                    0.5: "Balanced",
                    1: "Restored",
                  }}
                />
              </Form.Item>
            </Col>

            <Col xs={24} md={8}>
              <Form.Item
                label="Only Center Face"
                name="only_center_face"
                valuePropName="checked"
                tooltip="Restore only the largest/center face and leave others untouched"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              size="large"
              className="w-full bg-gradient-to-r from-[#667eea] to-[#764ba2] border-0 hover:opacity-90"
              style={{ height: "48px" }}
              icon={<Sparkles className="w-5 h-5" />}
            >
              {loading ? "Refining..." : "Refine Face"}
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
                <div className="text-center mb-2 font-semibold" style={{ color: "#667eea" }}>Refined</div>
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

export default FaceRefine;
