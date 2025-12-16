"""
Script to update the deployed service to use Cohere embeddings properly
This script outlines the changes needed to fix the embedding compatibility issue.
"""

print("COHERE EMBEDDING FIX FOR DEPLOYED RAG SERVICE")
print("=" * 60)
print()
print("ISSUE IDENTIFIED:")
print("- The deployed RAG service uses placeholder embeddings for queries")
print("- Stored vectors use Cohere embeddings (1536-dimensional)")
print("- Query embeddings use different method, causing mismatch")
print("- Similarity search fails to find matches")
print()
print("SOLUTION:")
print("1. Update the deployed service's qdrant_retriever.py file")
print("2. Replace the query embedding generation with Cohere")
print("3. Use the same Cohere model as during ingestion")
print()
print("REQUIRED CHANGES:")
print()
print("A. Update requirements.txt to ensure Cohere is available:")
print("   - Make sure 'cohere' is in the dependencies")
print()
print("B. Update the embedding generation in qdrant_retriever.py:")
print("   - Replace _get_placeholder_embedding() calls")
print("   - Use cohere.Client().embed() for query embedding")
print("   - Use the same model as used during ingestion")
print()
print("C. Example replacement for retrieve_chunks method:")
print("""
# OLD CODE (around line 94-96):
query_embedding = self._get_placeholder_embedding(query)

# NEW CODE:
import cohere
co = cohere.Client(settings.COHERE_API_KEY)
response = co.embed(
    texts=[query],
    model=settings.COHERE_MODEL  # Same as during ingestion
)
query_embedding = response.embeddings[0]
""")
print()
print("D. Environment variables needed:")
print("   - COHERE_API_KEY: Your Cohere API key")
print("   - COHERE_MODEL: The model used during ingestion")
print()
print("E. Redeploy the service to Render after making changes")
print()
print("EXPECTED RESULT:")
print("- Query embeddings will match the stored vector format")
print("- Similarity search will find relevant matches")
print("- RAG functionality will work properly")
print("- Chatbot will answer questions from the textbook")
print()
print("=" * 60)

# Additionally, let's create a patch file showing the exact changes needed
patch_content = '''
diff --git a/backend/rag-chatbot/utils/qdrant_retriever.py b/backend/rag-chatbot/utils/qdrant_retriever.py
index 1234567..89abcdef 100644
--- a/backend/rag-chatbot/utils/qdrant_retriever.py
+++ b/backend/rag-chatbot/utils/qdrant_retriever.py
@@ -90,10 +90,15 @@ class QdrantRetriever:
             # Embed the query using the same model as the ingestion service
             # Since we're using Cohere for the ingestion service
-            query_embedding = self.gemini_client.model.embed_content(
-                content=query
-            )['embedding'] if hasattr(self.gemini_client.model, 'embed_content') and self.gemini_client.model else self._get_placeholder_embedding(query)
+            import cohere
+            if hasattr(self, 'cohere_client') and self.cohere_client:
+                response = self.cohere_client.embed(
+                    texts=[query],
+                    model=settings.COHERE_MODEL
+                )
+                query_embedding = response.embeddings[0]
+            else:
+                # Fallback to placeholder if Cohere is not available
+                query_embedding = self._get_placeholder_embedding(query)

@@ -154,6 +154,11 @@ class QdrantRetriever:
         # Initialize Cohere client in __init__ method
+        # Initialize Cohere client
+        if settings.COHERE_API_KEY:
+            import cohere
+            self.cohere_client = cohere.Client(settings.COHERE_API_KEY)
+        else:
+            self.cohere_client = None
'''

with open('cohere_fix_patch.diff', 'w') as f:
    f.write(patch_content)

print("A patch file 'cohere_fix_patch.diff' has been created")
print("containing the exact changes needed to fix the service.")
print()
print("NEXT STEPS:")
print("1. Apply the changes to the deployed service code")
print("2. Update the deployment with Cohere integration")
print("3. Redeploy the fixed service to Render")
print("4. Test that retrieval and ask endpoints work properly")