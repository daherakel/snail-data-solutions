# Bedrock AI Agent - Frontend

Modern web interface for the AWS Bedrock AI Document Assistant.

## 🎨 Features

- **💬 Chat Interface** - ChatGPT-style conversation with your documents
- **📤 PDF Upload** - Drag & drop file upload with automatic processing
- **📚 Document Management** - View and manage indexed documents
- **🎨 Modern UI** - Beautiful, responsive design with Tailwind CSS
- **🌙 Dark Mode** - Automatic dark mode support
- **⚡ Real-time** - Instant responses from Lambda backend

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- AWS credentials with access to S3

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Edit .env.local with your AWS credentials
nano .env.local
```

### Configuration

Update `.env.local` with your AWS credentials:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
LAMBDA_QUERY_URL=your_lambda_url
```

### Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 📁 Project Structure

```
frontend/
├── app/
│   ├── api/
│   │   ├── upload/      # PDF upload endpoint
│   │   └── documents/   # List documents endpoint
│   ├── globals.css      # Global styles
│   ├── layout.tsx       # Root layout
│   └── page.tsx         # Main page with tabs
├── components/
│   ├── Chat.tsx         # Chat interface
│   ├── DocumentUpload.tsx  # File upload
│   └── DocumentList.tsx    # Document listing
└── public/              # Static assets
```

## 🎯 Usage

### Chat with Documents

1. Navigate to the "Chat" tab
2. Type your question about the uploaded documents
3. Get AI-powered answers with source citations

### Upload Documents

1. Go to the "Upload" tab
2. Drag & drop a PDF or click to select
3. Click "Subir" to upload
4. Document will be processed automatically (~4-10 seconds)

### View Documents

1. Switch to the "Documents" tab
2. See all indexed documents
3. View file sizes and upload dates

## 🛠️ Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **AWS SDK**: @aws-sdk/client-s3
- **Backend**: AWS Lambda + Bedrock

## 🔒 Security

- AWS credentials stored securely in environment variables
- API routes handle AWS operations server-side
- No credentials exposed to client

## 📊 Performance

- Server-side rendering for fast initial load
- Optimized bundle size
- Lazy loading of components
- Efficient AWS SDK usage

## 🐛 Troubleshooting

### Upload not working

- Check AWS credentials in `.env.local`
- Verify S3 bucket permissions
- Ensure bucket name matches in `route.ts`

### Documents not showing

- Verify AWS credentials
- Check S3 bucket has PDFs
- Inspect browser console for errors

### Chat not responding

- Confirm Lambda Function URL is correct
- Check Lambda has proper permissions
- Verify CORS is enabled on Function URL

## 📝 License

Part of the Snail Data Solutions project.

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Add environment variables in Vercel dashboard
```

### Docker

```bash
# Build image
docker build -t bedrock-frontend .

# Run container
docker run -p 3000:3000 bedrock-frontend
```

## 🤝 Contributing

This is part of a larger AWS Bedrock AI Agents module. See the main project README for contribution guidelines.

---

**Built with ❤️ using Next.js and AWS Bedrock**
