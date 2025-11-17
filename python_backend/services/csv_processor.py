"""
CSV Processing Service
"""
from typing import Dict, List, Any
from models.types import ErrorCode


class RowError:
    def __init__(self, row_number: int, field: str, error_code: ErrorCode, message: str):
        self.row_number = row_number
        self.field = field
        self.error_code = error_code
        self.message = message


class ProcessingResult:
    def __init__(self, valid_rows: List[Dict], invalid_rows: List[RowError], total_rows: int):
        self.valid_rows = valid_rows
        self.invalid_rows = invalid_rows
        self.total_rows = total_rows


class CSVProcessor:
    REQUIRED_HEADERS = [
        'your idea title',
        'brief summary of your idea',
    ]
    
    def validate_headers(self, headers: List[str]) -> Dict[str, Any]:
        """Validate CSV headers"""
        normalized_headers = [h.lower().strip() for h in headers]
        missing = [h for h in self.REQUIRED_HEADERS if h not in normalized_headers]
        
        return {
            'valid': len(missing) == 0,
            'missing': missing
        }
    
    async def process_rows(self, rows: List[Dict]) -> ProcessingResult:
        """Process and validate CSV rows"""
        valid_rows = []
        invalid_rows = []
        
        for i, row in enumerate(rows):
            row_number = i + 2  # +2 for header row and 1-based indexing
            errors = self.validate_row(row, row_number)
            
            if len(errors) == 0:
                valid_rows.append(row)
            else:
                invalid_rows.extend(errors)
        
        return ProcessingResult(
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            total_rows=len(rows)
        )
    
    def validate_row(self, row: Dict, row_number: int) -> List[RowError]:
        """Validate a single row"""
        errors = []
        
        # Title validation
        title = row.get('your idea title', '').strip()
        if not title:
            errors.append(RowError(
                row_number=row_number,
                field='your idea title',
                error_code=ErrorCode.ROW_MISSING_REQUIRED_FIELD,
                message='Idea title is required'
            ))
        elif len(title) < 5 or len(title) > 500:
            errors.append(RowError(
                row_number=row_number,
                field='your idea title',
                error_code=ErrorCode.ROW_TITLE_LENGTH,
                message='Title must be between 5 and 500 characters'
            ))
        
        # Brief summary validation
        summary = row.get('brief summary of your idea', '').strip()
        if not summary:
            errors.append(RowError(
                row_number=row_number,
                field='brief summary of your idea',
                error_code=ErrorCode.ROW_MISSING_REQUIRED_FIELD,
                message='Brief summary is required'
            ))
        elif len(summary) < 10:
            errors.append(RowError(
                row_number=row_number,
                field='brief summary of your idea',
                error_code=ErrorCode.ROW_LOGLINE_LENGTH,
                message='Brief summary must be at least 10 characters'
            ))
        
        return errors
    
    def generate_error_report(self, errors: List[RowError]) -> str:
        """Generate CSV error report"""
        header = 'row_number,field,error_code,message\n'
        rows = '\n'.join([
            f'{e.row_number},{e.field},{e.error_code.value},"{e.message}"'
            for e in errors[:50]  # First 50 errors
        ])
        
        return header + rows
