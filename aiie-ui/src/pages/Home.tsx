import { Typography, Card, Row, Col, Button } from "antd";
import { useNavigate } from "react-router-dom";
import {
  Image as ImageIcon,
  Wand2,
  ImagePlus,
  Pen,
  SquareBottomDashedScissors,
  Expand,
  ArrowRight,
  Palette,
  UserCircle2,
} from "lucide-react";
import React from "react";

const { Title, Paragraph } = Typography;

interface FeatureCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  path: string;
  iconColor?: string;
}

const FeatureCard = ({
  title,
  description,
  icon,
  path,
  iconColor = "#7c5aff",
}: FeatureCardProps) => {
  const navigate = useNavigate();

  return (
    <Card
      hoverable
      className="h-full flex flex-col card-hover-effect"
      style={{
        backgroundColor: "white",
        border: "2px solid #e5e7eb",
        borderRadius: "16px",
        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08)",
      }}
      
      actions={[
        <Button
          type="primary"
          onClick={() => navigate(path)}
          className="flex items-center justify-center gap-2 mx-auto btn-gradient"
          style={{
            background: `linear-gradient(135deg, ${iconColor}, ${iconColor}DD)`,
            border: "none",
            color: "white",
            borderRadius: "10px",
            padding: "8px 24px",
            height: "auto"
          }}
        >
          Try Now <ArrowRight className="w-4 h-4" />
        </Button>,
      ]}
    >
      <div className="flex items-center mb-4">
        <div
          className={`flex-shrink-0 mr-3 p-3 rounded-xl`}
          style={{ 
            background: `linear-gradient(135deg, ${iconColor}25, ${iconColor}10)`,
            boxShadow: `0px 4px 12px ${iconColor}30`
          }}
        >
          {React.cloneElement(icon as React.ReactElement, {
            className: `w-6 h-6`,
            style: { color: iconColor },
          })}
        </div>
        <Title level={4} style={{ margin: 0, color: "#1a1a1a" }}>
          {title}
        </Title>
      </div>
      <Paragraph className="flex-grow text-gray-600">{description}</Paragraph>
    </Card>
  );
};

const Home = () => {
  const features = [
    {
      title: "Super Resolution",
      description:
        "Enhance low-resolution images to reveal details and improve quality.",
      icon: <ImageIcon />,
      path: "/super-resolution",
      iconColor: "#667eea",
    },
    {
      title: "Text to Image",
      description: "Generate unique images from text descriptions using AI.",
      icon: <Wand2 />,
      path: "/text-to-image",
      iconColor: "#f093fb",
    },
    {
      title: "Image to Image",
      description: "Transform existing images into new styles or variations.",
      icon: <ImagePlus />,
      path: "/image-to-image",
      iconColor: "#4facfe",
    },
    {
      title: "Inpaint",
      description:
        "Replace or restore specific parts of an image intelligently.",
      icon: <Pen />,
      path: "/inpaint",
      iconColor: "#fa709a",
    },
    {
      title: "Segment",
      description:
        "Identify and extract specific objects or regions from images.",
      icon: <SquareBottomDashedScissors />,
      path: "/segment",
      iconColor: "#a8edea",
    },
    {
      title: "Expand",
      description:
        "Intelligently extend image boundaries beyond the original frame.",
      icon: <Expand />,
      path: "/expand",
      iconColor: "#00f2fe",
    },
    {
      title: "Colorization",
      description:
        "Transform black and white photos into vibrant colored images.",
      icon: <Palette />,
      path: "/colorization",
      iconColor: "#fa709a",
    },
    {
      title: "Face Refine",
      description:
        "Enhance facial features with AI-powered refinement and restoration.",
      icon: <UserCircle2 />,
      path: "/face-refine",
      iconColor: "#667eea",
    },
  ];

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Gradient Header Section */}
      <div className="rounded-2xl mb-12 p-10 text-white shadow-card" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <div className="text-center mb-8">
          <div className="flex justify-center items-center mb-2">
            <span className="font-bold text-4xl mr-2">An AI Tool to Restore and Enhance Images</span>
            <span className="text-xl text-white/80">
            </span>
          </div>
          <Title
            style={{
              color: "white",
            }}
            level={1}
            className="mb-6"
          >
            Transform Your Visual Content
          </Title>
          <Paragraph className="text-lg mt-4 mb-8 max-w-3xl mx-auto text-white/90">
            Our suite of AI-powered tools lets you enhance, generate, and modify
            images with state-of-the-art technology. Whether you're a designer,
            developer, or content creator, AIIE provides powerful solutions.
          </Paragraph>
        </div>
      </div>

      {/* Features Section */}
      <div className="mb-16">
        <Title level={2} className="text-center mb-2 gradient-text">
          Our AI Tools
        </Title>
        <Paragraph className="text-center text-gray-600 mb-8 text-lg">
          Powerful image processing tools to transform your creative projects
        </Paragraph>
        <Row gutter={[24, 24]} className="mb-12">
          {features.map((feature, index) => (
            <Col xs={24} sm={12} lg={8} key={index}>
              <FeatureCard
                title={feature.title}
                description={feature.description}
                icon={feature.icon}
                path={feature.path}
                iconColor={feature.iconColor}
              />
            </Col>
          ))}
        </Row>
      </div>

      {/* Chatbot Section */}
      <div
        className="mb-16 p-8 rounded-2xl shadow-card"
        style={{
          background: "white",
          border: "1px solid #e8e8e8",
        }}
      >
        <Row gutter={24} align="middle">
          <Col xs={24} md={12} className="mb-6 md:mb-0">
            <Title level={2} className="gradient-text mb-4">
              AI Chatbot Assistant
            </Title>
            <Paragraph className="text-gray-700 text-lg mb-6">
              Our intelligent chatbot helps you perform image operations with
              simple natural language commands. No need to navigate through
              different tools - just tell our assistant what you want to do.
            </Paragraph>
            <ul className="space-y-3 mb-6">
              <li className="flex items-start">
                <div
                  className="mr-3 p-1 rounded-full"
                  style={{ backgroundColor: "#7c5aff15" }}
                >
                  <Wand2 className="w-4 h-4" style={{ color: "#7c5aff" }} />
                </div>
                <span>
                  Request image generations with detailed descriptions
                </span>
              </li>
              <li className="flex items-start">
                <div
                  className="mr-3 p-1 rounded-full"
                  style={{ backgroundColor: "#5cb8e615" }}
                >
                  <ImageIcon className="w-4 h-4" style={{ color: "#5cb8e6" }} />
                </div>
                <span>
                  Ask for specific image enhancements or modifications
                </span>
              </li>
              <li className="flex items-start">
                <div
                  className="mr-3 p-1 rounded-full"
                  style={{ backgroundColor: "#7c5aff15" }}
                >
                  <Pen className="w-4 h-4" style={{ color: "#7c5aff" }} />
                </div>
                <span>
                  Get guidance on which tools to use for your specific needs
                </span>
              </li>
            </ul>
          </Col>
          <Col xs={24} md={12}>
            <div className="bg-white p-4 rounded-xl shadow-md">
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                {/* User Message */}
                <div className="flex items-start mb-4 justify-end">
                  <div className="bg-gray-100 rounded-lg p-3 max-w-[80%]">
                    <p className="text-gray-700">
                      Can you generate an image of a mountain landscape with a
                      sunset?
                    </p>
                  </div>
                  <div className="bg-blue-100 rounded-full p-2 ml-3">
                    <svg
                      className="w-5 h-5 text-blue-500"
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 19V21"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                      <path
                        d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </div>
                </div>

                {/* AI Message */}
                <div className="flex items-start mb-4">
                  <div className="rounded-full p-2 mr-3" style={{ background: '#7c5aff15' }}>
                    <Wand2 className="w-5 h-5" style={{ color: '#7c5aff' }} />
                  </div>
                  <div className="rounded-lg p-3 max-w-[80%]" style={{ background: 'linear-gradient(to right, rgba(124, 90, 255, 0.1), rgba(92, 184, 230, 0.1))' }}>
                    <p className="text-gray-700">
                      I'll create a mountain landscape with sunset for you.
                      Would you like to add any specific elements like trees,
                      lakes, or wildlife?
                    </p>
                  </div>
                </div>

                {/* Second User Message */}
                <div className="flex items-start mb-4 justify-end">
                  <div className="bg-gray-100 rounded-lg p-3 max-w-[80%]">
                    <p className="text-gray-700">
                      Yes, add a small lake and some pine trees please.
                    </p>
                  </div>
                  <div className="bg-blue-100 rounded-full p-2 ml-3">
                    <svg
                      className="w-5 h-5 text-blue-500"
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 19V21"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                      <path
                        d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </div>
                </div>

                {/* Typing Indicator */}
                <div className="flex items-start">
                  <div className="rounded-full p-2 mr-3" style={{ background: '#7c5aff15' }}>
                    <Wand2 className="w-5 h-5" style={{ color: '#7c5aff' }} />
                  </div>
                  <div className="flex justify-center items-center h-8">
                    <div className="h-1.5 w-1.5 bg-gray-400 rounded-full mr-1 animate-bounce"></div>
                    <div
                      className="h-1.5 w-1.5 bg-gray-400 rounded-full mr-1 animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                    <div
                      className="h-1.5 w-1.5 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.4s" }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </Col>
        </Row>
      </div>

      {/* About Section with improved design */}
      <Card className="mb-12 shadow-card border-gray-100">
        <Title level={2} className="mb-6 text-center gradient-text">
          About AIIE
        </Title>
        <Row gutter={16}>
          <Col xs={24} md={16}>
            <div className="p-6 bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg mb-4 md:mb-0">
              <Paragraph className="text-base">
                AIIE (Artificial Intelligence Image Editor) is a comprehensive
                platform that leverages the latest advancements in artificial
                intelligence to provide powerful image manipulation and
                generation capabilities.
              </Paragraph>
              <Paragraph className="text-base">
                Our tools are built on state-of-the-art machine learning models,
                including diffusion models like Stable Diffusion, to deliver
                high-quality results for a wide range of image processing needs.
              </Paragraph>
              <Paragraph className="text-base">
                Whether you're a designer, content creator, or developer, AIIE
                gives you the power to transform your visual content with ease
                and precision. Explore our suite of tools and discover new
                possibilities for your creative projects.
              </Paragraph>
            </div>
          </Col>
          <Col xs={24} md={8}>
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg h-full">
              <Title level={4} className="gradient-text">
                Getting Started
              </Title>
              <ol className="list-decimal pl-4 space-y-2 text-gray-700">
                <li>Choose a tool from the sidebar</li>
                <li>Upload or input your content</li>
                <li>Adjust parameters as needed</li>
                <li>Generate your results</li>
                <li>Download and use your enhanced images</li>
              </ol>
            </div>
          </Col>
        </Row>
      </Card>

      {/* CTA Section */}
      <div
        className="text-center p-10 rounded-xl shadow-card"
        style={{
          background:
            "linear-gradient(to right, rgba(158, 59, 255, 0.05), rgba(67, 202, 255, 0.05))",
        }}
      >
        <Title level={2} className="mb-6 gradient-text">
          Start Creating Now
        </Title>
        <Paragraph className="text-lg mb-8">
          Ready to transform your images? Choose any of our powerful tools and
          see the magic happen.
        </Paragraph>
        <Row gutter={[16, 16]} justify="center">
          <Col xs={24} sm={12} md={8} lg={6} xl={5}>
            <Button
              type="primary"
              size="large"
              onClick={() => (window.location.href = "/text-to-image")}
              className="min-w-[150px] w-full btn-gradient"
              style={{
                background: "linear-gradient(to right, #7c5aff, #5cb8e6)",
                border: "none",
              }}
            >
              Try Text to Image
            </Button>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6} xl={5}>
            <Button
              size="large"
              onClick={() => (window.location.href = "/super-resolution")}
              className="min-w-[150px] w-full border-gradient-to-r hover:text-[#7c5aff]"
            >
              Enhance Images
            </Button>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default Home;
