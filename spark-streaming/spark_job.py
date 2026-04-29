from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, from_unixtime, window, avg, stddev, when
from pyspark.sql.types import StructType, StringType, DoubleType
from pyspark.sql.functions import abs, to_json, struct

# ---------------- CREATE SPARK SESSION ----------------

spark = SparkSession.builder \
    .appName("IoT Spark Streaming") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("Spark session started")

# ---------------- DEFINE SCHEMA ----------------

schema = StructType() \
    .add("sensor_id", StringType()) \
    .add("temperature", DoubleType()) \
    .add("humidity", DoubleType()) \
    .add("timestamp", DoubleType())

# ---------------- READ FROM KAFKA ----------------

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "sensor-data") \
    .option("startingOffsets", "latest") \
    .load()

# ---------------- PARSE JSON ----------------

json_df = df.selectExpr("CAST(value AS STRING)")

parsed_df = json_df.select(
    from_json(col("value"), schema).alias("data")
).select("data.*")

# ---------------- CONVERT TIMESTAMP ----------------

final_df = parsed_df.withColumn(
    "time",
    from_unixtime(col("timestamp")).cast("timestamp")
).select("time", "sensor_id", "temperature", "humidity")

def write_to_db(batch_df, batch_id):
    batch_df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://db:5432/sensors") \
        .option("dbtable", "sensor_data") \
        .option("user", "admin") \
        .option("password", "admin123") \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

db_query = final_df.writeStream \
    .foreachBatch(write_to_db) \
    .outputMode("append") \
    .start()

# =====================================================
# 🔥 WINDOW AGGREGATION
# =====================================================

agg_df = final_df \
    .withWatermark("time", "1 minute") \
    .groupBy(
        window(col("time"), "30 seconds"),
        col("sensor_id")
    ) \
    .agg(
        avg("temperature").alias("mean_temp"),
        stddev("temperature").alias("stddev_temp")
    )

# =====================================================
# 🔥 JOIN
# =====================================================

joined_df = final_df.alias("raw").join(
    agg_df.alias("agg"),
    (col("raw.sensor_id") == col("agg.sensor_id")) &
    (col("raw.time") >= col("agg.window.start")) &
    (col("raw.time") <= col("agg.window.end"))
)

clean_df = joined_df.select(
    col("raw.sensor_id").alias("sensor_id"),
    col("raw.time").alias("time"),
    col("raw.temperature").alias("temperature"),
    col("agg.mean_temp"),
    col("agg.stddev_temp")
)

# =====================================================
# 🔥 Z-SCORE
# =====================================================

zscore_df = clean_df.withColumn(
    "z_score",
    when(col("stddev_temp").isNull() | (col("stddev_temp") == 0), 0)
    .otherwise((col("temperature") - col("mean_temp")) / col("stddev_temp"))
)

# =====================================================
# 🔥 SEVERITY (TUNED)
# =====================================================

severity_df = zscore_df.withColumn(
    "severity",
    when(abs(col("z_score")) > 1.5, "CRITICAL")
    .when(abs(col("z_score")) > 1.2, "HIGH")
    .when(abs(col("z_score")) > 0.8, "MEDIUM")
    .when(abs(col("z_score")) > 0.5, "LOW")
    .otherwise("NORMAL")
)

# =====================================================
# 🚨 ALERT STREAM → KAFKA ONLY
# =====================================================

alerts_df = severity_df.filter(col("severity") != "NORMAL")

alerts_kafka_df = alerts_df.selectExpr(
    "CAST(sensor_id AS STRING) AS key",
    """
    to_json(struct(
        sensor_id,
        temperature,
        z_score,
        severity,
        time
    )) AS value
    """
)

alerts_query = alerts_kafka_df.writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("topic", "alerts") \
    .option("checkpointLocation", "/tmp/alerts_checkpoint") \
    .outputMode("append") \
    .start()

print("Streaming (production mode) started...")

spark.streams.awaitAnyTermination()