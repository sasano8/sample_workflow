import pyarrow as pa
import pyarrow.parquet as pq

def to_int(v):
    if isinstance(v, str):
        v = str(v).lower()

    if "true":
        return 1
    elif "false":
        return 0
    else:
        return int(v)
    

class SchemaBuilerV01:
    VERSION = "1"

    def __init__(self, columns: list = None, metadata: dict = None):
        self._fields = columns or []
        self._metadata = metadata or {}

    def add(self, name, type, pk: int = 0, **kwargs: dict[bytes: bytes]):
        if pk:
            kwargs["pk"] = "1"

        if isinstance(type, pa.DataType):
            datatype = type
        else:
            # pa.timestamp("ms")
            datatype = {
                str: pa.string(),
                int: pa.int64(),
            }.get(type)

        metadata = self._get_encoded_meta(kwargs)
        field = pa.field(name, datatype, metadata=metadata)
        self._fields.append(field)
        return self
    
    def get_primary_keys(self):
        iter = ((f.name, (f.metadata.get(b"pk", b"0").decode())) for f in self._fields)
        return [field[0] for field in iter if int(field[1])]
    
    def get_meta(self):
        metadata = {k.decode(): v.decode() for k, v in self._metadata.items()}
        return metadata
    
    @classmethod
    def _get_encoded_meta(cls, metadata):
        return {k.encode(): v.encode() for k, v in metadata.items()}

    @classmethod
    def _get_decoded_meta(cls, metadata):
        return {k.decode(): v.decode() for k, v in metadata.items()}

    def build(self):
        self._metadata["myschemabuilder.version"] = self.VERSION
        metadata=self._get_encoded_meta(self._metadata)
        return pa.schema(self._fields, metadata)
    
    @classmethod
    def from_parquet(cls, path: str):
        schema = pq.read_schema(path)
        metadata = cls._get_decoded_meta(schema.metadata)
        fields = list(schema)
        return SchemaBuilerV01(fields, metadata)
    
    def dump(self, path: str):
        table_empty = pa.Table.from_batches([], schema=self.build())
        pq.write_table(table_empty, path)


if False:
    if False:
        schema = SchemaBuilerV01(metadata={"description": "sample schema."}).add(
            "id", int, pk=True
        ).add(
            "name", str
        ).add(
            "age", int
        ).add(
            "created_at", pa.timestamp("ms")
        )

        print(schema.get_primary_keys())

        # table_empty = pa.Table.from_batches([], schema=schema.build())
        # pq.write_table(table_empty, "schema_only.parquet")
        schema.dump("schema_only.parquet")

    else:
        print(SchemaBuilerV01.from_parquet("schema_only.parquet").build())


def load(filepath: str = "data/default/schema_only.parquet"):
    from os import environ

    AWS_ACCESS_KEY_ID = environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = environ.get("AWS_REGION")
    # AWS_BUCKET = environ.get("AWS_BUCKET")  # nessie から bucket の場所を受け取る
    ICEBERG_URL = environ.get("ICEBERG_URL")
    ICEBERG_REF = environ.get("ICEBERG_REF")
    ICEBERG_DEFAULT_NAMESPACE = environ.get("ICEBERG_DEFAULT_NAMESPACE", "default")

    load_to_iceberg(
        filepath,
        AWS_ACCESS_KEY_ID=AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY=AWS_SECRET_ACCESS_KEY,
        AWS_REGION=AWS_REGION,
        ICEBERG_URL=ICEBERG_URL,
        ICEBERG_REF=ICEBERG_REF,
        namespace=ICEBERG_DEFAULT_NAMESPACE
    )


def load_to_iceberg(filepath, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, ICEBERG_URL, ICEBERG_REF, namespace: str = "default"):
    from pyiceberg.catalog import load_catalog
    # import pandas as pd
    import pyarrow as pa
    import os

    catalog_name = "tutorial"
    conf_catalog = {
        "uri": ICEBERG_URL,
        "ref": ICEBERG_REF
    }

    catalog = load_catalog(
        catalog_name,
        **conf_catalog
    )

    catalog.create_namespace_if_not_exists(namespace)

    # TABLE_NAME = "default.taxi_dataset"

    # pa_table = pa.Table.from_pydict({
    #     "id": [1, 2, 3],
    #     "name": ["Alice", "Bob", "Charlie"],
    #     "age": [25, 30, 28],
    #     "salary": [50000.0, 60000.0, 55000.0]
    # })
    basename = os.path.basename(filepath)
    ext = os.path.splitext(basename)[-1]
    if ext != ".parquet":
        raise Exception()
    pa_table = pq.read_table(filepath)
    
    TABLE_NAME = namespace + "." + "".join(os.path.splitext(basename)[:-1])

    print(pa_table.schema)

    if not catalog.table_exists(TABLE_NAME):
        with catalog.create_table_transaction(
            identifier=TABLE_NAME,
            schema=pa_table.schema,
        ) as txn:
            txn.append(pa_table)

    loaded_table = catalog.load_table(TABLE_NAME)
    print(loaded_table.scan().to_arrow())


load()
