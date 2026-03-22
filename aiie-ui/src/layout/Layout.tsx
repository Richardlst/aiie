import { Layout as AntdLayout, message } from "antd";
import Navigation from "./Navigation";
import { Outlet, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { CommentOutlined } from "@ant-design/icons";
import { useAuth } from "../contexts/AuthContext";
import axiosInstance from "../services/apis/axios";
import Chat from "../components/Chat";
import CustomFloatButton from "./CustomFloatButton";
const { Content, Sider } = AntdLayout;

export default function Layout() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const { authData } = useAuth();

  const navigate = useNavigate();
  const [messageApi, messageContextHolder] = message.useMessage();
  const { logout } = useAuth();

  useEffect(() => {
    const interceptorId = axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          logout();
          navigate("/auth/login");
          messageApi.error("Session expired. Please login again.");
        }
        if (error.response?.status === 500) {
          messageApi.error("Internal server error");
        }

        return Promise.reject(error);
      }
    );

    return () => {
      axiosInstance.interceptors.response.eject(interceptorId);
    };
  }, [logout, navigate]);

  return (
    <AntdLayout
      className="min-h-screen"
      style={{
        background:
          'linear-gradient(135deg, #fae9ef 0%, #f3d6c4 50%, #e8c8b5 100%)',
      }}
    >
      {messageContextHolder}

      <Sider
        trigger={null}
        collapsible={false}
        collapsed={false}
        className="bg-white shadow-lg border-r border-gray-100 fixed h-screen overflow-y-auto z-20 top-0 left-0"
        width={240}
        style={{
          position: 'fixed',
          height: '100vh',
          background: 'white',
          boxShadow: '2px 0px 8px rgba(0, 0, 0, 0.06)',
          width: '240px'
        }}
      >
        <Navigation />
      </Sider>
      <AntdLayout className="min-h-screen ml-60">
        <Content className="p-4 md:p-6">
          <div className="rounded-xl shadow-card border border-gray-100 p-4 md:p-6 min-h-[calc(100vh-48px)]" style={{background: 'white'}}>
            <Outlet />
          </div>
          <CustomFloatButton
            icon={<CommentOutlined />}
            tooltip={authData ? "Agent" : "Login to use agent"}
            onClick={() => setIsChatOpen(!isChatOpen)}
            disabled={!authData}
            active={isChatOpen}
            style={{
              background: isChatOpen
                ? 'linear-gradient(to right, #7c5aff, #5cb8e6)'
                : 'white',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
              border: isChatOpen ? 'none' : '1px solid #e5e7eb'
            }}
          />
          <div
            className={`fixed bottom-14 md:bottom-8 right-4 md:right-24 transition-all duration-300 ease-in-out ${isChatOpen
                ? "opacity-100 translate-y-0"
                : "opacity-0 translate-y-16 pointer-events-none"
              }`}
          >
            {authData && isChatOpen && (
              <div className="shadow-xl rounded-xl overflow-hidden border border-gray-100">
                <Chat onClose={() => setIsChatOpen(false)} />
              </div>
            )}
          </div>
        </Content>
      </AntdLayout>
    </AntdLayout>
  );
}
