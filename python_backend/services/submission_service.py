"""
Submission Service - handles idea submissions
"""
import io
import csv
from typing import Dict, List, Any, Optional
from datetime import datetime
import openpyxl
import pandas as pd

from config.database import get_db_connection
from services.csv_processor import CSVProcessor, ProcessingResult


class SubmissionService:
    def __init__(self):
        self.csv_processor = CSVProcessor()
    
    async def process_submission_from_buffer(
        self,
        file_buffer: bytes,
        submitter_id: str,
        source_ip: Optional[str] = None,
        support_file_buffer: Optional[bytes] = None,
        support_file_type: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process submission from file buffer"""
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Begin transaction
                cursor.execute("BEGIN")
                
                print(f"Received file buffer of {len(file_buffer)} bytes")
                
                # Parse file based on type
                csv_data = await self.parse_file_buffer(file_buffer, file_type)
                print(f"Parsed {len(csv_data)} data rows from file")
                
                # Process CSV
                processing_result = await self.csv_processor.process_rows(csv_data)
                error_rate = len(processing_result.invalid_rows) / processing_result.total_rows
                
                # Check 5% threshold
                if error_rate > 0.05:
                    raise Exception(
                        f"Error rate {error_rate * 100:.1f}% exceeds 5% threshold. Upload rejected."
                    )
                
                # Create file URIs (mock for now)
                csv_uri = f"local://submissions/{int(datetime.now().timestamp())}.csv"
                support_uri = f"local://submissions/{int(datetime.now().timestamp())}.{support_file_type}" if support_file_buffer else None
                
                # Create submission record
                cursor.execute("""
                    INSERT INTO idea_submissions (
                        submitter_id, csv_file_uri, support_file_uri, support_file_type,
                        total_rows, valid_rows, invalid_rows, status, source_ip
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    submitter_id,
                    csv_uri,
                    support_uri,
                    support_file_type,
                    processing_result.total_rows,
                    len(processing_result.valid_rows),
                    len(processing_result.invalid_rows),
                    'validated',
                    source_ip
                ))
                
                submission_id = cursor.fetchone()[0]
                
                # Create idea records in batches
                await self.create_ideas_in_batches(
                    cursor,
                    submission_id,
                    processing_result.valid_rows
                )
                
                # Commit transaction
                cursor.execute("COMMIT")
                
                # Emit events (mock)
                await self.emit_events(submission_id, processing_result)
                
                return {
                    'submission_id': submission_id,
                    'total_rows': processing_result.total_rows,
                    'valid_rows': len(processing_result.valid_rows),
                    'invalid_rows': len(processing_result.invalid_rows),
                    'status': 'validated'
                }
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
            finally:
                cursor.close()
    
    async def parse_file_buffer(self, file_buffer: bytes, file_type: Optional[str] = None) -> List[Dict]:
        """Parse file buffer (CSV or XLSX)"""
        
        # Detect file type if not provided
        if not file_type:
            # Check for XLSX magic number (PK\x03\x04)
            if file_buffer[0:2] == b'PK':
                file_type = 'xlsx'
            else:
                file_type = 'csv'
        
        print(f"Detected file type: {file_type}")
        
        if file_type in ['xlsx', 'xls']:
            return await self.parse_xlsx_buffer(file_buffer)
        else:
            return await self.parse_csv_buffer(file_buffer)
    
    async def parse_xlsx_buffer(self, buffer: bytes) -> List[Dict]:
        """Parse XLSX file buffer"""
        print('Parsing XLSX file...')
        
        # Read workbook from buffer
        workbook = openpyxl.load_workbook(io.BytesIO(buffer))
        sheet = workbook.active
        
        # Get headers from first row
        headers = [cell.value.lower().strip() if cell.value else '' for cell in sheet[1]]
        
        # Parse data rows
        data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            row_dict = {}
            for i, value in enumerate(row):
                if i < len(headers):
                    row_dict[headers[i]] = str(value) if value is not None else ''
            data.append(row_dict)
        
        print(f"Parsed {len(data)} rows from XLSX")
        return data
    
    async def parse_csv_buffer(self, buffer: bytes) -> List[Dict]:
        """Parse CSV file buffer"""
        print('Parsing CSV file...')
        
        csv_text = buffer.decode('utf-8')
        print(f"CSV text length: {len(csv_text)} characters")
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        data = []
        
        for row in csv_reader:
            # Normalize keys to lowercase
            normalized_row = {k.lower().strip(): v for k, v in row.items()}
            data.append(normalized_row)
        
        print(f"Parsed {len(data)} rows from CSV")
        return data
    
    async def create_ideas_in_batches(self, cursor, submission_id: str, rows: List[Dict]):
        """Create idea records in batches"""
        batch_size = 100
        
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            
            for row in batch:
                cursor.execute("""
                    INSERT INTO ideas (
                        submission_id, title, brief_summary, challenge_opportunity,
                        novelty_benefits_risks, responsible_ai_adherence, additional_documentation,
                        supporting_artefacts, second_file_upload, preferred_week, build_phase_preference,
                        build_preference, code_development_preference, submitter_email
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    submission_id,
                    row.get('your idea title', ''),
                    row.get('brief summary of your idea', ''),
                    row.get('challenge/business opportunity being addressed and the ability to scale it across tcs and multiple customers.'),
                    row.get('novelty of the idea, benefits and risks.'),
                    row.get('highlight adherence to responsible ai principles such as security, fairness, privacy & legal compliance.'),
                    row.get('additional documentation – any additional information or prototype explaining technical approach, architecture, development timeline, success metrics and expected outcomes, and scalability potential. you can also share any research done on business model, competitive analysis, risk & mitigations. sharing relevant artefacts will boost your scores.'),
                    row.get('additional documentation – any additional information or prototype explaining technical approach, architecture, development timeline, success metrics and expected outcomes, and scalability potential. you can also share any research done on business model, competitive analysis, risk & mitigations. sharing relevant artefacts will boost your scores.'),
                    row.get('incase you have a second file that could further illustrate your solution, kindly upload the same here.'),
                    row.get('your preferred week of participation'),
                    row.get('your preference for build phase'),
                    row.get('your preference on how you want to  build your idea'),
                    row.get('your preference if you were to develop code'),
                    row.get('email', '')
                ))
    
    async def emit_events(self, submission_id: str, result: ProcessingResult):
        """Emit events (mock implementation)"""
        print('Event: IdeaSubmission.Validated', {
            'submission_id': submission_id,
            'valid_rows': len(result.valid_rows),
            'invalid_rows': len(result.invalid_rows),
        })
        
        print('Event: Idea.BulkCreated', {
            'submission_id': submission_id,
            'count': len(result.valid_rows),
        })
    
    async def submit_single_idea(
        self,
        user_id: str,
        idea_data: Dict[str, Any],
        source_ip: Optional[str] = None
    ) -> Dict[str, str]:
        """Submit a single idea via form"""
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("BEGIN")
                
                # Validate required fields
                if not idea_data.get('title') or len(idea_data['title'].strip()) < 5:
                    raise ValueError('Title is required and must be at least 5 characters')
                
                if not idea_data.get('brief_summary') or len(idea_data['brief_summary'].strip()) < 10:
                    raise ValueError('Brief summary is required and must be at least 10 characters')
                
                # Create submission record
                cursor.execute("""
                    INSERT INTO idea_submissions (
                        submitter_id, csv_file_uri, total_rows, valid_rows, invalid_rows, status, source_ip
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (user_id, 'single-submission', 1, 1, 0, 'validated', source_ip))
                
                submission_id = cursor.fetchone()[0]
                
                # Insert idea
                cursor.execute("""
                    INSERT INTO ideas (
                        submission_id, title, brief_summary, challenge_opportunity,
                        novelty_benefits_risks, responsible_ai_adherence, additional_documentation,
                        supporting_artefacts, second_file_upload, preferred_week, build_phase_preference,
                        build_preference, code_development_preference, submitter_email
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    submission_id,
                    idea_data['title'],
                    idea_data['brief_summary'],
                    idea_data.get('challenge_opportunity'),
                    idea_data.get('novelty_benefits_risks'),
                    idea_data.get('responsible_ai_adherence'),
                    idea_data.get('additional_documentation'),
                    idea_data.get('additional_documentation'),  # supporting_artefacts
                    idea_data.get('second_file_info'),
                    idea_data.get('preferred_week'),
                    idea_data.get('build_phase_preference'),
                    idea_data.get('build_preference'),
                    idea_data.get('code_development_preference'),
                    idea_data.get('submitter_email', 'unknown@example.com')
                ))
                
                idea_id = cursor.fetchone()[0]
                
                cursor.execute("COMMIT")
                
                print(f"Single idea submitted: {idea_id}")
                
                return {'idea_id': idea_id}
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
            finally:
                cursor.close()
    
    async def get_all_ideas(self) -> List[Dict]:
        """Get all ideas for admin dashboard"""
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    i.*,
                    s.submitter_id,
                    s.created_at as submission_date
                FROM ideas i
                JOIN idea_submissions s ON i.submission_id = s.id
                ORDER BY i.created_at DESC
                LIMIT 1000
            """)
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            cursor.close()
            return results
    
    async def get_user_submissions(self, user_id: str) -> List[Dict]:
        """Get user's submissions"""
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM idea_submissions 
                WHERE submitter_id = %s 
                ORDER BY created_at DESC 
                LIMIT 50
            """, (user_id,))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            cursor.close()
            return results
    
    async def delete_submission(self, submission_id: str, user_id: str) -> bool:
        """Delete a submission and all associated ideas"""
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("BEGIN")
                
                # Verify ownership
                cursor.execute(
                    "SELECT id FROM idea_submissions WHERE id = %s AND submitter_id = %s",
                    (submission_id, user_id)
                )
                
                if cursor.fetchone() is None:
                    raise ValueError('Submission not found or unauthorized')
                
                # Delete ideas
                cursor.execute("DELETE FROM ideas WHERE submission_id = %s", (submission_id,))
                
                # Delete submission
                cursor.execute("DELETE FROM idea_submissions WHERE id = %s", (submission_id,))
                
                cursor.execute("COMMIT")
                
                print(f"Deleted submission {submission_id} and all associated ideas")
                return True
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
            finally:
                cursor.close()
