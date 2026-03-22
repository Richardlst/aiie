import { Form, Input, Button, Card, message } from "antd";
import { LockOutlined, CheckCircleFilled } from "@ant-design/icons";
import { useNavigate, useSearchParams } from "react-router-dom";
import { resetPasswordApi } from "../services/apis";
import { useState } from "react";
import Loading from "../components/Loading";

interface ResetPasswordForm {
  password: string;
  confirmPassword: string;
}

export default function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [form] = Form.useForm();
  const [messageApi, messageContextHolder] = message.useMessage();
  const [loading, setLoading] = useState(false);
  const [resetSuccess, setResetSuccess] = useState(false);

  const onFinish = async (values: ResetPasswordForm) => {
    setLoading(true);
    try {
      if (!token) {
        messageApi.error(
          "Reset token is missing. Please request a new password reset link."
        );
        setTimeout(() => {
          navigate("/auth/forgot-password");
        }, 2000);
        return;
      }

      const response = await resetPasswordApi(token, values.password);

      if (response.status === 200) {
        setResetSuccess(true);
        messageApi.success("Password has been reset successfully!");
        setTimeout(() => {
          navigate("/auth/login");
        }, 4000);
      }
    } catch (error) {
      console.error("Password reset failed:", error);
      messageApi.error(
        "Failed to reset password. The link might be expired or invalid."
      );
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8" style={{ background: 'linear-gradient(135deg, #f5f7fa 0%, #f0f4f9 100%)' }}>
        <Card className="w-full max-w-md" style={{ borderRadius: '12px', boxShadow: '0px 8px 16px rgba(0, 0, 0, 0.08)' }}>
          <div className="text-center mb-8">
            <h2 className="text-3xl font-extrabold text-gray-900">
              Invalid Reset Link
            </h2>
            <p className="mt-2 text-gray-600">
              The password reset link is invalid or expired. Please request a
              new one.
            </p>
          </div>
          <Button
            type="primary"
            className="w-full"
            size="large"
            onClick={() => navigate("/auth/forgot-password")}
          >
            Request New Link
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8" style={{ background: 'linear-gradient(135deg, #f5f7fa 0%, #f0f4f9 100%)' }}>
      {messageContextHolder}
      <Card className="w-full max-w-md" style={{ borderRadius: '12px', boxShadow: '0px 8px 16px rgba(0, 0, 0, 0.08)' }}>
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-gray-900">
            Reset Your Password
          </h2>
          <p className="mt-2 text-gray-600">Enter your new password below</p>
        </div>

        {loading ? (
          <Loading message="Resetting password..." />
        ) : (
          <Form
            form={form}
            name="resetPassword"
            onFinish={onFinish}
            layout="vertical"
            requiredMark={false}
          >
            <Form.Item
              name="password"
              rules={[
                { required: true, message: "Please input your new password!" },
                { min: 6, message: "Password must be at least 6 characters!" },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="New Password"
                size="large"
                disabled={resetSuccess}
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
                    return Promise.reject(
                      new Error("The two passwords do not match!")
                    );
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Confirm New Password"
                size="large"
                disabled={resetSuccess}
              />
            </Form.Item>

            <Form.Item>
              {resetSuccess ? (
                <Button
                  type="primary"
                  className="w-full"
                  size="large"
                  icon={<CheckCircleFilled />}
                  style={{ backgroundColor: "#52c41a", borderColor: "#52c41a" }}
                  onClick={() => navigate("/auth/login")}
                >
                  Password Reset Successful! Redirecting...
                </Button>
              ) : (
                <Button
                  type="primary"
                  htmlType="submit"
                  className="w-full"
                  size="large"
                  loading={loading}
                >
                  Reset Password
                </Button>
              )}
            </Form.Item>
          </Form>
        )}
      </Card>
    </div>
  );
}
