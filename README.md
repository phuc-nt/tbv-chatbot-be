# Techbase Vietnam Assistant

This project is a Flask application that serves as an assistant for answering questions about Techbase Vietnam. It uses OpenAI's GPT model and Qdrant for searching similar sentences.

## Installation

First, clone the repository to your local machine:

\```sh
git clone https://github.com/yourusername/your-repo-name.git
\```

Install the requirements:

\```sh
pip install -r requirements.txt
\```

## Usage

To start the server, run:

\```sh
python app.py
\```

The server will start on `http://0.0.0.0:8080`.

## API Endpoints

- `GET /`: Returns the home page.
- `POST /api/chat`: Takes a JSON payload with a `query` and `context`, and returns a response from the GPT model.

## Environment Variables

The application uses the following environment variables, which are stored in a `.env` file:

\```properties
OPENAI_API_KEY=your_openai_api_key
QDRANT_API_KEY=your_qdrant_api_key
\```

## Contributing

Explain how to contribute to your project.

## License

Include information about the license.