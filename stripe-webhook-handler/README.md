# Stripe Webhook Handler

Production-ready Stripe webhook handler with signature verification, event processing, and database integration.

## Features

- **Signature Verification**: Validates Stripe webhook signatures to prevent fraudulent requests
- **Event Processing**: Routes different Stripe events to appropriate handlers
- **Database Integration**: Logs all events to PostgreSQL for audit trail
- **Error Handling**: Comprehensive error handling with retry logic
- **Docker Support**: Containerized deployment with Docker Compose
- **Testing**: Full test coverage with Jest
- **Monitoring**: Health check endpoint and logging

## Tech Stack

- Node.js 18+
- Express.js
- PostgreSQL
- Docker & Docker Compose
- Jest (testing)
- Stripe Node.js SDK

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Stripe keys and database URL
```

3. Start PostgreSQL with Docker:
```bash
docker-compose up -d postgres
```

4. Run migrations:
```bash
npm run migrate
```

5. Start the server:
```bash
npm start
```

## API Endpoints

### POST /webhook
Receives and processes Stripe webhook events.

### GET /health
Health check endpoint.

### GET /events/:id
Retrieve a specific event from the database.

## Environment Variables

- `STRIPE_SECRET_KEY`: Your Stripe secret key
- `STRIPE_WEBHOOK_SECRET`: Your webhook signing secret
- `DATABASE_URL`: PostgreSQL connection string
- `PORT`: Server port (default: 3000)

## Docker Deployment

```bash
docker-compose up -d
```

## Testing

```bash
npm test
```

## Event Types Supported

- `payment_intent.succeeded`
- `payment_intent.failed`
- `customer.subscription.created`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`

## Architecture

```
Stripe → Webhook → Signature Verification → Event Router → Handler → Database
                                              ↓
                                          Error Handler
```

## Security Features

- Webhook signature verification
- Input validation
- SQL injection prevention (parameterized queries)
- Rate limiting (recommended for production)
- HTTPS only (recommended for production)

## Monitoring

- Structured logging (JSON format)
- Event logging to database
- Health check endpoint
- Error tracking integration ready

## License

MIT