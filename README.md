# 👯 Clone Yourself with WhatsApp Chat History
This project allows you to clone your conversational style using your own WhatsApp chat history. Fine-tune a language model to mimic your tone, habits, and quirks.

## Model Link 
[![Open in Hugging Face](https://img.shields.io/badge/🤗%20Hugging%20Face-model-blue)](https://huggingface.co/aalize/Qwen2.5-7B-Instruct-AWQ-4bit)

## Demo 
> Since the model was trained on my personal chat history (in Chinese), the demo below features a Chinese conversation.

  <img width="250" alt="IMG_2996" src="https://github.com/user-attachments/assets/be3eedda-5e6e-409c-90ee-c26c82b9d065" />
 <img width="250" alt="IMG_2996" src="https://github.com/user-attachments/assets/382734b7-0057-4643-8565-32c7054ad4f8" />

## Quick Start
1. **Export Chat History**  
    Export a 1-on-1 chat from WhatsApp (text only, no media).
    
2. **Clean & Format the Data**  
    Remove noise and convert the chat into JSONL format for training. Example:
   ```
    {"role": "user", "content": "Hey, how are you?"}
    {"role": "assistant", "content": "All good! Just got back from work."}
   ```
    
4. **Train a Model on Your Chat Style**  
    Fine-tune a language model (default: Qwen-7B) using QLoRA or AWQ.
    
5. **Quantize for Efficient Inference**  
    Optionally apply quantization to reduce model size and speed up inference.
    
6. **Deploy Your Model**  
    Host your AI clone using Hugging Face TGI on Google Cloud Run (or your own infra).
    
7. **Chat with Your Clone**  
    Connect via Telegram bot or a custom frontend. The model will mimic your tone and chat style.

## Training & Quantization Options
You can train your model using one of the following two methods:
### 1. AWQ – Activation-aware Weight Quantization (Recommended)
- This method fine-tunes a full-precision model first, then applies post-training quantization.
- Although it consumes more memory during training, it produces a static quantized model that is:
  - Directly usable in Text Generation Inference (TGI) or vLLM
  - No special libraries required at inference time, such as bitsandbytes
- Training precision: FP16
- Recommended GPU: A100
- Training time: ~1 min for ~1800 rows
- VRAM usage:
  - Model loading: 14 GB
  - Training: ~26 GB

### 2. QLoRA with bitsandbytes
- This method trains directly on a quantized model, using LoRA adapters and bitsandbytes for memory efficiency.
- Works well even on L4 GPUs
- Produces models that still require bitsandbytes at inference time.
- Training time: ~5 min for ~1800 rows
- VRAM usage: 7–18 GB, depending on batch size and sequence length
> **Note:** Google Colab’s free T4 instances may run into memory issues with either method.

## Deployment
Use the Hugging Face TGI (Text Generation Inference) image via Google Cloud Run
```
gcloud run deploy $SERVICE_NAME \
  --image=$CONTAINER_URI \
  --args="--model-id=aalize/Clone-yourself,--max-concurrent-requests=64" \
  --set-env-vars=HF_HUB_ENABLE_HF_TRANSFER=1,HF_TOKEN=$HF_TOKEN \
  --port=8080 \
  --cpu=8 \
  --memory=32Gi \
  --no-cpu-throttling \
  --gpu=1 \
  --gpu-type=nvidia-l4 \
  --max-instances=3 \
  --concurrency=64 \
  --region=$LOCATION \
  --timeout=900 \
  --no-allow-unauthenticated
```

## Common Issues 
1. **Why does the model output random text even before training?**  
    Make sure you follow the required chat format. For example, Qwen-7B uses ChatML-style prompting, which looks like:  
    ```
    <|im_start|>user
    Hello!<|im_end|>
    <|im_start|>assistant
    Hi there!<|im_end|>
    ```
2. **How much data do I need?**  
    In general, more is better. I tested with 500 rows vs. 1800 rows, and the larger dataset produced noticeably better results.
   
3. **The model keeps repeating itself at the end — why?**  
   This often happens if you set the EOS token as the pad token. Don’t do that — otherwise, the model won’t learn when to stop generating output.
   
5. **Does completion-only training improve the model’s response quality?**  
   It might help slightly, but in my experience, the impact was minimal.
   
7. **Will the model leak my personal information in chat?**  
    The model only learns your style and tone — not factual personal info like your birthday, address, or job. If asked, it will just hallucinate an answer.
