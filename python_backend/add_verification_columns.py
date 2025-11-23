"""
Add Verification Columns Migration
Adds verification_status, verification_results, and verification_timestamp columns
"""
import sys
from pathlib import Path
from config.database import get_db_connection

def main():
    """Run the verification columns migration"""
    print("="*60)
    print("🗄️  ADDING VERIFICATION COLUMNS")
    print("="*60)
    print("\nThis will add:")
    print("  - verification_status (VARCHAR)")
    print("  - verification_results (JSONB)")
    print("  - verification_timestamp (TIMESTAMP)")
    print("\n" + "="*60)
    
    # Read SQL file
    sql_path = Path("../migrations/20251123_add-verification-columns.sql")
    if not sql_path.exists():
        print(f"❌ ERROR: Migration file not found: {sql_path}")
        return 1
    
    sql_content = sql_path.read_text()
    
    # Execute SQL
    try:
        print("\nExecuting migration...")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql_content)
            conn.commit()
            cursor.close()
            print("✅ SUCCESS: Verification columns added")
        
        # Verify columns were added
        print("\nVerifying columns...")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_name = 'hackathon_ideas' 
                AND column_name IN ('verification_status', 'verification_results', 'verification_timestamp')
                ORDER BY column_name
            """)
            columns = cursor.fetchall()
            cursor.close()
            
            if len(columns) == 3:
                print(f"✅ All 3 columns verified:")
                for col_name, col_type in columns:
                    print(f"   - {col_name} ({col_type})")
                print("\n" + "="*60)
                print("🎉 MIGRATION COMPLETE!")
                print("="*60)
                return 0
            else:
                print(f"⚠️  WARNING: Only {len(columns)}/3 columns found")
                return 1
                
    except Exception as e:
        print(f"❌ ERROR: Migration failed")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
