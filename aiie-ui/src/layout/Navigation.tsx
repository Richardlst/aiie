import { Menu, Dropdown, Button } from "antd";
import {
  Image as ImageIcon,
  Wand2,
  ImagePlus,
  Pen,
  SquareBottomDashedScissors,
  Expand,
  LogOut,
  User,
  UserCircle,
  History,
  Home as HomeIcon,
  Palette,
  UserCircle2,
} from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { authData, logout } = useAuth();

  const email = authData?.tokenData.email || "Guest";

  const handleLogout = () => {
    logout();
    navigate("/auth/login");
  };

  const userDropdownItems = [
    {
      key: "profile",
      label: "Profile",
      icon: <UserCircle className="w-4 h-4" />,
      onClick: () => navigate("/profile"),
    },
    {
      key: "logout",
      label: "Logout",
      icon: <LogOut className="w-4 h-4" />,
      onClick: handleLogout,
    },
  ];

  const mainItems = [
    {
      key: "home",
      icon: <HomeIcon className="w-5 h-5" />,
      label: "Home",
      style: { color: '#5568d3', fontWeight: '500' }
    },
    {
      key: "super-resolution",
      icon: <ImageIcon className="w-5 h-5" />,
      label: "Super Resolution",
      style: { color: '#5568d3', fontWeight: '500' }
    },
    {
      key: "text-to-image",
      icon: <Wand2 className="w-5 h-5" />,
      label: "Text to Image",
      style: { color: '#e074e3', fontWeight: '500' }
    },
    {
      key: "image-to-image",
      icon: <ImagePlus className="w-5 h-5" />,
      label: "Image to Image",
      style: { color: '#3d8eeb', fontWeight: '500' }
    },
    {
      key: "expand",
      icon: <Expand className="w-5 h-5" />,
      label: "Expand",
      style: { color: '#00d4e6', fontWeight: '500' }
    },
    {
      key: "segment",
      icon: <SquareBottomDashedScissors className="w-5 h-5" />,
      label: "Segment",
      style: { color: '#7ed4ca', fontWeight: '500' }
    },
    {
      key: "inpaint",
      icon: <Pen className="w-5 h-5" />,
      label: "Inpaint",
      style: { color: '#e8507a', fontWeight: '500' }
    },
    {
      key: "colorization",
      icon: <Palette className="w-5 h-5" />,
      label: "Colorization",
      style: { color: '#ff6b9d', fontWeight: '500' }
    },
    {
      key: "face-refine",
      icon: <UserCircle2 className="w-5 h-5" />,
      label: "Face Refine",
      style: { color: '#6366f1', fontWeight: '500' }
    },
    {
      key: "results",
      icon: <History className="w-5 h-5" />,
      label: "Results",
      style: { color: '#f59e0b', fontWeight: '500' }
    },
  ];

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Logo section */}
      <div className="p-6 text-center border-b border-gray-100" style={{ 
        background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)',
        borderRadius: '0 0 16px 16px',
        marginBottom: '12px'
      }}>
        <div className="font-bold bg-gradient-to-r from-[#667eea] to-[#764ba2] bg-clip-text text-transparent text-lg">
          AI TOOLS
        </div>
      </div>

      {/* Menu items */}
      <Menu
        mode="inline"
        selectedKeys={[location.pathname.replace("/", "") || "home"]}
        items={mainItems}
        onClick={({ key }) => {
          navigate(`/${key}`);
        }}
        className="border-0 flex-1 custom-menu"
        style={{
          padding: "12px",
          backgroundColor: "white",
          borderRight: "1px solid #e8e8e8"
        }}
      />

      {/* User section */}
      <div className="p-4 border-t border-gray-100" style={{ 
        background: 'linear-gradient(135deg, #667eea08 0%, #764ba208 100%)',
        borderRadius: '16px 16px 0 0',
        marginTop: '12px'
      }}>
        <Dropdown trigger={['click']} menu={{ items: userDropdownItems }} placement="bottomRight">
          <Button
            className="w-full flex items-center gap-3 hover:shadow-md"
            style={{
              padding: '10px 14px',
              border: '1px solid rgba(124, 90, 255, 0.2)',
              background: 'white',
              height: 'auto',
              boxShadow: '0px 4px 12px rgba(124, 90, 255, 0.1)',
              borderRadius: '12px',
              transition: 'all 0.3s ease'
            }}
          >
            <div className="flex-shrink-0 bg-gradient-to-r from-[#7c5aff] to-[#5cb8e6] p-2 rounded-full">
              <User className="w-5 h-5 text-white" />
            </div>
            <span className="flex-1 truncate text-sm font-medium text-gray-700">{email}</span>
          </Button>
        </Dropdown>
      </div>
    </div>
  );
};

export default Navigation;
