from collections.abc import Callable
import duckdb
import timeit


def run_prepped_reader(connection: duckdb.DuckDBPyConnection):
    batch_reader = connection.sql(
        """--sql
        from read_parquet('crash100k.zstd.parquet')
        limit $limit;
    """,
        params={"limit": 1_000_000},
    ).fetch_arrow_reader(batch_size=1000)

    for _ in batch_reader:
        pass


def run_normal_reader(connection: duckdb.DuckDBPyConnection):
    batch_reader = connection.sql(
        """--sql
        from read_parquet('crash100k.zstd.parquet')
        limit 1000000;
    """
    ).fetch_arrow_reader(batch_size=1000)

    for _ in batch_reader:
        pass


def benchmarkish(fn: Callable[[duckdb.DuckDBPyConnection], None], times=100):
    with duckdb.connect(
        ":memory:", config={"memory_limit": "4GB", "threads": "1"}
    ) as connection:
        return timeit.timeit(lambda: fn(connection), number=times)


def main():
    times = 100

    print(f"Timing normal ({times}x)...")
    normal = benchmarkish(run_normal_reader, times=times)

    print(f"Timing prepped ({times}x)...")
    prepped = benchmarkish(run_prepped_reader, times=times)

    print(f"Normal: {normal} seconds")
    print(f"Prepped: {prepped} seconds")


if __name__ == "__main__":
    main()
