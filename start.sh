#!/bin/sh

# MinerU使用了很抽象的全局配置，所以得生成下~/magic-pdf.json

CONFIG_FILE="$HOME/magic-pdf.json"

MODEL_PATH="${MODEL_PATH-/models/wanderkid/PDF-Extract-Kit/models}"
DEVICE="${DEVICE-cpu}"
ENABLE_TABLE_RECOG="${ENABLE_TABLE_RECOG-true}"
MAX_TIME="${MAX_TIME-400}"

echo "{
  \"models-dir\": \"$MODEL_PATH\",
  \"device-mode\": \"$DEVICE\",
  \"table-config\": {
    \"is_table_recog_enable\": $ENABLE_TABLE_RECOG,
    \"max_time\": $MAX_TIME
  }
}" > $CONFIG_FILE

# 启动服务

. /venv/bin/activate
exec python3 server.py
