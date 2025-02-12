from fastapi import FastAPI, Request
import json

app = FastAPI()

# CloudEvents
# イベントデータはベンダーや製品により様々なので、イベント構造を標準化する唯一のもの
# ただし、そんなに広まっていないようだ

# curl -XPOST http://localhost:9500/events/minio -H "accept: application/json" -d'{}'


handlers = {}


class AbstractEvent:
    def __init__(self, event: dict):
        self._event = event

class MinioEvent(AbstractEvent):
    ...


# Key にはバケットからのパスが含まれる
sample_data = """
{
  "EventName": "s3:ObjectCreated:Put",
  "Key": "test/sub/FullColor_1280x1024_72dpi.png",
  "Records": [
    {
      "eventVersion": "2.0",
      "eventSource": "minio:s3",
      "awsRegion": "",
      "eventTime": "2025-02-12T10:15:52.901Z",
      "eventName": "s3:ObjectCreated:Put",
      "userIdentity": {
        "principalId": "admin"
      },
      "requestParameters": {
        "principalId": "admin",
        "region": "",
        "sourceIPAddress": "172.22.0.1"
      },
      "responseElements": {
        "x-amz-id-2": "dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8",
        "x-amz-request-id": "18236E7A5B90F0B2",
        "x-minio-deployment-id": "68b33afd-8d5f-4697-8ea7-1ed75a245f09",
        "x-minio-origin-endpoint": "http://172.22.0.5:9000"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "Config",
        "bucket": {
          "name": "test",
          "ownerIdentity": {
            "principalId": "admin"
          },
          "arn": "arn:aws:s3:::test"
        },
        "object": {
          "key": "FullColor_1280x1024_72dpi.png",
          "size": 31670,
          "eTag": "e382f64a624eb3e5d731d093c402cebe",
          "contentType": "image/png",
          "userMetadata": {
            "content-type": "image/png"
          },
          "sequencer": "18236E7A5B9525D0"
        }
      },
      "source": {
        "host": "172.22.0.1",
        "port": "",
        "userAgent": "MinIO (linux; amd64) minio-go/v7.0.82 MinIO Console/(dev)"
      }
    }
  ]
}
"""

# 1. minio で Events から publisher を定義する
# 2. Bucket に対して subscriber を定義し、publisher と紐づける

@app.post("/events/minio")
async def handle_from_minio(request: Request):
    """s3 タイプのイベントを受け取る"""
    data = await request.json()
    print("Received event:", json.dumps(data, indent=2))

    for record in data.get("Records", []):
        event_name = record.get("eventName")
        bucket_name = record["s3"]["bucket"]["name"]
        object_key = record["s3"]["object"]["key"]

        print(f"Event: {event_name}, Bucket: {bucket_name}, Object: {object_key}")

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
