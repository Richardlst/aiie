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
  Tabs,
  Typography,
} from "antd";
import { FormOutlined } from "@ant-design/icons";
import type { UploadFile, RcFile } from "antd/es/upload/interface";
import { inpaintApi, saveImage } from "../services/apis";
import Canvas from "../components/Canvas";
import { type ReactSketchCanvasRef } from "react-sketch-canvas";
import { getBase64, handlePreviewCallback } from "../utils";
import UploadButton from "../components/UploadButton";
import { flushSync } from "react-dom";
import DisplayImage from "../components/DisplayImage";
import { InpaintRequest } from "../types/image";

const { Title, Paragraph } = Typography;

const initialValues: Omit<InpaintRequest, "image_url" | "mask_url" | "reference_image_url"> = {
  negative_prompt:
    "blurry, low quality, artifacts, seam, distorted, noise, grain, overexposed, underexposed, watermark, text, logo, signature, branding, copyright, watermark overlay, text overlay, branded content, emblem, symbol, badge, visible repairs, patchy, uneven, letters, numbers, rendered text, corrupted text, garbled text, random letters, legible text, gibberish, written text, handwriting, gray blocks, dark patches, pixelated, unnatural colors, blocked areas, dark spots, black marks, stains, specks, spots, blemishes",
  num_inference_steps: 30,
  guidance_scale: 7.5,
  strength: 0.8,
  ip_adapter_scale: 0.0,
  prompt: "restore damaged area, seamless repair, matching texture and tone, high quality, detailed, natural seamless restoration, smooth blending",
};

const Inpaint = () => {
  const [loading, setLoading] = useState(false);
  const [maskMode, setMaskMode] = useState<"upload" | "draw">("draw");
  const [backgroundImage, setBackgroundImage] = useState<string | undefined>(
    undefined
  );
  const [refImageFileList, setRefImageFileList] = useState<UploadFile[]>([]);
  const [imageFileList, setImageFileList] = useState<UploadFile[]>([]);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewImage, setPreviewImage] = useState<string | undefined>(
    undefined
  );
  const [maskFileList, setMaskFileList] = useState<UploadFile[]>([]);
  const [processedImages, setProcessedImages] = useState<{
    original: string;
    processed: string;
    mask: string;
  } | null>(null);
  const [imageSize, setImageSize] = useState<{ width: number; height: number }>(
    { width: 0, height: 0 }
  );
  const aspectRatio = imageSize.width / imageSize.height || 1;

  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage();
  const resultsRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<ReactSketchCanvasRef>(null!);

  const handleUpload = async (file: File) => {
    const base64 = await getBase64(file);

    const img = new (window.Image as any)();
    img.onload = () => {
      setBackgroundImage(base64);
      setImageSize({ width: img.width, height: img.height });
    };
    img.src = base64;

    const isLt10M = file.size / 1024 / 1024 < 10;
    if (!isLt10M) {
      messageApi.error("File size must be smaller than 10MB!");
      return Upload.LIST_IGNORE;
    }

    return false;
  };

  const handleRemove = () => {
    setBackgroundImage("");
    canvasRef.current?.resetCanvas();
  };

  const getDrawingMaskFile = async () => {
    const currentBackground = backgroundImage;
    try {
      flushSync(() => {
        setBackgroundImage("");
      });

      const imageDataUrl = await canvasRef.current?.exportImage("png");

      if (!imageDataUrl) {
        throw new Error("Failed to generate mask image");
      }
      const response = await fetch(imageDataUrl);
      const blob = await response.blob();

      const tempCanvas = document.createElement("canvas");
      tempCanvas.width = imageSize.width;
      tempCanvas.height = imageSize.height;
      const tempCtx = tempCanvas.getContext("2d");

      const imageBitmap = await createImageBitmap(blob);
      tempCtx?.drawImage(imageBitmap, 0, 0, imageSize.width, imageSize.height);

      const resizedBlob = await new Promise<Blob>((resolve) => {
        tempCanvas.toBlob((blob) => resolve(blob!), "image/png");
      });

      const maskFile = new File([resizedBlob], "mask.png", {
        type: "image/png",
      }) as RcFile;
      Object.defineProperty(maskFile, "uid", { value: "-1", writable: false });

      return {
        uid: "-1",
        name: "mask.png",
        type: "image/png",
        originFileObj: maskFile,
      };
    } catch (error) {
      console.error("Error processing mask image:", error);
      throw error;
    } finally {
      setBackgroundImage(currentBackground);
    }
  };

  const handleGenerate = async (
    values: Omit<InpaintRequest, "image_url" | "mask_url">
  ) => {
    if (imageFileList.length === 0) {
      messageApi.error("Please upload an input image");
      return;
    }

    if (maskMode === "upload" && maskFileList.length === 0) {
      messageApi.error("Please upload a mask image");
      return;
    }

    setLoading(true);
    try {
      const imageUrl = (await saveImage(imageFileList[0])).data.url;

      const maskFile =
        maskMode === "upload" ? maskFileList[0] : await getDrawingMaskFile();
      const maskUrl = (await saveImage(maskFile)).data.url;

      if (!maskUrl) {
        messageApi.error("Failed to generate mask image");
        return;
      }

      let refImageUrl: string | undefined;
      if (refImageFileList.length > 0) {
        refImageUrl = (await saveImage(refImageFileList[0])).data.url;
      }

      const requestData: InpaintRequest = {
        ...values,
        image_url: imageUrl,
        mask_url: maskUrl,
        ...(refImageUrl ? { reference_image_url: refImageUrl } : {}),
      };

      const response = await inpaintApi(requestData);

      setProcessedImages({
        original: imageUrl,
        processed: response.image_url,
        mask: maskUrl,
      });

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

      {/* Header Section */}
      <div className="rounded-2xl mb-12 p-10 bg-gradient-to-r from-[#a8edea] to-[#fed6e3] text-white shadow-card" style={{
        boxShadow: '0 8px 24px rgba(168, 237, 234, 0.35)'
      }}>
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm mb-4">
            <FormOutlined style={{ fontSize: 32 }} className="text-white" />
          </div>
          <Title style={{ color: "white" }} level={1} className="mb-6">
            AI Image Inpainting
          </Title>
          <Paragraph className="text-lg mt-4 mb-8 max-w-3xl mx-auto text-white/90">
            Our advanced AI inpainting tool allows you to seamlessly remove
            unwanted objects, replace elements, or restore damaged areas in your
            images. Simply upload an image, create or upload a mask, and let our
            AI do the magic.
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
                    style={{ backgroundColor: "#7c5aff15" }}
                  >
                    <FormOutlined
                      className="w-4 h-4"
                      style={{ color: "#7c5aff" }}
                    />
                  </div>
                  <span>Upload your source image for inpainting</span>
                </li>
                <li className="flex items-start">
                  <div
                    className="mr-3 p-1 rounded-full"
                    style={{ backgroundColor: "#5cb8e615" }}
                  >
                    <FormOutlined
                      className="w-4 h-4"
                      style={{ color: "#5cb8e6" }}
                    />
                  </div>
                  <span>
                    Create or upload a mask to specify the area to inpaint
                  </span>
                </li>
                <li className="flex items-start">
                  <div
                    className="mr-3 p-1 rounded-full"
                    style={{ backgroundColor: "#7c5aff15" }}
                  >
                    <FormOutlined
                      className="w-4 h-4"
                      style={{ color: "#7c5aff" }}
                    />
                  </div>
                  <span>
                    AI will seamlessly fill the masked area based on your prompt
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
                  <FormOutlined className="w-5 h-5 text-[#7c5aff]" />
                </div>
                <span className="text-lg font-medium">Upload Image</span>
              </div>
            }
          >
            <div className="flex flex-col items-center justify-center p-4">
              <Upload
                fileList={imageFileList}
                onChange={({ fileList }) => setImageFileList(fileList)}
                onPreview={handlePreviewCallback(
                  setPreviewImage,
                  setPreviewOpen
                )}
                beforeUpload={handleUpload}
                onRemove={handleRemove}
                maxCount={1}
                accept="image/*"
                listType="picture-circle"
              >
                {imageFileList.length >= 1 ? null : <UploadButton />}
              </Upload>

              <div className="w-full mt-6 space-y-3">
                <div className="flex items-center p-3 bg-white rounded-lg border border-gray-200">
                  <div className="p-2 bg-purple-100 rounded-full mr-3">
                    <FormOutlined className="text-[#7c5aff]" />
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
                    <FormOutlined className="text-[#5cb8e6]" />
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-800">
                      Automatic Processing
                    </p>
                    <p className="text-gray-600">
                      Our AI will inpaint your image automatically
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
            <Col xs={24} md={12}>
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
                  className="rounded-lg"
                />
              </Form.Item>

              <Form.Item name="negative_prompt" label="Negative Prompt">
                <Input.TextArea
                  rows={3}
                  placeholder="Enter negative prompt (optional)"
                  className="rounded-lg"
                />
              </Form.Item>

              <Row gutter={[16, 16]}>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="ip_adapter_scale"
                    label="IP-Adapter Scale"
                    tooltip="Higher = more like reference image. 0.6 is balanced."
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
                </Col>
                <Col xs={24} sm={12}>
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
                </Col>
                <Col xs={24} sm={12}>
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
                </Col>
                <Col xs={24} sm={12}>
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
                </Col>
              </Row>
            </Col>

            <Col xs={24} md={12}>
              <Card
                className="shadow-md border-gray-100"
                title={
                  <div className="flex items-center gap-3">
                    <div
                      className="p-2 rounded-lg"
                      style={{ backgroundColor: "#7c5aff15" }}
                    >
                      <FormOutlined className="w-5 h-5 text-[#7c5aff]" />
                    </div>
                    <span className="text-lg font-medium">Mask Selection</span>
                  </div>
                }
              >
                <Tabs
                  activeKey={maskMode}
                  onChange={(key) => setMaskMode(key as "upload" | "draw")}
                  items={[
                    {
                      key: "draw",
                      label: "Draw Mask",
                      children: (
                        <div className="mt-4">
                          <Canvas
                            canvasRef={canvasRef}
                            backgroundImage={backgroundImage}
                            setBackgroundImage={setBackgroundImage}
                            aspectRatio={aspectRatio}
                            imageWidth={imageSize.width}
                            imageHeight={imageSize.height}
                          />
                        </div>
                      ),
                    },
                    {
                      key: "upload",
                      label: "Upload Mask",
                      children: (
                        <Form.Item label="Upload mask image" className="mt-4">
                          <Upload
                            fileList={maskFileList}
                            onChange={({ fileList }) =>
                              setMaskFileList(fileList)
                            }
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
                            {maskFileList.length >= 1 ? null : <UploadButton />}
                          </Upload>
                        </Form.Item>
                      ),
                    },
                  ]}
                />
              </Card>
            </Col>
          </Row>
        </Card>

        {/* Reference Image (optional) */}
        <Card
          className="shadow-md border-gray-100 mb-8"
          title={
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg" style={{ backgroundColor: "#7c5aff15" }}>
                <FormOutlined className="w-5 h-5 text-[#7c5aff]" />
              </div>
              <span className="text-lg font-medium">Reference Image</span>
              <span className="text-sm font-normal text-gray-400">(optional — IP-Adapter will copy its style/colours)</span>
            </div>
          }
        >
          <div className="flex flex-col items-center justify-center p-4">
            <Upload
              fileList={refImageFileList}
              onChange={({ fileList }) => setRefImageFileList(fileList)}
              onPreview={handlePreviewCallback(setPreviewImage, setPreviewOpen)}
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
              {refImageFileList.length >= 1 ? null : <UploadButton />}
            </Upload>
            <p className="mt-3 text-sm text-gray-500 text-center">
              If left empty, the source image is used as self-reference to preserve identity.
            </p>
          </div>
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
                disabled={imageFileList.length === 0}
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
            Generated Results
          </Title>
          <Row gutter={[24, 24]}>
            <Col xs={24} md={8}>
              <Card
                className="shadow-card border-gray-100"
                title="Original Image"
              >
                <DisplayImage imageUrl={processedImages.original} />
              </Card>
            </Col>
            <Col xs={24} md={8}>
              <Card className="shadow-card border-gray-100" title="Mask Image">
                <DisplayImage imageUrl={processedImages.mask} />
              </Card>
            </Col>
            <Col xs={24} md={8}>
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
    </div>
  );
};

export default Inpaint;
