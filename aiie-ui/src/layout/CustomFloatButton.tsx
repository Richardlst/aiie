import React from "react";
import { Button, Tooltip } from "antd";
import { CommentOutlined } from "@ant-design/icons";

interface CustomFloatButtonProps {
  icon?: React.ReactNode;
  tooltip?: string;
  onClick?: () => void;
  disabled?: boolean;
  active?: boolean;
  style?: React.CSSProperties;
}

const CustomFloatButton = ({
  icon = <CommentOutlined />,
  tooltip = "Agent",
  onClick,
  disabled = false,
  active = false,
  style = {},
}: CustomFloatButtonProps) => {
  return (
    <div className="fixed right-4 md:right-8 bottom-4 md:bottom-8 z-50">
      <Tooltip title={tooltip} placement="top">
        <Button
          type={active ? "primary" : "default"}
          shape="circle"
          icon={icon}
          onClick={onClick}
          disabled={disabled}
          size="large"
          className={`shadow-lg hover:shadow-xl transition-all ${disabled
            ? "opacity-50 cursor-not-allowed"
            : "hover:scale-105 card-hover-effect"
            }`}
          style={{
            background: active ? 'linear-gradient(to right, #7c5aff, #5cb8e6)' : 'white',
            border: active ? 'none' : '1px solid #e5e7eb',
            color: active ? 'white' : '#6B7280',
            ...style
          }}
        />
      </Tooltip>
    </div>
  );
};

export default CustomFloatButton;
