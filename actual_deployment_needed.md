# Actual Deployment Steps Needed

The RAG chatbot fix has been prepared but needs to be deployed to the live service. Here are the actual steps that need to be performed:

## 1. Update the Backend Service Files

The following files in the deployed service need to be updated:

### A. Update `backend/rag-chatbot/utils/qdrant_retriever.py`
- Line 90-106: Replace the query embedding code to use Cohere instead of the placeholder/Gemini approach
- Lines 13-51: Add Cohere client initialization in the `__init__` method

### B. Update `backend/rag-chatbot/requirements.txt`
- Add: `cohere==4.32`

### C. Ensure environment variables are set on Render:
- `COHERE_API_KEY`: Your Cohere API key
- `COHERE_MODEL`: Should be set to `embed-multilingual-v2.0` or similar

## 2. Redeployment Process

Since the service is deployed on Render, you need to:

1. **Clone the repository locally** (if not already done):
   ```bash
   git clone <your-repo-url>
   cd physical-ai-humanoid-robotics-textbook
   ```

2. **Update the files** with the fixes mentioned above

3. **Commit and push the changes**:
   ```bash
   git add .
   git commit -m "Fix: Use Cohere embeddings for query compatibility"
   git push origin main
   ```

4. **Monitor the Render deployment** to ensure it completes successfully

5. **Test the endpoints** after deployment:
   ```bash
   curl -X POST https://rag-chatbot-81k7.onrender.com/retrieve \
        -H "Content-Type: application/json" \
        -d '{"query_text": "Physical AI", "top_k": 3}'

   curl -X POST https://rag-chatbot-81k7.onrender.com/ask \
        -H "Content-Type: application/json" \
        -d '{"query_text": "What is Physical AI?"}'
   ```

## 3. Expected Results After Deployment

After the fix is deployed:

- The `/retrieve` endpoint should return relevant chunks instead of empty arrays
- The `/ask` endpoint should provide contextual answers from the textbook
- Query embeddings will be compatible with stored vectors (both using Cohere)
- The similarity search will find relevant matches in the Qdrant database
- The frontend chatbot component will receive proper responses

## 4. Verification Steps

Once deployed, verify functionality:

1. Test retrieval with various queries
2. Test the ask endpoint with questions about the textbook
3. Verify response times are acceptable
4. Check that the frontend properly displays responses

The fix addresses the core issue: the deployed service was generating query embeddings using a different method than the one used during ingestion, causing no matches to be found during similarity search. With both using Cohere embeddings, the system should work properly.