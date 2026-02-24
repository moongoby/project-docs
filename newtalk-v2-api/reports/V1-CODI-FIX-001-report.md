# V1 코디등록 오류 조사 보고서
- 조사일시: 2026-02-24 11:02:39 KST
- 작업자: AI Agent

## STEP 1: 코디 관련 소스파일
```
--- Controllers ---
/home/danharoo/www/application/controllers/wemakeprice.php
  MATCH: /home/danharoo/www/application/controllers/wemakeprice.php
/home/danharoo/www/application/controllers/products_20230830.php
  MATCH: /home/danharoo/www/application/controllers/products_20230830.php
/home/danharoo/www/application/controllers/products_20210926.php
  MATCH: /home/danharoo/www/application/controllers/products_20210926.php
/home/danharoo/www/application/controllers/products_20220925.php
  MATCH: /home/danharoo/www/application/controllers/products_20220925.php
/home/danharoo/www/application/controllers/products_20210927.php
  MATCH: /home/danharoo/www/application/controllers/products_20210927.php
/home/danharoo/www/application/controllers/products_20210915.php
  MATCH: /home/danharoo/www/application/controllers/products_20210915.php
/home/danharoo/www/application/controllers/products.php
  MATCH: /home/danharoo/www/application/controllers/products.php
/home/danharoo/www/application/controllers/vendor/aws/aws-crt-php/src/AWS/CRT/HTTP/Headers.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-crt-php/src/AWS/CRT/HTTP/Headers.php
/home/danharoo/www/application/controllers/vendor/aws/aws-crt-php/src/AWS/CRT/HTTP/Message.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-crt-php/src/AWS/CRT/HTTP/Message.php
/home/danharoo/www/application/controllers/vendor/aws/aws-crt-php/src/AWS/CRT/Internal/Encoding.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-crt-php/src/AWS/CRT/Internal/Encoding.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/CloudFront/CloudFrontClient.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/CloudFront/CloudFrontClient.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/CloudTrail/LogFileIterator.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/CloudTrail/LogFileIterator.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/CloudTrail/LogFileReader.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/CloudTrail/LogFileReader.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/CloudTrail/LogRecordIterator.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/CloudTrail/LogRecordIterator.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/Sns/MessageValidator/Message.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/Sns/MessageValidator/Message.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/Common/Signature/SignatureV2.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/Common/Signature/SignatureV2.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/Route53/Resources/route53-2013-04-01.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/Route53/Resources/route53-2013-04-01.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/SimpleDb/Resources/simpledb-2009-04-15.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/SimpleDb/Resources/simpledb-2009-04-15.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/Iam/Resources/iam-2010-05-08.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/Iam/Resources/iam-2010-05-08.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/DynamoDb/Session/SessionHandler.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/DynamoDb/Session/SessionHandler.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/DynamoDb/Resources/dynamodb-2011-12-05.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/DynamoDb/Resources/dynamodb-2011-12-05.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/DynamoDb/DynamoDbCommand.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/DynamoDb/DynamoDbCommand.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/S3/Model/PostObject.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/S3/Model/PostObject.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/S3/Enum/EncodingType.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/S3/Enum/EncodingType.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/S3/SseCpkListener.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/S3/SseCpkListener.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/S3/Resources/s3-2006-03-01.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/S3/Resources/s3-2006-03-01.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/S3/S3Signature.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/S3/S3Signature.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/ConfigService/Resources/configservice-2014-11-12.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Aws/ConfigService/Resources/configservice-2014-11-12.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/IVS/IVSClient.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/IVS/IVSClient.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/CloudTrail/LogFileIterator.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/CloudTrail/LogFileIterator.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/CloudTrail/LogFileReader.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/CloudTrail/LogFileReader.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/CloudTrail/LogRecordIterator.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/CloudTrail/LogRecordIterator.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/StreamRequestPayloadMiddleware.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/StreamRequestPayloadMiddleware.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Crypto/MaterialsProviderInterfaceV2.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Crypto/MaterialsProviderInterfaceV2.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Crypto/MaterialsProvider.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Crypto/MaterialsProvider.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Crypto/MaterialsProviderV2.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Crypto/MaterialsProviderV2.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Crypto/MetadataStrategyInterface.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Crypto/MetadataStrategyInterface.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Crypto/MaterialsProviderInterface.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Crypto/MaterialsProviderInterface.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Api/Parser/EventParsingIterator.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Api/Parser/EventParsingIterator.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Api/Parser/DecodingEventStreamIterator.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Api/Parser/DecodingEventStreamIterator.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/EndpointV2/EndpointV2SerializerTrait.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/EndpointV2/EndpointV2SerializerTrait.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Token/SsoTokenProvider.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Token/SsoTokenProvider.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Sqs/SqsClient.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Sqs/SqsClient.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/RequestCompressionMiddleware.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/RequestCompressionMiddleware.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/S3/Crypto/HeadersMetadataStrategy.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/S3/Crypto/HeadersMetadataStrategy.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/S3/Crypto/InstructionFileMetadataStrategy.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/S3/Crypto/InstructionFileMetadataStrategy.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/S3/S3Client.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/S3/S3Client.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/S3/SSECMiddleware.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/S3/SSECMiddleware.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Connect/ConnectClient.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/Connect/ConnectClient.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/firehose/2015-08-04/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/firehose/2015-08-04/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/email/2010-12-01/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/email/2010-12-01/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/athena/2017-05-18/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/athena/2017-05-18/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/honeycode/2020-03-01/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/honeycode/2020-03-01/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/m2/2021-04-28/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/m2/2021-04-28/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/iotwireless/2020-11-22/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/iotwireless/2020-11-22/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/route53/2013-04-01/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/route53/2013-04-01/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/route53/2013-04-01/paginators-1.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/route53/2013-04-01/paginators-1.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/pinpoint/2016-12-01/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/pinpoint/2016-12-01/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/sagemaker-featurestore-runtime/2020-07-01/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/sagemaker-featurestore-runtime/2020-07-01/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/codeguruprofiler/2019-07-18/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/codeguruprofiler/2019-07-18/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/cloudfront/2020-05-31/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/cloudfront/2020-05-31/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/kinesisanalytics/2015-08-14/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/kinesisanalytics/2015-08-14/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/ebs/2019-11-02/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/ebs/2019-11-02/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/ivs-realtime/2020-07-14/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/ivs-realtime/2020-07-14/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/lightsail/2016-11-28/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/lightsail/2016-11-28/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/medialive/2017-10-14/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/medialive/2017-10-14/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/greengrassv2/2020-11-30/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/greengrassv2/2020-11-30/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/ivs/2020-07-14/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/ivs/2020-07-14/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/ivs/2020-07-14/paginators-1.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/ivs/2020-07-14/paginators-1.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/data.iot/2015-05-28/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/data.iot/2015-05-28/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/kinesisanalyticsv2/2018-05-23/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/kinesisanalyticsv2/2018-05-23/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/quicksight/2018-04-01/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/quicksight/2018-04-01/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/ssm-incidents/2018-05-10/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/ssm-incidents/2018-05-10/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/ec2/2016-11-15/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/ec2/2016-11-15/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/kinesis/2013-12-02/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/kinesis/2013-12-02/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/kinesis/2013-12-02/endpoint-rule-set-1.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/kinesis/2013-12-02/endpoint-rule-set-1.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/greengrass/2017-06-07/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/greengrass/2017-06-07/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/securityhub/2018-10-26/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/securityhub/2018-10-26/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/mediaconnect/2018-11-14/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/mediaconnect/2018-11-14/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/backup/2018-11-15/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/backup/2018-11-15/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/connect/2017-08-08/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/connect/2017-08-08/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/synthetics/2017-10-11/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/synthetics/2017-10-11/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/mediaconvert/2017-08-29/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/mediaconvert/2017-08-29/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/timestream-write/2018-11-01/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/timestream-write/2018-11-01/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/s3control/2018-08-20/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/s3control/2018-08-20/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/s3control/2018-08-20/endpoint-rule-set-1.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/s3control/2018-08-20/endpoint-rule-set-1.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/metering.marketplace/2016-01-14/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/metering.marketplace/2016-01-14/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/comprehendmedical/2018-10-30/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/comprehendmedical/2018-10-30/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/sagemaker-geospatial/2020-05-27/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/sagemaker-geospatial/2020-05-27/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/omics/2022-11-28/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/omics/2022-11-28/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/s3/2006-03-01/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/s3/2006-03-01/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/s3/2006-03-01/endpoint-rule-set-1.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/s3/2006-03-01/endpoint-rule-set-1.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/sagemaker/2017-07-24/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/sagemaker/2017-07-24/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/iam/2010-05-08/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/iam/2010-05-08/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/neptunedata/2023-08-01/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/neptunedata/2023-08-01/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/medical-imaging/2023-07-19/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/medical-imaging/2023-07-19/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/dms/2016-01-01/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/dms/2016-01-01/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/config/2014-11-12/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/config/2014-11-12/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/servicecatalog/2015-12-10/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/servicecatalog/2015-12-10/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/groundstation/2019-05-23/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/groundstation/2019-05-23/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/iot-roborunner/2018-05-10/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/iot-roborunner/2018-05-10/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/macie2/2020-01-01/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/macie2/2020-01-01/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/opsworks/2013-02-18/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/opsworks/2013-02-18/api-2.json.php
/home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/chime-sdk-media-pipelines/2021-07-15/api-2.json.php
  MATCH: /home/danharoo/www/application/controllers/vendor/aws/aws-sdk-php/src/data/chime-sdk-media-pipelines/2021-07-15/api-2.json.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/Message/Request.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/Message/Request.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/Message/RequestFactory.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/Message/RequestFactory.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/Message/EntityEnclosingRequest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/Message/EntityEnclosingRequest.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/Message/Response.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/Message/Response.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/EntityBodyInterface.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/EntityBodyInterface.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/AbstractEntityBodyDecorator.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/AbstractEntityBodyDecorator.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/CachingEntityBody.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/CachingEntityBody.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/QueryString.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/QueryString.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/QueryAggregator/DuplicateAggregator.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/QueryAggregator/DuplicateAggregator.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/QueryAggregator/CommaAggregator.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/QueryAggregator/CommaAggregator.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/Curl/CurlHandle.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/Curl/CurlHandle.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/EntityBody.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Http/EntityBody.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Parser/Cookie/CookieParser.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Parser/Cookie/CookieParser.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Parser/UriTemplate/UriTemplate.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Parser/UriTemplate/UriTemplate.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Plugin/Cache/DefaultCacheStorage.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Plugin/Cache/DefaultCacheStorage.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Plugin/Cookie/CookieJar/CookieJarInterface.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Plugin/Cookie/CookieJar/CookieJarInterface.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Plugin/Cookie/Cookie.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Plugin/Cookie/Cookie.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Plugin/Md5/Md5ValidatorPlugin.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Plugin/Md5/Md5ValidatorPlugin.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Service/Description/Parameter.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Service/Description/Parameter.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Service/Command/LocationVisitor/Request/BodyVisitor.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Service/Command/LocationVisitor/Request/BodyVisitor.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Service/Command/LocationVisitor/Request/XmlVisitor.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/src/Guzzle/Service/Command/LocationVisitor/Request/XmlVisitor.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/Message/ResponseTest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/Message/ResponseTest.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/Message/RequestTest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/Message/RequestTest.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/Message/RequestFactoryTest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/Message/RequestFactoryTest.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/Message/EntityEnclosingRequestTest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/Message/EntityEnclosingRequestTest.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/EntityBodyTest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/EntityBodyTest.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/QueryStringTest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/QueryStringTest.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/QueryAggregator/CommaAggregatorTest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/QueryAggregator/CommaAggregatorTest.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/QueryAggregator/DuplicateAggregatorTest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/QueryAggregator/DuplicateAggregatorTest.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/QueryAggregator/PhpAggregatorTest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/QueryAggregator/PhpAggregatorTest.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/Curl/CurlMultiTest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/Curl/CurlMultiTest.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/Curl/CurlHandleTest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/Curl/CurlHandleTest.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/AbstractEntityBodyDecoratorTest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/AbstractEntityBodyDecoratorTest.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/CachingEntityBodyTest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Http/CachingEntityBodyTest.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Plugin/Md5/Md5ValidatorPluginTest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Plugin/Md5/Md5ValidatorPluginTest.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Service/Command/LocationVisitor/Request/BodyVisitorTest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Service/Command/LocationVisitor/Request/BodyVisitorTest.php
/home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Service/Command/LocationVisitor/Request/XmlVisitorTest.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzle/guzzle/tests/Guzzle/Tests/Service/Command/LocationVisitor/Request/XmlVisitorTest.php
/home/danharoo/www/application/controllers/vendor/symfony/polyfill-mbstring/Mbstring.php
  MATCH: /home/danharoo/www/application/controllers/vendor/symfony/polyfill-mbstring/Mbstring.php
/home/danharoo/www/application/controllers/vendor/symfony/polyfill-mbstring/bootstrap80.php
  MATCH: /home/danharoo/www/application/controllers/vendor/symfony/polyfill-mbstring/bootstrap80.php
/home/danharoo/www/application/controllers/vendor/symfony/polyfill-mbstring/bootstrap.php
  MATCH: /home/danharoo/www/application/controllers/vendor/symfony/polyfill-mbstring/bootstrap.php
/home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/Handler/CurlFactory.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/Handler/CurlFactory.php
/home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/Handler/StreamHandler.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/Handler/StreamHandler.php
/home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/Handler/EasyHandle.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/Handler/EasyHandle.php
/home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/RequestOptions.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/RequestOptions.php
/home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/Cookie/SetCookie.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/Cookie/SetCookie.php
/home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/Cookie/CookieJarInterface.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/Cookie/CookieJarInterface.php
/home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/Client.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/Client.php
/home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/Utils.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/Utils.php
/home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/functions.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/functions.php
/home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/PrepareBodyMiddleware.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/PrepareBodyMiddleware.php
/home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/Middleware.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzlehttp/guzzle/src/Middleware.php
/home/danharoo/www/application/controllers/vendor/guzzlehttp/psr7/src/UriNormalizer.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzlehttp/psr7/src/UriNormalizer.php
/home/danharoo/www/application/controllers/vendor/guzzlehttp/psr7/src/Message.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzlehttp/psr7/src/Message.php
/home/danharoo/www/application/controllers/vendor/guzzlehttp/psr7/src/Query.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzlehttp/psr7/src/Query.php
/home/danharoo/www/application/controllers/vendor/guzzlehttp/psr7/src/Uri.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzlehttp/psr7/src/Uri.php
/home/danharoo/www/application/controllers/vendor/guzzlehttp/psr7/src/InflateStream.php
  MATCH: /home/danharoo/www/application/controllers/vendor/guzzlehttp/psr7/src/InflateStream.php
/home/danharoo/www/application/controllers/vendor/psr/http-message/src/UriInterface.php
  MATCH: /home/danharoo/www/application/controllers/vendor/psr/http-message/src/UriInterface.php
/home/danharoo/www/application/controllers/products_20230920.php
  MATCH: /home/danharoo/www/application/controllers/products_20230920.php
/home/danharoo/www/application/controllers/products_220627.php
  MATCH: /home/danharoo/www/application/controllers/products_220627.php
```
*(STEP 1 Controllers 일부까지 수집됨. 스크립트가 STEP 1 중단 후 서버에서 전체 재실행 권장.)*

## STEP 2~7: 서버 실행 시 수집 항목
- **STEP 2**: DB 테이블(coord/codi/cordi/style_set/look 등) 구조·건수·샘플
- **STEP 3**: Apache/CI 에러 로그 (코디 관련)
- **STEP 4**: routes.php 코디 라우팅
- **STEP 5**: 코디 컨트롤러/모델 소스 전체
- **STEP 6**: PHP 버전, upload_max_filesize, 디스크/업로드 디렉터리
- **STEP 7**: V1 HTTP Health Check

**서버 실행 방법**: `ssh -p 7916 -i ~/.ssh/id_ed25519_newtalk root@114.207.244.86` 접속 후  
`/srv/newtalk-v2/docs/scripts/V1-CODI-FIX-001-investigate.sh` 실행.

## 결론
- STEP 1에서 코디 관련 매치 파일 다수 확인(products*.php, wemakeprice.php, vendor 내 coord 등). 실제 코디 전용 컨트롤러/모델은 서버에서 조사 스크립트 전체 실행 후 확인 필요.
- **V1 소스 수정이 필요한 경우 대표님 승인 후 진행합니다.**
