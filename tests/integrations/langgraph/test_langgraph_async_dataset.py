import os
import asyncio
import time
from deepeval.integrations.langchain.callback import CallbackHandler
from deepeval.metrics import TaskCompletionMetric
import deepeval
from langgraph.prebuilt import create_react_agent
from deepeval.evaluate import dataset, test_run
from deepeval.dataset import Golden
from deepeval.evaluate.configs import AsyncConfig


task_completion = TaskCompletionMetric(
    threshold=0.7, model="gpt-4o-mini", include_reason=True
)


def get_weather(city: str) -> str:
    """Returns the weather in a city"""
    return f"It's always sunny in {city}!"


agent = create_react_agent(
    model="openai:gpt-4o-mini",
    tools=[get_weather],
    prompt="You are a helpful assistant",
)

goldens = [
    Golden(input="What is the weather in Bogotá, Colombia?"),
    Golden(input="What is the weather in Paris, France?"),
]


def main():
    for golden in dataset(goldens=goldens):
        test_run.append(
            asyncio.create_task(
                agent.ainvoke(
                    input={
                        "messages": [{"role": "user", "content": golden.input}]
                    },
                    config={
                        "callbacks": [
                            CallbackHandler(
                                metrics=[task_completion],
                                metric_collection="task_completion",
                            )
                        ]
                    },
                )
            )
        )


if __name__ == "__main__":
    main()
    time.sleep(7)
