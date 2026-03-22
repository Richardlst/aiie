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
    "Enchanted forest at twilight, magical glowing mushrooms, ancient twisted trees with faces, ethereal mist, small fairies with luminescent wings, moonlight filtering through leaves, detailed foliage, fantasy atmosphere, mystical, dreamy, photorealistic, cinematic lighting, 8k resolution, highly detailed, intricate, sharp focus, dramatic lighting, volumetric light, depth of field, concept art",
  negative_prompt:
    "ugly, deformed, disfigured, poor anatomy, bad proportions, extra limbs, missing limbs, poorly drawn face, mutation, mutated, blurry, watermark, text, signature, cut off, low quality, low resolution, bad art, jpeg artifacts, pixelated, out of frame, cropped, draft, amateur, badly drawn, distorted proportions",
  num_inference_steps: 20,
  guidance_scale: 7.5,
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
      const response = await textToImageApi(values);
      const data = response;
      setGeneratedImage(data.image_url);

      // Scroll to results after image is set
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
            Transform your creative ideas into stunning visuals using our
            advanced AI image generation system. Simply describe what you want
            to see, and watch as our AI brings your vision to life.
          </Paragraph>
        </div>
      </div>

      <Form
        form={form}
        onFinish={handleGenerate}
        layout="vertical"
        initialValues={initialValues}
      >
        {/* Main Content Row */}
        <Row gutter={[24, 24]} className="">
          {/* How It Works Column */}
          <Col xs={24} lg={9}>
            <Card className="shadow-card border-gray-100">
              <Title level={4} className="mb-4">
                How It Works
              </Title>

              <div className="space-y-6">
                <ul className="space-y-4">
                  <li className="flex items-start gap-3">
                    <div
                      className="p-2 rounded-lg shrink-0"
                      style={{ backgroundColor: "#7c5aff15" }}
                    >
                      <Wand2 className="w-4 h-4" style={{ color: "#7c5aff" }} />
                    </div>
                    <div>
                      <p className="font-medium text-gray-800">
                        Describe Your Vision
                      </p>
                      <p className="text-gray-600 text-sm">
                        Enter a detailed description of the image you want to
                        create
                      </p>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <div
                      className="p-2 rounded-lg shrink-0"
                      style={{ backgroundColor: "#5cb8e615" }}
                    >
                      <Settings
                        className="w-4 h-4"
                        style={{ color: "#5cb8e6" }}
                      />
                    </div>
                    <div>
                      <p className="font-medium text-gray-800">
                        Adjust Settings
                      </p>
                      <p className="text-gray-600 text-sm">
                        Fine-tune parameters to control the generation process
                      </p>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <div
                      className="p-2 rounded-lg shrink-0"
                      style={{ backgroundColor: "#7c5aff15" }}
                    >
                      <ImageIcon
                        className="w-4 h-4"
                        style={{ color: "#7c5aff" }}
                      />
                    </div>
                    <div>
                      <p className="font-medium text-gray-800">
                        Generate & Review
                      </p>
                      <p className="text-gray-600 text-sm">
                        AI generates your image based on your inputs
                      </p>
                    </div>
                  </li>
                </ul>

                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <p className="font-medium text-gray-800 mb-2">Tips</p>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li className="flex items-center gap-2">
                      <div className="w-1 h-1 rounded-full bg-purple-400"></div>
                      <span>Be specific and detailed in descriptions</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="w-1 h-1 rounded-full bg-blue-400"></div>
                      <span>Use artistic terms for style control</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="w-1 h-1 rounded-full bg-pink-400"></div>
                      <span>Higher steps = better quality</span>
                    </li>
                  </ul>
                </div>
              </div>
            </Card>
          </Col>

          {/* Form Column */}
          <Col xs={24} lg={15}>
            <Card className="shadow-md border-gray-100 mb-8">
              <Row gutter={[24, 24]}>
                <Col xs={24}>
                  <Form.Item
                    name="model"
                    label="Model"
                    rules={[
                      { required: true, message: "Please select a model!" },
                    ]}
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

                  <Form.Item name="negative_prompt" label="Negative Prompt">
                    <Input.TextArea
                      rows={3}
                      placeholder="Enter negative prompt (optional)"
                    />
                  </Form.Item>
                </Col>

                <Col xs={24}>
                  <div className="">
                    <Row gutter={[16, 16]}>
                      <Col xs={24} sm={12}>
                        <Form.Item
                          name="num_inference_steps"
                          label="Inference Steps"
                          rules={[
                            { required: true, message: "Required" },
                            {
                              type: "number",
                              min: 1,
                              max: 100,
                              message: "1-100",
                            },
                          ]}
                        >
                          <InputNumber
                            min={1}
                            max={100}
                            style={{ width: "100%" }}
                          />
                        </Form.Item>
                      </Col>

                      <Col xs={24} sm={12}>
                        <Form.Item
                          name="guidance_scale"
                          label="Guidance Scale"
                          rules={[
                            { required: true, message: "Required" },
                            {
                              type: "number",
                              min: 1,
                              max: 20,
                              message: "1-20",
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

                      <Col xs={24} sm={12}>
                        <Form.Item
                          name="width"
                          label="Width"
                          rules={[
                            { required: true, message: "Required" },
                            {
                              type: "number",
                              min: 128,
                              max: 1024,
                              message: "128-1024",
                            },
                          ]}
                        >
                          <InputNumber
                            min={128}
                            max={1024}
                            step={64}
                            style={{ width: "100%" }}
                          />
                        </Form.Item>
                      </Col>

                      <Col xs={24} sm={12}>
                        <Form.Item
                          name="height"
                          label="Height"
                          rules={[
                            { required: true, message: "Required" },
                            {
                              type: "number",
                              min: 128,
                              max: 1024,
                              message: "128-1024",
                            },
                          ]}
                        >
                          <InputNumber
                            min={128}
                            max={1024}
                            step={64}
                            style={{ width: "100%" }}
                          />
                        </Form.Item>
                      </Col>
                    </Row>
                  </div>
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>

        {/* Process Button */}
        <Card className="shadow-md border-gray-100 mb-8 p-0">
          <div className="flex justify-center">
            <Form.Item className="w-full mb-0">
              <Button
                type="primary"
                htmlType="submit"
                icon={<FormOutlined />}
                loading={loading}
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
      {generatedImage ? (
        <div
          className="p-6 rounded-xl shadow-card animate-fade-in"
          style={{
            background: "white",
          }}
        >
          <Title level={2} className="text-center mb-8 gradient-text">
            Generated Results
          </Title>
          <div className="flex justify-center">
            <Card className="shadow-card border-gray-100 inline-block">
              <Image
                src={generatedImage}
                alt="Generated"
                className="rounded-lg"
                style={{ display: "block", maxWidth: "100%", height: "auto" }}
              />
            </Card>
          </div>
        </div>
      ) : null}

      <div ref={resultsRef} />
    </div>
  );
};

export default TextToImage;
