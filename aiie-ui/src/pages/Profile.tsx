import { useState, useEffect } from "react";
import {
  Form,
  Input,
  Button,
  Card,
  message,
  Spin,
  Typography,
} from "antd";
import { LockOutlined, MailOutlined } from "@ant-design/icons";
import { getUserApi, updateUserApi } from "../services/apis";
import { UpdateUserRequest, User } from "../types/user";
import { useAuth } from "../contexts/AuthContext";

const { Title, Text } = Typography;

export default function Profile() {
  const { authData } = useAuth();
  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage();
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [userData, setUserData] = useState<User | null>(null);

  // Fetch user data when component mounts (only if logged in)
  useEffect(() => {
    if (authData) {
      fetchUserData();
    }
  }, [authData]);

  const fetchUserData = async () => {
    setLoading(true);
    try {
      const response = await getUserApi();
      if (response.status === 200) {
        setUserData(response.data);
      }
    } catch (error) {
      console.error("Failed to fetch user data:", error);
      messageApi.error("Failed to load user profile data");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values: UpdateUserRequest) => {
    // Check if password is provided and not empty
    if (!values.password) {
      messageApi.warning("Please enter a new password");
      return;
    }

    setSubmitting(true);
    try {
      const response = await updateUserApi({ password: values.password });
      if (response.status === 200) {
        messageApi.success("Password updated successfully");
        form.resetFields(["password", "confirmPassword"]);
      }
    } catch (error) {
      console.error("Failed to update password:", error);
      messageApi.error("Failed to update password");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spin size="large" />
        <Text className="ml-2">Loading profile...</Text>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto p-4">
      {contextHolder}
      <Card
        title={<Title level={3}>Profile Settings</Title>}
        className="shadow-md"
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item label="Email">
            <Input
              prefix={<MailOutlined />}
              value={userData?.email}
              disabled
              readOnly
            />
          </Form.Item>

          <Form.Item
            name="password"
            label="New Password"
            rules={[
              { min: 8, message: "Password must be at least 8 characters" },
              {
                pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                message:
                  "Password must contain uppercase, lowercase and numbers",
              },
            ]}
            hasFeedback
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Enter new password"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            label="Confirm New Password"
            dependencies={["password"]}
            hasFeedback
            rules={[
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue("password") === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error("Passwords do not match"));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Confirm new password"
            />
          </Form.Item>

          <Form.Item className="mt-5">
            <Button
              type="primary"
              htmlType="submit"
              loading={submitting}
              className="w-full"
            >
              Update Password
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
