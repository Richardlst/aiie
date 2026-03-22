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
import "./index.css";
const defaultRoute = "/home";

function App() {
  return (
    <Routes>
      <Route path="/auth">
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        <Route path="callback" element={<Callback />} />
        <Route path="forgot-password" element={<ForgotPassword />} />
        <Route path="reset-password" element={<ResetPassword />} />
        <Route path="verify-email" element={<EmailVerification />} />
      </Route>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to={defaultRoute} replace />} />
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
