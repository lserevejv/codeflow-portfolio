const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const db = require('../database/connection');
const logger = require('../utils/logger');

// Event handlers for different Stripe event types
const eventHandlers = {
  'payment_intent.succeeded': handlePaymentIntentSucceeded,
  'payment_intent.failed': handlePaymentIntentFailed,
  'customer.subscription.created': handleSubscriptionCreated,
  'customer.subscription.deleted': handleSubscriptionDeleted,
  'invoice.payment_succeeded': handleInvoicePaymentSucceeded,
  'invoice.payment_failed': handleInvoicePaymentFailed,
};

async function handleWebhook(rawBody, sig) {
  let event;

  try {
    // Verify webhook signature
    event = stripe.webhooks.constructEvent(
      rawBody,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    logger.error('Webhook signature verification failed', { error: err.message });
    throw new Error('Invalid signature');
  }

  logger.info(`Processing webhook event: ${event.type}`, {
    eventId: event.id,
    eventType: event.type
  });

  // Log event to database
  await logEventToDatabase(event);

  // Route to appropriate handler
  const handler = eventHandlers[event.type];
  if (handler) {
    try {
      await handler(event.data.object);
      logger.info(`Successfully handled event: ${event.type}`);
    } catch (error) {
      logger.error(`Error handling event ${event.type}`, { error: error.message });
      throw error;
    }
  } else {
    logger.info(`No handler for event type: ${event.type}`);
  }
}

async function logEventToDatabase(event) {
  const query = `
    INSERT INTO stripe_events (event_id, event_type, processed, created_at)
    VALUES ($1, $2, $3, NOW())
    ON CONFLICT (event_id) DO UPDATE SET
      event_type = EXCLUDED.event_type,
      processed = EXCLUDED.processed
    RETURNING id
  `;

  try {
    await db.query(query, [event.id, event.type, false]);
  } catch (error) {
    logger.error('Failed to log event to database', { error: error.message });
    throw error;
  }
}

// Event handler implementations
async function handlePaymentIntentSucceeded(paymentIntent) {
  logger.info('Payment succeeded', { paymentIntentId: paymentIntent.id });
  await updateEventStatus(paymentIntent.id, true);
}

async function handlePaymentIntentFailed(paymentIntent) {
  logger.warn('Payment failed', { paymentIntentId: paymentIntent.id });
  await updateEventStatus(paymentIntent.id, true);
}

async function handleSubscriptionCreated(subscription) {
  logger.info('Subscription created', { subscriptionId: subscription.id });
  await updateEventStatus(subscription.id, true);
}

async function handleSubscriptionDeleted(subscription) {
  logger.info('Subscription deleted', { subscriptionId: subscription.id });
  await updateEventStatus(subscription.id, true);
}

async function handleInvoicePaymentSucceeded(invoice) {
  logger.info('Invoice payment succeeded', { invoiceId: invoice.id });
  await updateEventStatus(invoice.id, true);
}

async function handleInvoicePaymentFailed(invoice) {
  logger.warn('Invoice payment failed', { invoiceId: invoice.id });
  await updateEventStatus(invoice.id, true);
}

async function updateEventStatus(eventId, processed) {
  const query = `
    UPDATE stripe_events
    SET processed = $1
    WHERE event_id = $2
  `;

  try {
    await db.query(query, [processed, eventId]);
  } catch (error) {
    logger.error('Failed to update event status', { error: error.message });
  }
}

module.exports = { handleWebhook };