import { useState, useEffect } from "react";
import {
  ReactSketchCanvas,
  type ReactSketchCanvasRef,
} from "react-sketch-canvas";
import type { InputNumberProps } from "antd";
import { Col, InputNumber, Row, Slider, Button } from "antd";
import {
  UndoOutlined,
  RedoOutlined,
  ClearOutlined,
  SignatureOutlined,
  DownloadOutlined,
} from "@ant-design/icons";
import { downloadImage } from "../utils";
import { flushSync } from "react-dom";
import { Eraser } from "lucide-react";

export interface CanvasProps {
  backgroundImage: string | undefined;
  setBackgroundImage: (image: string | undefined) => void;
  canvasRef: React.RefObject<ReactSketchCanvasRef>;
  aspectRatio: number;
  imageWidth: number;
  imageHeight: number;
}

const Canvas = ({
  backgroundImage,
  setBackgroundImage,
  canvasRef,
  aspectRatio,
  imageWidth,
  imageHeight,
}: CanvasProps) => {
  const [eraserMode, setEraserMode] = useState(false);
  const [cursorWidth, setCursorWidth] = useState<number>(10);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Undo: Ctrl/Cmd + Z
      if ((e.ctrlKey || e.metaKey) && e.key === "z") {
        e.preventDefault();
        canvasRef.current?.undo();
      }
      // Redo: Ctrl/Cmd + Y
      if ((e.ctrlKey || e.metaKey) && e.key === "y") {
        e.preventDefault();
        canvasRef.current?.redo();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [canvasRef]);

  const onSliderChange: InputNumberProps["onChange"] = (newValue) => {
    setCursorWidth(newValue as number);
  };

  const handleDownload = async () => {
    const currentBackground = backgroundImage;
    try {
      // Ensure the background image is cleared before exporting
      flushSync(() => {
        setBackgroundImage("");
      });

      const imageDataUrl = await canvasRef.current?.exportImage("png");

      if (!imageDataUrl) {
        throw new Error("Failed to generate mask image");
      }

      const response = await fetch(imageDataUrl);
      const blob = await response.blob();

      const tempCanvas = document.createElement("canvas");
      tempCanvas.width = imageWidth;
      tempCanvas.height = imageHeight;
      const tempCtx = tempCanvas.getContext("2d");

      const imageBitmap = await createImageBitmap(blob);
      tempCtx?.drawImage(imageBitmap, 0, 0, imageWidth, imageHeight);

      const resizedImageDataUrl = tempCanvas.toDataURL("image/png");
      downloadImage(resizedImageDataUrl);
    } catch (error) {
      console.error("Error processing mask image:", error);
      throw error;
    } finally {
      setBackgroundImage(currentBackground);
    }
  };

  return (
    <div className="p-4">
      <Row gutter={[16, 16]} justify="center">
        <Col span={24}>
          <Row
            gutter={[4, 4]}
            justify="center"
            className="max-w-[600px] mx-auto"
          >
            <Col xs={12} sm={8} md={4} className="flex justify-center">
              <Button
                icon={<SignatureOutlined />}
                onClick={() => {
                  canvasRef.current?.eraseMode(false);
                  setEraserMode(false);
                }}
                type={!eraserMode ? "primary" : "default"}
                title="Stroke Mode"
                className="w-[95%]"
              />
            </Col>
            <Col xs={12} sm={8} md={4} className="flex justify-center">
              <Button
                icon={<Eraser className="w-4 h-4" />}
                onClick={() => {
                  setEraserMode(true);
                  canvasRef.current?.eraseMode(true);
                }}
                type={eraserMode ? "primary" : "default"}
                title="Eraser Mode"
                className="w-[95%]"
              />
            </Col>
            <Col xs={12} sm={8} md={4} className="flex justify-center">
              <Button
                icon={<UndoOutlined />}
                onClick={() => canvasRef.current?.undo()}
                title="Undo"
                className="w-[95%]"
              />
            </Col>
            <Col xs={12} sm={8} md={4} className="flex justify-center">
              <Button
                icon={<RedoOutlined />}
                onClick={() => canvasRef.current?.redo()}
                title="Redo"
                className="w-[95%]"
              />
            </Col>
            <Col xs={12} sm={8} md={4} className="flex justify-center">
              <Button
                icon={<ClearOutlined />}
                onClick={() => canvasRef.current?.clearCanvas()}
                title="Clear"
                className="w-[95%]"
              />
            </Col>
            <Col xs={12} sm={8} md={4} className="flex justify-center">
              <Button
                icon={<DownloadOutlined />}
                onClick={handleDownload}
                title="Download"
                className="w-[95%]"
              />
            </Col>
          </Row>
        </Col>
        <Col span={24}>
          <Row justify="center" align="middle" gutter={[16, 16]}>
            <Col xs={24} sm={12} md={12}>
              <Slider
                min={1}
                max={50}
                onChange={onSliderChange}
                value={typeof cursorWidth === "number" ? cursorWidth : 0}
              />
            </Col>
            <Col xs={24} sm={4} md={4}>
              <InputNumber
                min={1}
                max={50}
                value={cursorWidth}
                onChange={onSliderChange}
                style={{ width: "100%" }}
              />
            </Col>
          </Row>
        </Col>
        <Col span={24}>
          <ReactSketchCanvas
            ref={canvasRef}
            backgroundImage={backgroundImage}
            canvasColor="black"
            strokeColor="white"
            strokeWidth={cursorWidth}
            eraserWidth={cursorWidth}
            width={`${imageWidth}px`}
            height={`${imageHeight}px`}
            exportWithBackgroundImage={false}
            style={{
              cursor: eraserMode ? "crosshair" : "default",
              borderRadius: "0.25rem",
              maxWidth: "100%",
              height: "auto",
              display: "block",
              margin: "0 auto",
              aspectRatio: aspectRatio,
            }}
          />
        </Col>
      </Row>
    </div>
  );
};

export default Canvas;
