import boto3
import duckdb

print("seeding bucket...")

s3 = boto3.client(
    "s3",
    aws_access_key_id="admin",
    aws_secret_access_key="admin123",
    region_name="us-east-1",
    endpoint_url="http://localhost:9000",
)
bucket_name = "boom"
object_key = "format=SomeFormatOrSomething/$year=2024/$month=10/boom.zstd.parquet"
try:
    s3.create_bucket(Bucket=bucket_name)
except:
    pass
s3.upload_file("boom.zstd.parquet", bucket_name, object_key)

print("trying to crash...")

for _ in range(0, 1000):
    with duckdb.connect(
        ":memory:",
        config={"memory_limit": "4GB", "threads": "1"},
    ) as connection:
        connection.execute("""--sql
            create secret (
                type s3,
                endpoint 'localhost:9000',
                region 'us-east-1',
                key_id 'admin',
                secret 'admin123',
                url_style 'path',
                use_ssl false
            );
        """)

        batch_reader = connection.sql(
            """--sql
            from read_parquet('s3://boom/format=SomeFormatOrSomething/$year=2024/$month=10/boom.zstd.parquet')
            limit $foo;
        """,
            params={"foo": 10_000},
        ).fetch_arrow_reader(batch_size=1000)

        for _ in batch_reader:
            pass
