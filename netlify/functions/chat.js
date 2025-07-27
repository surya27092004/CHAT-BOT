exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    const body = JSON.parse(event.body || '{}');
    const message = (body.message || '').toLowerCase();
    
    let response = "Hello! I'm your Amazon shopping assistant! I can help you find products, check deals, track orders, and more! What are you looking for today?";
    
    if (message.includes('laptop')) {
      response = "Great! Here are some popular laptops:\n\n💻 MacBook Air M2 - $999\n💻 Dell XPS 13 - $849\n💻 ASUS ROG Gaming - $1,299\n\nWhat's your budget?";
    } else if (message.includes('phone')) {
      response = "Here are today's top smartphones:\n\n📱 iPhone 15 Pro - $999\n📱 Samsung Galaxy S24 - $799\n📱 Google Pixel 8 - $699\n\nWhich features matter most?";
    } else if (message.includes('deal')) {
      response = "Great deals available:\n\n💰 Today's Deals - Up to 70% off\n⚡ Lightning Deals - Limited time\n🏷️ Coupons - Extra discounts\n\nWhat's your budget range?";
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        response: response,
        user_id: body.user_id || 'user_123',
        session_id: 'session_' + Date.now(),
        timestamp: new Date().toISOString(),
        suggestions: ['Show me laptops', 'Find deals', 'Track order', 'Prime benefits']
      })
    };

  } catch (error) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: 'Internal server error',
        response: 'Sorry, I encountered an error. Please try again.'
      })
    };
  }
};
