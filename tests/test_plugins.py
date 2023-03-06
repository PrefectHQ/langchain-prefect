from langchain.llms import OpenAI

from prefect_langchain.plugins import llm_invocation_summary


class TestParseInvocationSummary:
    def test_parse_callable_llm(self):
        """Test that LLM invocation summary is parsed correctly using a callable LLM."""
        llm_input = "What would be a good name for a company that makes colorful socks?"

        artifact = llm_invocation_summary(OpenAI(), llm_input)

        assert artifact.content["llm_endpoint"] == "langchain.llms.openai"
        assert artifact.content["text_input"] == llm_input
