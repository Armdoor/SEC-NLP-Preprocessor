import os

DB_URI = os.getenv("DB_URI",
    "postgresql://bojackhorse:Iowa+25march@"
    "database-1.c9ko8uwa4nsf.us-east-1.rds.amazonaws.com:5432/postgres"
)

PRETRAINED_MODEL = "yiyanghkust/finbert-tone"
OUTPUT_DIR      = "./training/checkpoints"
NUM_EPOCHS      = 3
BATCH_SIZE      = 8
MAX_LEN         = 512
PSEUDO_LABEL_THRESHOLD = 0.9