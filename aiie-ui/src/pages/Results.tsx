import { useState, useEffect } from "react";
import {
  Card,
  Table,
  Tag,
  Typography,
  Pagination,
  Space,
  message,
  Spin,
  TableColumnsType,
} from "antd";
import { getResultsPagingApi } from "../services/apis/result";
import { ResultResponse, ResultType } from "../types/result";
import { CalendarOutlined } from "@ant-design/icons";
import DisplayImage from "../components/DisplayImage";
import DatetimeRenderer from "../components/DatetimeRenderer";

const { Title } = Typography;

// Map result types to descriptive names
const resultTypeNames: Record<ResultType, string> = {
  [ResultType.SR]: "Super Resolution",
  [ResultType.T2I]: "Text to Image",
  [ResultType.I2I]: "Image to Image",
  [ResultType.INP]: "Inpaint",
  [ResultType.EXP]: "Expand",
  [ResultType.SEG]: "Segment",
  [ResultType.COL]: "Colorization",
  [ResultType.FR]: "Face Refine",
};

// Map result types to colors
const resultTypeColors: Record<ResultType, string> = {
  [ResultType.SR]: "blue",
  [ResultType.T2I]: "purple",
  [ResultType.I2I]: "geekblue",
  [ResultType.INP]: "orange",
  [ResultType.EXP]: "green",
  [ResultType.SEG]: "magenta",
  [ResultType.COL]: "pink",
  [ResultType.FR]: "volcano",
};

const Results = () => {
  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState<ResultResponse[]>([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    totalPages: 0,
  });
  const [messageApi, contextHolder] = message.useMessage();

  const fetchResults = async (page = 1, pageSize = 10) => {
    setLoading(true);
    try {
      const response = await getResultsPagingApi({
        page,
        page_size: pageSize,
      });

      setResults(response.data);
      setPagination({
        current: response.page,
        pageSize: response.page_size,
        total: response.total,
        totalPages: response.total_pages,
      });
    } catch (error) {
      console.error("Error fetching results:", error);
      messageApi.error("Failed to load results");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResults(pagination.current, pagination.pageSize);
  }, []);

  const handlePageChange = (page: number, pageSize?: number) => {
    fetchResults(page, pageSize || pagination.pageSize);
  };

  const columns: TableColumnsType<any> = [
    {
      title: "Image",
      key: "image",
      responsive: ["xs", "sm", "md", "lg", "xl"],
      width: "10%",
      render: (record: ResultResponse) => (
        <div className="cursor-pointer">
          <DisplayImage
            style={{ maxWidth: "60px" }}
            imageUrl={record.url}
            displayDownloadButton={false}
          />
        </div>
      ),
    },
    {
      title: "Type",
      key: "type",
      responsive: ["xs", "sm", "md", "lg", "xl"],
      width: "20%",
      render: (record: ResultResponse) => (
        <Tag color={resultTypeColors[record.type]} className="truncate max-w-[100px] sm:max-w-full">
          {resultTypeNames[record.type]}
        </Tag>
      ),
    },
    {
      title: "Created",
      key: "created_at",
      responsive: ["xs", "sm", "md", "lg", "xl"],
      width: "20%",
      render: (record: ResultResponse) => (
        <Space direction="vertical" size="small">
          <span>
            <CalendarOutlined className="mr-1" />
            <DatetimeRenderer>
              {record.created_at}
            </DatetimeRenderer>
          </span>
          <span className="text-sm text-gray-500"></span>
        </Space>
      ),
    },
  ];

  return (
    <div className="max-w-6xl mx-auto p-6">
      {contextHolder}
      {/* Gradient Header Section */}
      <div className="rounded-2xl mb-12 p-10 bg-gradient-to-r from-[#7c5aff] to-[#5cb8e6] text-white shadow-card">
        <div className="text-center mb-8">
          <Title style={{ color: 'white' }} level={1} className="mb-6">Your Creation History</Title>
          <Typography.Paragraph className="text-lg mt-4 mb-8 max-w-3xl mx-auto text-white/90">
            Track all your AI-generated images and transformations in one place. Review, download, and get inspired by your past creations.
          </Typography.Paragraph>
        </div>
      </div>

      {/* Results Section */}
      <Card
        className="shadow-card border-gray-100"
        style={{
          background: 'white'
        }}
      >
        <div className="mb-8">
          <Title level={2} className="text-center mb-2 gradient-text">
            Generated Results
          </Title>
          <Typography.Paragraph className="text-center text-gray-600 mb-8 text-lg">
            All your AI-powered image transformations in chronological order
          </Typography.Paragraph>
        </div>

        {loading ? (
          <div className="flex items-center justify-center p-12">
            <Spin size="large" />
          </div>
        ) : (
          <>
            <div className="mb-6 overflow-x-auto">
              <Table
                dataSource={results}
                columns={columns}
                rowKey="id"
                pagination={false}
                className="custom-table"
              />
            </div>
            <div className="flex justify-center mt-8 mb-4">
              <Pagination
                current={pagination.current}
                pageSize={pagination.pageSize}
                total={pagination.total}
                onChange={handlePageChange}
                showSizeChanger
                showQuickJumper
                showTotal={(total) => (
                  <span className="text-gray-600">
                    Total {total} items
                  </span>
                )}
                className="custom-pagination"
              />
            </div>
          </>
        )}
      </Card>
    </div>
  );
};

export default Results;
