# Kimi-K2 AI Guide

This comprehensive guide covers deployment and tool calling for Kimi-K2, the state-of-the-art agentic AI model.

## Table of Contents
- [Deployment](#deployment)
  - [vLLM Deployment](#vllm-deployment)
  - [SGLang Deployment](#sglang-deployment)
  - [KTransformers Deployment](#ktransformers-deployment)
  - [TensorRT-LLM Deployment](#tensorrt-llm-deployment)
  - [Other Frameworks](#other-frameworks)
- [Tool Calling](#tool-calling)
  - [Preparing Tools](#preparing-tools)
  - [Chat with Tools](#chat-with-tools)
  - [Tool Calling in Streaming Mode](#tool-calling-in-streaming-mode)
  - [Manually Parsing Tool Calls](#manually-parsing-tool-calls)

---

## Deployment

> [!Note]
> This guide only provides some examples of deployment commands for Kimi-K2, which may not be the optimal configuration. Since inference engines are still being updated frequently, please continue to follow the guidance from their homepage if you want to achieve better inference performance.
>
> You can access Kimi K2's API on https://platform.moonshot.ai, we provide an OpenAI/Anthropic-compatible API for you.
>
> The Anthropic-compatible API maps temperature by `real_temperature = request_temperature * 0.6` for better compatibility with existing applications.

Our model checkpoints are stored in block-fp8 format, you can find it on [Huggingface](https://huggingface.co/moonshotai/Kimi-K2-Instruct).

Currently, it is recommended to run Kimi-K2 on the following inference engines:

* vLLM
* SGLang
* KTransformers
* TensorRT-LLM

### vLLM Deployment

vLLM version v0.10.0rc1 or later is required.

The smallest deployment unit for Kimi-K2 FP8 weights with 128k seqlen on mainstream H200 or H20 platform is a cluster with 16 GPUs with either Tensor Parallel (TP) or "data parallel + expert parallel" (DP+EP).  
Running parameters for this environment are provided below. You may scale up to more nodes and increase expert-parallelism to enlarge the inference batch size and overall throughput.

#### Tensor Parallelism

When the parallelism degree ≤ 16, you can run inference with pure Tensor Parallelism. A sample launch command is:

``` bash
# start ray on node 0 and node 1

# node 0:
vllm serve $MODEL_PATH \
  --port 8000 \
  --served-model-name kimi-k2 \
  --trust-remote-code \
  --tensor-parallel-size 16 \
  --enable-auto-tool-choice \
  --tool-call-parser kimi_k2
```

**Key parameter notes:**
- `--tensor-parallel-size 16`: If using more than 16 GPUs, combine with pipeline-parallelism.
- `--enable-auto-tool-choice`: Required when enabling tool usage.
- `--tool-call-parser kimi_k2`: Required when enabling tool usage.

#### Data Parallelism + Expert Parallelism

You can install libraries like DeepEP and DeepGEMM as needed. Then run the command (example on H200):

``` bash
# node 0
vllm serve $MODEL_PATH --port 8000 --served-model-name kimi-k2 --trust-remote-code --data-parallel-size 16 --data-parallel-size-local 8 --data-parallel-address $MASTER_IP --data-parallel-rpc-port $PORT --enable-expert-parallel --max-num-batched-tokens 8192 --max-num-seqs 256 --gpu-memory-utilization 0.85 --enable-auto-tool-choice --tool-call-parser kimi_k2

# node 1
vllm serve $MODEL_PATH --headless --data-parallel-start-rank 8 --port 8000 --served-model-name kimi-k2 --trust-remote-code --data-parallel-size 16 --data-parallel-size-local 8 --data-parallel-address $MASTER_IP --data-parallel-rpc-port $PORT --enable-expert-parallel --max-num-batched-tokens 8192 --max-num-seqs 256 --gpu-memory-utilization 0.85 --enable-auto-tool-choice --tool-call-parser kimi_k2
```

### SGLang Deployment

Similarly, we can use TP or DP+EP in SGLang for Deployment, here are the examples.

#### Tensor Parallelism

Here is the simple example code to run TP16 with two nodes on H200:

``` bash
# Node 0
python -m sglang.launch_server --model-path $MODEL_PATH --tp 16 --dist-init-addr $MASTER_IP:50000 --nnodes 2 --node-rank 0 --trust-remote-code --tool-call-parser kimi_k2

# Node 1
python -m sglang.launch_server --model-path $MODEL_PATH --tp 16 --dist-init-addr $MASTER_IP:50000 --nnodes 2 --node-rank 1 --trust-remote-code --tool-call-parser kimi_k2
```

**Key parameter notes:**
- `--tool-call-parser kimi_k2`: Required when enabling tool usage.

#### Data Parallelism + Expert Parallelism

Here is an example for large scale Prefill-Decode Disaggregation (4P12D H200) with DP+EP in SGLang:

``` bash
# for prefill node
MC_TE_METRIC=true SGLANG_DISAGGREGATION_HEARTBEAT_INTERVAL=10000000 SGLANG_DISAGGREGATION_BOOTSTRAP_TIMEOUT=100000 SGLANG_DISAGGREGATION_WAITING_TIMEOUT=100000 PYTHONUNBUFFERED=1 \
python -m sglang.launch_server --model-path $MODEL_PATH \
--trust-remote-code --disaggregation-mode prefill --dist-init-addr $PREFILL_NODE0$:5757 --tp-size 32 --dp-size 32 --enable-dp-attention --host $LOCAL_IP --decode-log-interval 1 --disable-radix-cache --enable-deepep-moe --moe-dense-tp-size 1 --enable-dp-lm-head --disable-shared-experts-fusion --watchdog-timeout 1000000 --enable-two-batch-overlap --disaggregation-ib-device $IB_DEVICE --chunked-prefill-size 131072 --mem-fraction-static 0.85 --deepep-mode normal --ep-dispatch-algorithm dynamic --eplb-algorithm deepseek --max-running-requests 1024 --nnodes 4 --node-rank $RANK --tool-call-parser kimi_k2


# for decode node
SGLANG_DEEPEP_NUM_MAX_DISPATCH_TOKENS_PER_RANK=480 MC_TE_METRIC=true SGLANG_DISAGGREGATION_HEARTBEAT_INTERVAL=10000000 SGLANG_DISAGGREGATION_BOOTSTRAP_TIMEOUT=100000 SGLANG_DISAGGREGATION_WAITING_TIMEOUT=100000 PYTHONUNBUFFERED=1 \
python -m sglang.launch_server --model-path $MODEL_PATH --trust-remote-code --disaggregation-mode decode --dist-init-addr $DECODE_NODE0:5757 --tp-size 96 --dp-size 96 --enable-dp-attention --host $LOCAL_IP --decode-log-interval 1 --context-length 2176 --disable-radix-cache --enable-deepep-moe --moe-dense-tp-size 1 --enable-dp-lm-head --disable-shared-experts-fusion --watchdog-timeout 1000000 --enable-two-batch-overlap --disaggregation-ib-device $IB_DEVICE  --deepep-mode low_latency --mem-fraction-static 0.8 --cuda-graph-bs 480 --max-running-requests 46080 --ep-num-redundant-experts 96 --nnodes 12 --node-rank $RANK --tool-call-parser kimi_k2

# pdlb
PYTHONUNBUFFERED=1 python -m sglang.srt.disaggregation.launch_lb --prefill http://${PREFILL_NODE0}:30000 --decode http://${DECODE_NODE0}:30000 
```

### KTransformers Deployment

Please copy all configuration files (i.e., everything except the .safetensors files) into the GGUF checkpoint folder at /path/to/K2. Then run:
``` bash
python ktransformers/server/main.py  --model_path /path/to/K2 --gguf_path /path/to/K2 --cache_lens 30000
```

To enable AMX optimization, run:

``` bash
python ktransformers/server/main.py  --model_path /path/to/K2 --gguf_path /path/to/K2 --cache_lens 30000 --optimize_config_path ktransformers/optimize/optimize_rules/DeepSeek-V3-Chat-fp8-linear-ggml-experts-serve-amx.yaml
```

### TensorRT-LLM Deployment

#### Prerequisite
Please refer to [this guide](https://nvidia.github.io/TensorRT-LLM/installation/build-from-source-linux.html) to build TensorRT-LLM v1.0.0-rc2 from source and start a TRT-LLM docker container. 

install blobfile by:
```bash
pip install blobfile
```

#### Multi-node Serving
TensorRT-LLM supports multi-node inference. You can use mpirun to launch Kimi-K2 with multi-node jobs. We will use two nodes for this example.

##### mpirun
mpirun requires each node to have passwordless ssh access to the other node. We need to setup the environment inside the docker container. Run the container with host network and mount the current directory as well as model directory to the container.

```bash
# use host network
IMAGE=<YOUR_IMAGE>
NAME=test_2node_docker
# host1
docker run -it --name ${NAME}_host1 --ipc=host --gpus=all --network host --privileged --ulimit memlock=-1 --ulimit stack=67108864 -v ${PWD}:/workspace -v <YOUR_MODEL_DIR>:/models/DeepSeek-V3 -w /workspace ${IMAGE}
# host2
docker run -it --name ${NAME}_host2 --ipc=host --gpus=all --network host --privileged --ulimit memlock=-1 --ulimit stack=67108864 -v ${PWD}:/workspace -v <YOUR_MODEL_DIR>:/models/DeepSeek-V3 -w /workspace ${IMAGE}
```

Set up ssh inside the container

```bash
apt-get update && apt-get install -y openssh-server

# modify /etc/ssh/sshd_config
PermitRootLogin yes
PubkeyAuthentication yes
# modify /etc/ssh/sshd_config, change default port 22 to another unused port
port 2233

# modify /etc/ssh
```

Generate ssh key on host1 and copy to host2, vice versa.

```bash
# on host1
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@<HOST2>
# on host2
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@<HOST1>

# restart ssh service on host1 and host2
service ssh restart # or
/etc/init.d/ssh restart # or
systemctl restart ssh
```

Generate additional config for trtllm serve.
```bash
cat >/path/to/TensorRT-LLM/extra-llm-api-config.yml <<EOF
cuda_graph_config:
  padding_enabled: true
  batch_sizes:
    - 1
    - 2
    - 4
    - 8
    - 16
    - 32
    - 64
    - 128
print_iter_log: true
enable_attention_dp: true
EOF
```


After the preparations,you can run the trtllm-serve on two nodes using mpirun:

```bash
mpirun -np 16 \
-H <HOST1>:8,<HOST2>:8 \
-mca plm_rsh_args "-p 2233" \
--allow-run-as-root \
trtllm-llmapi-launch trtllm-serve serve \
--backend pytorch \
--tp_size 16 \
--ep_size 8 \
--kv_cache_free_gpu_memory_fraction 0.95 \
--trust_remote_code \
--max_batch_size 128 \
--max_num_tokens 4096 \
--extra_llm_api_options /path/to/TensorRT-LLM/extra-llm-api-config.yml \
--port 8000 \
<YOUR_MODEL_DIR> 
```

### Other Frameworks

Kimi-K2 reuses the `DeepSeekV3CausalLM` architecture and convert it's weight into proper shape to save redevelopment effort. To let inference engines distinguish it from DeepSeek-V3 and apply the best optimizations, we set `"model_type": "kimi_k2"` in `config.json`.

If you are using a framework that is not on the recommended list, you can still run the model by manually changing `model_type` to "deepseek_v3" in `config.json` as a temporary workaround. You may need to manually parse tool calls in case no tool call parser is available in your framework.

---

## Tool Calling

To enable the tool calling feature, you may need to set certain tool calling parser options when starting the service. See the [deployment sections](#deployment) above for details.

In Kimi-K2, a tool calling process includes:
- Passing function descriptions to Kimi-K2
- Kimi-K2 decides to make a function call and returns the necessary information for the function call to the user
- The user performs the function call, collects the call results, and passes the function call results to Kimi-K2
- Kimi-K2 continues to generate content based on the function call results until the model believes it has obtained sufficient information to respond to the user

### Preparing Tools

Suppose we have a function `get_weather` that can query the weather conditions in real-time. 
This function accepts a city name as a parameter and returns the weather conditions. We need to prepare a structured description for it so that Kimi-K2 can understand its functionality.

```python
def get_weather(city):
    return {"weather": "Sunny"}

# Collect the tool descriptions in tools
tools = [{
    "type": "function",
    "function": {        
        "name": "get_weather", 
        "description": "Get weather information. Call this tool when the user needs to get weather information", 
         "parameters": {
              "type": "object",
              "required": ["city"], 
              "properties": { 
                  "city": { 
                      "type": "string", 
                      "description": "City name", 
                }
            }
        }
    }
}]

# Tool name->object mapping for easy calling later
tool_map = {
    "get_weather": get_weather
}
```

### Chat with Tools

We use `openai.OpenAI` to send messages to Kimi-K2 along with tool descriptions. Kimi-K2 will autonomously decide whether to use and how to use the provided tools. 
If Kimi-K2 believes a tool call is needed, it will return a result with `finish_reason='tool_calls'`. At this point, the returned result includes the tool call information. 
After calling tools with the provided information, we then need to append the tool call results to the chat history and continue calling Kimi-K2. 
Kimi-K2 may need to call tools multiple times until the model believes the current results can answer the user's question. We should check `finish_reason` until it is not `tool_calls`.

The results obtained by the user after calling the tools should be added to `messages` with `role='tool'`.

```python
import json
from openai import OpenAI
model_name='moonshotai/Kimi-K2-Instruct'
client = OpenAI(base_url=endpoint, 
                        api_key='xxx')

messages = [
{"role": "user", "content": "What's the weather like in Beijing today? Let's check using the tool."}
]
finish_reason = None
while finish_reason is None or finish_reason == "tool_calls":
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.3,
        tools=tools, 
        tool_choice="auto",
    )
    choice = completion.choices[0]
    finish_reason = choice.finish_reason
    # Note: The finish_reason when tool calls end may vary across different engines, so this condition check needs to be adjusted accordingly
    if finish_reason == "tool_calls": 
        messages.append(choice.message)
        for tool_call in choice.message.tool_calls: 
            tool_call_name = tool_call.function.name
            tool_call_arguments = json.loads(tool_call.function.arguments) 
            tool_function = tool_map[tool_call_name] 
            tool_result = tool_function(tool_call_arguments)
            print("tool_result", tool_result)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call_name,
                "content": json.dumps(tool_result), 
            })
print('-' * 100)
print(choice.message.content)
```

### Tool Calling in Streaming Mode

Tool calling can also be used in streaming mode. In this case, we need to collect the tool call information returned in the stream until we have a complete tool call. Please refer to the code below:

```python
messages = [
    {"role": "user", "content": "What's the weather like in Beijing today? Let's check using the tool."}
]
finish_reason = None
msg = ''
while finish_reason is None or finish_reason == "tool_calls":
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.3,
        tools=tools,
        tool_choice="auto",
        stream=True 
    )
    tool_calls = []
    for chunk in completion:
        delta = chunk.choices[0].delta
        if delta.content:
            msg += delta.content
        if delta.tool_calls:
            for tool_call_chunk in delta.tool_calls:
                if tool_call_chunk.index is not None:
                    # Extend the tool_calls list
                    while len(tool_calls) <= tool_call_chunk.index:
                        tool_calls.append({
                            "id": "",
                            "type": "function",
                            "function": {
                                "name": "",
                                "arguments": ""
                            }
                        })

                    tc = tool_calls[tool_call_chunk.index]

                    if tool_call_chunk.id:
                        tc["id"] += tool_call_chunk.id
                    if tool_call_chunk.function.name:
                        tc["function"]["name"] += tool_call_chunk.function.name
                    if tool_call_chunk.function.arguments:
                        tc["function"]["arguments"] += tool_call_chunk.function.arguments

        finish_reason = chunk.choices[0].finish_reason
    # Note: The finish_reason when tool calls end may vary across different engines, so this condition check needs to be adjusted accordingly
    if finish_reason == "tool_calls":
        for tool_call in tool_calls:
            tool_call_name = tool_call['function']['name']
            tool_call_arguments = json.loads(tool_call['function']['arguments'])
            tool_function = tool_map[tool_call_name] 
            tool_result = tool_function(tool_call_arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call['id'],
                "name": tool_call_name,
                "content": json.dumps(tool_result),
            })
        # The text generated by the tool call is not the final version, reset msg
        msg = ''

    print(msg)
```

### Manually Parsing Tool Calls

The tool call requests generated by Kimi-K2 can also be parsed manually, which is especially useful when the service you are using does not provide a tool-call parser. 
The tool call requests generated by Kimi-K2 are wrapped by `<|tool_calls_section_begin|>` and `<|tool_calls_section_end|>`, 
with each tool call wrapped by `<|tool_call_begin|>` and `<|tool_call_end|>`. The tool ID and arguments are separated by `<|tool_call_argument_begin|>`. 
The format of the tool ID is `functions.{func_name}:{idx}`, from which we can parse the function name.

Based on the above rules, we can directly post a request to the completions interface and manually parse tool calls.

```python
import requests
from transformers import AutoTokenizer
messages = [
    {"role": "user", "content": "What's the weather like in Beijing today? Let's check using the tool."}
]
msg = ''
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
while True:
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        tools=tools,
        add_generation_prompt=True,
    )
    payload = {
        "model": model_name,
        "prompt": text,
        "max_tokens": 512
    }
    response = requests.post(
        f"{endpoint}/completions",
        headers={"Content-Type": "application/json"},
        json=payload,
        stream=False,
    )
    raw_out = response.json()

    raw_output = raw_out["choices"][0]["text"]
    tool_calls = extract_tool_call_info(raw_output)
    if len(tool_calls) == 0:
        # No tool calls
        msg = raw_output
        break
    else:
        for tool_call in tool_calls:
            tool_call_name = tool_call['function']['name']
            tool_call_arguments = json.loads(tool_call['function']['arguments'])
            tool_function = tool_map[tool_call_name]
            tool_result = tool_function(tool_call_arguments)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call['id'],
                "name": tool_call_name,
                "content": json.dumps(tool_result), 
            })
print('-' * 100)          
print(msg)
```

Here, `extract_tool_call_info` parses the model output and returns the model call information. A simple implementation would be:

```python
def extract_tool_call_info(tool_call_rsp: str):
    if '<|tool_calls_section_begin|>' not in tool_call_rsp:
        # No tool calls
        return []
    import re
    pattern = r"<\|tool_calls_section_begin\|>(.*?)<\|tool_calls_section_end\|>"
    
    tool_calls_sections = re.findall(pattern, tool_call_rsp, re.DOTALL)
    
    # Extract multiple tool calls
    func_call_pattern = r"<\|tool_call_begin\|>\s*(?P<tool_call_id>[\w\.]+:\d+)\s*<\|tool_call_argument_begin\|>\s*(?P<function_arguments>.*?)\s*<\|tool_call_end\|>"
    tool_calls = []
    for match in re.findall(func_call_pattern, tool_calls_sections[0], re.DOTALL):
        function_id, function_args = match
        # function_id: functions.get_weather:0
        function_name = function_id.split('.')[1].split(':')[0]
        tool_calls.append(
            {
                "id": function_id,
                "type": "function",
                "function": {
                    "name": function_name,
                    "arguments": function_args
                }
            }
        )  
    return tool_calls
```
