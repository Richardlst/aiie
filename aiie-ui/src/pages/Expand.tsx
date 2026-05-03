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
  Select,
  Typography,
} from "antd";
import { FormOutlined } from "@ant-design/icons";
import { Image as ImageIcon, Wand2, Expand as ExpandIcon } from "lucide-react";
import type { UploadFile } from "antd/es/upload/interface";
import { expandApi, saveImage } from "../services/apis";
import { EXPAND_OPTIONS } from "../constant/modelOptions";
import { getBase64, handlePreviewCallback } from "../utils";
import UploadButton from "../components/UploadButton";
import DisplayImage from "../components/DisplayImage";
import { ExpandRequest } from "../types/image";

const { Title, Paragraph } = Typography;

// Sử dụng interface ExpandRequest từ types/image.ts
// Bỏ image_url vì sẽ được thêm vào sau khi upload file
const initialValues: Omit<ExpandRequest, "image_url"> = {
  model: "runwayml/stable-diffusion-inpainting",
  prompt:
    "natural background continuation, same landscape, trees, grass, sky, seamless extension, high quality, detailed, no new subjects",
  negative_prompt:
    "animal, giraffe, wildlife, creature, duplicate, copy, cars, vehicles, buildings, people, text, watermark, pixelated, distorted, color shift, harsh transition, blurry, low quality, artifacts, seam, logo, signature, branding, copyright mark, text overlay, branded watermark, symbol, emblem, badge, unnatural extension",
  num_inference_steps: 50,
  guidance_scale: 12,
  expand_top: 0,
  expand_bottom: 0,
  expand_left: 0,
  expand_right: 0,
};

const Expand = () => {
  const [loading, setLoading] = useState(false);
  const [imageFileList, setImageFileList] = useState<UploadFile[]>([]);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewImage, setPreviewImage] = useState("");
  const [processedImages, setProcessedImages] = useState<{
    original: string;
    processed: string;
  } | null>(null);
  const [imageDimensions, setImageDimensions] = useState({
    width: 0,
    height: 0,
  });
  const [expandValues, setExpandValues] = useState({
    top: 0,
    bottom: 0,
    left: 0,
    right: 0,
  });
  const resultsRef = useRef<HTMLDivElement>(null);

  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage();

  const handleUpload = async (file: File) => {
    const base64 = await getBase64(file);
    const img = new window.Image();
    img.src = base64;
    img.onload = () => {
      const originalDimensions = { width: img.width, height: img.height };
      setImageDimensions(originalDimensions);
    };


      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        messageApi.error("File size must be smaller than 10MB!");
        return Upload.LIST_IGNORE;
      }
    return false;
  };

  const handleGenerate = async (values: Omit<ExpandRequest, "image_url">) => {
    if (imageFileList.length === 0) {
      messageApi.error("Vui lòng tải lên một ảnh");
      return;
    }

    setLoading(true);
    try {
      const saveResponseData = await saveImage(imageFileList[0]);
      const imageUrl = saveResponseData.data.url;

      // Tạo đối tượng request từ form values, expand values và image URL
      const requestData: ExpandRequest = {
        ...values,
        image_url: imageUrl,
        expand_top: expandValues.top,
        expand_bottom: expandValues.bottom,
        expand_left: expandValues.left,
        expand_right: expandValues.right,
      };

      const responseData = await expandApi(requestData);
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
      messageApi.error("Lỗi khi tạo ảnh");
    } finally {
      setLoading(false);
    }
  };

  const handleExpandChange = (
    value: number | null,
    type: "top" | "bottom" | "left" | "right"
  ) => {
    setExpandValues((prev) => ({
      ...prev,
      [type]: value || 0,
    }));
  };

  const handleAspectRatio = (targetRatio: number) => {
    const currentWidth = imageDimensions.width;
    const currentHeight = imageDimensions.height;
    const currentRatio = currentWidth / currentHeight;

    if (currentRatio < targetRatio) {
      // Cần mở rộng chiều rộng
      const newWidth = currentHeight * targetRatio;
      const totalExpand = newWidth - currentWidth;
      setExpandValues({
        top: 0,
        bottom: 0,
        left: Math.floor(totalExpand / 2),
        right: Math.ceil(totalExpand / 2),
      });
    } else {
      // Cần mở rộng chiều cao
      const newHeight = currentWidth / targetRatio;
      const totalExpand = newHeight - currentHeight;
      setExpandValues({
        top: Math.floor(totalExpand / 2),
        bottom: Math.ceil(totalExpand / 2),
        left: 0,
        right: 0,
      });
    }
  };

  const finalWidth =
    imageDimensions.width + expandValues.left + expandValues.right;
  const finalHeight =
    imageDimensions.height + expandValues.top + expandValues.bottom;

  return (
    <div className="max-w-6xl mx-auto p-6">
      {contextHolder}

      {/* Gradient Header Section */}
      <div className="rounded-2xl mb-12 p-10 text-white shadow-card" style={{
        boxShadow: '0 8px 24px rgba(233, 213, 202, 0.35)',
        background: 'linear-gradient(135deg, #e9d5ca 0%, #d4b5a7 100%)'
      }}>
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm mb-4">
            <ExpandIcon size={32} className="text-white" />
          </div>
          <Title style={{ color: "white" }} level={1} className="mb-6">
            Image Expansion
          </Title>
          <Paragraph className="text-lg mt-4 mb-8 max-w-3xl mx-auto text-white/90">
            Expand your images beyond their original boundaries with AI-powered
            content generation. Perfect for creating wider landscapes, extending
            backgrounds, or adjusting aspect ratios.
          </Paragraph>
        </div>
      </div>

      {/* Input Image Section */}
      <Row gutter={[24, 24]} className="mb-8">
        <Col xs={24} lg={12}>
          <Card className="shadow-card border-gray-100 h-full">
            <Title level={4} className="mb-4">
              Input Image
            </Title>

            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <Title level={5} className="mb-4 gradient-text">
                Upload Guidelines
              </Title>
              <ul className="space-y-3 text-gray-600">
                <li className="flex items-start">
                  <div
                    className="mr-3 p-1 rounded-full"
                    style={{ backgroundColor: "#d4b5a715" }}
                  >
                    <ImageIcon
                      className="w-4 h-4"
                      style={{ color: "#d4b5a7" }}
                    />
                  </div>
                  <span>
                    Upload clear, high-quality images for best results
                  </span>
                </li>
                <li className="flex items-start">
                  <div
                    className="mr-3 p-1 rounded-full"
                    style={{ backgroundColor: "#d4b5a715" }}
                  >
                    <ExpandIcon
                      className="w-4 h-4"
                      style={{ color: "#d4b5a7" }}
                    />
                  </div>
                  <span>The image will be expanded based on your settings</span>
                </li>
                <li className="flex items-start">
                  <div
                    className="mr-3 p-1 rounded-full"
                    style={{ backgroundColor: "#7c5aff15" }}
                  >
                    <Wand2 className="w-4 h-4" style={{ color: "#7c5aff" }} />
                  </div>
                  <span>AI will generate content to fill expanded areas</span>
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

            <div className="mt-6 p-4 bg-white/50 rounded-lg border border-gray-100">
              <Title level={5} className="mb-3">
                Upload Image
              </Title>
              <div className="mb-6">
                <Form.Item>
                  <Upload
                    fileList={imageFileList}
                    onChange={({ fileList }) => setImageFileList(fileList)}
                    onPreview={handlePreviewCallback(
                      setPreviewImage,
                      setPreviewOpen
                    )}
                    beforeUpload={handleUpload}
                    maxCount={1}
                    accept="image/*"
                    listType="picture-card"
                  >
                    {imageFileList.length >= 1 ? null : <UploadButton />}
                  </Upload>
                </Form.Item>
              </div>
            </div>
          </Card>
        </Col>

        {/* Generation Settings Section */}
        <Col xs={24} lg={12}>
          <Card className="shadow-card border-gray-100 h-full">
            <Form
              form={form}
              onFinish={handleGenerate}
              layout="vertical"
              initialValues={initialValues}
            >
              <Title level={4} className="mb-4">
                Generation Settings
              </Title>

              <Form.Item
                name="model"
                label="Model"
                rules={[{ required: true, message: "Please select a model!" }]}
              >
                <Select options={EXPAND_OPTIONS} />
              </Form.Item>

              <div className="bg-white rounded-lg p-6 mb-6 border border-gray-200">
                <Form.Item
                  name="prompt"
                  label="Prompt"
                  rules={[
                    { required: true, message: "Please enter a prompt!" },
                  ]}
                >
                  <Input.TextArea rows={4} placeholder="Enter your prompt..." />
                </Form.Item>

                <Form.Item name="negative_prompt" label="Negative Prompt">
                  <Input.TextArea
                    rows={4}
                    placeholder="Enter negative prompt (optional)"
                  />
                </Form.Item>
              </div>

              <Row gutter={[16, 16]}>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="num_inference_steps"
                    label="Inference Steps"
                    rules={[
                      {
                        required: true,
                        message: "Please enter inference steps!",
                      },
                      {
                        type: "number",
                        min: 1,
                        max: 100,
                        message: "Value must be between 1 and 100",
                      },
                    ]}
                  >
                    <InputNumber min={1} max={100} style={{ width: "100%" }} />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="guidance_scale"
                    label="Guidance Scale"
                    rules={[
                      {
                        required: true,
                        message: "Please enter guidance scale!",
                      },
                      {
                        type: "number",
                        min: 1,
                        max: 20,
                        message: "Value must be between 1 and 20",
                      },
                    ]}
                  >
                    <InputNumber
                      min={1}
                      max={20}
                      step={0.1}
                      style={{ width: "100%" }}
                    />
                  </Form.Item>
                </Col>
              </Row>
            </Form>
          </Card>
        </Col>
      </Row>

      {/* Expansion Settings Section */}
      {imageFileList.length > 0 && (
        <Card className="shadow-card border-gray-100 mb-8">
          <Title level={4} className="mb-6">
            Expansion Settings
          </Title>

          <Row gutter={[24, 24]}>
            <Col xs={24} lg={14}>
              <div className="flex flex-col h-full space-y-6">
                {/* Dimensions Input Area */}
                <div className="bg-white rounded-lg p-6 border border-gray-200">
                  <Row gutter={[16, 16]}>
                    <Col xs={12} sm={6}>
                      <div className="text-center">
                        <div className="font-medium mb-2">Top (px)</div>
                        <InputNumber
                          min={0}
                          value={expandValues.top}
                          onChange={(value) => handleExpandChange(value, "top")}
                          style={{ width: "100%" }}
                        />
                      </div>
                    </Col>
                    <Col xs={12} sm={6}>
                      <div className="text-center">
                        <div className="font-medium mb-2">Bottom (px)</div>
                        <InputNumber
                          min={0}
                          value={expandValues.bottom}
                          onChange={(value) =>
                            handleExpandChange(value, "bottom")
                          }
                          style={{ width: "100%" }}
                        />
                      </div>
                    </Col>
                    <Col xs={12} sm={6}>
                      <div className="text-center">
                        <div className="font-medium mb-2">Left (px)</div>
                        <InputNumber
                          min={0}
                          value={expandValues.left}
                          onChange={(value) =>
                            handleExpandChange(value, "left")
                          }
                          style={{ width: "100%" }}
                        />
                      </div>
                    </Col>
                    <Col xs={12} sm={6}>
                      <div className="text-center">
                        <div className="font-medium mb-2">Right (px)</div>
                        <InputNumber
                          min={0}
                          value={expandValues.right}
                          onChange={(value) =>
                            handleExpandChange(value, "right")
                          }
                          style={{ width: "100%" }}
                        />
                      </div>
                    </Col>
                  </Row>

                  <div className="mt-6">
                    <div className="text-center mb-2 font-medium">
                      Final Dimensions
                    </div>
                    <div className="text-center text-gray-600">
                      {imageDimensions.width} x {imageDimensions.height} px →{" "}
                      {finalWidth} x {finalHeight} px
                    </div>
                  </div>
                </div>

                {/* Quick Aspect Ratios Area */}
                <div className="bg-white rounded-lg p-6 border border-gray-100">
                  <Title level={5} className="mb-4">
                    Quick Aspect Ratios
                  </Title>
                  <div className="grid grid-cols-3 gap-2">
                    <Button
                      htmlType="button"
                      size="small"
                      onClick={() => handleAspectRatio(1)}
                    >
                      1:1
                    </Button>
                    <Button
                      htmlType="button"
                      size="small"
                      onClick={() => handleAspectRatio(2 / 3)}
                    >
                      2:3
                    </Button>
                    <Button
                      htmlType="button"
                      size="small"
                      onClick={() => handleAspectRatio(3 / 2)}
                    >
                      3:2
                    </Button>
                    <Button
                      htmlType="button"
                      size="small"
                      onClick={() => handleAspectRatio(4 / 3)}
                    >
                      4:3
                    </Button>
                    <Button
                      htmlType="button"
                      size="small"
                      onClick={() => handleAspectRatio(3 / 4)}
                    >
                      3:4
                    </Button>
                    <Button
                      htmlType="button"
                      size="small"
                      onClick={() => handleAspectRatio(5 / 4)}
                    >
                      5:4
                    </Button>
                    <Button
                      htmlType="button"
                      size="small"
                      onClick={() => handleAspectRatio(4 / 5)}
                    >
                      4:5
                    </Button>
                    <Button
                      htmlType="button"
                      size="small"
                      onClick={() => handleAspectRatio(16 / 9)}
                    >
                      16:9
                    </Button>
                    <Button
                      htmlType="button"
                      size="small"
                      onClick={() => handleAspectRatio(9 / 16)}
                    >
                      9:16
                    </Button>
                  </div>
                </div>
              </div>
            </Col>

            {/* Preview Area - Column 2 */}
            <Col xs={24} lg={10}>
              <div className="bg-white rounded-lg p-6 border border-gray-100 h-[400px] flex flex-col">
                <Title level={5} className="mb-4">
                  Preview
                </Title>
                <div className="flex-grow flex items-center justify-center overflow-auto">
                  <div
                    className="relative"
                    style={{
                      height: "300px",
                      width: `${(finalWidth / finalHeight) * 300}px`,
                      minWidth: "200px",
                      background: "#f0f0f0",
                    }}
                  >
                    <div
                      style={{
                        position: "absolute",
                        top: `${(expandValues.top / finalHeight) * 100}%`,
                        left: `${(expandValues.left / finalWidth) * 100}%`,
                        width: `${(imageDimensions.width / finalWidth) * 100}%`,
                        height: `${
                          (imageDimensions.height / finalHeight) * 100
                        }%`,
                        border: "2px solid #1890ff",
                        background: "rgba(24, 144, 255, 0.1)",
                      }}
                    />
                    <div
                      style={{
                        position: "absolute",
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: "rgba(82, 196, 26, 0.1)",
                        border: "2px dashed #52c41a",
                      }}
                    />
                  </div>
                </div>
              </div>
            </Col>
          </Row>

          <div className="mt-8">
            <Button
              type="primary"
              htmlType="submit"
              icon={<FormOutlined />}
              loading={loading}
              disabled={imageFileList.length === 0}
              className="w-full"
              style={{
                background: "linear-gradient(to right, #7c5aff, #5cb8e6)",
                border: "none",
                height: "40px",
              }}
              onClick={() => form.submit()}
            >
              Generate
            </Button>
          </div>
        </Card>
      )}

      <AntImage
        style={{ display: "none" }}
        preview={{
          visible: previewOpen,
          onVisibleChange: (visible) => setPreviewOpen(visible),
          afterOpenChange: (visible) => !visible && setPreviewImage(""),
        }}
        src={previewImage}
      />

      {/* Results Section */}
      {processedImages && !loading && (
        <div
          ref={resultsRef}
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
                <DisplayImage
                  imageUrl={processedImages.original}
                  imageWidth="auto"
                  imageStyle={{ maxWidth: "100%", display: "block" }}
                />
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
      )}
    </div>
  );
};

export default Expand;
