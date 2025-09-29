"""
OpenSearch utilities for managing video transcription index and searching
"""
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
from dotenv import load_dotenv

load_dotenv()


class OpenSearchManager:
    def __init__(self, index_name: str = "video-transcriptions"):
        self.opensearch_endpoint = os.getenv('AWS_OPENSEARCH_ENDPOINT')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.index_name = index_name
        
        if not all([self.opensearch_endpoint, self.aws_access_key_id, self.aws_secret_access_key]):
            raise ValueError("OpenSearch configuration incomplete. Check environment variables.")
        
        # Setup OpenSearch client
        host = self.opensearch_endpoint.replace('https://', '').replace('http://', '')
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(
            self.aws_access_key_id,
            self.aws_secret_access_key,
            self.aws_region,
            'es',
            session_token=credentials.token if credentials else None
        )
        
        self.client = OpenSearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            pool_maxsize=20
        )

    def create_index(self, force_recreate: bool = False):
        """Create or recreate the OpenSearch index with proper mappings"""
        if force_recreate and self.client.indices.exists(index=self.index_name):
            self.client.indices.delete(index=self.index_name)
            print(f"Deleted existing index: {self.index_name}")
        
        if not self.client.indices.exists(index=self.index_name):
            index_body = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1,
                    "analysis": {
                        "analyzer": {
                            "default": {
                                "type": "standard"
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "job_id": {
                            "type": "keyword"
                        },
                        "url": {
                            "type": "keyword"
                        },
                        "title": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "transcription": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "summary": {
                            "type": "text"
                        },
                        "tags": {
                            "type": "keyword"
                        },
                        "created_at": {
                            "type": "date"
                        },
                        "completed_at": {
                            "type": "date"
                        },
                        "processing_time_seconds": {
                            "type": "float"
                        },
                        "status": {
                            "type": "keyword"
                        }
                    }
                }
            }
            
            self.client.indices.create(
                index=self.index_name,
                body=index_body
            )
            print(f"Created index: {self.index_name}")
        else:
            print(f"Index {self.index_name} already exists")

    def search_transcriptions(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        size: int = 10
    ) -> Dict:
        """
        Search transcriptions with various filters
        
        Args:
            query: Search query text
            tags: Optional list of tags to filter by
            date_from: Optional start date for filtering
            date_to: Optional end date for filtering
            size: Number of results to return
            
        Returns:
            OpenSearch response dictionary
        """
        must_clauses = []
        
        # Text search in title and transcription
        if query:
            must_clauses.append({
                "multi_match": {
                    "query": query,
                    "fields": ["title^2", "transcription", "summary"],
                    "type": "best_fields"
                }
            })
        
        # Tag filter
        if tags:
            must_clauses.append({
                "terms": {
                    "tags": tags
                }
            })
        
        # Date range filter
        if date_from or date_to:
            date_range = {}
            if date_from:
                date_range["gte"] = date_from.isoformat()
            if date_to:
                date_range["lte"] = date_to.isoformat()
            
            must_clauses.append({
                "range": {
                    "created_at": date_range
                }
            })
        
        # Build the query
        if must_clauses:
            search_body = {
                "query": {
                    "bool": {
                        "must": must_clauses
                    }
                },
                "size": size,
                "sort": [
                    {"_score": {"order": "desc"}},
                    {"created_at": {"order": "desc"}}
                ]
            }
        else:
            # If no search criteria, return recent documents
            search_body = {
                "query": {
                    "match_all": {}
                },
                "size": size,
                "sort": [
                    {"created_at": {"order": "desc"}}
                ]
            }
        
        response = self.client.search(
            index=self.index_name,
            body=search_body
        )
        
        return response

    def get_document_by_id(self, job_id: str) -> Optional[Dict]:
        """Retrieve a specific document by job ID"""
        try:
            response = self.client.get(
                index=self.index_name,
                id=job_id
            )
            return response['_source']
        except Exception as e:
            print(f"Document not found: {e}")
            return None

    def update_tags(self, job_id: str, tags: List[str]):
        """Update tags for an existing document"""
        self.client.update(
            index=self.index_name,
            id=job_id,
            body={
                "doc": {
                    "tags": tags
                }
            }
        )
        print(f"Updated tags for {job_id}")

    def delete_document(self, job_id: str):
        """Delete a document from the index"""
        self.client.delete(
            index=self.index_name,
            id=job_id
        )
        print(f"Deleted document {job_id}")

    def get_stats(self) -> Dict:
        """Get index statistics"""
        stats = self.client.indices.stats(index=self.index_name)
        count = self.client.count(index=self.index_name)
        
        return {
            "total_documents": count['count'],
            "index_size": stats['_all']['primaries']['store']['size_in_bytes'],
            "index_size_human": stats['_all']['primaries']['store']['size']
        }


def main():
    """Example usage and one-time setup"""
    manager = OpenSearchManager()
    
    # Create index (run this once)
    manager.create_index(force_recreate=False)
    
    # Example searches
    print("\n=== Example Searches ===\n")
    
    # Search for content
    results = manager.search_transcriptions(
        query="python programming",
        tags=["tutorial"],
        size=5
    )
    
    print(f"Found {results['hits']['total']['value']} results")
    for hit in results['hits']['hits']:
        source = hit['_source']
        print(f"- {source.get('title', 'Untitled')} (Score: {hit['_score']:.2f})")
    
    # Get index stats
    stats = manager.get_stats()
    print(f"\n=== Index Stats ===")
    print(f"Total documents: {stats['total_documents']}")
    print(f"Index size: {stats['index_size_human']}")


if __name__ == "__main__":
    main()