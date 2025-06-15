from django.core.management.base import BaseCommand
from django.db import connection
from django_tenants.utils import schema_context

class Command(BaseCommand):
    help = 'Check the schema of the chat_channelparticipant table'

    def handle(self, *args, **options):
        with schema_context('turtlesoftware'):
            with connection.cursor() as cursor:
                # Get column information
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = 'chat_channelparticipant'
                    ORDER BY ordinal_position
                """)
                
                self.stdout.write(self.style.SUCCESS('Columns in chat_channelparticipant:'))
                columns = cursor.fetchall()
                for col in columns:
                    self.stdout.write(f"- {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'} {f'DEFAULT {col[3]}' if col[3] else ''}")
                
                # Check for indexes and constraints
                cursor.execute("""
                    SELECT 
                        t.relname as table_name,
                        i.relname as index_name,
                        a.attname as column_name,
                        ix.indisunique as is_unique,
                        ix.indisprimary as is_primary,
                        pg_get_indexdef(ix.indexrelid) as definition
                    FROM 
                        pg_class t,
                        pg_class i,
                        pg_index ix,
                        pg_attribute a
                    WHERE 
                        t.oid = ix.indrelid
                        AND i.oid = ix.indexrelid
                        AND a.attrelid = t.oid
                        AND a.attnum = ANY(ix.indkey)
                        AND t.relkind = 'r'
                        AND t.relname = 'chat_channelparticipant'
                    ORDER BY 
                        t.relname,
                        i.relname
                """)
                
                self.stdout.write(self.style.SUCCESS('\nIndexes on chat_channelparticipant:'))
                indexes = cursor.fetchall()
                if indexes:
                    for idx in indexes:
                        self.stdout.write(f"- {idx[1]}: {idx[5]}")
                else:
                    self.stdout.write("No indexes found")
                
                # Check for foreign key constraints
                cursor.execute("""
                    SELECT 
                        tc.constraint_name,
                        tc.table_name,
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM 
                        information_schema.table_constraints AS tc 
                        JOIN information_schema.key_column_usage AS kcu
                            ON tc.constraint_name = kcu.constraint_name
                            AND tc.table_schema = kcu.table_schema
                        JOIN information_schema.constraint_column_usage AS ccu
                            ON ccu.constraint_name = tc.constraint_name
                            AND ccu.table_schema = tc.table_schema
                    WHERE 
                        tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_name = 'chat_channelparticipant'
                """)
                
                self.stdout.write(self.style.SUCCESS('\nForeign key constraints:'))
                fks = cursor.fetchall()
                if fks:
                    for fk in fks:
                        self.stdout.write(f"- {fk[0]}: {fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]}")
                else:
                    self.stdout.write("No foreign key constraints found")
