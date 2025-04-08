import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import configparser
from openai import OpenAI
from logger import app_logger

class RAGSystem:
    def __init__(self, data_path, embeddings_path="embeddings.xlsx"):
        self.data_path = data_path
        self.embeddings_path = embeddings_path
        
        # Load OpenAI API key from config.ini
        config = configparser.ConfigParser()
        config.read('config.ini')
        api_key = config['OPENAI_API']['OPENAI_KEY']
        
        self.client = OpenAI(api_key=api_key)
        self.data = None
        self.embeddings = None
        self.load_data()
        
    def load_data(self):
        """Load the Twitter data and embeddings if they exist"""
        try:
            self.data = pd.read_csv(self.data_path)
        except Exception as e:
            raise Exception(f"Error loading Twitter data: {str(e)}")
        
        # Try to load existing embeddings
        try:
            if os.path.exists(self.embeddings_path):
                self.embeddings = pd.read_excel(self.embeddings_path)
                
                # Verify that embeddings match the data
                if len(self.embeddings) != len(self.data):
                    print("Warning: Embeddings file does not match data. Regenerating embeddings...")
                    self.generate_embeddings()
            else:
                # Generate embeddings for all tweets
                self.generate_embeddings()
        except Exception as e:
            print(f"Error loading embeddings: {str(e)}. Regenerating embeddings...")
            self.generate_embeddings()
            
    def get_embedding(self, text):
        """Get embedding using OpenAI API"""
        try:
            text = text.replace("\n", " ")
            app_logger.log_embedding_request(text)
            embedding = self.client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding
            app_logger.log_openai_call("text-embedding-3-small", "create_embedding")
            return embedding
        except Exception as e:
            app_logger.log_embedding_request(text, success=False, error=str(e))
            app_logger.log_openai_call("text-embedding-3-small", "create_embedding", success=False, error=str(e))
            raise Exception(f"Error getting embedding from OpenAI API: {str(e)}")
            
    def generate_embeddings(self):
        """Generate embeddings for all tweets and save them"""
        # Generate embeddings for customer tweets
        customer_embeddings = [self.get_embedding(tweet) for tweet in self.data['customer_tweet'].tolist()]
        
        # Create DataFrame with embeddings
        self.embeddings = pd.DataFrame(customer_embeddings)
        
        # Save embeddings to Excel
        self.embeddings.to_excel(self.embeddings_path, index=False)
        
    def find_most_relevant_tweet(self, query, company, top_k=1):
        """Find the most relevant tweet for a given query and company"""
        # Filter data for the specified company (handle both formats)
        company_data = self.data[
            (self.data['company'] == company) | 
            (self.data['company'] == f"@{company}")
        ]
        
        # Return None if no tweets found for the company
        if len(company_data) == 0:
            return None
            
        company_embeddings = self.embeddings.iloc[company_data.index]
        
        # Generate embedding for the query
        query_embedding = self.get_embedding(query)
        
        # Calculate similarity with company embeddings
        similarities = cosine_similarity([query_embedding], company_embeddings)[0]
        
        # Get indices of top k most similar tweets
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return the most relevant tweets and their responses
        results = []
        for idx in top_indices:
            original_idx = company_data.index[idx]
            results.append({
                'customer_tweet': self.data.iloc[original_idx]['customer_tweet'],
                'company_tweet': self.data.iloc[original_idx]['company_tweet'],
                'company': self.data.iloc[original_idx]['company'],
                'similarity_score': similarities[idx]
            })
            
        return results[0] if results else None

    def generate_tweet(self, query, company):
        """Generate a tweet response using GPT-4o-mini based on a similar example"""
        try:
            # Find the most relevant example using RAG
            relevant_tweet = self.find_most_relevant_tweet(query, company)
            
            if not relevant_tweet:
                return {
                    "tweet": "I apologize, but I couldn't find a relevant response for your query.",
                    "similarity_score": 0.0,
                    "original_tweet": None
                }

            # Create the prompt for GPT-4o-mini
            instruction = f"""You are a chatbot answering customer's tweet. You are working for a company called {company}. 
You are provided with an example of a similar interaction between a customer and an agent. Reply to the customer's tweet in the same tone, structure and style than the provided example.

#####
Example:
Customer: "{relevant_tweet['customer_tweet']}"
Agent: "{relevant_tweet['company_tweet']}"

#####
Tweet to answer:
"{query}"
"""

            # Generate response using GPT-4o-mini
            messages = [
                {"role": "user", "content": instruction}
            ]

            app_logger.log_openai_call("gpt-4o-mini", "chat_completion", prompt=instruction)
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )

            generated_tweet = response.choices[0].message.content.strip()

            return {
                "tweet": generated_tweet,
                "similarity_score": float(relevant_tweet['similarity_score']),
                "original_tweet": relevant_tweet['customer_tweet']
            }
        except Exception as e:
            app_logger.log_openai_call("gpt-4o-mini", "chat_completion", success=False, error=str(e), prompt=instruction if 'instruction' in locals() else None)
            return {
                "tweet": "I apologize, but I encountered an error while generating the response. Please try again later.",
                "similarity_score": 0.0,
                "original_tweet": None,
                "error": str(e)
            } 