# vLLM servers: start lines and sampling settings as logged

## base

- version line: `v0.30.0`
- start line: `(APIServer pid=4629) INFO 10-23 21:36:38 [api_utils.py:286] non-default args: {'model_tag': '/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9/', 'max_log_len': 300, 'model': '/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9/', 'dtype': 'bfloat16', 'seed': 20260928, 'max_model_len': 32768, 'served_model_name': ['target'], 'generation_config': 'vllm', 'language_model_only': True, 'max_num_seqs': 256, 'enable_log_requests': True}`

| requests | temperature | top_p | top_k (0 = off) | min_p | rep. pen. | presence | frequency | max_tokens |
|---|---|---|---|---|---|---|---|---|
| 500 | 1.0 | 1.0 | -1 | 0.0 | 1.0 | 0.0 | 0.0 | 4096 |
| 500 | 0.7 | 1.0 | -1 | 0.0 | 1.0 | 0.0 | 0.0 | 4096 |
| 500 | 1.0 | 1.0 | -1 | 0.05 | 1.0 | 0.0 | 0.0 | 4096 |
| 320 | 1.0 | 1.0 | -1 | 0.05 | 1.0 | 0.0 | 0.0 | 400 |
| 200 | 0.0 | 1.0 | 0 | 0.0 | 1.0 | 0.0 | 0.0 | 4096 |
| 100 | 0.0 | 1.0 | 0 | 0.0 | 1.0 | 0.0 | 0.0 | 1024 |

Example request lines:

    (APIServer pid=4629) INFO 10-23 21:42:45 [request_logger.py:63] Received request cmpl-beaac4079f061994-0: params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.0, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=0, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=1024, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None), lora_request: None.
    (APIServer pid=4629) INFO 10-23 21:42:45 [request_logger.py:63] Received request cmpl-9607cee5be84a1ed-0: params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.0, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=2447120294, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=4096, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None), lora_request: None.
    (APIServer pid=4629) INFO 10-23 21:42:46 [request_logger.py:63] Received request cmpl-bedd1156ecf7ce40-0: params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=1.0, top_k=-1, min_p=0.0, seed=3371652057, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=4096, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None), lora_request: None.
    (APIServer pid=4629) INFO 10-23 21:42:46 [request_logger.py:63] Received request cmpl-89bb6db2bdaeda3c-0: params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=-1, min_p=0.0, seed=1854377605, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=4096, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None), lora_request: None.
    (APIServer pid=4629) INFO 10-23 21:43:45 [request_logger.py:63] Received request cmpl-92135da25c487712-0: params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=1.0, top_k=-1, min_p=0.05, seed=1251013285, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=4096, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None), lora_request: None.
    (APIServer pid=4629) INFO 10-23 21:44:53 [request_logger.py:63] Received request cmpl-b68665bbe5f4acd3-0: params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=1.0, top_k=-1, min_p=0.05, seed=124004070, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=400, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None), lora_request: None.

## hc_db_s0

- version line: `v0.30.0`
- start line: `(APIServer pid=13068) INFO 10-23 22:00:48 [api_utils.py:286] non-default args: {'model_tag': '/scratch/r05/merged/hc_db_s0', 'max_log_len': 300, 'model': '/scratch/r05/merged/hc_db_s0', 'dtype': 'bfloat16', 'seed': 20260928, 'max_model_len': 32768, 'served_model_name': ['target'], 'generation_config': 'vllm', 'max_num_seqs': 256, 'enable_log_requests': True}`

| requests | temperature | top_p | top_k (0 = off) | min_p | rep. pen. | presence | frequency | max_tokens |
|---|---|---|---|---|---|---|---|---|
| 500 | 1.0 | 1.0 | -1 | 0.0 | 1.0 | 0.0 | 0.0 | 4096 |
| 500 | 0.7 | 1.0 | -1 | 0.0 | 1.0 | 0.0 | 0.0 | 4096 |
| 500 | 1.0 | 1.0 | -1 | 0.05 | 1.0 | 0.0 | 0.0 | 4096 |
| 200 | 0.0 | 1.0 | 0 | 0.0 | 1.0 | 0.0 | 0.0 | 4096 |
| 160 | 1.0 | 1.0 | -1 | 0.05 | 1.0 | 0.0 | 0.0 | 400 |

Example request lines:

    (APIServer pid=13068) INFO 10-23 22:03:37 [request_logger.py:63] Received request cmpl-b61eda5aac5cd113-0: params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=1.0, top_k=-1, min_p=0.0, seed=1251013285, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=4096, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None), lora_request: None.
    (APIServer pid=13068) INFO 10-23 22:03:38 [request_logger.py:63] Received request cmpl-824aba7f10a20b21-0: params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=-1, min_p=0.0, seed=1854377605, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=4096, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None), lora_request: None.
    (APIServer pid=13068) INFO 10-23 22:03:38 [request_logger.py:63] Received request cmpl-8dcade40b891b17b-0: params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.0, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=18642032, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=4096, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None), lora_request: None.
    (APIServer pid=13068) INFO 10-23 22:03:39 [request_logger.py:63] Received request cmpl-807405f4731e95cb-0: params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=1.0, top_k=-1, min_p=0.05, seed=3835888678, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=400, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None), lora_request: None.
    (APIServer pid=13068) INFO 10-23 22:03:53 [request_logger.py:63] Received request cmpl-ad3ad3e380d65261-0: params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=1.0, top_k=-1, min_p=0.05, seed=1251013285, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=4096, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None), lora_request: None.

## hb_dc_s0

- version line: `v0.30.0`
- start line: `(APIServer pid=18601) INFO 10-23 22:13:36 [api_utils.py:286] non-default args: {'model_tag': '/scratch/r05/merged/hb_dc_s0', 'max_log_len': 300, 'model': '/scratch/r05/merged/hb_dc_s0', 'dtype': 'bfloat16', 'seed': 20260928, 'max_model_len': 32768, 'served_model_name': ['target'], 'generation_config': 'vllm', 'max_num_seqs': 256, 'enable_log_requests': True}`

| requests | temperature | top_p | top_k (0 = off) | min_p | rep. pen. | presence | frequency | max_tokens |
|---|---|---|---|---|---|---|---|---|
| 500 | 1.0 | 1.0 | -1 | 0.0 | 1.0 | 0.0 | 0.0 | 4096 |
| 500 | 0.7 | 1.0 | -1 | 0.0 | 1.0 | 0.0 | 0.0 | 4096 |
| 500 | 1.0 | 1.0 | -1 | 0.05 | 1.0 | 0.0 | 0.0 | 4096 |
| 200 | 0.0 | 1.0 | 0 | 0.0 | 1.0 | 0.0 | 0.0 | 4096 |
| 160 | 1.0 | 1.0 | -1 | 0.05 | 1.0 | 0.0 | 0.0 | 400 |

Example request lines:

    (APIServer pid=18601) INFO 10-23 22:16:27 [request_logger.py:63] Received request cmpl-967edcf28ab71141-0: params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.0, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=752987642, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=4096, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None), lora_request: None.
    (APIServer pid=18601) INFO 10-23 22:16:27 [request_logger.py:63] Received request cmpl-90bc0bff467033df-0: params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=1.0, top_k=-1, min_p=0.05, seed=124004070, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=400, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None), lora_request: None.
    (APIServer pid=18601) INFO 10-23 22:16:27 [request_logger.py:63] Received request cmpl-bb97a0a838f8200f-0: params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=1.0, top_k=-1, min_p=0.0, seed=1251013285, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=4096, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None), lora_request: None.
    (APIServer pid=18601) INFO 10-23 22:16:27 [request_logger.py:63] Received request cmpl-a79b63bac193c626-0: params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=-1, min_p=0.0, seed=1251013285, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=4096, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None), lora_request: None.
    (APIServer pid=18601) INFO 10-23 22:17:02 [request_logger.py:63] Received request cmpl-92d6869feafce127-0: params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=1.0, top_k=-1, min_p=0.05, seed=1251013285, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=4096, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None), lora_request: None.

