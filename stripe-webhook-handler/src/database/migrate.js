const db = require('./connection');
const logger = require('../utils/logger');

async function migrate() {
  try {
    // Create stripe_events table
    await db.query(`
      CREATE TABLE IF NOT EXISTS stripe_events (
        id SERIAL PRIMARY KEY,
        event_id VARCHAR(255) UNIQUE NOT NULL,
        event_type VARCHAR(255) NOT NULL,
        processed BOOLEAN DEFAULT FALSE,
        payload JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Create index on event_id for faster lookups
    await db.query(`
      CREATE INDEX IF NOT EXISTS idx_stripe_events_event_id 
      ON stripe_events(event_id)
    `);

    // Create index on event_type for filtering
    await db.query(`
      CREATE INDEX IF NOT EXISTS idx_stripe_events_event_type 
      ON stripe_events(event_type)
    `);

    // Create function to update updated_at timestamp
    await db.query(`
      CREATE OR REPLACE FUNCTION update_updated_at_column()
      RETURNS TRIGGER AS $$
      BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
      END;
      $$ language 'plpgsql'
    `);

    // Create trigger to auto-update updated_at
    await db.query(`
      DROP TRIGGER IF EXISTS update_stripe_events_updated_at ON stripe_events
    `);
    
    await db.query(`
      CREATE TRIGGER update_stripe_events_updated_at
      BEFORE UPDATE ON stripe_events
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column()
    `);

    logger.info('Database migration completed successfully');
  } catch (error) {
    logger.error('Migration failed', { error: error.message });
    process.exit(1);
  } finally {
    process.exit(0);
  }
}

migrate();