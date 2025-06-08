const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 3000;
const FLASK_API_URL = 'http://127.0.0.1:5000'; // This is for your Flask API endpoints

// Middleware
app.use(cors({
  origin: 'http://localhost:8080', // Allow requests from React frontend
}));
app.use(express.json()); // Parse JSON bodies

// --- CRITICAL FIX: Serve static images directly from Express ---
// This tells Express to serve files from your 'static' folder
// whenever a request comes to '/static'.
// Make sure this path correctly points to your Flask app's 'static' folder.
// Using forward slashes for cross-platform compatibility.
app.use('/static', express.static('C:/Users/Arjun/Desktop/Arjun/Projects/Swipe now/server/flask app/static'));

// Proxy endpoint for recommendations
app.post('/api/recommend', async (req, res) => {
  try {
    const { query } = req.body;
    if (!query) {
      return res.status(400).json({ error: 'Query is required' });
    }

    // Forward request to Flask backend for recommendations logic
    const response = await axios.post(`${FLASK_API_URL}/recommend`, { query });
    res.json(response.data);
  } catch (error) {
    console.error('Error forwarding request to Flask:', error.message);
    res.status(500).json({ error: 'Failed to fetch recommendations' });
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'Express middleware is running' });
});

app.listen(PORT, () => {
  console.log(`Express server running on http://localhost:${PORT}`);
  console.log(`Serving static files from C:/Users/Arjun/Desktop/Arjun/Projects/Swipe now/server/flask app/static under /static URL`);
});