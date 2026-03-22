import { Button, Image } from "antd";
import { DownloadOutlined } from "@ant-design/icons";
import { downloadImage } from "../utils";

export default function DisplayImage({
  imageUrl,
  style = {},
  imageStyle = {},
  displayDownloadButton = true,
  imageWidth = "100%",
}: {
  imageUrl: string;
  style?: React.CSSProperties;
  imageStyle?: React.CSSProperties;
  displayDownloadButton?: boolean;
  imageWidth?: string | number;
}) {
  const handleDownload = () => {
    downloadImage(imageUrl);
  };
  return (
    <div style={style}>
      <Image src={imageUrl} width={imageWidth} style={imageStyle} alt="Generated" />
      {displayDownloadButton && (
        <Button
          icon={<DownloadOutlined />}
          onClick={handleDownload}
          className="absolute top-3 right-3"
        />
      )}
    </div>
  );
}
