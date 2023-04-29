from psycopg_pool import ConnectionPool
import os

class Db:
  def __init__(self):
    self.init_pool()
  
  def init_pool(self):
    connection_url = os.getenv("CONNECTION_URL")
    self.pool = ConnectionPool(connection_url)
  
  # we want to commit data such as an insert
  # be sure to check for RETURNING in all uppercases 
  def query_commit():
      try:  
        with self.pool.connection() as conn:
          with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()
      except (Exception, psycopg2.DatabaseError) as error:
        self.print_sql_err(error)
        #conn.rollback()

  # When we want to return a json object
  def query_array_json(self,sql,params={}):
    self.print_sql('array',sql,params)
    
    wrapped_sql = self.query_wrap_array(sql)
    with self.pool.connection() as conn:
      with conn.cursor() as cur:
        cur.execute(wrapped_sql,params)
        json = cur.fetchone()
        return json[0]

  # When we want to return an array of json objects
  def query_object_json(self,sql,params={}):
    
    self.print_sql('json',sql,params)
    self.print_params(params)
    wrapped_sql = self.query_wrap_object(sql)
    
    with self.pool.connection() as conn:
      with conn.cursor() as cur:
        cur.execute(wrapped_sql,params)
        json = cur.fetchone()
        if json == None:
          return "{}"
        else:
          return json[0]

  def query_wrap_object(template):
    sql = f"""
    (SELECT COALESCE(row_to_json(object_row),'{{}}'::json) FROM (
    {template}
    ) object_row);
    """
    return sql

  def query_wrap_array(template):
    sql = f"""
    (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
    {template}
    ) array_row);
    """
    return sql

  def print_sql_err(self,err):
    # get details about the exception
    err_type, err_obj, traceback = sys.exc_info()
   
    # get the line number when exception occured
    line_num = traceback.tb_lineno
    
    # print the connect() error
    print ("\npsycopg ERROR:", err, "on line number:", line_num)
    print ("psycopg traceback:", traceback, "-- type:", err_type)
   
    # print the pgcode and pgerror exceptions
    print ("pgerror:", err.pgerror)
    print ("pgcode:", err.pgcode, "\n")

db = Db()
