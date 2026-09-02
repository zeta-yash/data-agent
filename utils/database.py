import psycopg2 # just like mysql-connector

class DatabaseUtil:

    def __init__(self, db_config):
            self.db_config = db_conifg
        try:
            self.connection = psycopg2.connect(**db_config)
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            self.connection = None

    def schema_details(self, schema_name): # find the context from the database

        schema_info_context = "" #isme dheere dheere table ki details (t_name, all col names ,dummy data) add hota jayega
        connection = self.connection 
        cursor = connection.cursor()

        schema_info_context = f"Database Schema: {schema_name} \n"
        cursor.execute("SELECT table_name from information_schema.tables where table_schema = %s;",(schema_name)) 
        #information schema ek default master table hai that stores all table names



