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

    // Simple chatbot responses
    let response;
    let intent;

    if (message.includes('hello') || message.includes('hi') || message.includes('hey')) {
      response = "Hello! How can I help you today?";
      intent = 'greeting';
    } else if (message.includes('product') || message.includes('service')) {
      response = "We offer a wide range of products including software solutions, consulting services, and technical support. What specific product are you interested in?";
      intent = 'products';
    } else if (message.includes('account') || message.includes('login') || message.includes('password')) {
      response = "I can help you with account-related issues. Please describe what specific problem you're experiencing with your account.";
      intent = 'account';
    } else if (message.includes('hours') || message.includes('time') || message.includes('open')) {
      response = "Our business hours are Monday to Friday, 9 AM to 6 PM EST. For urgent issues, you can create a support ticket anytime.";
      intent = 'hours';
    } else if (message.includes('ticket') || message.includes('support') || message.includes('help')) {
      response = "I can help you create a support ticket. Please provide details about your issue and I'll escalate it to our support team.";
      intent = 'ticket';
    } else {
      response = "I understand you need help. Could you please provide more details about your question?";
      intent = 'default';
    }

    // Generate suggestions based on intent
    const suggestions = {
      'greeting': ['Tell me about your products', 'I need help with my account', 'What are your business hours?'],
      'products': ['Show me pricing', 'Technical specifications', 'Contact sales'],
      'account': ['Reset password', 'Update profile', 'Billing questions'],
      'hours': ['Create support ticket', 'Contact sales', 'Emergency support'],
      'ticket': ['Billing issues', 'Technical problems', 'Account access'],
      'default': ['Create support ticket', 'Talk to human agent', 'FAQ']
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
