# CraveConnect 🍽️

<div align="center">

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/🦜_LangChain-2C2C2C?style=for-the-badge)](https://www.langchain.com/)
[![Google AI](https://img.shields.io/badge/Google_AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

</div>

## 📋 About The Project

CraveConnect is an innovative platform that leverages AI and modern technology to enhance the food and dining experience. Built with a powerful tech stack combining FastAPI, LangChain, and Google's Generative AI, it offers a seamless interface for users to interact with food-related services.

## 🚀 Tech Stack

### Backend
- **FastAPI**: High-performance web framework for building APIs
- **Python 3.x**: Core programming language
- **LangChain**: Framework for developing applications powered by language models
- **Google Generative AI**: Advanced AI model integration
- **PostgreSQL with pgvector**: Database with vector similarity search capabilities
- **Uvicorn**: Lightning-fast ASGI server
- **Pydantic**: Data validation using Python type annotations
- **Python-multipart**: Handling multipart form data
- **Pillow**: Image processing capabilities
- **Pytesseract**: Optical Character Recognition (OCR)

### Environment & Utilities
- **python-dotenv**: Environment variable management
- **requests**: HTTP library for API requests

## 🛠️ Setup and Installation

1. Clone the repository
```bash
git clone https://github.com/arjunsaxaena/CraveConnect.git
cd CraveConnect
```

2. Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

## 🏃‍♂️ Running the Application

### Backend
```bash
cd backend
uvicorn app.main:app --reload --port 4001
```

## 📝 API Documentation

Coming Soon

## 🤝 Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📬 Contact

Arjun Saxena - arjunsaxena04@gmail.com

Project Link: [https://github.com/arjunsaxaena/CraveConnect](https://github.com/arjunsaxaena/CraveConnect)

---