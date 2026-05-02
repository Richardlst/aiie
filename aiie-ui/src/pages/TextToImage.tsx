import { useState, useRef } from "react";
import {
  Form,
  Input,
  Button,
  Card,
  Row,
  Col,
  InputNumber,
  Image,
  message,
  Select,
  Typography,
} from "antd";
import { FormOutlined } from "@ant-design/icons";
import { ImageIcon, Wand2, Settings } from "lucide-react";
import { textToImageApi } from "../services/apis";
import { MODEL_OPTIONS } from "../constant/modelOptions";
import { Text2ImgRequest } from "../types/image";

const { Title, Paragraph } = Typography;


const initialValues: Text2ImgRequest = {
  model: "runwayml/stable-diffusion-v1-5", 
  prompt:
    "RAW photo, close-up portrait of a gorgeous Vietnamese young woman, wearing elegant white Ao Dai, soft smile, standing in a lush green garden, highly detailed skin, visible skin pores, natural makeup, soft natural lighting, dappled sunlight, shot on Sony A7R IV, 85mm lens, f/1.8, blurred background, bokeh, photorealistic, 8k resolution, masterpiece, extremely detailed",
  negative_prompt:
    "(deformed iris, deformed pupils:1.4), (worst quality, low quality:1.4), CGI, 3D, illustration, cartoon, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, text, watermark, ugly, deformed, blurry, low quality, watermark, text, cartoon, anime, sketch, painting, drawing, bad anatomy",
  num_inference_steps: 6,  // Mặc định 6 bước cho Hyper
  guidance_scale: 1.5,   
  width: 512,
  height: 512,
};

const TextToImage = () => {
  const [loading, setLoading] = useState(false);
  const [generatedImage, setGeneratedImage] = useState<string>("");
  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage();
  const resultsRef = useRef<HTMLDivElement>(null);

  const handleGenerate = async (values: Text2ImgRequest) => {
    setLoading(true);
    try {
      // Gọi API đến Backend
      const response = await textToImageApi(values);
      
      // Cập nhật URL ảnh từ kết quả trả về
      setGeneratedImage(response.image_url);

      // Cuộn xuống phần kết quả sau khi ảnh đã load
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 100);
      
      messageApi.success("Image generated successfully!");
    } catch (error: any) {
      console.error("Error generating image:", error);
      // Hiển thị chi tiết lỗi từ Server nếu có (ví dụ: lỗi Tensor 9 vs 4)
      const errorDetail = error.response?.data?.detail || "Error generating image";
      messageApi.error(errorDetail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {contextHolder}

      {/* Header Section */}
      <div className="rounded-2xl mb-12 p-10 bg-gradient-to-r from-[#a18cd1] to-[#fbc2eb] text-white shadow-card" style={{
        boxShadow: '0 8px 24px rgba(161, 140, 209, 0.35)'
      }}>
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm mb-4">
            <Wand2 size={32} className="text-white" />
          </div>
          <Title style={{ color: "white" }} level={1} className="mb-6">
            Text to Image Generation
          </Title>
          <Paragraph className="text-lg mt-4 mb-8 max-w-3xl mx-auto text-white/90">
            Experience lightning-fast image creation powered by the Hyper model. Just describe your concept, and watch AI turn your vision into reality in seconds.
          </Paragraph>
        </div>
      </div>

      <Form
        form={form}
        onFinish={handleGenerate}
        layout="vertical"
        initialValues={initialValues}
      >
        <Row gutter={[24, 24]}>
          {/* Cột hướng dẫn bên trái */}
         <Col xs={24} lg={9}>
  <Card className="shadow-card border-gray-100 h-full">
    <Title level={4} className="mb-4">Tips & Guidelines</Title>
    
    <div className="space-y-6">
      {/* New: How to Use Section */}
      <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-100">
        <p className="font-medium text-emerald-800 mb-2"> How to Use</p>
        <ul className="space-y-2 text-sm text-emerald-700">
          <li><strong>1. Upload:</strong> Select your grayscale or black-and-white image.</li>
          <li><strong>2. Describe:</strong> Add a prompt to guide the AI's colors (optional).</li>
          <li><strong>3. Generate:</strong> Click the colorize button and wait for the magic!</li>
        </ul>
      </div>

      {/*  Translated: Hyper Mode Section */}
      <div className="bg-purple-50 rounded-lg p-4 border border-purple-100">
        <p className="font-medium text-purple-800 mb-2"> Hyper Mode Active</p>
        <ul className="space-y-2 text-sm text-purple-700">
          <li>• Keep Steps between 6 and 10 for the best results.</li>
          <li>• Guidance Scale should be kept low (1.5 - 2.5).</li>
          <li>• The more detailed the prompt, the sharper the result.</li>
        </ul>
      </div>

      {/*  Translated: Standard Size Section */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-100 text-sm">
        <p className="font-medium text-blue-800 mb-2">Recommended Size</p>
        <p className="text-blue-700">
          The model performs best and remains most stable at 512x512 or 512x768 resolutions.
        </p>
      </div>
      
    </div>
  </Card>
</Col>

          {/* Cột Form điều khiển bên phải */}
          <Col xs={24} lg={15}>
            <Card className="shadow-md border-gray-100 mb-8">
              <Form.Item
                name="model"
                label="Model Selection"
                rules={[{ required: true }]}
              >
                <Select options={MODEL_OPTIONS} placeholder="Chọn mô hình..." />
              </Form.Item>

              <Form.Item
                name="prompt"
                label="Prompt"
                rules={[{ required: true, message: "Vui lòng nhập mô tả!" }]}
              >
                <Input.TextArea
                  rows={4}
                  placeholder="Example: A majestic dragon flying over snow-capped mountains..."
                />
              </Form.Item>

              <Form.Item name="negative_prompt" label="Negative Prompt">
                <Input.TextArea rows={2} placeholder="Example: low quality, blurry, distorted..." />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="num_inference_steps"
                    label="Inference Steps"
                    rules={[{ type: 'number', min: 1, max: 25, message: "1-25 steps" }]}
                  >
                    <InputNumber style={{ width: "100%" }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="guidance_scale"
                    label="Guidance Scale"
                    rules={[{ type: 'number', min: 1, max: 5, message: "1-5" }]}
                  >
                    <InputNumber step={0.1} style={{ width: "100%" }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="width" label="Width">
                    <InputNumber step={64} style={{ width: "100%" }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="height" label="Height">
                    <InputNumber step={64} style={{ width: "100%" }} />
                  </Form.Item>
                </Col>
              </Row>
            </Card>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                icon={<FormOutlined />}
                loading={loading}
                size="large"
                className="w-full h-14 text-lg rounded-xl"
                style={{
                  background: "linear-gradient(to right, #7c5aff, #5cb8e6)",
                  border: "none",
                  boxShadow: "0 4px 12px rgba(124, 90, 255, 0.3)"
                }}
              >
                {loading ? "Generating image..." : "Generate Image"}
              </Button>
            </Form.Item>
          </Col>
        </Row>
      </Form>

      {/* Results Section */}
      <div ref={resultsRef} className="mt-12">
        {generatedImage && (
          <Card 
            className="shadow-card border-none animate-fade-in"
            title={<Title level={3} className="text-center m-0 py-4">Kết quả</Title>}
          >
            <div className="flex justify-center p-4">
              <Image
                src={generatedImage}
                alt="Generated Result"
                className="rounded-lg shadow-lg"
                style={{ maxWidth: "100%", height: "auto" }}
                fallback="https://via.placeholder.com/512?text=Error+Loading+Image"
              />
            </div>
            <div className="text-center mt-6">
              <Button 
                type="default" 
                href={generatedImage} 
                download="generated_image.png"
                target="_blank"
              >
                Tải ảnh về máy
              </Button>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default TextToImage;