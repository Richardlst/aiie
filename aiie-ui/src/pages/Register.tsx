import { Form, Input, Button, Card, message } from "antd";
import { LockOutlined, MailOutlined } from "@ant-design/icons";
import { Link, useNavigate } from "react-router-dom";
import { registerApi } from "../services/apis";
import { useState } from "react";
import Loading from "../components/Loading";

interface RegisterForm {
  email: string;
  password: string;
  confirmPassword: string;
}

export default function Register() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [messageApi, messageContextHolder] = message.useMessage();

  const onFinish = async (values: RegisterForm) => {
    setLoading(true);
    try {
      const response = await registerApi(values.email, values.password);

      if (response.status === 200) {
        messageApi.success("Registration successful! Please sign in.");
        setTimeout(() => {
          navigate("/auth/login");
        }, 1500);
      } else {
        messageApi.error("Registration failed. Please try again.");
      }
    } catch (error: any) {
      messageApi.error(error.response?.data?.detail || "Registration failed");
      console.error("Register failed:", error);
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
            Create your account
          </h2>
        </div>

        {loading ? (
          <Loading message="Creating your account..." />
        ) : (
          <Form
            form={form}
            name="signup"
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

            <Form.Item
              name="password"
              rules={[
                { required: true, message: "Please input your password!" },
                { min: 6, message: "Password must be at least 6 characters!" },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Password"
                size="large"
              />
            </Form.Item>

            <Form.Item
              name="confirmPassword"
              dependencies={["password"]}
              rules={[
                { required: true, message: "Please confirm your password!" },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue("password") === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error("Passwords do not match!"));
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Confirm Password"
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
                Sign up
              </Button>
            </Form.Item>

            <div className="text-center">
              <span className="text-gray-600">Already have an account? </span>
              <Link
                to="/auth/login"
                className="text-purple-600 hover:text-purple-500"
              >
                Sign in
              </Link>
            </div>
          </Form>
        )}
      </Card>
    </div>
  );
}
