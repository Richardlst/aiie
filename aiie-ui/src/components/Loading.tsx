import { Spin } from "antd";

interface LoadingProps {
  message?: string;
}

export default function Loading({ message = "Loading..." }: LoadingProps) {
  return (
    <div className="text-center py-12">
      <Spin size="large" />
      <p className="mt-4">{message}</p>
    </div>
  );
}
