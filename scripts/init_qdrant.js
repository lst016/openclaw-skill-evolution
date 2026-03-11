#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');
const { QdrantClient } = require('@qdrant/js-client-rest');

async function initQdrantCollections() {
  console.log('🔄 Initializing Qdrant collections...');
  
  const client = new QdrantClient({ 
    host: 'localhost', 
    port: 6333 
  });
  
  // Schema directory
  const schemaDir = path.join(process.cwd(), 'memory', 'qdrant', 'schemas');
  
  // Collection schemas to create
  const collections = ['skills', 'workflows', 'experiences', 'trajectories'];
  
  for (const collection of collections) {
    try {
      const schemaPath = path.join(schemaDir, `${collection}_schema.json`);
      const schema = JSON.parse(await fs.readFile(schemaPath, 'utf8'));
      
      // Check if collection already exists
      try {
        await client.getCollection(collection);
        console.log(`✅ Collection ${collection} already exists`);
        continue;
      } catch (error) {
        // Collection doesn't exist, create it
      }
      
      // Create collection
      await client.createCollection(collection, {
        vectors: {
          size: schema.vector_size || 1536,
          distance: schema.distance || 'Cosine'
        },
        hnsw_config: schema.hnsw_config || {
          m: 16,
          ef_construct: 100
        }
      });
      
      console.log(`✅ Created collection: ${collection}`);
      
    } catch (error) {
      console.error(`❌ Failed to create collection ${collection}:`, error.message);
    }
  }
  
  console.log('✨ Qdrant initialization completed!');
}

// Run the initialization
if (require.main === module) {
  initQdrantCollections().catch(console.error);
}

module.exports = { initQdrantCollections };