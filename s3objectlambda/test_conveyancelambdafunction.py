import unittest
from unittest.mock import patch, MagicMock
from conveyancelambdafunction import redact_ssn, lambda_handler

class TestRedactSSN(unittest.TestCase):
    def test_redact_ssn(self):
        self.assertEqual(redact_ssn("My SSN is 123-45-6789"), "My SSN is ***-**-****")
        self.assertEqual(redact_ssn("No SSN here!"), "No SSN here!")
        self.assertEqual(redact_ssn("Multiple SSNs: 123-45-6789 and 987-65-4321"),
                         "Multiple SSNs: ***-**-**** and ***-**-****")

class TestLambdaHandler(unittest.TestCase):
    @patch('conveyancelambdafunction.boto3.client')
    @patch('conveyancelambdafunction.logger')
    @patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_SESSION_TOKEN': 'testing'
    })
    def test_lambda_handler(self, mock_boto_client, mock_logger):
        mock_s3_client_instance = MagicMock()
        mock_boto_client.return_value = mock_s3_client_instance

        mock_s3_client_instance.get_object.return_value = {
            'Body': MagicMock(read=MagicMock(return_value=b'My SSN is 123-45-6789'))
        }

        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'test-bucket'},
                    'object': {'key': 'test-key'}
                }
            }]
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertIn('SSNs redacted successfully', response['body'])
        mock_s3_client_instance.get_object.assert_called_once_with(Bucket='test-bucket', Key='test-key')

if __name__ == '__main__':
    unittest.main()