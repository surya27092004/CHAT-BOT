exports.handler = async (event, context) => {
  // Handle CORS
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    // Parse request body
    const body = JSON.parse(event.body || '{}');
    const message = (body.message || '').toLowerCase();
    const userId = body.user_id || 'user_' + Math.random().toString(36).substr(2, 9);

    // Amazon Product Assistant responses
    let response;
    let intent;
    let productRecommendations = [];

    if (message.includes('hello') || message.includes('hi') || message.includes('hey')) {
      response = "Hello! Welcome to Amazon Assistant! 🛒 I'm here to help you find the perfect products. What are you looking for today?";
      intent = 'greeting';
    } else if (message.includes('laptop') || message.includes('computer')) {
      response = "Great choice! I can help you find the perfect laptop. Here are some popular options:\n\n📱 **MacBook Air M2** - $999\n💻 **Dell XPS 13** - $849\n🎮 **ASUS ROG Gaming Laptop** - $1,299\n\nWhat's your budget and primary use case?";
      intent = 'electronics';
      productRecommendations = ['MacBook Air M2', 'Dell XPS 13', 'ASUS ROG Gaming'];
    } else if (message.includes('phone') || message.includes('mobile') || message.includes('smartphone')) {
      response = "Looking for a new smartphone? Here are today's top picks:\n\n📱 **iPhone 15 Pro** - $999\n🤖 **Samsung Galaxy S24** - $799\n📲 **Google Pixel 8** - $699\n\nWhich features matter most to you - camera, battery life, or performance?";
      intent = 'electronics';
      productRecommendations = ['iPhone 15 Pro', 'Samsung Galaxy S24', 'Google Pixel 8'];
    } else if (message.includes('book') || message.includes('read')) {
      response = "Perfect! Amazon has millions of books. Here are some trending categories:\n\n📚 **Fiction Bestsellers**\n🧠 **Self-Help & Personal Development**\n💼 **Business & Leadership**\n🔬 **Science & Technology**\n\nWhat genre interests you, or are you looking for a specific title?";
      intent = 'books';
    } else if (message.includes('clothes') || message.includes('fashion') || message.includes('shirt') || message.includes('dress')) {
      response = "Fashion shopping made easy! Here are popular categories:\n\n👔 **Men's Clothing** - Shirts, Jeans, Suits\n👗 **Women's Fashion** - Dresses, Tops, Accessories\n👟 **Shoes & Footwear** - Sneakers, Boots, Heels\n🎒 **Bags & Accessories**\n\nWhat type of clothing are you shopping for?";
      intent = 'fashion';
    } else if (message.includes('home') || message.includes('kitchen') || message.includes('furniture')) {
      response = "Transform your home! Popular home categories:\n\n🏠 **Furniture** - Sofas, Tables, Beds\n🍳 **Kitchen & Dining** - Appliances, Cookware\n🛏️ **Bedding & Bath** - Sheets, Towels, Decor\n🌱 **Garden & Outdoor** - Plants, Tools, Patio\n\nWhat room are you looking to upgrade?";
      intent = 'home';
    } else if (message.includes('price') || message.includes('cost') || message.includes('cheap') || message.includes('deal')) {
      response = "Looking for great deals? Here's how to save on Amazon:\n\n💰 **Today's Deals** - Up to 70% off\n⚡ **Lightning Deals** - Limited time offers\n📦 **Amazon Prime** - Free shipping & exclusive deals\n🏷️ **Coupons** - Extra discounts on thousands of items\n\nWhat's your budget range?";
      intent = 'deals';
    } else if (message.includes('delivery') || message.includes('shipping') || message.includes('when')) {
      response = "Amazon delivery options:\n\n🚚 **FREE Standard Delivery** - 3-5 business days\n⚡ **Prime Same-Day** - Order by 12pm (Prime members)\n📦 **Prime Next-Day** - Free for Prime members\n🎯 **Amazon Locker** - Secure pickup locations\n\nDo you have Amazon Prime for faster shipping?";
      intent = 'shipping';
    } else if (message.includes('return') || message.includes('refund') || message.includes('exchange')) {
      response = "Amazon's hassle-free returns:\n\n↩️ **30-day return window** for most items\n📦 **Free returns** on eligible orders\n🏪 **Drop-off locations** - Whole Foods, UPS, Kohl's\n💳 **Quick refunds** - Usually 3-5 business days\n\nNeed help with a specific return?";
      intent = 'returns';
    } else if (message.includes('prime') || message.includes('membership')) {
      response = "Amazon Prime benefits:\n\n📦 **FREE Fast Shipping** - 1-2 day delivery\n📺 **Prime Video** - Movies, TV shows, originals\n🎵 **Prime Music** - 2 million songs ad-free\n📚 **Prime Reading** - Books, magazines, comics\n🛒 **Exclusive deals** - Prime-only discounts\n\n💰 Only $14.99/month or $139/year. Want to learn more?";
      intent = 'prime';
    } else if (message.includes('track') || message.includes('order') || message.includes('status')) {
      response = "Track your Amazon orders easily:\n\n📱 **Amazon App** - Real-time tracking\n📧 **Email updates** - Automatic notifications\n🗺️ **Live map tracking** - See your delivery\n📞 **Order details** - In Your Account > Your Orders\n\nDo you need help finding a specific order?";
      intent = 'tracking';
    } else {
      response = "I'm your Amazon shopping assistant! I can help you with:\n\n🛒 **Product recommendations**\n💰 **Finding deals & discounts**\n📦 **Shipping & delivery info**\n↩️ **Returns & exchanges**\n🔍 **Product comparisons**\n\nWhat would you like to shop for today?";
      intent = 'help';
    }

    // Generate suggestions based on intent
    const suggestions = {
      'greeting': ['Show me laptops', 'Find deals and discounts', 'Track my order', 'Amazon Prime benefits'],
      'electronics': ['Compare prices', 'Check reviews', 'See more options', 'Add to cart'],
      'books': ['Bestsellers', 'Kindle books', 'Audiobooks', 'Book recommendations'],
      'fashion': ['Mens clothing', 'Womens fashion', 'Shoes and accessories', 'Size guide'],
      'home': ['Kitchen appliances', 'Furniture deals', 'Home decor', 'Garden supplies'],
      'deals': ['Lightning deals', 'Todays deals', 'Prime exclusive', 'Coupons available'],
      'shipping': ['Prime membership', 'Delivery options', 'Amazon lockers', 'Express shipping'],
      'returns': ['Return policy', 'Print return label', 'Refund status', 'Exchange item'],
      'prime': ['Join Prime', 'Prime benefits', 'Prime Video', 'Prime Music'],
      'tracking': ['Track package', 'Delivery updates', 'Order history', 'Contact carrier'],
      'help': ['Browse categories', 'Search products', 'Customer service', 'Shopping cart']
    };

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        response: response,
        confidence: 0.8,
        intent: intent,
        session_id: 'session_' + Math.random().toString(36).substr(2, 9),
        processing_time: 0.1,
        timestamp: new Date().toISOString(),
        suggestions: suggestions[intent] || [],
        requires_human: false,
        entities: {},
        user_id: userId
      })
    };

  } catch (error) {
    console.error('Error in chat function:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: 'Internal server error',
        response: 'I apologize, but I encountered an error. Please try again.'
      })
    };
  }
};
