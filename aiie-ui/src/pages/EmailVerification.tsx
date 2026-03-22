import { useEffect, useState } from "react";
import { Card, Button, Result } from "antd";
import { useNavigate, useSearchParams } from "react-router-dom";
import { verifyEmailApi, sendVerificationEmailApi } from "../services/apis";
import Loading from "../components/Loading";

export default function EmailVerification() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const email = searchParams.get("email");

  const [loading, setLoading] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState<
    "idle" | "success" | "error"
  >("idle");
  const [resendStatus, setResendStatus] = useState<
    "idle" | "success" | "error"
  >("idle");
  const [isVerifying, setIsVerifying] = useState(token ? true : false);

  useEffect(() => {
    const verifyEmail = async () => {
      if (token) {
        setIsVerifying(true);
        setLoading(true);
        try {
          const response = await verifyEmailApi(token);
          if (response.status === 200) {
            setVerificationStatus("success");
          } else {
            setVerificationStatus("error");
          }
        } catch (error) {
          console.error("Email verification failed:", error);
          setVerificationStatus("error");
        } finally {
          setLoading(false);
          setIsVerifying(false);
        }
      }
    };

    verifyEmail();
  }, [token]);

  const handleResendVerification = async () => {
    if (!email) return;

    setResendStatus("idle");
    setLoading(true);
    try {
      const response = await sendVerificationEmailApi(email);
      if (response.status === 200) {
        setResendStatus("success");
      } else {
        setResendStatus("error");
      }
    } catch (error) {
      console.error("Failed to resend verification email:", error);
      setResendStatus("error");
    } finally {
      setLoading(false);
    }
  };

  // Token verification in progress
  if (isVerifying && loading) {
    return (
      <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8" style={{ background: 'linear-gradient(135deg, #f5f7fa 0%, #f0f4f9 100%)' }}>
        <Loading message="Verifying your email address..." />
      </div>
    );
  }

  // Token verification successful
  if (token && verificationStatus === "success") {
    return (
      <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8" style={{ background: 'linear-gradient(135deg, #f5f7fa 0%, #f0f4f9 100%)' }}>
        <Result
          status="success"
          title="Email Verified Successfully!"
          subTitle="Your email has been verified. You can now log in to your account."
          extra={[
            <Button
              type="primary"
              key="login"
              onClick={() => navigate("/auth/login")}
            >
              Go to Login
            </Button>,
          ]}
        />
      </div>
    );
  }

  // Token verification failed
  if (token && verificationStatus === "error") {
    return (
      <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8" style={{ background: 'linear-gradient(135deg, #f5f7fa 0%, #f0f4f9 100%)' }}>
        <Result
          status="error"
          title="Verification Failed"
          subTitle="The verification link is invalid or has expired."
          extra={[
            email ? (
              <Button
                type="primary"
                key="resend"
                loading={loading}
                onClick={handleResendVerification}
              >
                Resend Verification Email
              </Button>
            ) : (
              <Button
                type="primary"
                key="login"
                onClick={() => navigate("/auth/login")}
              >
                Back to Login
              </Button>
            ),
          ]}
        />
      </div>
    );
  }

  // No token provided - verification page
  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8" style={{ background: 'linear-gradient(135deg, #f5f7fa 0%, #f0f4f9 100%)' }}>
      <Card className="w-full max-w-md" style={{ borderRadius: '12px', boxShadow: '0px 8px 16px rgba(0, 0, 0, 0.08)' }}>
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-gray-900">
            Email Verification
          </h2>
          {!email ? (
            <p className="mt-2 text-gray-600">
              Please check your email for the verification link we sent you.
            </p>
          ) : (
            <p className="mt-2 text-gray-600">
              We've sent a verification link to <strong>{email}</strong>. Please
              check your inbox.
            </p>
          )}
        </div>

        {loading ? (
          <Loading message="Sending verification email..." />
        ) : (
          <>
            {resendStatus === "success" && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md text-green-700 text-center">
                Verification email has been sent successfully! Please check your
                inbox.
              </div>
            )}

            {resendStatus === "error" && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md text-red-700 text-center">
                Failed to send verification email. Please try again.
              </div>
            )}

            <div className="flex flex-col space-y-4">
              {email && (
                <Button
                  type="primary"
                  size="large"
                  loading={loading}
                  onClick={handleResendVerification}
                >
                  Resend Verification Email
                </Button>
              )}

              <Button
                type="default"
                size="large"
                onClick={() => navigate("/auth/login")}
              >
                Back to Login
              </Button>
            </div>
          </>
        )}
      </Card>
    </div>
  );
}
