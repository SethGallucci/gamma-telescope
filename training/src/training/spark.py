from pyspark.sql import SparkSession


def get_spark(master: str | None = "local[*]") -> SparkSession:
    """Return a SparkSession for this project, creating it if none is running.

    Args:
        master: The Spark master URL. The default, "local[*]", runs Spark on this
            machine with all CPU cores. Pass None on AWS Glue, which sets its own
            master; setting one there would override Glue's cluster.
    """
    builder = SparkSession.builder.appName("gamma-telescope")
    if master is not None:
        builder = builder.master(master)

    return builder.getOrCreate()
