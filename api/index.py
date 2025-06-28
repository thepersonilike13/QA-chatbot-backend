from flask import Flask, request, session, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import os

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat(history=[])

# Flask setup
app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app)

# Mock knowledge base
knowledge_base = {
    "shipping": (
        "📦 **Shipping Information**\n"
        "We offer **free standard shipping** on all orders over $50. "
        "Standard delivery typically takes **3-5 business days**. "
        "Express shipping is available at an additional cost and takes **1-2 business days**. "
        "Orders placed before 2 PM are processed the same day."
    ),

    "returns": (
        "🔁 **Return Policy**\n"
        "You can return or exchange items within **30 days of purchase**. "
        "Products must be unused and in original packaging. "
        "Refunds will be issued to your original payment method within **5-7 business days** of processing."
    ),

    "support": (
        "📞 **Customer Support**\n"
        "Our support team is available **24/7** via chat and email. "
        "For urgent queries, you can call our hotline at **1-800-555-HELP**. "
        "We strive to respond to emails within **12 hours**."
    ),

    "warranty": (
        "🛡️ **Warranty Information**\n"
        "All electronic products come with a **1-year limited warranty** covering manufacturing defects. "
        "Extended warranties are available at checkout for select items."
    ),

    "payments": (
        "💳 **Payment Options**\n"
        "We accept major credit/debit cards, PayPal, and UPI. "
        "All payments are securely processed through encrypted gateways. "
        "Installment options are available for purchases above $100."
    ),

    "order tracking": (
        "📍 **Order Tracking**\n"
        "Once your order is shipped, you'll receive an email with a tracking link. "
        "You can also track your order from your account dashboard under 'My Orders'."
    ),

    "account": (
        "👤 **Account Help**\n"
        "You can update your email, password, or shipping address by logging into your account. "
        "If you’ve forgotten your password, use the 'Forgot Password' option to reset it via email."
    ),

    "privacy": (
        "🔒 **Privacy Policy**\n"
        "We value your privacy. Your personal data is encrypted and never shared with third parties "
        "without consent. Read our full [Privacy Policy](https://yourstore.com/privacy) for more details."
    ),

    "refunds": (
        "💰 **Refund Information**\n"
        "Refunds are processed within **5-7 business days** once your return is received and inspected. "
        "You’ll receive an email confirmation when your refund has been issued."
    ),

    "cancellations": (
        "❌ **Order Cancellations**\n"
        "Orders can be canceled within **2 hours of placement** if they haven’t shipped yet. "
        "Please contact support immediately to request a cancellation."
    )
}

@app.route('/chat', methods=['POST'])

def chat_with_bot():
    
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    # Init chat history if needed
    if 'chat_history' not in session:
        session['chat_history'] = []

    session['chat_history'].append(("You", user_message))
    val = f"knowladge:{knowledge_base}, user_message:{user_message} return a short answer to the user message based on the knowledge base, do not include any other information, just the answer, as short as possible, do not include any other information, just the answer, as short as possible, if u do not answer the user message based on the knowledge base, return 'I do not know the answer to that question, a representative will contact you shortly.'"
    # Check knowledge base
    response = chat.send_message(val, stream=False)
    bot_reply = response.text

    session['chat_history'].append(("Bot", bot_reply))
    session.modified = True

    return jsonify({
        "response": bot_reply,
        "chat_history": session['chat_history']
    })

@app.route('/reset', methods=['POST'])
def reset_chat():
    session.pop('chat_history', None)
    global chat
    chat = model.start_chat(history=[])
    return jsonify({"message": "Chat history cleared."})


@app.route('/history', methods=['GET'])
def get_chat_history():
    chat_history = session.get('chat_history', [])
    return jsonify({
        "chat_history": chat_history
    })


# if __name__ == '__main__':
#     app.run(debug=True)
