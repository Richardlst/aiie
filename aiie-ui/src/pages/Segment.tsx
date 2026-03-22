import { useState, useRef } from "react";
import {
  Form,
  Input,
  Button,
  Card,
  Row,
  Col,
  Upload,
  Image,
  message,
  Typography,
} from "antd";
import { FormOutlined, PlusOutlined } from "@ant-design/icons";
import {
  Wand2,
  Settings,
  SquareBottomDashedScissors,
} from "lucide-react";
import type { UploadFile } from "antd/es/upload/interface";
import { saveImage, segmentApi } from "../services/apis";
import DisplayImage from "../components/DisplayImage";
import { SegmentRequest } from "../types/image";

const { Title, Paragraph } = Typography;

// Sử dụng interface SegmentRequest từ types/image.ts
// Bỏ image_url vì sẽ được thêm vào sau khi upload file
const initialValues: Omit<SegmentRequest, "image_url"> = {
  prompts: "head",
};

const Segment = () => {
  const [loading, setLoading] = useState(false);
  const [processedImages, setProcessedImages] = useState<{
    original: string;
    segmented: string;
  } | null>(null);
  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage();
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewImage, setPreviewImage] = useState("");
  const resultsRef = useRef<HTMLDivElement>(null);

  const getBase64 = (file: File): Promise<string> =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = (error) => reject(error);
    });

  const handlePreview = async (file: UploadFile) => {
    if (!file.url && !file.preview) {
      file.preview = await getBase64(file.originFileObj as File);
    }

    setPreviewImage(file.url || (file.preview as string));
    setPreviewOpen(true);
  };

  const handleChange = ({
    fileList: newFileList,
  }: {
    fileList: UploadFile[];
  }) => {
    setFileList(newFileList);
  };

  const handleGenerate = async (values: Omit<SegmentRequest, "image_url">) => {
    if (!fileList[0]) {
      messageApi.error("Please upload an image first!");
      return;
    }

    setLoading(true);
    try {
      const saveResponseData = await saveImage(fileList[0]);
      const imageUrl = saveResponseData.data.url;

      const requestData: SegmentRequest = {
        ...values,
        image_url: imageUrl,
      };

      const responseData = await segmentApi(requestData);

      setProcessedImages({
        original: imageUrl,
        segmented: responseData.image_url,
      });

      // Scroll to results after images are set
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (error) {
      console.error("Error generating segmentation:", error);
      messageApi.error("Error generating segmentation");
    } finally {
      setLoading(false);
    }
  };

  const uploadButton = (
    <button style={{ border: 0, background: "none" }} type="button">
      <PlusOutlined />
      <div style={{ marginTop: 8 }}>Upload</div>
    </button>
  );

  return (
    <div className="max-w-6xl mx-auto p-6">
      {contextHolder}

      {/* Header Section */}
      <div className="rounded-2xl mb-12 p-10 bg-gradient-to-r from-[#667eea] to-[#764ba2] text-white shadow-card" style={{
        boxShadow: '0 8px 24px rgba(102, 126, 234, 0.35)'
      }}>
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm mb-4">
            <SquareBottomDashedScissors size={32} className="text-white" />
          </div>
          <Title style={{ color: "white" }} level={1} className="mb-6">
            Image Segmentation
          </Title>
          <Paragraph className="text-lg mt-4 mb-8 max-w-3xl mx-auto text-white/90">
            Identify and extract specific objects or regions from your images
            using our advanced AI segmentation tool.
          </Paragraph>
        </div>
      </div>

      {/* Row 1: Upload Image and How It Works */}
      <Row gutter={[24, 24]} className="mb-8">
        <Col xs={24} md={12}>
          <Card className="shadow-card border-gray-100 h-full">
            <Title level={4} className="mb-4">
              How It Works
            </Title>

            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <Title level={5} className="mb-4 gradient-text">
                Process Overview
              </Title>
              <ul className="space-y-3 text-gray-600">
                <li className="flex items-start">
                  <div
                    className="mr-3 p-1 rounded-full"
                    style={{ backgroundColor: "#667eea15" }}
                  >
                    <SquareBottomDashedScissors
                      className="w-4 h-4"
                      style={{ color: "#667eea" }}
                    />
                  </div>
                  <span>Upload your source image for segmentation</span>
                </li>
                <li className="flex items-start">
                  <div
                    className="mr-3 p-1 rounded-full"
                    style={{ backgroundColor: "#5cb8e615" }}
                  >
                    <Wand2 className="w-4 h-4" style={{ color: "#5cb8e6" }} />
                  </div>
                  <span>Specify what you want to segment in the image</span>
                </li>
                <li className="flex items-start">
                  <div
                    className="mr-3 p-1 rounded-full"
                    style={{ backgroundColor: "#7c5aff15" }}
                  >
                    <Settings
                      className="w-4 h-4"
                      style={{ color: "#7c5aff" }}
                    />
                  </div>
                  <span>
                    AI will identify and segment your specified target
                  </span>
                </li>
              </ul>

              <div className="mt-6 p-4 bg-white/50 rounded-lg border border-gray-100">
                <Title level={5} className="mb-3">
                  Supported Formats
                </Title>
                <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                  <div>• PNG</div>
                  <div>• JPEG/JPG</div>
                  <div>• WebP</div>
                  <div>• GIF (static)</div>
                </div>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card
            className="shadow-md border-gray-100 h-full"
            title={
              <div className="flex items-center gap-3">
                <div
                  className="p-2 rounded-lg"
                  style={{ backgroundColor: "#7c5aff15" }}
                >
                  <SquareBottomDashedScissors className="w-5 h-5 text-[#7c5aff]" />
                </div>
                <span className="text-lg font-medium">Upload Image</span>
              </div>
            }
          >
            <div className="flex flex-col items-center justify-center p-4">
              <Upload
                fileList={fileList}
                onChange={handleChange}
                onPreview={handlePreview}
                beforeUpload={(file) => {
                  const isLt10M = file.size / 1024 / 1024 < 10;
                  if (!isLt10M) {
                    messageApi.error("File size must be smaller than 10MB!");
                    return Upload.LIST_IGNORE;
                  }
                  return false;
                }}
                maxCount={1}
                accept="image/*"
                listType="picture-circle"
              >
                {fileList.length >= 1 ? null : uploadButton}
              </Upload>

              <div className="w-full mt-6 space-y-3">
                <div className="flex items-center p-3 bg-white rounded-lg border border-gray-200">
                  <div className="p-2 bg-purple-100 rounded-full mr-3">
                    <SquareBottomDashedScissors className="text-[#7c5aff]" />
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-800">
                      High Quality Images
                    </p>
                    <p className="text-gray-600">
                      For best results, use clear, high-resolution images
                    </p>
                  </div>
                </div>

                <div className="flex items-center p-3 bg-white rounded-lg border border-gray-200">
                  <div className="p-2 bg-blue-100 rounded-full mr-3">
                    <Settings className="text-[#5cb8e6]" />
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-800">
                      Automatic Processing
                    </p>
                    <p className="text-gray-600">
                      Our AI will segment your image automatically
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Row 2: Form and Settings */}
      <Form
        form={form}
        onFinish={handleGenerate}
        layout="vertical"
        initialValues={initialValues}
      >
        <Card className="shadow-md border-gray-100 mb-8">
          <Row gutter={[24, 24]}>
            <Col xs={24} md={15}>
              <Form.Item
                name="prompts"
                label="What would you like to segment?"
                rules={[
                  { required: true, message: "Please input your prompts!" },
                ]}
              >
                <Input.TextArea
                  rows={6}
                  placeholder="Enter what you want to segment (e.g., 'head', 'person', 'car')"
                  className="rounded-lg"
                />
              </Form.Item>
            </Col>

            <Col xs={24} md={9}>
              <Card
                className="shadow-md border-gray-100"
                title={
                  <div className="flex items-center gap-3">
                    <div
                      className="p-2 rounded-lg"
                      style={{ backgroundColor: "#7c5aff15" }}
                    >
                      <Settings className="w-5 h-5 text-[#7c5aff]" />
                    </div>
                    <span className="text-lg font-medium">
                      Segmentation Settings
                    </span>
                  </div>
                }
              >
                <div className="text-gray-600">
                  <p className="mb-2">• Be specific in your prompts</p>
                  <p className="mb-2">• Use clear, descriptive language</p>
                  <p>• Multiple objects can be specified</p>
                </div>
              </Card>
            </Col>
          </Row>
        </Card>

        {/* Submit Button */}
        <Card className="shadow-md border-gray-100 mb-8 p-0">
          <div className="flex justify-center">
            <Form.Item className="w-full mb-0">
              <Button
                type="primary"
                htmlType="submit"
                icon={<FormOutlined />}
                loading={loading}
                disabled={fileList.length === 0}
                size="large"
                className="w-full"
                style={{
                  background: "linear-gradient(to right, #7c5aff, #5cb8e6)",
                  border: "none",
                }}
              >
                Generate Segmentation
              </Button>
            </Form.Item>
          </div>
        </Card>
      </Form>

      {/* Results Section */}
      {processedImages ? (
        <div
          ref={resultsRef}
          className="p-6 rounded-xl shadow-card animate-fade-in"
          style={{
            background: "white",
          }}
        >
          <Title level={2} className="text-center mb-8 gradient-text">
            Segmentation Results
          </Title>
          <Row gutter={[24, 24]}>
            <Col xs={24} md={12}>
              <Card
                className="shadow-card border-gray-100"
                title="Original Image"
              >
                <DisplayImage imageUrl={processedImages.original} />
              </Card>
            </Col>
            <Col xs={24} md={12}>
              <Card
                className="shadow-card border-gray-100"
                title="Segmented Image"
              >
                <DisplayImage imageUrl={processedImages.segmented} />
              </Card>
            </Col>
          </Row>
        </div>
      ) : null}

      <Image
        style={{ display: "none" }}
        preview={{
          visible: previewOpen,
          onVisibleChange: (visible) => setPreviewOpen(visible),
          afterOpenChange: (visible) => !visible && setPreviewImage(""),
        }}
        src={previewImage}
      />
    </div>
  );
};

export default Segment;
