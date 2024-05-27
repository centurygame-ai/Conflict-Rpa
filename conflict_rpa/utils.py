import os
from openai import OpenAI, NOT_GIVEN

if os.environ.get("OPENAI_API_KEY") is None:
    raise Exception("在运行之前， 配置一下你的 OPENAI_API_KEY. 例如 export OPENAI_API_KEY=sk-XXXXXXX")

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE") if os.environ.get("OPENAI_API_BASE") else None
)


def _base_message(role, content):
    return {"role": role, "content": content}


def UserMessage(content):
    return _base_message("user", content)


class LLMParams:
    def __init__(
            self,
            model="gpt-4-turbo-preview",
            temperature=0.2,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            json_mode=False,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.json_mode = json_mode

    def from_dict(params):
        model = params.get("model", "gpt-4-1106-preview")
        temperature = params.get("temperature", 0.2)
        max_tokens = params.get("max_tokens", 256)
        top_p = params.get("top_p", 1)
        frequency_penalty = params.get("frequency_penalty", 0)
        presence_penalty = params.get("presence_penalty", 0)
        json_mode = params.get("json_mode", False)
        return LLMParams(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            json_mode=json_mode,
        )

    def to_dict(self):
        return vars(self)

    def copy(self, **params):
        # copy一份和当前参数一样的数据，并且支持参数的调整
        new_params = self.to_dict().copy()
        new_params.update(params)
        return LLMParams(**new_params)

    def on_attempt(self, attempt):
        """根据重试次数自适应参数变化"""
        # 改变温度
        assert attempt >= 0
        if self.temperature <= 0.9:
            new_temperature = self.temperature + 0.01 * attempt

        new_model = self.model
        if attempt >= 2 and new_model == "gpt-4-0125-preview":
            new_model = "gpt-4-1106-preview"
            if attempt >= 4:
                new_model = "gpt-4-0613"
        return self.copy(model=new_model, temperature=new_temperature)


async def async_chat(
        messages,
        llm_params=LLMParams(),
        stream=False,
        auto_decode=False,
        auto_retry=True,
):
    """异步聊天"""
    response = client.chat.completions.create(
        messages=messages,
        model=llm_params.model if llm_params.model else 'gpt-4-1106-preview',
        response_format={"type": "json_object"} if llm_params.json_mode else NOT_GIVEN
    )

    result = response.choices[0].message.content
    return result
