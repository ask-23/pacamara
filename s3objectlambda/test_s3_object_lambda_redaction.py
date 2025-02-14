import subprocess

def validate_template(template_path):
    try:
        result = subprocess.run(['cfn-lint', template_path], check=True, capture_output=True, text=True)
        print("Template is valid.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Template validation failed.")
        print(e.stdout)
        print(e.stderr)

if __name__ == "__main__":
    validate_template('s3objectlambda/s3_object_lambda_redaction.yaml')