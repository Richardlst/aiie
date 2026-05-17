import { Routes, Route, Navigate } from "react-router-dom";
import {
  Expand,
  Inpaint,
  ImageToImage,
  Segment,
  SuperResolution,
  TextToImage,
  Login,
  Register,
  Callback,
  ForgotPassword,
  ResetPassword,
  EmailVerification,
  Profile,
  Results,
  Home,
  Colorization,
  FaceRefine,
} from "./pages";
import Layout from "./layout/Layout";
import { useAuth } from "./contexts/AuthContext";
import "./index.css";

// Protected layout wrapper - redirects to login if not authenticated
const ProtectedLayout = () => {
  const { authData } = useAuth();

  if (!authData) {
    return <Navigate to="/auth/login" replace />;
  }

  return <Layout />;
};

function App() {
  return (
    <Routes>
      {/* Public auth routes */}
      <Route path="/auth">
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        <Route path="callback" element={<Callback />} />
        <Route path="forgot-password" element={<ForgotPassword />} />
        <Route path="reset-password" element={<ResetPassword />} />
        <Route path="verify-email" element={<EmailVerification />} />
      </Route>

      {/* Protected app routes */}
      <Route path="/" element={<ProtectedLayout />}>
        <Route index element={<Navigate to="/home" replace />} />
        <Route path="home" element={<Home />} />
        <Route path="super-resolution" element={<SuperResolution />} />
        <Route path="text-to-image" element={<TextToImage />} />
        <Route path="image-to-image" element={<ImageToImage />} />
        <Route path="inpaint" element={<Inpaint />} />
        <Route path="segment" element={<Segment />} />
        <Route path="expand" element={<Expand />} />
        <Route path="colorization" element={<Colorization />} />
        <Route path="face-refine" element={<FaceRefine />} />
        <Route path="results" element={<Results />} />
        <Route path="profile" element={<Profile />} />
      </Route>
    </Routes>
  );
}

export default App;
