FROM vllm/vllm-openai:latest
ENV MODEL_NAME="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
ENV MAX_MODEL_LEN="4096"
ENV GPU_MEMORY_UTIL="0.9"
CMD python -m vllm.entrypoints.openai.api_server \
    --model $MODEL_NAME \
    --max-model-len $MAX_MODEL_LEN \
    --gpu-memory-utilization $GPU_MEMORY_UTIL \
    --port 8000
