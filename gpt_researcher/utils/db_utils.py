from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from supabase import create_client, Client
from supabase.client import ClientOptions
import os
import logging
import traceback
import json

# Configure logging
logger = logging.getLogger("db_operations")


class DatabaseManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.supabase_url = os.environ.get("SUPABASE_URL")
            self.supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

            if not self.supabase_url or not self.supabase_key:
                error_msg = "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables must be set"
                logger.error(error_msg)
                raise ValueError(error_msg)

            try:
                self.supabase: Client = create_client(
                    supabase_url=self.supabase_url,
                    supabase_key=self.supabase_key,
                    options=ClientOptions(
                        headers={"Authorization": f"Bearer {self.supabase_key}"},
                        schema="scraping",
                    ),
                )
                logger.info(
                    "Successfully initialized Supabase client with service role"
                )
                logger.debug(f"Supabase URL: {self.supabase_url}")
                logger.debug(f"Service role key length: {len(self.supabase_key)}")
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise

    def _log_response_details(self, response: Any, operation: str) -> None:
        """Helper method to log detailed response information."""
        logger.debug(f"=== {operation} Response Details ===")
        logger.debug(f"Response type: {type(response)}")
        logger.debug(
            f"Response dict: {response.__dict__ if hasattr(response, '__dict__') else 'No dict'}"
        )
        logger.debug(
            f"Response data: {response.data if hasattr(response, 'data') else 'No data'}"
        )
        logger.debug(
            f"Response error: {response.error if hasattr(response, 'error') else 'No error'}"
        )
        if hasattr(response, "status_code"):
            logger.debug(f"Response status code: {response.status_code}")
        logger.debug("=====================================")

    def create_research_job(
        self,
        query: str,
        agent: Optional[str] = None,
        role: Optional[str] = None,
        report_type: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new research job record in the database."""
        try:
            # Convert additional_info to JSONB string if provided
            additional_info_json = (
                json.dumps(additional_info) if additional_info else "{}"
            )

            job_data = {
                "id": str(uuid.uuid4()),
                "query": query,
                "agent": agent,
                "role": role,
                "report_type": report_type,
                "started_at": datetime.utcnow().isoformat(),
                "status": "in_progress",
                "research_costs": 0.0,
                "visited_urls": json.dumps([]),  # Convert to JSONB string
                "report": None,
                "additional_info": additional_info_json,
            }

            logger.debug(
                f"Creating research job with data: {json.dumps(job_data, indent=2)}"
            )

            try:
                response = self.supabase.table("jobs").insert(job_data).execute()
            except Exception as e:
                logger.error(e)

            self._log_response_details(response, "Create Research Job")

            if hasattr(response, "error") and response.error:
                error_msg = f"Error creating job: {response.error}"
                logger.error(error_msg)
                raise Exception(error_msg)

            if not response.data:
                error_msg = "No data returned from insert operation"
                logger.error(error_msg)
                raise Exception(error_msg)

            logger.info(f"Successfully created research job with ID: {job_data['id']}")
            return job_data["id"]

        except Exception as e:
            logger.error(f"Failed to create research job: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Agent: {agent}")
            logger.error(f"Role: {role}")
            logger.error(f"Report Type: {report_type}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def insert_scraped_page(
        self,
        job_id: str,
        url: str,
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Insert a scraped page record into the database."""
        try:
            # Convert metadata to JSONB string if provided
            metadata_json = json.dumps(metadata) if metadata else "{}"

            page_data = {
                "id": str(uuid.uuid4()),
                "job_id": job_id,
                "url": url,
                "title": title,
                "content": content,
                "metadata": metadata_json,
                "scraped_at": datetime.utcnow().isoformat(),
            }

            logger.debug(f"Inserting scraped page for job {job_id}: {url}")
            logger.debug(f"Page data: {json.dumps(page_data, indent=2)}")

            response = self.supabase.table("pages").insert(page_data).execute()

            self._log_response_details(response, "Insert Scraped Page")

            if hasattr(response, "error") and response.error:
                error_msg = f"Error inserting scraped page: {response.error}"
                logger.error(error_msg)
                raise Exception(error_msg)

            if not response.data:
                error_msg = "No data returned from insert operation"
                logger.error(error_msg)
                raise Exception(error_msg)

            logger.info(f"Successfully inserted scraped page for URL: {url}")
            return page_data

        except Exception as e:
            logger.error(f"Failed to insert scraped page: {str(e)}")
            logger.error(f"Job ID: {job_id}")
            logger.error(f"URL: {url}")
            logger.error(f"Title: {title}")
            logger.error(f"Content length: {len(content) if content else 0}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def update_research_job(
        self,
        job_id: str,
        status: str,
        research_costs: Optional[float] = None,
        visited_urls: Optional[List[str]] = None,
        report: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a research job record with completion information."""
        try:
            update_data = {
                "finished_at": datetime.utcnow().isoformat(),
                "status": status,
                "error_message": error_message,
            }

            if research_costs is not None:
                update_data["research_costs"] = research_costs
            if visited_urls is not None:
                update_data["visited_urls"] = json.dumps(
                    visited_urls
                )  # Convert to JSONB string
            if report is not None:
                update_data["report"] = report

            logger.debug(f"Updating research job {job_id} with data: {update_data}")
            response = (
                self.supabase.table("jobs")
                .update(update_data)
                .eq("id", job_id)
                .execute()
            )

            if hasattr(response, "error") and response.error:
                error_msg = f"Error updating job: {response.error}"
                logger.error(error_msg)
                raise Exception(error_msg)

            logger.info(
                f"Successfully updated research job {job_id} with status: {status}"
            )
            return response.data[0] if response.data else None

        except Exception as e:
            logger.error(f"Failed to update research job: {str(e)}")
            logger.error(f"Job ID: {job_id}")
            logger.error(f"Status: {status}")
            logger.error(f"Research Costs: {research_costs}")
            logger.error(
                f"Visited URLs count: {len(visited_urls) if visited_urls else 0}"
            )
            logger.error(f"Report length: {len(report) if report else 0}")
            raise

    def get_research_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a research job record by ID."""
        try:
            logger.debug(f"Retrieving research job: {job_id}")
            response = (
                self.supabase.table("jobs").select("*").eq("id", job_id).execute()
            )

            if hasattr(response, "error") and response.error:
                error_msg = f"Error retrieving job: {response.error}"
                logger.error(error_msg)
                raise Exception(error_msg)

            job_data = response.data[0] if response.data else None
            if job_data:
                logger.info(f"Successfully retrieved research job: {job_id}")
            else:
                logger.warning(f"No research job found with ID: {job_id}")

            return job_data

        except Exception as e:
            logger.error(f"Failed to retrieve research job: {str(e)}")
            logger.error(f"Job ID: {job_id}")
            raise

    def get_scraped_pages(self, job_id: str) -> List[Dict[str, Any]]:
        """Retrieve all scraped pages for a research job."""
        try:
            logger.debug(f"Retrieving scraped pages for job: {job_id}")
            response = (
                self.supabase.table("pages").select("*").eq("job_id", job_id).execute()
            )

            if hasattr(response, "error") and response.error:
                error_msg = f"Error retrieving scraped pages: {response.error}"
                logger.error(error_msg)
                raise Exception(error_msg)

            pages = response.data
            logger.info(
                f"Successfully retrieved {len(pages)} scraped pages for job: {job_id}"
            )
            return pages

        except Exception as e:
            logger.error(f"Failed to retrieve scraped pages: {str(e)}")
            logger.error(f"Job ID: {job_id}")
            raise

    def insert_log(
        self,
        job_id: str,
        level: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Insert a log record into the database."""
        try:
            # Convert details to JSONB string if provided
            details_json = json.dumps(details) if details else "{}"

            log_data = {
                "id": str(uuid.uuid4()),
                "job_id": job_id,
                "level": level,
                "message": message,
                "details": details_json,
                "created_at": datetime.utcnow().isoformat(),
            }

            logger.debug(f"Inserting log for job {job_id}: {message}")
            logger.debug(f"Log data: {json.dumps(log_data, indent=2)}")

            response = self.supabase.table("logs").insert(log_data).execute()

            self._log_response_details(response, "Insert Log")

            if hasattr(response, "error") and response.error:
                error_msg = f"Error inserting log: {response.error}"
                logger.error(error_msg)
                raise Exception(error_msg)

            if not response.data:
                error_msg = "No data returned from insert operation"
                logger.error(error_msg)
                raise Exception(error_msg)

            logger.info(f"Successfully inserted log for job {job_id}")
            return log_data

        except Exception as e:
            logger.error(f"Failed to insert log: {str(e)}")
            logger.error(f"Job ID: {job_id}")
            logger.error(f"Level: {level}")
            logger.error(f"Message: {message}")
            logger.error(f"Details: {details}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
