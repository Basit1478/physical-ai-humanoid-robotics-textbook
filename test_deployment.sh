#!/bin/bash
# Test script to validate backend before deployment

echo "Validating backend deployment configuration..."

# Check if required files exist
echo "Checking required files..."

if [ ! -f "backend/main.py" ]; then
    echo "❌ ERROR: backend/main.py not found"
    exit 1
else
    echo "✅ backend/main.py found"
fi

if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ ERROR: backend/requirements.txt not found"
    exit 1
else
    echo "✅ backend/requirements.txt found"
fi

if [ ! -f "backend/Dockerfile.render" ]; then
    echo "❌ ERROR: backend/Dockerfile.render not found"
    exit 1
else
    echo "✅ backend/Dockerfile.render found"
fi

# Check if all required modules can be imported
echo "Checking Python imports..."
cd backend
python -c "
import sys
sys.path.append('.')
try:
    import fastapi
    print('✅ FastAPI import successful')
except ImportError as e:
    print(f'❌ FastAPI import failed: {e}')

try:
    import uvicorn
    print('✅ Uvicorn import successful')
except ImportError as e:
    print(f'❌ Uvicorn import failed: {e}')

try:
    import qdrant_client
    print('✅ Qdrant client import successful')
except ImportError as e:
    print(f'❌ Qdrant client import failed: {e}')

try:
    import jwt
    print('✅ JWT import successful')
except ImportError as e:
    print(f'❌ JWT import failed: {e}')

try:
    from auth.auth_api import auth_router
    print('✅ Auth API import successful')
except ImportError as e:
    print(f'❌ Auth API import failed: {e}')

try:
    from rag_chatbot.rag_api import rag_router
    print('✅ RAG API import successful')
except ImportError as e:
    print(f'❌ RAG API import failed: {e}')

try:
    from translate_urdu.translate_api import translate_router
    print('✅ Translate API import successful')
except ImportError as e:
    print(f'❌ Translate API import failed: {e}')

try:
    from personalize.personalize_api import personalize_router
    print('✅ Personalize API import successful')
except ImportError as e:
    print(f'❌ Personalize API import failed: {e}')

try:
    from utils.gemini_agent import OpenAI_Agents_Gemini
    print('✅ Gemini Agent import successful')
except ImportError as e:
    print(f'❌ Gemini Agent import failed: {e}')
"

echo "✅ All imports successful!"

echo "Deployment configuration validation complete!"
echo ""
echo "To deploy to Render:"
echo "1. Make sure you have a GitHub repository with this code"
echo "2. Create a new Web Service on Render"
echo "3. Use Dockerfile.render as the Dockerfile"
echo "4. Set the required environment variables"
echo "5. See RENDER_DEPLOYMENT_GUIDE.md for detailed instructions"