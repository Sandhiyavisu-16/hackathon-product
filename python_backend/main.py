"""
Main FastAPI Application
Innovation Idea Submission Platform - Python Backend
"""
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager
from typing import Optional, List
import uvicorn

from config.settings import get_settings
from config.database import init_pool, close_pool, test_connection
from config.redis_client import get_redis_client, close_redis_client
from services.submission_service import SubmissionService
from models.types import Permission, ActivateConfigRequest

settings = get_settings()


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting application...")
    
    # Initialize database
    init_pool()
    test_connection()
    
    # Initialize Redis (with timeout)
    try:
        await get_redis_client()
    except Exception as e:
        print(f"Redis connection failed (non-critical): {e}")
    
    yield
    
    # Shutdown
    print("Shutting down application...")
    close_pool()
    await close_redis_client()


# Create FastAPI app
app = FastAPI(
    title="Innovation Idea Submission Platform",
    description="Backend API for idea submission and evaluation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.node_env == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import for static files
import os
from pathlib import Path

# Get the public directory path
public_dir = Path(__file__).parent.parent / "public"

if not public_dir.exists():
    print(f"Warning: Public directory not found at {public_dir}")


# Mock authentication (replace with real JWT auth)
async def get_current_user(request: Request):
    """Mock user authentication - replace with real JWT validation"""
    return {
        'user_id': 1,  # Integer user ID
        'email': 'admin@example.com',
        'role': 'admin',
        'permissions': [p.value for p in Permission]
    }


# Health check endpoint removed - was causing too many logs


# ============================================================================
# IDEA SUBMISSION ROUTES
# ============================================================================

submission_service = SubmissionService()


@app.get("/api/ideas/template")
async def download_template(user=Depends(get_current_user)):
    """Download CSV template"""
    template = 'Idea Id,Your idea title,Brief summary of your Idea,Challenge/Business opportunity being addressed and the ability to scale it across TCS and multiple customers.,Novelty of the idea benefits and risks.,Highlight adherence to Responsible AI principles such as Security Fairness Privacy & Legal compliance.,Additional Documentation – Any additional information or prototype explaining technical approach architecture development timeline success metrics and expected outcomes and scalability potential. You can also share any research done on business model competitive analysis risk & mitigations. Sharing relevant artefacts will boost your scores.,Incase you have a second file that could further illustrate your solution kindly upload the same here.,Your preferred week of participation,Your preference for Build Phase,Your preference on how you want to  build your idea,Your preference if you were to develop code\n'
    
    return PlainTextResponse(
        content=template,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ideas_template.csv"}
    )


@app.post("/api/ideas/single")
async def submit_single_idea(
    request: Request,
    title: str = Form(...),
    brief_summary: str = Form(...),
    challenge_opportunity: Optional[str] = Form(None),
    novelty_benefits_risks: Optional[str] = Form(None),
    responsible_ai_adherence: Optional[str] = Form(None),
    additional_documentation: Optional[UploadFile] = File(None),
    supporting_artefacts: Optional[UploadFile] = File(None),
    second_file_upload: Optional[UploadFile] = File(None),
    preferred_week: Optional[str] = Form(None),
    build_phase_preference: Optional[str] = Form(None),
    build_method_preference: Optional[str] = Form(None),
    code_development_preference: Optional[str] = Form(None),
    user=Depends(get_current_user)
):
    """Submit a single idea via form"""
    try:
        # Store file names if files are uploaded
        additional_doc_name = additional_documentation.filename if additional_documentation else None
        supporting_art_name = supporting_artefacts.filename if supporting_artefacts else None
        second_file_name = second_file_upload.filename if second_file_upload else None
        
        idea_data = {
            'title': title,
            'brief_summary': brief_summary,
            'challenge_opportunity': challenge_opportunity,
            'novelty_benefits_risks': novelty_benefits_risks,
            'responsible_ai_adherence': responsible_ai_adherence,
            'additional_documentation': additional_doc_name,
            'supporting_artefacts': supporting_art_name,
            'second_file_info': second_file_name,
            'preferred_week': preferred_week,
            'build_phase_preference': build_phase_preference,
            'build_method_preference': build_method_preference,
            'code_development_preference': code_development_preference,
        }
        
        # TODO: Save the actual files to storage (S3, local filesystem, etc.)
        # For now, we just store the filenames in the database
        
        result = await submission_service.submit_single_idea(
            user['user_id'],
            idea_data,
            request.client.host
        )
        
        return {
            'success': True,
            'idea_id': result['idea_id'],
            'message': 'Idea submitted successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ideas/all")
async def get_all_ideas(user=Depends(get_current_user)):
    """Get all ideas for admin dashboard"""
    try:
        ideas = await submission_service.get_all_ideas()
        return {'ideas': ideas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ideas/uploads/url")
async def get_presigned_urls(
    types: List[str],
    user=Depends(get_current_user)
):
    """Get presigned URLs for file uploads (mock)"""
    from datetime import datetime
    
    urls = {}
    for file_type in types:
        urls[file_type] = f"https://storage.example.com/upload/{file_type}/{int(datetime.now().timestamp())}"
    
    return {
        'urls': urls,
        'expires_in': 900
    }


@app.post("/api/ideas/submit")
async def submit_ideas(
    request: Request,
    csv: UploadFile = File(...),
    supportFile: Optional[UploadFile] = File(None),
    user=Depends(get_current_user)
):
    """Submit ideas with file upload"""
    try:
        # Read file buffer
        file_buffer = await csv.read()
        
        # Get file extension
        file_type = csv.filename.split('.')[-1].lower() if csv.filename else None
        
        # Read support file if provided
        support_file_buffer = None
        support_file_type = None
        if supportFile:
            support_file_buffer = await supportFile.read()
            support_file_type = supportFile.filename.split('.')[-1].lower() if supportFile.filename else None
            
            # Validate support file size (100MB limit)
            file_size = len(support_file_buffer)
            max_size = settings.max_doc_size  # 100MB for documents
            
            # Check if it's a video file (mp4)
            if support_file_type == 'mp4':
                max_size = settings.max_mp4_size  # 100MB for videos
            
            if file_size > max_size:
                max_size_mb = max_size / (1024 * 1024)
                actual_size_mb = file_size / (1024 * 1024)
                raise HTTPException(
                    status_code=400, 
                    detail=f'Support file is too large ({actual_size_mb:.1f}MB). Maximum allowed size is {max_size_mb:.0f}MB'
                )
        
        # Process submission
        result = await submission_service.process_submission_from_buffer(
            file_buffer=file_buffer,
            submitter_id=user['user_id'],
            source_ip=request.client.host,
            support_file_buffer=support_file_buffer,
            support_file_type=support_file_type,
            file_type=file_type
        )
        
        return {
            'success': True,
            'submission_id': result['submission_id'],
            'status': result['status'],
            'total_rows': result['total_rows'],
            'valid_rows': result['valid_rows'],
            'invalid_rows': result['invalid_rows'],
            'message': 'Submission processed successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ideas/submissions")
async def get_user_submissions(user=Depends(get_current_user)):
    """Get user's submissions"""
    try:
        submissions = await submission_service.get_user_submissions(user['user_id'])
        return {'submissions': submissions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/ideas/{submission_id}")
async def delete_submission(
    submission_id: str,
    user=Depends(get_current_user)
):
    """Delete a submission"""
    try:
        await submission_service.delete_submission(submission_id, user['user_id'])
        return {
            'success': True,
            'message': 'Submission and all associated ideas deleted successfully'
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MODEL CONFIG & LLM ROUTES
# ============================================================================

from services.llm_service import llm_service
from pydantic import BaseModel


class TestModelRequest(BaseModel):
    provider: str
    model_name: str
    api_key: str
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    azure_endpoint: Optional[str] = None
    prompt: Optional[str] = "Hello, this is a test message. Please respond with 'Test successful'."


class ChatCompletionRequest(BaseModel):
    provider: str
    model_name: str
    messages: List[dict]
    api_key: str
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    azure_endpoint: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000


class ScoreIdeaRequest(BaseModel):
    provider: str
    model_name: str
    api_key: str
    idea_title: str
    idea_summary: str
    rubric_criteria: List[dict]
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    azure_endpoint: Optional[str] = None


@app.post("/api/llm/test")
async def test_llm_model(
    request: TestModelRequest,
    user=Depends(get_current_user)
):
    """Test an LLM model configuration using LiteLLM"""
    # Build settings dict
    settings = {
        'api_key': request.api_key,
        'api_base': request.api_base,
        'api_version': request.api_version
    }
    
    result = await llm_service.test_model(
        provider=request.provider,
        model_name=request.model_name,
        settings=settings,
        prompt=request.prompt
    )
    return result


@app.post("/api/llm/chat")
async def chat_completion(
    request: ChatCompletionRequest,
    user=Depends(get_current_user)
):
    """Send a chat completion request using LiteLLM"""
    # Build settings dict
    settings = {
        'api_key': request.api_key,
        'api_base': request.api_base,
        'api_version': request.api_version
    }
    
    result = await llm_service.chat_completion(
        provider=request.provider,
        model_name=request.model_name,
        messages=request.messages,
        settings=settings,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )
    return result


@app.post("/api/llm/score-idea")
async def score_idea(
    request: ScoreIdeaRequest,
    user=Depends(get_current_user)
):
    """Score an idea using LLM"""
    result = await llm_service.score_idea(
        provider=request.provider,
        model_name=request.model_name,
        api_key=request.api_key,
        idea_title=request.idea_title,
        idea_summary=request.idea_summary,
        rubric_criteria=request.rubric_criteria,
        api_base=request.api_base,
        api_version=request.api_version,
        azure_endpoint=request.azure_endpoint
    )
    return result


from services.model_config_service import model_config_service


class CreateConfigRequest(BaseModel):
    provider: str
    name: str
    settings: dict
    notes: Optional[str] = None


class UpdateConfigRequest(BaseModel):
    name: Optional[str] = None
    settings: Optional[dict] = None
    notes: Optional[str] = None


@app.get("/api/config/model")
async def get_model_config(user=Depends(get_current_user)):
    """Get active model configuration and history"""
    try:
        active = await model_config_service.get_active_config()
        history = await model_config_service.get_config_history(10)
        
        return {
            'active': active,
            'history': history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config/model")
async def create_model_config(
    request: CreateConfigRequest,
    user=Depends(get_current_user)
):
    """Create model configuration"""
    try:
        config = await model_config_service.create_config(
            provider=request.provider,
            name=request.name,
            settings=request.settings,
            created_by=user['user_id'],
            notes=request.notes
        )
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config/model/{config_id}")
async def get_config_detail(
    config_id: str,
    user=Depends(get_current_user)
):
    """Get configuration detail"""
    try:
        config = await model_config_service.get_config_by_id(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        return config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config/model/{config_id}/test")
async def test_config(
    config_id: str,
    user=Depends(get_current_user)
):
    """Test configuration"""
    try:
        print(f"Testing configuration: {config_id}")
        result = await model_config_service.test_connection(config_id)
        print(f"Test result: {result}")
        return result
    except ValueError as e:
        print(f"ValueError in test_config: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Exception in test_config: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config/model/{config_id}/activate")
async def activate_config(
    config_id: str,
    request: ActivateConfigRequest,
    user=Depends(get_current_user)
):
    """Activate configuration for a specific purpose"""
    try:
        print(f"Activating configuration: {config_id} for purpose: {request.purpose}")
        config = await model_config_service.activate_config(config_id, request.purpose.value)
        print(f"Configuration activated successfully: {config['id']} for {request.purpose}")
        return config
    except ValueError as e:
        print(f"ValueError in activate_config: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Exception in activate_config: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config/model/{config_id}/deactivate")
async def deactivate_config(
    config_id: str,
    user=Depends(get_current_user)
):
    """Deactivate configuration"""
    try:
        print(f"Deactivating configuration: {config_id}")
        config = await model_config_service.deactivate_config(config_id)
        print(f"Configuration deactivated successfully: {config['id']}")
        return config
    except ValueError as e:
        print(f"ValueError in deactivate_config: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Exception in deactivate_config: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/config/model/{config_id}")
async def update_config(
    config_id: str,
    request: UpdateConfigRequest,
    user=Depends(get_current_user)
):
    """Update configuration"""
    try:
        config = await model_config_service.update_config(
            config_id=config_id,
            name=request.name,
            settings=request.settings,
            notes=request.notes
        )
        return config
    except ValueError as e:
        if 'not found' in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/config/model/{config_id}")
async def delete_config(
    config_id: str,
    user=Depends(get_current_user)
):
    """Delete configuration"""
    try:
        await model_config_service.delete_config(config_id)
        return {'success': True, 'message': 'Configuration deleted successfully'}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config/model/{config_id}/rollback")
async def rollback_config(
    config_id: str,
    user=Depends(get_current_user)
):
    """Rollback to a previous configuration"""
    try:
        config = await model_config_service.get_config_by_id(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        if config['status'] != 'inactive':
            raise HTTPException(status_code=400, detail="Can only rollback to inactive configurations")
        
        activated_config = await model_config_service.activate_config(config_id)
        return activated_config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RUBRIC ROUTES (Placeholder - implement RubricService)
# ============================================================================

@app.get("/api/rubrics")
async def get_rubrics(user=Depends(get_current_user)):
    """Get all rubrics"""
    try:
        from config.database import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM rubrics
                WHERE is_active = true
                ORDER BY display_order ASC, created_at DESC
            """)
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            
            rubrics = []
            for row in rows:
                rubric = dict(zip(columns, row))
                # Convert datetime to ISO string
                if rubric.get('created_at'):
                    rubric['created_at'] = rubric['created_at'].isoformat()
                if rubric.get('updated_at'):
                    rubric['updated_at'] = rubric['updated_at'].isoformat()
                rubrics.append(rubric)
            
            return {'rubrics': rubrics}
    except Exception as e:
        print(f"Error fetching rubrics: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


class CreateRubricRequest(BaseModel):
    name: str
    description: str
    guidance: str
    weight: int


@app.post("/api/rubrics")
async def create_rubric(
    request: CreateRubricRequest,
    user=Depends(get_current_user)
):
    """Create a custom rubric"""
    try:
        from config.database import get_db_connection
        
        # Validate weight
        if request.weight < 0 or request.weight > 100:
            raise HTTPException(status_code=400, detail="Weight must be between 0 and 100")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Insert new rubric
            cursor.execute("""
                INSERT INTO rubrics (name, description, guidance, weight, is_default, is_active, display_order, created_by)
                VALUES (%s, %s, %s, %s, false, true, 999, %s)
                RETURNING id, name, description, guidance, weight, is_default, is_active, display_order, created_at
            """, (request.name, request.description, request.guidance, request.weight, user['user_id']))
            
            row = cursor.fetchone()
            columns = [desc[0] for desc in cursor.description]
            conn.commit()
            cursor.close()
            
            rubric = dict(zip(columns, row))
            if rubric.get('created_at'):
                rubric['created_at'] = rubric['created_at'].isoformat()
            
            return rubric
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating rubric: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


class UpdateRubricRequest(BaseModel):
    weight: Optional[int] = None
    is_active: Optional[bool] = None


@app.patch("/api/rubrics/{rubric_id}")
async def update_rubric(
    rubric_id: int,
    request: UpdateRubricRequest,
    user=Depends(get_current_user)
):
    """Update rubric weight or active status"""
    try:
        from config.database import get_db_connection
        
        weight = request.weight
        is_active = request.is_active
        
        if weight is not None and (weight < 0 or weight > 100):
            raise HTTPException(status_code=400, detail="Weight must be between 0 and 100")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically
            updates = []
            params = []
            
            if weight is not None:
                updates.append("weight = %s")
                params.append(weight)
            
            if is_active is not None:
                updates.append("is_active = %s")
                params.append(is_active)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(rubric_id)
            
            query = f"UPDATE rubrics SET {', '.join(updates)} WHERE id = %s RETURNING *"
            cursor.execute(query, params)
            
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Rubric not found")
            
            columns = [desc[0] for desc in cursor.description]
            conn.commit()
            cursor.close()
            
            rubric = dict(zip(columns, row))
            if rubric.get('created_at'):
                rubric['created_at'] = rubric['created_at'].isoformat()
            if rubric.get('updated_at'):
                rubric['updated_at'] = rubric['updated_at'].isoformat()
            
            return rubric
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating rubric: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/rubrics/{rubric_id}")
async def delete_rubric(
    rubric_id: int,
    user=Depends(get_current_user)
):
    """Delete a custom rubric"""
    try:
        from config.database import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if rubric exists and is not a default rubric
            cursor.execute("""
                SELECT id, name, is_default FROM rubrics WHERE id = %s
            """, (rubric_id,))
            
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Rubric not found")
            
            rubric_id_db, rubric_name, is_default = row
            
            if is_default:
                raise HTTPException(status_code=400, detail="Cannot delete default rubrics")
            
            # Delete the rubric
            cursor.execute("""
                DELETE FROM rubrics WHERE id = %s
            """, (rubric_id,))
            
            conn.commit()
            cursor.close()
            
            return {
                'success': True,
                'message': f'Rubric "{rubric_name}" deleted successfully'
            }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting rubric: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EVALUATION PIPELINE ROUTES
# ============================================================================

from services.evaluation_service import evaluation_service


@app.post("/api/evaluation/start")
async def start_evaluation_pipeline(user=Depends(get_current_user)):
    """Start the evaluation pipeline for pending ideas"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = await evaluation_service.start_pipeline()
        return result
    except Exception as e:
        print(f"Error starting evaluation pipeline: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/evaluation/status")
async def get_evaluation_status(user=Depends(get_current_user)):
    """Get current pipeline status and progress"""
    try:
        return await evaluation_service.get_status()
    except Exception as e:
        print(f"Error getting evaluation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ideas/{idea_id}/scores")
async def get_idea_scores(idea_id: int, user=Depends(get_current_user)):
    """Get evaluation scores and results for a specific idea"""
    try:
        result = await evaluation_service.get_idea_scores(idea_id)
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting idea scores: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Mount static files at the end (after all API routes)
# This serves files like app.js, index.html, etc. directly
if public_dir.exists():
    app.mount("/", StaticFiles(directory=str(public_dir), html=True), name="public")
    print(f"Static files mounted from: {public_dir}")


# Run the application
if __name__ == "__main__":
    from datetime import datetime
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.node_env == "development"
    )
