const express = require('express');
const router = express.Router();
const webhookController = require('../handlers/webhook');
const logger = require('../utils/logger');

// Webhook endpoint
router.post('/', async (req, res) => {
  try {
    const sig = req.headers['stripe-signature'];
    
    if (!sig) {
      logger.warn('Webhook received without signature');
      return res.status(400).json({ error: 'Missing stripe-signature header' });
    }

    await webhookController.handleWebhook(req.body, sig);
    
    res.json({ received: true });
  } catch (error) {
    logger.error('Webhook processing error', { error: error.message });
    res.status(400).json({ error: error.message });
  }
});

module.exports = router;