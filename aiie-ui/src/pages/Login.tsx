import { Form, Input, Button, Card, message } from "antd";
import { UserOutlined, LockOutlined, GoogleOutlined } from "@ant-design/icons";
import { Link, useNavigate } from "react-router-dom";
import { LoginResponse } from "../types";
import { loginApi, sendVerificationEmailApi } from "../services/apis";
import { useAuth } from "../contexts/AuthContext";
import { useState } from "react";
import Loading from "../components/Loading";

interface LoginForm {
  email: string;
  password: string;
}

const GOOGLE_CLIENT_ID = import.meta.env.VITE_OAUTH_GOOGLE_CLIENT_ID;
const GOOGLE_REDIRECT_URI = import.meta.env.VITE_OAUTH_GOOGLE_REDIRECT_URI;

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [needsVerification, setNeedsVerification] = useState(false);
  const [resendVerificationLoading, setResendVerificationLoading] =
    useState(false);
  const [messageApi, messageContextHolder] = message.useMessage();

  const onFinish = async (values: LoginForm) => {
    setLoading(true);
    const { email, password } = values;

    try {
      const response = await loginApi(email, password);

      if (response.status === 200) {
        const data = response.data as LoginResponse;
        const token = data.access_token;

        messageApi.success("Login successful!");
        console.log("Token received:", token);
        login(token);
        navigate("/");
      } else {
        const errorData = response.data;
        messageApi.error(errorData.detail || "Login failed");
      }
    } catch (error: any) {
      console.error("Login failed:");
      console.error(error);
      if (
        error.response.status == 400 &&
        (error.response?.data?.detail as string).includes("verif")
      ) {
        // Show resend verification option
        setNeedsVerification(true);
        messageApi.error(
          "Email not verified. Please verify your email or resend the verification link."
        );
      } else {
        messageApi.error(error.response?.data?.detail || "Invalid credentials");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResendVerification = async () => {
    setResendVerificationLoading(true);
    try {
      const email = form.getFieldValue("email");
      if (!email) {
        messageApi.error("Please enter your email address");
        setResendVerificationLoading(false);
        return;
      }

      const response = await sendVerificationEmailApi(email);
      if (response.status === 200) {
        messageApi.success(
          "Verification email has been sent. Please check your inbox."
        );
        setNeedsVerification(false);
      } else {
        messageApi.error(
          "Failed to send verification email. Please try again."
        );
      }
    } catch (error: any) {
      console.error("Failed to resend verification email:", error);
      messageApi.error(
        error.response?.data?.detail || "Failed to send verification email"
      );
    } finally {
      setResendVerificationLoading(false);
    }
  };

  const handleGuestLogin = async () => {
    navigate("/");
    messageApi.success("Logged in as guest");
  };

  const handleGoogleLogin = () => {
    setGoogleLoading(true);
    try {
      window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${GOOGLE_CLIENT_ID}&redirect_uri=${GOOGLE_REDIRECT_URI}&response_type=code&scope=openid email profile`;
    } catch (error) {
      console.error("Google login failed:", error);
      messageApi.error("Failed to redirect to Google login");
      setGoogleLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8" style={{ background: 'linear-gradient(135deg, #f5f7fa 0%, #f0f4f9 100%)' }}>
      {messageContextHolder}
      <Card className="w-full max-w-md" style={{ borderRadius: '12px', boxShadow: '0px 8px 16px rgba(0, 0, 0, 0.08)' }}>
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
        </div>

        {loading ? (
          <Loading message="Signing in..." />
        ) : (
          <Form
            form={form}
            name="login"
            onFinish={onFinish}
            layout="vertical"
            requiredMark={false}
          >
            <Form.Item
              name="email"
              rules={[{ required: true, message: "Please input your email!" }]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="Email"
                size="large"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[
                { required: true, message: "Please input your password!" },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Password"
                size="large"
              />
            </Form.Item>

            <div className="flex justify-end mb-4">
              <Link
                to="/auth/forgot-password"
                className="text-purple-600 hover:text-purple-500 text-sm"
              >
                Forgot password?
              </Link>
            </div>

            {needsVerification && (
              <div className="mb-4">
                <Button
                  type="primary"
                  onClick={handleResendVerification}
                  loading={resendVerificationLoading}
                  className="w-full"
                >
                  Resend Verification Email
                </Button>
              </div>
            )}

            <Form.Item shouldUpdate>
              {() => (
                <Button
                  type="primary"
                  htmlType="submit"
                  className="w-full"
                  size="large"
                  loading={loading}
                  disabled={
                    loading || resendVerificationLoading
                  }
                >
                  Sign in
                </Button>
              )}
            </Form.Item>

            <div className="flex flex-col space-y-4">
              <Button
                onClick={handleGuestLogin}
                className="w-full"
                size="large"
                disabled={loading || resendVerificationLoading}
              >
                Continue as Guest
              </Button>
              <Button
                danger
                onClick={handleGoogleLogin}
                className="w-full"
                size="large"
                loading={googleLoading}
                disabled={loading || resendVerificationLoading}
              >
                <GoogleOutlined />
                Sign in with Google
              </Button>

              <div className="text-center">
                <span className="text-gray-600">Don't have an account? </span>
                <Link
                  to="/auth/register"
                  className="text-purple-600 hover:text-purple-500"
                >
                  Sign up
                </Link>
              </div>
            </div>
          </Form>
        )}
      </Card>
    </div>
  );
}
