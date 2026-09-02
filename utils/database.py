import psycopg2 # just like mysql-connector

class DatabaseUtil:

    def __init__(self, db_config):
        self.db_config = db_config
        try:
            self.connection = psycopg2.connect(**db_config)
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            self.connection = None

    def schema_details(self, schema_name): # find the context from the database

        try:
            schema_info_context = "" #isme dheere dheere table ki details (t_name, all col names ,dummy data) add hota jayega
            connection = self.connection 
            cursor = connection.cursor()

            schema_info_context = f"Database Schema: {schema_name} \n"
            cursor.execute("SELECT table_name from information_schema.tables where table_schema = %s;",(schema_name,)) 
            #information schema ek default master table hai that stores all table names

            table_list = cursor.fetchall()

            for table in table_list: 
                table_name = table[0]

                schema_info_context = f"{schema_info_context} \n Table: {table_name}\n"

            # Adding columns and datatypes
                cursor.execute("SELECT column_name,data_type from information_schema.columns where table_name = %s;",(table_name,)) 
                column_list = cursor.fetchall()

                for column in column_list:
                    column_name = column[0]
                    data_type = column[1]
                    schema_info_context = f"{schema_info_context} Column: {column_name}, Data Type: {data_type}\n"

                # Adding sampling data
                cursor.execute(f"SELECT * FROM {schema_name}.{table_name} LIMIT 5;")
                sample_data = cursor.fetchall()

                schema_info_context = f"{schema_info_context} Sample data: \n"
                for row in sample_data:
                    schema_info_context = f"{schema_info_context}  {row} \n"
        except Exception as e:
             print(f"Error fetching schema details: {e}")
             schema_info_context = f"Error fetching schema details: {e}"

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return schema_info_context

obj = DatabaseUtil({
    "host": "localhost",
    "port": 5432,
    "user": "yashgupta",
    "password": "root",
    "dbname": "postgres"
})

result = obj.schema_details("public")

with open("test_schema_details.txt", "w") as f:
    f.write(result)

