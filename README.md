# huffnpuff
Huffman encoder from (I think) a coding challenges newsletter. 
* Features: TDD, docstrings++, comments.
* Missing: any real-world application unlike tarfile, or compelling story like PKZIP

# s3objectlambda
AWS Object Lambda for Privacy Protection. 
* Features: Edge processing to redact sensitive data before serving it to applications.
In this example, SSNs are redacted for departments that don't need them. This can be extended to
redact any sensitive information from your data objects before serving them.
* Missing: additional test coverage, slimmed down execution role in the SAM file