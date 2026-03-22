import { Form, Input, Button, Card, message } from "antd";
import { MailOutlined } from "@ant-design/icons";
import { Link, useNavigate } from "react-router-dom";
import { forgotPasswordApi } from "../services/apis";
import { useState } from "react";
import Loading from "../components/Loading";

export default function ForgotPassword() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [messageApi, messageContextHolder] = message.useMessage();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: { email: string }) => {
    setLoading(true);
    try {
      const response = await forgotPasswordApi(values.email);

      if (response.status === 200) {
        messageApi.success(
          "Password reset instructions have been sent to your email address."
        );
        // Navigate to login after a short delay
        setTimeout(() => {
          navigate("/auth/login");
        }, 2000);
      }
    } catch (error) {
      console.error("Forgot password request failed:", error);
      messageApi.error("Failed to process your request. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8" style={{ background: 'linear-gradient(135deg, #f5f7fa 0%, #f0f4f9 100%)' }}>
      {messageContextHolder}
      <Card className="w-full max-w-md" style={{ borderRadius: '12px', boxShadow: '0px 8px 16px rgba(0, 0, 0, 0.08)' }}>
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-gray-900">
            Forgot Password
          </h2>
          <p className="mt-2 text-gray-600">
            Enter your email address and we'll send you a link to reset your
            password.
          </p>
        </div>

        {loading ? (
          <Loading message="Sending reset instructions..." />
        ) : (
          <Form
            form={form}
            name="forgotPassword"
            onFinish={onFinish}
            layout="vertical"
            requiredMark={false}
          >
            <Form.Item
              name="email"
              rules={[
                { required: true, message: "Please input your email!" },
                { type: "email", message: "Please enter a valid email!" },
              ]}
            >
              <Input
                prefix={<MailOutlined />}
                placeholder="Email"
                size="large"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                className="w-full"
                size="large"
                loading={loading}
              >
                Send Reset Link
              </Button>
            </Form.Item>

            <div className="text-center">
              <Link
                to="/auth/login"
                className="text-purple-600 hover:text-purple-500"
              >
                Back to Login
              </Link>
            </div>
          </Form>
        )}
      </Card>
    </div>
  );
}
