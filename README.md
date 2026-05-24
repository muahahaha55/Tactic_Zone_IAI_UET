# ⚽ Tactic Zone IAI-UET 🤖

---

## 📝 Giới thiệu & Mục tiêu 🎯

**Tactic Zone** là một hệ thống đa tác nhân thông minh (**Multi-Agent AI System**) được nghiên cứu và phát triển nhằm tối ưu hóa các quyết định phân tích dữ liệu, từ đó nâng cao tỷ lệ chiến thắng khi dự đoán kết quả bóng đá giải Ngoại hạng Anh (**Premier League**). Thay vì dựa vào những nhận định cảm tính cá nhân, hệ thống giải quyết bài toán cốt lõi bằng cách ứng dụng AI để mổ xẻ các số liệu chiến thuật chuyên sâu một cách khách quan và thực tế.

Quy trình vận hành lõi của hệ thống được vận hành khép kín qua 3 giai đoạn chính:
1. **📥 Thu thập & Chuẩn hóa dữ liệu:** Hệ thống tự động cào dữ liệu thống kê chi tiết của các câu lạc bộ từ nguồn uy tín, sau đó chuyển đổi các bảng tính phức tạp thành văn bản định dạng Markdown cấu trúc cao nhờ sức mạnh xử lý ngôn ngữ của LLM Groq.
2. **💾 Lưu trữ tri thức (RAG):** Cơ sở dữ liệu vectơ ChromaDB chịu trách nhiệm băm nhỏ, nhúng (Embedding) và lưu trữ các phân tích chiến thuật này, đảm bảo dữ liệu luôn sẵn sàng được truy xuất chính xác theo ngữ cảnh câu hỏi.
3. **🤝 Phối hợp đa tác nhân (Multi-Agent Workflow):** Khi nhận truy vấn, mạng lưới Agent chuyên biệt bao gồm *Query Analyzer* (Phân tích ý định), *Search Agent* (Tìm kiếm nâng cao), *Strategist* (Lên chiến thuật) và *Report Agent* (Tổng hợp báo cáo) sẽ cùng phối hợp chặt chẽ để đưa ra câu trả lời sắc bén nhất qua giao diện Streamlit trực quan.

---

## 🐳 Hướng dẫn triển khai bằng Docker 🚀

Để khởi chạy toàn bộ hệ thống một cách nhanh chóng, đồng bộ và tránh lỗi môi trường trên máy tính, bạn hãy thực hiện theo các bước chi tiết sau:

### 🔑 Bước 1: Thiết lập cấu hình môi trường
Tạo một file có tên chính xác là `.env` tại thư mục gốc của dự án (nằm cùng cấp với file `Dockerfile`) và khai báo các mã khóa API của bạn:
```env
GROQ_API_KEY=your_groq_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```
⚠️ Lưu ý quan trọng: Hệ thống đã được nâng cấp toàn diện sang sử dụng bộ não CDhatGroq. Hãy đảm bảo bạn đã điền chính xác mã GROQ_API_KEY để các Agent không bị mất kết nối.

### 🛠️ Bước 2: Xây dựng Docker Image

Mở Terminal ngay tại đường dẫn thư mục dự án của bạn và chạy lệnh sau để tiến hành đóng gói toàn bộ ứng dụng:

```
Bash
docker build -t tactic-zone-agent .
```

### 🏃‍♂️ Bước 3: Khởi chạy Docker Container

Sau khi quá trình build hoàn tất thành công, bạn chạy lệnh dưới đây để kích hoạt container chạy ngầm và liên kết file môi trường .env đã cấu hình ở Bước 1:

```
Bash
docker run --name my-tactic-agent -d -p 8501:8501 --env-file .env tactic-zone-agent
```

### 🌐 Bước 4: Truy cập giao diện ứng dụng
Bây giờ, ứng dụng phân tích chiến thuật đã sẵn sàng! Bạn hãy mở trình duyệt web lên và truy cập vào đường dẫn sau để trải nghiệm:
```
Plaintext
http://localhost:8501
```