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
    Image,
    message,
    Select,
    Typography,
  } from "antd";
  import { FormOutlined, PictureOutlined } from "@ant-design/icons";
  import { ImageIcon, Wand2, Settings } from "lucide-react";
  import type { UploadFile } from "antd/es/upload/interface";
  import { imageToImageApi, saveImage } from "../services/apis";
  import { MODEL_OPTIONS } from "../constant/modelOptions";
  import { handlePreviewCallback } from "../utils";
  import UploadButton from "../components/UploadButton";
  import DisplayImage from "../components/DisplayImage";
  import { Img2ImgRequest } from "../types/image";
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
    Image,
    message,
    Select,
    Typography,
  } from "antd";
  import { FormOutlined, PictureOutlined } from "@ant-design/icons";
  import { ImageIcon, Wand2, Settings } from "lucide-react";
  import type { UploadFile } from "antd/es/upload/interface";
  import { imageToImageApi, saveImage } from "../services/apis";
  import { MODEL_OPTIONS } from "../constant/modelOptions";
  import { handlePreviewCallback } from "../utils";
  import UploadButton from "../components/UploadButton";
  import DisplayImage from "../components/DisplayImage";
  import { Img2ImgRequest } from "../types/image";

  const { Title, Paragraph } = Typography;
  const { Title, Paragraph } = Typography;

  const initialValues: Omit<Img2ImgRequest, "image_url"> = {
    model: "runwayml/stable-diffusion-v1-5",
    prompt:
      "anime style, flat color, simple background, lineart, masterpiece, high quality, 2d, looking at camera",
    negative_prompt:  
      "realistic, photorealistic, 3d, render, lowres, bad anatomy, bad proportions, blurry, worst quality, low quality, jpeg artifacts, watermark, signature, extra limbs, missing fingers, mutated hands, poorly drawn face, deformed",
    num_inference_steps: 50,
    guidance_scale: 9.5,
    strength: 0.60,
    canny_low_threshold: 100,
    canny_high_threshold: 180,
    controlnet_conditioning_scale: 0.65,
  };

  const ImageToImage = () => {
    const [loading, setLoading] = useState(false);
    const [fileList, setFileList] = useState<UploadFile[]>([]);
    const [processedImages, setProcessedImages] = useState<{
      original: string;
      processed: string;
    } | null>(null);
    const [previewOpen, setPreviewOpen] = useState(false);
    const [previewImage, setPreviewImage] = useState("");
    const [form] = Form.useForm();
    const [messageApi, contextHolder] = message.useMessage();
    const resultsRef = useRef<HTMLDivElement>(null);
  const ImageToImage = () => {
    const [loading, setLoading] = useState(false);
    const [fileList, setFileList] = useState<UploadFile[]>([]);
    const [processedImages, setProcessedImages] = useState<{
      original: string;
      processed: string;
    } | null>(null);
    const [previewOpen, setPreviewOpen] = useState(false);
    const [previewImage, setPreviewImage] = useState("");
    const [form] = Form.useForm();
    const [messageApi, contextHolder] = message.useMessage();
    const resultsRef = useRef<HTMLDivElement>(null);

    const handleGenerate = async (values: Omit<Img2ImgRequest, "image_url">) => {
      if (fileList.length === 0) return;
    const handleGenerate = async (values: Omit<Img2ImgRequest, "image_url">) => {
      if (fileList.length === 0) return;

      setLoading(true);
      setProcessedImages(null);
      try {
        if (fileList.length === 0) {
          messageApi.error("Please upload an image");
          return;
        }
      setLoading(true);
      setProcessedImages(null);
      try {
        if (fileList.length === 0) {
          messageApi.error("Please upload an image");
          return;
        }

        const saveResponseData = await saveImage(fileList[0]);
        const imageUrl = saveResponseData.data.url;
        const saveResponseData = await saveImage(fileList[0]);
        const imageUrl = saveResponseData.data.url;

        const requestData: Img2ImgRequest = {
          ...values,
          image_url: imageUrl,
        };
        const requestData: Img2ImgRequest = {
          ...values,
          image_url: imageUrl,
        };

        const responseData = await imageToImageApi(requestData);
        const responseData = await imageToImageApi(requestData);

        setProcessedImages({
          original: imageUrl,
          processed: responseData.image_url,
        });
        setProcessedImages({
          original: imageUrl,
          processed: responseData.image_url,
        });

        // Scroll to results after images are set
        setTimeout(() => {
          resultsRef.current?.scrollIntoView({ behavior: "smooth" });
        }, 100);
      } catch (error) {
        console.error("Error generating image:", error);
        messageApi.error("Error generating image");
      } finally {
        setLoading(false);
      }
    };
        // Scroll to results after images are set
        setTimeout(() => {
          resultsRef.current?.scrollIntoView({ behavior: "smooth" });
        }, 100);
      } catch (error) {
        console.error("Error generating image:", error);
        messageApi.error("Error generating image");
      } finally {
        setLoading(false);
      }
    };

    return (
      <div className="max-w-6xl mx-auto p-6">
        {contextHolder}
    return (
      <div className="max-w-6xl mx-auto p-6">
        {contextHolder}

        {/* Header Section */}
        <div className="rounded-2xl mb-12 p-10 text-white shadow-card" style={{
          boxShadow: '0 8px 24px rgba(198, 215, 207, 0.35)',
          background: 'linear-gradient(135deg, #c6d7cf 0%, #9eb3a8 100%)'
        }}>
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm mb-4">
              <ImageIcon size={32} className="text-white" />
            </div>
            <Title style={{ color: "white" }} level={1} className="mb-6">
              Image to Image Transformation
            </Title>
            <Paragraph className="text-lg mt-4 mb-8 max-w-3xl mx-auto text-white/90">
              Transform your existing images into new variations using
              state-of-the-art AI models. Perfect for style transfer, artistic
              modifications, and creative transformations.
            </Paragraph>
          </div>
        </div>
        {/* Header Section */}
        <div className="rounded-2xl mb-12 p-10 text-white shadow-card" style={{
          boxShadow: '0 8px 24px rgba(198, 215, 207, 0.35)',
          background: 'linear-gradient(135deg, #c6d7cf 0%, #9eb3a8 100%)'
        }}>
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm mb-4">
              <ImageIcon size={32} className="text-white" />
            </div>
            <Title style={{ color: "white" }} level={1} className="mb-6">
              Image to Image Transformation
            </Title>
            <Paragraph className="text-lg mt-4 mb-8 max-w-3xl mx-auto text-white/90">
              Transform your existing images into new variations using
              state-of-the-art AI models. Perfect for style transfer, artistic
              modifications, and creative transformations.
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
                      style={{ backgroundColor: "#9eb3a815" }}
                    >
                      <ImageIcon
                        className="w-4 h-4"
                        style={{ color: "#9eb3a8" }}
                      />
                    </div>
                    <span>Upload your source image for transformation</span>
                  </li>
                  <li className="flex items-start">
                    <div
                      className="mr-3 p-1 rounded-full"
                      style={{ backgroundColor: "#9eb3a815" }}
                    >
                      <Wand2 className="w-4 h-4" style={{ color: "#9eb3a8" }} />
                    </div>
                    <span>Configure transformation settings and prompts</span>
                  </li>
                  <li className="flex items-start">
                    <div
                      className="mr-3 p-1 rounded-full"
                      style={{ backgroundColor: "#9eb3a815" }}
                    >
                      <Settings
                        className="w-4 h-4"
                        style={{ color: "#9eb3a8" }}
                      />
                    </div>
                    <span>
                      AI will transform your image based on your settings
                    </span>
                  </li>
                </ul>
              <div className="bg-white rounded-lg p-6 border border-gray-200">
                <Title level={5} className="mb-4 gradient-text">
                  Process Overview
                </Title>
                <ul className="space-y-3 text-gray-600">
                  <li className="flex items-start">
                    <div
                      className="mr-3 p-1 rounded-full"
                      style={{ backgroundColor: "#9eb3a815" }}
                    >
                      <ImageIcon
                        className="w-4 h-4"
                        style={{ color: "#9eb3a8" }}
                      />
                    </div>
                    <span>Upload your source image for transformation</span>
                  </li>
                  <li className="flex items-start">
                    <div
                      className="mr-3 p-1 rounded-full"
                      style={{ backgroundColor: "#9eb3a815" }}
                    >
                      <Wand2 className="w-4 h-4" style={{ color: "#9eb3a8" }} />
                    </div>
                    <span>Configure transformation settings and prompts</span>
                  </li>
                  <li className="flex items-start">
                    <div
                      className="mr-3 p-1 rounded-full"
                      style={{ backgroundColor: "#9eb3a815" }}
                    >
                      <Settings
                        className="w-4 h-4"
                        style={{ color: "#9eb3a8" }}
                      />
                    </div>
                    <span>
                      AI will transform your image based on your settings
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
                    <ImageIcon className="w-5 h-5 text-[#7c5aff]" />
                  </div>
                  <span className="text-lg font-medium">Upload Image</span>
                </div>
              }
            >
              <div className="flex flex-col items-center justify-center p-4">
                <Upload
                  fileList={fileList}
                  onChange={({ fileList }) => setFileList(fileList)}
                  onPreview={handlePreviewCallback(
                    setPreviewImage,
                    setPreviewOpen
                  )}
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
                  {fileList.length >= 1 ? null : <UploadButton />}
                </Upload>
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
                    <ImageIcon className="w-5 h-5 text-[#7c5aff]" />
                  </div>
                  <span className="text-lg font-medium">Upload Image</span>
                </div>
              }
            >
              <div className="flex flex-col items-center justify-center p-4">
                <Upload
                  fileList={fileList}
                  onChange={({ fileList }) => setFileList(fileList)}
                  onPreview={handlePreviewCallback(
                    setPreviewImage,
                    setPreviewOpen
                  )}
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
                  {fileList.length >= 1 ? null : <UploadButton />}
                </Upload>

                <div className="w-full mt-6 space-y-3">
                  <div className="flex items-center p-3 bg-blue-50 rounded-lg">
                    <div className="p-2 bg-blue-100 rounded-full mr-3">
                      <PictureOutlined className="text-[#7c5aff]" />
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
                <div className="w-full mt-6 space-y-3">
                  <div className="flex items-center p-3 bg-blue-50 rounded-lg">
                    <div className="p-2 bg-blue-100 rounded-full mr-3">
                      <PictureOutlined className="text-[#7c5aff]" />
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

                  <div className="flex items-center p-3 bg-purple-50 rounded-lg">
                    <div className="p-2 bg-purple-100 rounded-full mr-3">
                      <Settings className="text-purple-600" />
                    </div>
                    <div className="text-sm">
                      <p className="font-medium text-gray-800">
                        Automatic Processing
                      </p>
                      <p className="text-gray-600">
                        Our AI will enhance your image automatically
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </Col>
        </Row>
                  <div className="flex items-center p-3 bg-purple-50 rounded-lg">
                    <div className="p-2 bg-purple-100 rounded-full mr-3">
                      <Settings className="text-purple-600" />
                    </div>
                    <div className="text-sm">
                      <p className="font-medium text-gray-800">
                        Automatic Processing
                      </p>
                      <p className="text-gray-600">
                        Our AI will enhance your image automatically
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </Col>
        </Row>

        {/* Row 2: Model, Prompts, and Settings */}
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
                  name="model"
                  label="Model"
                  rules={[{ required: true, message: "Please select a model!" }]}
                >
                  <Select options={MODEL_OPTIONS} />
                </Form.Item>
        {/* Row 2: Model, Prompts, and Settings */}
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
                  name="model"
                  label="Model"
                  rules={[{ required: true, message: "Please select a model!" }]}
                >
                  <Select options={MODEL_OPTIONS} />
                </Form.Item>

                <Form.Item
                  name="prompt"
                  label="Prompt"
                  rules={[
                    { required: true, message: "Please input your prompt!" },
                  ]}
                >
                  <Input.TextArea
                    rows={4}
                    placeholder="Enter your prompt here..."
                    className="mb-4"
                  />
                </Form.Item>
                <Form.Item
                  name="prompt"
                  label="Prompt"
                  rules={[
                    { required: true, message: "Please input your prompt!" },
                  ]}
                >
                  <Input.TextArea
                    rows={4}
                    placeholder="Enter your prompt here..."
                    className="mb-4"
                  />
                </Form.Item>

                <Form.Item name="negative_prompt" label="Negative Prompt">
                  <Input.TextArea
                    rows={3}
                    placeholder="Enter negative prompt (optional)"
                  />
                </Form.Item>
              </Col>
                <Form.Item name="negative_prompt" label="Negative Prompt">
                  <Input.TextArea
                    rows={3}
                    placeholder="Enter negative prompt (optional)"
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
                        Advanced Settings
                      </span>
                    </div>
                  }
                >
                  <Form.Item
                    name="num_inference_steps"
                    label="Inference Steps"
                    rules={[
                      { required: true, message: "Required" },
                      { type: "number", min: 1, max: 100, message: "1-100" },
                    ]}
                  >
                    <InputNumber min={1} max={100} style={{ width: "100%" }} />
                  </Form.Item>
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
                        Advanced Settings
                      </span>
                    </div>
                  }
                >
                  <Form.Item
                    name="num_inference_steps"
                    label="Inference Steps"
                    rules={[
                      { required: true, message: "Required" },
                      { type: "number", min: 1, max: 100, message: "1-100" },
                    ]}
                  >
                    <InputNumber min={1} max={100} style={{ width: "100%" }} />
                  </Form.Item>

                  <Form.Item
                    name="guidance_scale"
                    label="Guidance Scale"
                    rules={[
                      { required: true, message: "Required" },
                      { type: "number", min: 1, max: 20, message: "1-20" },
                    ]}
                  >
                    <InputNumber
                      min={1}
                      max={20}
                      step={0.1}
                      style={{ width: "100%" }}
                    />
                  </Form.Item>
                  <Form.Item
                    name="guidance_scale"
                    label="Guidance Scale"
                    rules={[
                      { required: true, message: "Required" },
                      { type: "number", min: 1, max: 20, message: "1-20" },
                    ]}
                  >
                    <InputNumber
                      min={1}
                      max={20}
                      step={0.1}
                      style={{ width: "100%" }}
                    />
                  </Form.Item>

                  <Form.Item
                    name="strength"
                    label="Strength"
                    rules={[
                      { required: true, message: "Required" },
                      { type: "number", min: 0, max: 1, message: "0-1" },
                    ]}
                  >
                    <InputNumber
                      min={0}
                      max={1}
                      step={0.1}
                      style={{ width: "100%" }}
                    />
                  </Form.Item>
                </Card>
              </Col>
            </Row>
          </Card>
                  <Form.Item
                    name="strength"
                    label="Strength"
                    rules={[
                      { required: true, message: "Required" },
                      { type: "number", min: 0, max: 1, message: "0-1" },
                    ]}
                  >
                    <InputNumber
                      min={0}
                      max={1}
                      step={0.1}
                      style={{ width: "100%" }}
                    />
                  </Form.Item>
                </Card>
              </Col>
            </Row>
          </Card>

          {/* Row 2: Process Button */}
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
                  Generate Image
                </Button>
              </Form.Item>
            </div>
          </Card>
        </Form>
          {/* Row 2: Process Button */}
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
                  Generate Image
                </Button>
              </Form.Item>
            </div>
          </Card>
        </Form>

        {/* Row 3: Results */}
        {processedImages ? (
          <div
            className="p-6 rounded-xl shadow-card animate-fade-in"
            style={{
              background: "white",
            }}
          >
            <Title level={2} className="text-center mb-8 gradient-text">
              Generated Results
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
                  title="Generated Image"
                >
                  <DisplayImage imageUrl={processedImages.processed} />
                </Card>
              </Col>
            </Row>
          </div>
        ) : null}
        {/* Row 3: Results */}
        {processedImages ? (
          <div
            className="p-6 rounded-xl shadow-card animate-fade-in"
            style={{
              background: "white",
            }}
          >
            <Title level={2} className="text-center mb-8 gradient-text">
              Generated Results
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
                  title="Generated Image"
                >
                  <DisplayImage imageUrl={processedImages.processed} />
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
        <div ref={resultsRef} />
      </div>
    );
  };
        <Image
          style={{ display: "none" }}
          preview={{
            visible: previewOpen,
            onVisibleChange: (visible) => setPreviewOpen(visible),
            afterOpenChange: (visible) => !visible && setPreviewImage(""),
          }}
          src={previewImage}
        />
        <div ref={resultsRef} />
      </div>
    );
  };

  export default ImageToImage;
  export default ImageToImage;
