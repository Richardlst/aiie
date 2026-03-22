import { useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate, useSearchParams } from "react-router-dom";

export default function Callback() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const accessToken = searchParams.get("access_token");
    if (accessToken) {
      login(accessToken);
      navigate("/");
    }
  }, [searchParams.get("access_token"), navigate]);

  return <div>Đang xử lý đăng nhập...</div>;
}
