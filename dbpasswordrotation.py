import pymysql.cursors
import json 
import sys
import random
import string
import os
import boto3
from botocore.exceptions import ClientError

def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    print("Random alphanumeric String is IN THE FUNCTION:", result_str)
    return result_str

def lambda_handler(event, context):
  
  new_password = get_random_alphanumeric_string(24)
  secret_name = "prod/admin"
  region_name = "us-east-1"
  host = os.environ.get('hostname')
  user = os.environ.get('user')
  password = os.environ.get('pass')
  db = 'test_lambda'
  session = boto3.session.Session()
  client = session.client(service_name='secretsmanager',region_name=region_name,)
  
  get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
  
  # Connect to the database
  connection = pymysql.connect(host=host,
                               user=user,
                               password=password,
                               db=db,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
  
  try:
      with connection.cursor() as cursor:
          
          # Update the password
          cursor.execute("SET PASSWORD FOR test_lambda@'%' = '{}'".format(new_password))
          connection.commit()
  finally:
      connection.close()

  # Update the AWS Secrets with new password
  
  try:
      put_secret_value_response = client.put_secret_value(SecretId='prod/admin',SecretString=new_password)
      
  except ClientError as e:
      if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
      elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
      elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e) 