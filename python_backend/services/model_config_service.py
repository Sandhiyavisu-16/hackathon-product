"""
Model Configuration Service
Manages LLM provider configurations
"""
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

from config.database import get_db_connection
from config.redis_client import get_redis_client
from services.llm_service import llm_service
from models.types import Provider, ConfigStatus


class ModelConfigService:
    CACHE_KEY = "active_model_config"
    CACHE_TTL = 300  # 5 minutes
    
    async def create_config(
        self,
        provider: str,
        name: str,
        settings: Dict[str, Any],
        created_by: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new model configuration"""
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO model_provider_configs (provider, name, settings, status, notes, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                provider,
                name,
                json.dumps(settings),
                'draft',
                notes,
                created_by
            ))
            
            row = cursor.fetchone()
            conn.commit()
            cursor.close()
            
            return self._map_row_to_config(row, cursor.description)
    
    async def get_active_config(self) -> Optional[Dict[str, Any]]:
        """Get the currently active configuration"""
        
        # Try cache first
        try:
            redis = await get_redis_client()
            cached = await redis.get(self.CACHE_KEY)
            if cached:
                return json.loads(cached)
        except:
            pass  # Redis not available, continue to database
        
        # Query database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM model_provider_configs
                WHERE is_active = true
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            description = cursor.description
            cursor.close()
            
            if not row:
                return None
            
            config = self._map_row_to_config(row, description)
            
            # Cache the result
            try:
                redis = await get_redis_client()
                await redis.setex(self.CACHE_KEY, self.CACHE_TTL, json.dumps(config, default=str))
            except:
                pass  # Redis not available
            
            return config
    
    async def get_config_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get configuration history"""
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM model_provider_configs
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
            
            rows = cursor.fetchall()
            description = cursor.description
            cursor.close()
            
            return [self._map_row_to_config(row, description) for row in rows]
    
    async def get_config_by_id(self, config_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration by ID"""
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM model_provider_configs
                WHERE id = %s
            """, (config_id,))
            
            row = cursor.fetchone()
            description = cursor.description
            cursor.close()
            
            if not row:
                return None
            
            return self._map_row_to_config(row, description)
    
    async def update_config_status(self, config_id: str, status: str) -> Dict[str, Any]:
        """Update configuration status"""
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE model_provider_configs
                SET status = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING *
            """, (status, config_id))
            
            row = cursor.fetchone()
            description = cursor.description
            conn.commit()
            cursor.close()
            
            if not row:
                raise ValueError('Configuration not found')
            
            print(f"Updated config {config_id} status to: {status}")
            
            return self._map_row_to_config(row, description)
    
    async def activate_config(self, config_id: str, purpose: str) -> Dict[str, Any]:
        """Activate a configuration for a specific purpose"""
        
        if purpose not in ['evaluation', 'verification']:
            raise ValueError('Purpose must be either "evaluation" or "verification"')
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("BEGIN")
                
                # First check if the config exists and its current status
                cursor.execute("""
                    SELECT id, name, status, is_active, purpose
                    FROM model_provider_configs
                    WHERE id = %s
                """, (config_id,))
                
                check_row = cursor.fetchone()
                if not check_row:
                    raise ValueError(f'Configuration {config_id} not found')
                
                config_name, config_status, config_is_active, config_purpose = check_row[1], check_row[2], check_row[3], check_row[4]
                print(f"Config to activate: {config_name}, status={config_status}, is_active={config_is_active}, purpose={config_purpose}")
                
                if config_status not in ['tested', 'inactive']:
                    raise ValueError(f'Configuration must be in "tested" or "inactive" state to activate (current: {config_status})')
                
                # Deactivate current active config for this purpose
                cursor.execute("""
                    UPDATE model_provider_configs
                    SET is_active = false, status = 'inactive', updated_at = NOW()
                    WHERE is_active = true AND purpose = %s
                """, (purpose,))
                
                deactivated_count = cursor.rowcount
                print(f"Deactivated {deactivated_count} config(s) for purpose: {purpose}")
                
                # Activate new config with purpose
                cursor.execute("""
                    UPDATE model_provider_configs
                    SET is_active = true, status = 'active', purpose = %s, updated_at = NOW()
                    WHERE id = %s
                    RETURNING *
                """, (purpose, config_id))
                
                row = cursor.fetchone()
                
                if not row:
                    raise ValueError('Failed to activate configuration')
                
                # Capture description before commit
                description = cursor.description
                
                cursor.execute("COMMIT")
                print(f"Successfully activated config {config_id} for purpose: {purpose}")
                
                # Invalidate cache
                try:
                    redis = await get_redis_client()
                    await redis.delete(self.CACHE_KEY)
                except:
                    pass
                
                config = self._map_row_to_config(row, description)
                cursor.close()
                
                return config
                
            except Exception as e:
                print(f"Error in activate_config: {e}")
                cursor.execute("ROLLBACK")
                cursor.close()
                raise e
    
    async def deactivate_config(self, config_id: str) -> Dict[str, Any]:
        """Deactivate a configuration"""
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("BEGIN")
                
                # Deactivate the config
                cursor.execute("""
                    UPDATE model_provider_configs
                    SET is_active = false, status = 'tested', updated_at = NOW()
                    WHERE id = %s AND is_active = true
                    RETURNING *
                """, (config_id,))
                
                row = cursor.fetchone()
                
                if not row:
                    raise ValueError('Configuration not found or not currently active')
                
                # Capture description before commit
                description = cursor.description
                
                cursor.execute("COMMIT")
                
                # Invalidate cache
                try:
                    redis = await get_redis_client()
                    await redis.delete(self.CACHE_KEY)
                except:
                    pass
                
                config = self._map_row_to_config(row, description)
                cursor.close()
                
                return config
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                cursor.close()
                raise e
    
    async def test_connection(self, config_id: str) -> Dict[str, Any]:
        """Test a configuration"""
        
        print(f"ModelConfigService.test_connection called with config_id: {config_id}")
        
        config = await self.get_config_by_id(config_id)
        
        print(f"Retrieved config: {config}")
        
        if not config:
            raise ValueError(f'Configuration not found for id: {config_id}')
        
        # Extract model name
        model_name = config['settings'].get('model_name') or config['settings'].get('deployment_name') or config['settings'].get('model', '')
        
        # Extract Azure endpoint (try multiple field names)
        azure_endpoint = (
            config['settings'].get('azure_endpoint') or 
            config['settings'].get('endpoint') or 
            config['settings'].get('azure_endpoint_url') or
            config['settings'].get('api_base')  # Fallback to api_base for Azure
        )
        
        print(f"Testing with provider: {config['provider']}, model: {model_name}")
        print(f"Settings: {config['settings']}")
        
        # Test using LLM service (now using LiteLLM)
        result = await llm_service.test_model(
            provider=config['provider'],
            model_name=model_name,
            settings=config['settings']
        )
        
        print(f"LLM test result: {result}")
        
        # Update status if successful
        if result['success']:
            await self.update_config_status(config_id, 'tested')
        
        return result
    
    async def update_config(
        self,
        config_id: str,
        name: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a configuration"""
        
        config = await self.get_config_by_id(config_id)
        
        if not config:
            raise ValueError('Configuration not found')
        
        if config['is_active']:
            raise ValueError('Cannot update active configuration. Deactivate it first or create a new version.')
        
        # Build update query
        updates = []
        values = []
        
        if name is not None:
            updates.append("name = %s")
            values.append(name)
        
        if settings is not None:
            # Merge with existing settings
            merged_settings = {**config['settings'], **settings}
            updates.append("settings = %s")
            values.append(json.dumps(merged_settings))
            # Reset status to draft if settings changed
            updates.append("status = %s")
            values.append('draft')
        
        if notes is not None:
            updates.append("notes = %s")
            values.append(notes)
        
        if not updates:
            return config  # No changes
        
        updates.append("updated_at = NOW()")
        values.append(config_id)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = f"""
                UPDATE model_provider_configs
                SET {', '.join(updates)}
                WHERE id = %s
                RETURNING *
            """
            
            cursor.execute(query, values)
            row = cursor.fetchone()
            conn.commit()
            cursor.close()
            
            if not row:
                raise ValueError('Configuration not found')
            
            return self._map_row_to_config(row, cursor.description)
    
    async def delete_config(self, config_id: str) -> bool:
        """Delete a configuration"""
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM model_provider_configs
                WHERE id = %s AND is_active = false
            """, (config_id,))
            
            deleted = cursor.rowcount > 0
            conn.commit()
            cursor.close()
            
            if not deleted:
                raise ValueError('Configuration not found or is currently active')
            
            return True
    
    def _map_row_to_config(self, row: tuple, description) -> Dict[str, Any]:
        """Map database row to config dict"""
        columns = [desc[0] for desc in description]
        config = dict(zip(columns, row))
        
        # Parse JSON settings if it's a string
        if isinstance(config.get('settings'), str):
            config['settings'] = json.loads(config['settings'])
        
        # Convert datetime to ISO string
        if config.get('created_at'):
            config['created_at'] = config['created_at'].isoformat()
        if config.get('updated_at'):
            config['updated_at'] = config['updated_at'].isoformat()
        
        return config


# Global instance
model_config_service = ModelConfigService()
