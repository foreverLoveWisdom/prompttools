# Copyright (c) Hegel AI, Inc.
# All rights reserved.
#
# This source code's license can be found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Dict, List, Optional
import openai

from prompttools.selector.prompt_selector import PromptSelector
from prompttools.mock.mock import mock_openai_completion_fn
from .experiment import Experiment


class OpenAICompletionExperiment(Experiment):
    r"""
    This class defines an experiment for OpenAI's completion API.
    It accepts lists for each argument passed into OpenAI's API, then creates
    a cartesian product of those arguments, and gets results for each.

    Note:
        - All arguments here should be a ``list``, even if you want to keep the argument frozen
          (i.e. ``temperature=[1.0]``), because the experiment will try all possible combination
          of the input arguments.
    """

    def __init__(
        self,
        model: List[str],
        prompt: List[str],
        suffix: Optional[List[str]] = [None],
        max_tokens: Optional[List[int]] = [float("inf")],
        temperature: Optional[List[float]] = [1.0],
        top_p: Optional[List[float]] = [1.0],
        n: Optional[List[int]] = [1],
        stream: Optional[List[bool]] = [False],
        logprobs: Optional[List[int]] = [None],
        echo: Optional[List[bool]] = [False],
        stop: Optional[List[List[str]]] = [None],
        presence_penalty: Optional[List[float]] = [0],
        frequency_penalty: Optional[List[float]] = [0],
        best_of: Optional[List[int]] = [1],
        logit_bias: Optional[Dict] = [None],
    ):
        self.completion_fn = openai.Completion.create
        if os.getenv("DEBUG", default=False):
            self.completion_fn = mock_openai_completion_fn

        # If we are using a prompt selector, we need to render
        # messages, as well as create prompt_keys to map the messages
        # to corresponding prompts in other models.
        if isinstance(prompt[0], PromptSelector):
            self.prompt_keys = {
                selector.for_openai_completion(): selector.for_openai_completion() for selector in prompt
            }
            prompt = [selector.for_openai_completion() for selector in prompt]
        else:
            self.prompt_keys = prompt

        self.all_args = dict(
            model=model,
            prompt=prompt,
            suffix=suffix,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            n=n,
            stream=stream,
            logprobs=logprobs,
            echo=echo,
            stop=stop,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            best_of=best_of,
            logit_bias=logit_bias,
        )
        super().__init__()

    @staticmethod
    def _extract_responses(output: Dict[str, object]) -> list[str]:
        return [choice["text"] for choice in output["choices"]][0]

    def _get_model_names(self):
        return [combo["model"] for combo in self.argument_combos]
